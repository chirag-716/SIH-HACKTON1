# GUVNL Queue Management System

A comprehensive digital queue management solution for Gujarat Urja Vikas Nigam Limited (GUVNL) offices.

## 🏗️ Project Structure

```
guvnl-queue-management/
├── backend/                 # Python Flask API server
│   ├── app/                # Application factory and main app
│   ├── config/             # Configuration files
│   ├── models/             # Database models
│   ├── routes/             # API route handlers
│   ├── services/           # Business logic services
│   ├── utils/              # Utility functions
│   └── migrations/         # Database migrations
├── frontend/               # React web application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API service functions
│   │   ├── utils/          # Utility functions
│   │   └── hooks/          # Custom React hooks
│   └── public/             # Static assets
├── mobile-app/             # React Native mobile application
├── database/               # Database schemas and seed data
├── deployment/             # Docker and deployment configurations
├── docs/                   # Additional documentation
└── tests/                  # Test files and configurations

```

## 🚀 Features

- **Online Appointment Booking**: Citizens can book appointments through web/mobile
- **Digital Token System**: Automated token generation with queue position tracking
- **Real-time Updates**: Live queue status and waiting time estimates
- **Admin Dashboard**: Staff interface for queue management and analytics
- **Multi-channel Notifications**: SMS, Email, and Push notifications
- **Performance Analytics**: Comprehensive metrics and reporting
- **Mobile-first Design**: Responsive web app and native mobile application

## 🛠️ Technology Stack

### Backend
- **Python Flask** - REST API framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Celery** - Background task processing
- **SocketIO** - Real-time communication

### Frontend
- **React + TypeScript** - Web application
- **Material-UI** - UI component library
- **React Query** - Data fetching and caching
- **Redux Toolkit** - State management

### Mobile
- **React Native** - Cross-platform mobile app
- **Expo** - Development and deployment platform

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Web server and load balancer
- **GitHub Actions** - CI/CD pipeline

## 📋 Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.9+ and pip
- PostgreSQL 13+
- Redis 6+
- Docker and Docker Compose (for deployment)

## 🏃‍♂️ Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Mobile App Setup
```bash
cd mobile-app
npm install
npx expo start
```

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📚 API Documentation

API documentation is available at `http://localhost:5000/api/docs` when running the backend server.

## 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test

# Integration tests
cd tests && python -m pytest
```

## 🔧 Configuration

Configuration files are located in:
- Backend: `backend/config/`
- Frontend: `frontend/src/config/`
- Deployment: `deployment/`

## 📈 Monitoring

The system includes built-in monitoring with:
- Application performance metrics
- Queue analytics dashboard
- Error tracking and logging
- Health check endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For technical support or questions, please contact the development team or create an issue in the repository.