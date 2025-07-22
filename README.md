# User Management System

A modern, secure user management system built with FastAPI, MongoDB, and vanilla JavaScript.

## 🚀 Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 👥 **User Management** - Complete CRUD operations for users
- 🛡️ **Role-Based Access Control** - Admin and user roles with proper permissions
- 📱 **Responsive UI** - Modern, mobile-friendly interface with Tailwind CSS
- 🐳 **Docker Support** - Easy deployment with Docker Compose
- 🔒 **Security Best Practices** - Password hashing, input validation, CORS protection
- 📊 **Health Checks** - Built-in health monitoring endpoints
- 🎯 **SOP Tools** - Standard Operating Procedures integration
- 🌐 **Network Flexible** - Works with localhost and IP addresses

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework with automatic API documentation
- **MongoDB** - NoSQL database with proper connection pooling
- **JWT** - JSON Web Tokens for secure authentication
- **Pydantic v2** - Data validation and serialization
- **Passlib** - Secure password hashing with bcrypt
- **Uvicorn** - High-performance ASGI server

### Frontend
- **Vanilla JavaScript** - No framework dependencies, lightweight and fast
- **Tailwind CSS** - Utility-first CSS framework for rapid UI development
- **Responsive Design** - Mobile-first approach with proper breakpoints

### Infrastructure
- **Docker & Docker Compose** - Containerization for easy deployment
- **Nginx** - Web server, reverse proxy, and load balancer
- **MongoDB** - Database with authentication and health checks

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- At least 2GB RAM available

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd user-management-system
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration if needed
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - **Frontend**: http://localhost:8080 or http://YOUR_IP:8080
   - **Backend API**: http://localhost:8000 or http://YOUR_IP:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Alternative API Docs**: http://localhost:8000/redoc

### 🔑 Default Admin Account
- **Username**: `sysadmin`
- **Password**: `admin123`

⚠️ **CRITICAL**: Change the default admin password immediately in production!

## 🌐 Network Access

The application supports both localhost and IP address access:

- **Localhost**: http://localhost:8080
- **IP Address**: http://192.168.130.21:8080 (replace with your actual IP)
- **LAN Access**: Accessible from other devices on the same network

### Network Configuration
If accessing via IP address, ensure:
1. Your IP is added to `ALLOWED_ORIGINS` in docker-compose.yml
2. Firewall allows traffic on ports 8080 and 8000
3. Docker containers can communicate properly

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/login` - User login (returns JWT token)
- `POST /api/v1/register` - User registration
- `GET /api/v1/profile` - Get current user profile
- `PUT /api/v1/profile` - Update current user profile

### Admin Endpoints (Requires Admin Role)
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users` - Create new user
- `GET /api/v1/admin/users/{id}` - Get user by ID
- `PUT /api/v1/admin/users/{id}` - Update user
- `DELETE /api/v1/admin/users/{id}` - Delete user

### System Endpoints
- `GET /health` - Application health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Application entry point
│   ├── config.py           # Configuration management
│   ├── database.py         # MongoDB connection handling
│   ├── models.py           # Pydantic models and validation
│   ├── auth.py             # Authentication and authorization
│   ├── routes/             # API route handlers
│   │   ├── user.py         # User-related endpoints
│   │   └── admin.py        # Admin-only endpoints
│   ├── services/           # Business logic services
│   │   └── admin.py        # Admin service functions
│   └── requirements.txt    # Python dependencies
├── frontend/               # Static web frontend
│   ├── index.html          # Login page
│   ├── register.html       # User registration
│   ├── dashboard.html      # User dashboard
│   ├── admin.html          # Admin panel
│   ├── gift_sop.html       # SOP checklist tool
│   └── js/
│       └── api.js          # API client library
├── dockerfile              # Backend container definition
├── docker-compose.yml      # Multi-container orchestration
├── nginx.conf             # Nginx web server configuration
├── .env.example           # Environment variables template
└── README.md              # This documentation
```

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure, stateless authentication
- **Password Hashing**: Bcrypt with salt for password security
- **Role-Based Access**: Admin and user roles with proper permissions
- **Token Expiration**: Configurable token lifetime (default: 30 minutes)

### Input Validation & Security
- **Pydantic Validation**: Comprehensive input validation and sanitization
- **SQL Injection Prevention**: MongoDB with parameterized queries
- **XSS Protection**: Proper input escaping and validation
- **CORS Configuration**: Configurable cross-origin resource sharing

### Infrastructure Security
- **Security Headers**: Nginx security headers (X-Frame-Options, etc.)
- **Rate Limiting**: Built-in FastAPI rate limiting capabilities
- **Health Checks**: Container health monitoring
- **Non-root User**: Docker containers run as non-root user

## 🚀 Development

### Local Development Setup

1. **Backend Development**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   # Serve with any static file server
   python -m http.server 8080
   # Or use Node.js
   npx serve -p 8080
   ```

3. **Database Development**
   ```bash
   # Start only MongoDB
   docker-compose up -d mongo
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_HOST` | MongoDB hostname | `mongo` |
| `MONGO_PORT` | MongoDB port | `27017` |
| `MONGO_USERNAME` | MongoDB username | `admin` |
| `MONGO_PASSWORD` | MongoDB password | `admin` |
| `MONGO_DB_NAME` | Database name | `appdb` |
| `SECRET_KEY` | JWT secret key | `your-secret-key...` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:8080,...` |

## 🐳 Docker Management

### Basic Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# View running containers
docker-compose ps
```

### Database Management

**Connect to MongoDB**
```bash
docker exec -it mongodb mongosh -u admin -p admin --authenticationDatabase admin
```

**Database Operations**
```bash
# Backup database
docker exec mongodb mongodump --username admin --password admin --authenticationDatabase admin --db appdb --out /backup

# Restore database
docker exec mongodb mongorestore --username admin --password admin --authenticationDatabase admin --db appdb /backup/appdb
```

## 🌐 Production Deployment

### Environment Configuration
Create a production `.env` file:
```bash
# Strong secret key (generate with: openssl rand -hex 32)
SECRET_KEY=your-very-long-and-random-secret-key-here

# Strong MongoDB password
MONGO_PASSWORD=your-strong-mongodb-password

# Your domain origins
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Production database name
MONGO_DB_NAME=production_db
```

### Security Checklist
- [ ] Change default admin password (`sysadmin/admin123`)
- [ ] Set strong `SECRET_KEY` (use `openssl rand -hex 32`)
- [ ] Configure strong MongoDB password
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure proper CORS origins for your domain
- [ ] Enable MongoDB authentication in production
- [ ] Configure firewall rules (allow only necessary ports)
- [ ] Set up monitoring and logging
- [ ] Regular security updates
- [ ] Backup strategy implementation

### Performance Optimization
- [ ] Enable Nginx gzip compression
- [ ] Configure proper caching headers
- [ ] Set up MongoDB indexes for frequently queried fields
- [ ] Monitor resource usage and scale as needed
- [ ] Implement rate limiting for API endpoints

## 📊 Monitoring & Troubleshooting

### Health Checks
- **Backend**: `GET /health` - Returns application status
- **Frontend**: `GET /health` - Returns Nginx status
- **Database**: Built-in MongoDB health checks in Docker

### Log Management
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongo

# Follow logs in real-time
docker-compose logs -f backend
```

### Common Issues & Solutions

1. **"Cannot connect to backend"**
   - Check if backend container is running: `docker-compose ps`
   - Verify network connectivity: `docker-compose logs backend`
   - Ensure MongoDB is accessible: `docker-compose logs mongo`

2. **"Authentication failed"**
   - Verify JWT secret key configuration
   - Check token expiration settings
   - Validate user credentials in database

3. **"CORS errors when accessing via IP"**
   - Add your IP to `ALLOWED_ORIGINS` in docker-compose.yml
   - Restart containers: `docker-compose restart`

4. **"Database connection refused"**
   - Verify MongoDB container is running and healthy
   - Check MongoDB credentials in environment variables
   - Ensure database initialization completed

### Reset Everything
```bash
# Complete reset (removes all data)
docker-compose down -v
docker system prune -f
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add docstrings to functions and classes
- Update documentation for new features
- Test your changes thoroughly

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- **Issues**: Create an issue in the repository
- **Documentation**: Check this README and API docs at `/docs`
- **Logs**: Check application logs for error details
- **Community**: Contribute to discussions and improvements

## 🔄 Changelog

### v1.0.0 (Current)
- Initial release with full user management
- JWT authentication system
- Admin panel with user CRUD operations
- Docker containerization
- Responsive web interface
- SOP tools integration
- Network flexibility (localhost + IP access)

---

**Made with ❤️ for efficient user management**