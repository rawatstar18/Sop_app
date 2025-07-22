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

    // SOP Activity methods
    async logSOPActivity(sopType, taskId, taskDescription) {
        return await this.request('/sop/activity', {
            method: 'POST',
            body: JSON.stringify({
                sop_type: sopType,
                task_id: taskId,
                task_description: taskDescription
            }),
        });
    }

    async getUserSOPActivities(sopType = null) {
        const endpoint = sopType ? `/sop/activities?sop_type=${sopType}` : '/sop/activities';
        return await this.request(endpoint);
    }

    // Admin SOP methods
    async getAllSOPActivities(sopType = null, userId = null, days = 30) {
        let endpoint = `/admin/sop/activities?days=${days}`;
        if (sopType) endpoint += `&sop_type=${sopType}`;
        if (userId) endpoint += `&user_id=${userId}`;
        return await this.request(endpoint);
    }

    async downloadSOPReport(sopType = null, userId = null, days = 30, format = 'csv') {
        let endpoint = `/admin/sop/report?format=${format}&days=${days}`;
        if (sopType) endpoint += `&sop_type=${sopType}`;
        if (userId) endpoint += `&user_id=${userId}`;
        
        const url = `${this.baseURL}${endpoint}`;
        const response = await fetch(url, {
            headers: this.getHeaders(),
        });
        
        if (!response.ok) {
            throw new Error('Failed to download report');
        }
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `sop_report_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
    }

    async getSOPSummary(sopType = null, days = 30) {
        let endpoint = `/admin/sop/summary?days=${days}`;
        if (sopType) endpoint += `&sop_type=${sopType}`;
        return await this.request(endpoint);
    }
}

// Global API client instance
const api = new ApiClient();