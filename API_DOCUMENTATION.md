# GUVNL Queue Management System - API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [WebSocket Events](#websocket-events)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

## Overview

The GUVNL Queue Management System provides a RESTful API for managing appointments, queues, and notifications for Gujarat Urja Vikas Nigam Limited offices.

**Base URL:** `http://localhost:5000/api` (Development)  
**Production URL:** `https://yourdomain.com/api`

**Content-Type:** `application/json`  
**Authentication:** JWT Bearer Token

## Authentication

### User Registration
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+919876543210",
  "address": "123 Street, City, State",
  "date_of_birth": "1990-01-01"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "citizen"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### User Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "identifier": "user@example.com",  // email or phone
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "citizen",
    "is_verified": true
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### Token Refresh
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | User login | No |
| POST | `/auth/refresh` | Refresh access token | Yes (Refresh) |
| POST | `/auth/logout` | User logout | Yes |
| GET | `/auth/profile` | Get user profile | Yes |
| PUT | `/auth/profile` | Update user profile | Yes |
| POST | `/auth/change-password` | Change password | Yes |

### Queue Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/queues` | Get all queues | No |
| GET | `/queues/{id}` | Get queue by ID | No |
| GET | `/queues/status` | Get queue status summary | No |
| POST | `/queues` | Create new queue | Yes (Admin) |
| PUT | `/queues/{id}` | Update queue | Yes (Staff) |
| DELETE | `/queues/{id}` | Delete queue | Yes (Admin) |

### Appointment Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/appointments` | Get user appointments | Yes |
| GET | `/appointments/{id}` | Get appointment details | Yes |
| POST | `/appointments` | Book new appointment | Yes |
| PUT | `/appointments/{id}` | Update appointment | Yes |
| DELETE | `/appointments/{id}` | Cancel appointment | Yes |
| POST | `/appointments/{id}/check-in` | Check in for appointment | Yes |

### Office & Service Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/offices` | Get all offices | No |
| GET | `/offices/{id}` | Get office details | No |
| GET | `/services` | Get all services | No |
| GET | `/services/{id}` | Get service details | No |
| GET | `/offices/{id}/services` | Get services by office | No |

### Admin Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/dashboard` | Get dashboard data | Yes (Staff+) |
| GET | `/admin/appointments` | Get all appointments | Yes (Staff+) |
| PUT | `/admin/appointments/{id}/status` | Update appointment status | Yes (Staff+) |
| GET | `/admin/metrics` | Get queue metrics | Yes (Staff+) |
| GET | `/admin/users` | Get all users | Yes (Admin+) |
| PUT | `/admin/users/{id}/role` | Update user role | Yes (Admin+) |

### Notification Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/notifications` | Get user notifications | Yes |
| PUT | `/notifications/{id}/read` | Mark notification as read | Yes |
| POST | `/notifications/send` | Send manual notification | Yes (Staff+) |

## Detailed API Examples

### Book an Appointment

```http
POST /api/appointments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "office_id": "office-uuid",
  "service_id": "service-uuid",
  "appointment_date": "2024-01-15",
  "appointment_time": "10:30",
  "notes": "Need help with new connection"
}
```

**Response:**
```json
{
  "message": "Appointment booked successfully",
  "appointment": {
    "id": "appointment-uuid",
    "token_number": 15,
    "status": "scheduled",
    "appointment_date": "2024-01-15",
    "appointment_time": "10:30:00",
    "estimated_wait_time": 45,
    "queue": {
      "id": "queue-uuid",
      "office": {
        "name": "GUVNL Head Office",
        "address": "Vadodara, Gujarat"
      },
      "service": {
        "name": "New Electricity Connection",
        "estimated_duration": 45
      }
    }
  }
}
```

### Get Queue Status

```http
GET /api/queues/status?date=2024-01-15&office_id=office-uuid
```

**Response:**
```json
{
  "queues": [
    {
      "queue_id": "queue-uuid",
      "office_name": "GUVNL Head Office",
      "service_name": "New Electricity Connection",
      "queue_date": "2024-01-15",
      "current_token_number": 12,
      "total_appointments": 45,
      "completed_appointments": 11,
      "pending_appointments": 34,
      "avg_wait_time": 32.5,
      "status": "active"
    }
  ]
}
```

### Update Appointment Status (Admin)

```http
PUT /api/admin/appointments/appointment-uuid/status
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "status": "in_progress",
  "notes": "Customer called to counter"
}
```

## WebSocket Events

The system uses Socket.IO for real-time updates.

**Connection URL:** `http://localhost:5000` (with Socket.IO client)

### Client Events (Emit)

| Event | Data | Description |
|-------|------|-------------|
| `join_queue` | `{queue_id: "uuid"}` | Join queue room for updates |
| `leave_queue` | `{queue_id: "uuid"}` | Leave queue room |
| `join_appointment` | `{appointment_id: "uuid"}` | Join appointment room |

### Server Events (Listen)

| Event | Data | Description |
|-------|------|-------------|
| `queue_update` | Queue status object | Queue status changed |
| `appointment_update` | Appointment object | Appointment status changed |
| `token_called` | Token info | Next token called |
| `notification` | Notification object | New notification |

### WebSocket Example (JavaScript)

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

// Join a queue room
socket.emit('join_queue', { queue_id: 'queue-uuid' });

// Listen for queue updates
socket.on('queue_update', (data) => {
  console.log('Queue updated:', data);
  // Update UI with new queue status
});

// Listen for appointment updates
socket.on('appointment_update', (data) => {
  console.log('Appointment updated:', data);
  // Update appointment status in UI
});

// Listen for notifications
socket.on('notification', (data) => {
  console.log('New notification:', data);
  // Show notification to user
});
```

## Error Handling

All API endpoints return standardized error responses:

```json
{
  "message": "Error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "details": {
    "field": "Specific field error message"
  }
}
```

### Common HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |

### Error Examples

```json
// Validation Error (422)
{
  "message": "Validation failed",
  "details": {
    "email": "Invalid email format",
    "phone": "Phone number is required"
  }
}

// Authentication Error (401)
{
  "message": "Invalid or expired token",
  "error_code": "INVALID_TOKEN"
}

// Authorization Error (403)
{
  "message": "Insufficient permissions",
  "error_code": "INSUFFICIENT_PERMISSIONS"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **General endpoints:** 60 requests per minute per IP
- **Authentication endpoints:** 10 requests per minute per IP
- **Admin endpoints:** 100 requests per minute per authenticated user

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination:

```http
GET /api/appointments?page=1&limit=20&sort=created_at&order=desc
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Filtering and Search

Most list endpoints support filtering:

```http
GET /api/appointments?status=scheduled&date_from=2024-01-01&date_to=2024-01-31&search=connection
```

## API Testing

Use the provided Postman collection or test with curl:

```bash
# Register a new user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+919876543210"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "test@example.com",
    "password": "password123"
  }'

# Get queue status (no auth required)
curl -X GET http://localhost:5000/api/queues/status
```

For more examples and interactive testing, import the Postman collection from `/docs/postman/`.