class ApiClient {
    constructor() {
        // Dynamically determine the API base URL
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        const port = hostname === 'localhost' || hostname === '127.0.0.1' ? '8000' : '8000';
        this.baseURL = `${protocol}//${hostname}:${port}/api/v1`;
        this.token = localStorage.getItem('access_token');
    }

    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('access_token', token);
        } else {
            localStorage.removeItem('access_token');
        }
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options,
        };

        console.log('Making API request to:', url);
        
        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                this.setToken(null);
                window.location.href = '/index.html';
                return;
            }
            
            const data = await response.json();
            
            if (!response.ok) {
                console.error('API request failed:', response.status, data);
                throw new Error(data.detail || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Auth methods
    async login(username, password) {
        const response = await this.request('/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        
        if (response.access_token) {
            this.setToken(response.access_token);
            localStorage.setItem('user', JSON.stringify(response.user));
        }
        
        return response;
    }

    async register(formData) {
        return await this.request('/register', {
            method: 'POST',
            headers: {}, // Let browser set content-type for FormData
            body: formData,
        });
    }

    async getProfile() {
        return await this.request('/profile');
    }

    async updateProfile(formData) {
        return await this.request('/profile', {
            method: 'PUT',
            headers: {}, // Let browser set content-type for FormData
            body: formData,
        });
    }

    // Admin methods
    async getUsers() {
        return await this.request('/admin/users');
    }

    async createUser(userData) {
        return await this.request('/admin/users', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    async updateUser(userId, userData) {
        return await this.request(`/admin/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(userData),
        });
    }

    async deleteUser(userId) {
        return await this.request(`/admin/users/${userId}`, {
            method: 'DELETE',
        });
    }

    async getUserById(userId) {
        return await this.request(`/admin/users/${userId}`);
    }

    logout() {
        this.setToken(null);
        localStorage.removeItem('user');
        window.location.href = '/index.html';
    }

    isAuthenticated() {
        return !!this.token;
    }

    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
}

// Global API client instance
const api = new ApiClient();