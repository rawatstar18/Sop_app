# User Management System

A modern, secure user management system built with FastAPI, MongoDB, and vanilla JavaScript.

## Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 👥 **User Management** - Complete CRUD operations for users
- 🛡️ **Role-Based Access Control** - Admin and user roles
- 📱 **Responsive UI** - Modern, mobile-friendly interface
- 🐳 **Docker Support** - Easy deployment with Docker Compose
- 🔒 **Security Best Practices** - Password hashing, input validation, CORS protection
- 📊 **Health Checks** - Built-in health monitoring
- 🎯 **SOP Tools** - Standard Operating Procedures integration

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **JWT** - JSON Web Tokens for authentication
- **Pydantic** - Data validation and serialization
- **Passlib** - Password hashing
- **Uvicorn** - ASGI server

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **Tailwind CSS** - Utility-first CSS framework
- **Nginx** - Web server and reverse proxy

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **MongoDB** - Database with replica set support

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd user-management-system
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Default Admin Account
- **Username**: `sysadmin`
- **Password**: `admin123`

⚠️ **Important**: Change the default admin password in production!

## API Endpoints

### Authentication
- `POST /api/v1/login` - User login
- `POST /api/v1/register` - User registration
- `GET /api/v1/profile` - Get user profile
- `PUT /api/v1/profile` - Update user profile

### Admin Endpoints
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users` - Create user
- `GET /api/v1/admin/users/{id}` - Get user by ID
- `PUT /api/v1/admin/users/{id}` - Update user
- `DELETE /api/v1/admin/users/{id}` - Delete user

### System
- `GET /health` - Health check

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # Pydantic models
│   ├── auth.py              # Authentication logic
│   ├── routes/
│   │   ├── user.py          # User routes
│   │   └── admin.py         # Admin routes
│   ├── services/
│   │   └── admin.py         # Admin services
│   ├── requirements.txt     # Python dependencies
│   └── dockerfile           # Backend Docker image
├── frontend/
│   ├── index.html           # Login page
│   ├── register.html        # Registration page
│   ├── dashboard.html       # User dashboard
│   ├── admin.html           # Admin panel
│   ├── gift_sop.html        # SOP checklist
│   └── js/
│       └── api.js           # API client
├── docker-compose.yml       # Docker services
├── nginx.conf              # Nginx configuration
└── README.md               # This file
```

## Security Features

- **Password Hashing**: Bcrypt with salt
- **JWT Tokens**: Secure token-based authentication
- **Input Validation**: Pydantic models with validation
- **CORS Protection**: Configurable CORS policies
- **SQL Injection Prevention**: MongoDB with proper queries
- **Rate Limiting**: Built-in FastAPI rate limiting
- **Security Headers**: Nginx security headers

## Development

### Local Development Setup

1. **Backend Development**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   # Serve with any static file server
   python -m http.server 8080
   ```

### Database Management

**Connect to MongoDB**
```bash
docker exec -it mongodb mongosh -u admin -p admin
```

**Backup Database**
```bash
docker exec mongodb mongodump --username admin --password admin --authenticationDatabase admin --db appdb --out /backup
```

## Production Deployment

### Environment Variables
Set these in production:
- `SECRET_KEY`: Strong secret key for JWT
- `MONGO_PASSWORD`: Strong MongoDB password
- `ALLOWED_ORIGINS`: Your domain origins

### Security Checklist
- [ ] Change default admin password
- [ ] Set strong SECRET_KEY
- [ ] Configure HTTPS
- [ ] Set up proper CORS origins
- [ ] Enable MongoDB authentication
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging

## Monitoring

### Health Checks
- Backend: `GET /health`
- Frontend: `GET /health`
- Database: Built-in MongoDB health checks

### Logs
```bash
# View application logs
docker-compose logs -f backend

# View nginx logs
docker-compose logs -f frontend

# View database logs
docker-compose logs -f mongo
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if services are running: `docker-compose ps`
   - Check logs: `docker-compose logs`

2. **Authentication Errors**
   - Verify JWT secret key
   - Check token expiration
   - Validate user credentials

3. **Database Connection Issues**
   - Verify MongoDB is running
   - Check connection string
   - Validate credentials

### Reset Everything
```bash
docker-compose down -v
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API docs at `/docs`