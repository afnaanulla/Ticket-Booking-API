# 🎬 Movie Ticket Booking System

## A Django REST Framework-based movie ticket booking system with JWT authentication, multi-passenger booking, age validation, and comprehensive edge case handling.

### 📋 Table of Contents
- Features
- Tech Stack
- Installation
- API Endpoints
- Edge Cases & Validations
- Testing Guide
- Swagger Documentation

### ✨ Features

1) JWT Authentication - Secure user authentication with access/refresh tokens
2) Multi-Passenger Booking - Book multiple consecutive seats in one transaction
3) Age Validation - Enforce movie age restrictions with genre-based enhancements
4) Seat Management - Prevent double booking and overbooking
5) Booking Cancellation - Cancel bookings and automatically free up seats
6) Race Condition Protection - Database-level locks prevent concurrent booking conflicts
7) Swagger Documentation - Complete API documentation at /swagger/

### 🛠 Tech Stack

- Python 3.x
- Django 4.x
- Django REST Framework
- djangorestframework-simplejwt (JWT)
- drf-yasg (Swagger)
- SQLite (default, configurable to PostgreSQL/MySQL)

### 📦 Installation
1. Create Folder and in that folder create Python Virtual environment

```
git clone <repository-url>
cd movie-booking-system
```
2. Create virtual environment
```
python -m venv venv
source venv/bin/activate
```
3. Install dependencies
```
pip install django djangorestframework djangorestframework-simplejwt drf-yasg
```
4. Run migrations
```
python manage.py makemigrations
python manage.py migrate
```
5. Create sample data (optional)
```
python manage.py shell
```
```
from bookings.models import Movie, Show
from django.utils import timezone

# Create movies
movie1 = Movie.objects.create(
    title="Inception",
    duration_minutes=148,
    genre="Sci-Fi",
    rating="U/A 13+",
    age_limit=13
)

movie2 = Movie.objects.create(
    title="The Conjuring",
    duration_minutes=112,
    genre="Horror",
    rating="A",
    age_limit=18
)

# Create shows
Show.objects.create(
    movie=movie1,
    screen_name="Screen 1",
    date_time=timezone.now() + timezone.timedelta(days=1),
    total_seats=50
)

Show.objects.create(
    movie=movie2,
    screen_name="Screen 2",
    date_time=timezone.now() + timezone.timedelta(days=1),
    total_seats=30
)
```

6. Run server
```
python manage.py runserver
```
7. Access APIs

```
API Base URL: http://localhost:8000/api/
Swagger UI: http://localhost:8000/swagger/
ReDoc: http://localhost:8000/redoc/
```

## 🔌 API Endpoints

- ### Authentication
- #### Signup
```
httpPOST /api/signup/
Content-Type: application/json
```
```
{
  "username": "johndoe",
  "password": "securepass123",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```
- #### Response
```
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

- #### Login
```
httpPOST /api/login/
Content-Type: application/json
```
```
{
  "username": "johndoe",
  "password": "securepass123"
}
```
- #### Response:
```
json{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

- #### Refresh Token
```
httpPOST /api/token/refresh/
Content-Type: application/json
```
```
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Movies & Shows
- ### List All Movies
```
GET /api/movies/
```
- #### Response
```
[
  {
    "id": 1,
    "title": "Inception",
    "duration_minutes": 148,
    "genre": "Sci-Fi",
    "rating": "U/A 13+",
    "age_limit": 13
  }
]
```

- #### List Shows for a Movie
```
GET /api/movies/1/shows/
```
- #### Response
```
[
  {
    "id": 1,
    "movie": {
      "id": 1,
      "title": "Inception",
      "duration_minutes": 148,
      "genre": "Sci-Fi",
      "rating": "U/A 13+",
      "age_limit": 13
    },
    "screen_name": "Screen 1",
    "date_time": "2025-10-06T18:00:00Z",
    "total_seats": 50,
    "available_seats": 47,
    "status": "Available"
  }
]
```
- ### Bookings
- #### Book Tickets (Single Passenger)
```
POST /api/shows/1/book/
Authorization: Bearer <access_token>
Content-Type: application/json
```
```
{
  "seat_number": 5,
  "passengers": [
    {
      "passenger_name": "Alice Johnson",
      "passenger_age": 25
    }
  ]
}
```

- #### Response:
```
json{
  "message": "1 ticket(s) booked successfully!",
  "bookings": [
    {
      "id": 1,
      "user": "johndoe",
      "show": {...},
      "seat_number": 5,
      "status": "booked",
      "created_at": "2025-10-05T12:30:00Z"
    }
  ]
}
```

- #### Book Tickets (Multiple Passengers)
```
POST /api/shows/1/book/
Authorization: Bearer <access_token>
Content-Type: application/json
```
```
{
  "seat_number": 10,
  "passengers": [
    {
      "passenger_name": "Bob Smith",
      "passenger_age": 30
    },
    {
      "passenger_name": "Carol White",
      "passenger_age": 28
    },
    {
      "passenger_name": "David Brown",
      "passenger_age": 35
    }
  ]
}
```
- #### Response:
```
json{
  "message": "3 ticket(s) booked successfully!",
  "bookings": [
    {
      "id": 2,
      "seat_number": 10,
      ...
    },
    {
      "id": 3,
      "seat_number": 11,
      ...
    },
    {
      "id": 4,
      "seat_number": 12,
      ...
    }
  ]
}
```
- #### Cancel Booking
```
POST /api/bookings/1/cancel/
Authorization: Bearer <access_token>
```
- #### Response:
```
json{
  "detail": "Booking cancelled."
}
```
- #### My Bookings
```
GET /api/my-bookings/
Authorization: Bearer <access_token>
```

- #### Response:
```
json[
  {
    "id": 1,
    "user": "johndoe",
    "show": {...},
    "seat_number": 5,
    "status": "booked",
    "created_at": "2025-10-05T12:30:00Z"
  }
]
```

 ### 🛡️ Edge Cases & Validations
- #### Authentication Edge Cases
❌ Signup with existing username
```
json{
  "username": "johndoe"  // Already exists
}
```
```
Error: 400 Bad Request - Username already exists
```
❌ Weak password
```
json{
  "password": "123"  // Less than 6 characters
}
```
```
Error: 400 Bad Request - Password must be at least 6 characters
```
❌ Invalid credentials on login
```
json{
  "username": "johndoe",
  "password": "wrongpassword"
}
```
```
Error: 401 Unauthorized - Invalid credentials
```
❌ Accessing protected endpoint without token
```
GET /api/my-bookings/
// No Authorization header
```
```
Error: 401 Unauthorized - Authentication credentials were not provided
```
❌ Expired JWT token
```
Authorization: Bearer <expired_token>
Error: 401 Unauthorized - Token is expired
```

- #### Booking Edge Cases
❌ Show doesn't exist
```
POST /api/shows/999/book/
```
```
Error: 404 Not Found - No Show matches the given query
```
❌ Show is fully booked
```
json{
  "seat_number": 1,
  "passengers": [{"passenger_name": "Test", "passenger_age": 25}]
}
```
```
Error: 400 Bad Request - Show is fully booked
```
❌ No passengers provided
```
json{
  "seat_number": 1,
  "passengers": []
}
```
```
Error: 400 Bad Request - At least one passenger is required
```
❌ Requesting more seats than available
```
json{
  "seat_number": 1,
  "passengers": [
    {"passenger_name": "P1", "passenger_age": 25},
    {"passenger_name": "P2", "passenger_age": 30},
    {"passenger_name": "P3", "passenger_age": 28}
  ]
}
// Only 2 seats available
```

```
Error: 400 Bad Request - Only 2 seats available, but 3 passengers requested
```
❌ Invalid seat number
```
json{
  "seat_number": 0,  // Or negative, or > total_seats
  "passengers": [{"passenger_name": "Test", "passenger_age": 25}]
}
```
```
Error: 400 Bad Request - seat_number must be between 1 and 50
```
❌ Seat already booked
```
json{
  "seat_number": 5,  // Already booked
  "passengers": [{"passenger_name": "Test", "passenger_age": 25}]
}
```
```
Error: 400 Bad Request - Seat 5 is already booked
```
❌ Not enough consecutive seats

```
json{
  "seat_number": 49,
  "passengers": [
    {"passenger_name": "P1", "passenger_age": 25},
    {"passenger_name": "P2", "passenger_age": 30},
    {"passenger_name": "P3", "passenger_age": 28}
  ]
}
// Show has 50 total seats, only 2 available from seat 49
```
```
Error: 400 Bad Request - Cannot book 3 consecutive seats starting from seat 49. Only 2 seats available from that position
```
❌ Some consecutive seats already booked
```
json{
  "seat_number": 10,
  "passengers": [
    {"passenger_name": "P1", "passenger_age": 25},
    {"passenger_name": "P2", "passenger_age": 30},
    {"passenger_name": "P3", "passenger_age": 28}
  ]
}
// Seats 10 and 12 are available, but seat 11 is already booked
```

```
Error: 400 Bad Request - Cannot book consecutive seats starting from 10. Seats [11] are already booked
```
- #### Age Restriction Edge Cases
❌ Passenger below age limit
```
json{
  "seat_number": 1,
  "passengers": [
    {"passenger_name": "Child", "passenger_age": 10}
  ]
}
// Movie has age_limit: 13
```
```
Error: 400 Bad Request - Passenger Child (age 10) does not meet the Sci-Fi age limit (13+)
```
❌ Multiple passengers, one underage
```
json{
  "seat_number": 1,
  "passengers": [
    {"passenger_name": "Adult", "passenger_age": 30},
    {"passenger_name": "Teen", "passenger_age": 15},
    {"passenger_name": "Child", "passenger_age": 12}
  ]
}
// Movie has age_limit: 13
Error: 400 Bad Request - The following passengers do not meet the age requirement (13+): Child (age 12)
```
❌ Horror genre with stricter age requirement

```
json{
  "seat_number": 1,
  "passengers": [
    {"passenger_name": "Teen", "passenger_age": 18}
  ]
}
// Movie: genre="Horror", age_limit=18
// Effective age limit: 18 + 2 = 20 (Horror bonus)
```
```
Error: 400 Bad Request - Passenger Teen (age 18) does not meet the Horror age limit (20+)
```
❌ Negative age
```
json{
  "passengers": [
    {"passenger_name": "Invalid", "passenger_age": -5}
  ]
}
```
```
Error: 400 Bad Request - Ensure this value is greater than or equal to 0
```

- #### Cancellation Edge Cases
❌ Booking doesn't exist
```
POST /api/bookings/999/cancel/
```

```
Error: 404 Not Found - No Booking matches the given query
```
❌ Cancelling someone else's booking
```
POST /api/bookings/5/cancel/
// Booking belongs to user "alice", but logged in as "bob"
```
```
Error: 403 Forbidden - You may only cancel your own bookings
```
❌ Already cancelled booking
```
POST /api/bookings/1/cancel/
// Booking status is already "cancelled"
```
```
Error: 400 Bad Request - Booking already cancelled
```
❌ Cancelling without authentication
```
POST /api/bookings/1/cancel/
// No Authorization header
```
```
Error: 401 Unauthorized - Authentication credentials were not provided
```

- #### Race Condition Edge Cases

### ✅ Concurrent booking prevention
**Scenario:** ***Two users try to book the same seat simultaneously***

**Implementation:**

- Database-level ``unique_together`` constraint on ``(show, seat_number)``
- ``select_for_update()`` lock in transaction
- IntegrityError handling

**Result:**

- First request: ``201 Created ``✅
- Second request: ``409 Conflict - Some seats were just booked by another user`` ❌

✅ **Overbooking prevention**

**Scenario:** ***Multiple users booking when only 1 seat left***

**Implementation:**

- Check available seats inside transaction with database lock
- Validate total bookings vs total seats

**Result:**

- Only the first request succeeds
Others get: ``400 Bad Request - Show is fully booked``


###  Data Integrity Edge Cases
✅ Seat freed after cancellation
``` Before cancellation
available_seats = 10

# Cancel booking
POST /api/bookings/5/cancel/

# After cancellation
available_seats = 11  # ✅ Seat freed
```
✅ Available seats calculation excludes cancelled bookings

```
Formula: total_seats - bookings with status='booked'
# Cancelled bookings are NOT counted
```

### 🧪 Testing Guide
**Test 1: Complete Booking Flow**
```
# 1. Signup
curl -X POST http://localhost:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","email":"test@test.com"}'

# 2. Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# 3. Get movies
curl http://localhost:8000/api/movies/

# 4. Get shows for movie
curl http://localhost:8000/api/movies/1/shows/

# 5. Book tickets
curl -X POST http://localhost:8000/api/shows/1/book/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"seat_number":1,"passengers":[{"passenger_name":"Test","passenger_age":25}]}'

# 6. View bookings
curl http://localhost:8000/api/my-bookings/ \
  -H "Authorization: Bearer <access_token>"

# 7. Cancel booking
curl -X POST http://localhost:8000/api/bookings/1/cancel/ \
  -H "Authorization: Bearer <access_token>"
```
**Test 2: Edge Case Validation**

In Django shell
```
from bookings.models import Movie, Show, Booking
from django.contrib.auth.models import User

# Create test data
user = User.objects.create_user('testuser', password='test123')
movie = Movie.objects.create(title="Test Movie", duration_minutes=120, age_limit=18)
show = Show.objects.create(movie=movie, screen_name="Screen 1", total_seats=5)

# Test double booking
Booking.objects.create(user=user, show=show, seat_number=1, status='booked')
# Try to book seat 1 again via API - should fail

# Test age validation
# Try booking with passenger_age=15 - should fail
```

### 📚 Swagger Documentation
**Access Swagger UI**

1) Start server: ``python manage.py runserver``
2) Visit: ``http://localhost:8000/swagger/``
####

**Using JWT in Swagger**

1) Click **"Authorize"** button (top right)
2) Enter: **Bearer <your_access_token>**
3) Click **"Authorize"**
4) Test protected endpoints with "Try it out"
####

**Getting Access Token**

1) Use ``/api/login/`` endpoint in Swagger
2) Copy the ``access`` token from response
3) Use it in the Authorize dialog


### 🎯 Business Rules Summary

| **Rule** | **Implementation** | **Edge Case Handling** |
|-----------|--------------------|------------------------|
| **Prevent Double Booking** | DB unique constraint + validation | Returns `400 / 409` error |
| **Prevent Overbooking** | Check available seats inside transaction | Returns `400` error |
| **Age Restrictions** | Validate all passengers before booking | Returns `400` with passenger names |
| **Consecutive Seats** | Allocate seats sequentially from start | Validates seat availability upfront |
| **Seat Liberation** | `status='cancelled'` excluded from count | Seats become available immediately after cancel |
| **Race Conditions** | `select_for_update()` lock | Ensures first-come-first-served booking |
| **Authorization** | JWT required for bookings | `401 Unauthorized` if token missing |
| **Ownership** | User can only cancel their own bookings | `403 Forbidden` if not the owner |


### 📝 Model Schema
- #### Movie
```
{
  "title": "string",
  "duration_minutes": "integer",
  "genre": "string",
  "rating": "U | U/A 13+ | U/A 16+ | A",
  "age_limit": "integer"
}
```
- #### Show
```
{
  "movie": "FK(Movie)",
  "screen_name": "string",
  "date_time": "datetime",
  "total_seats": "integer"
}
```
- #### Booking
```
{
  "user": "FK(User)",
  "show": "FK(Show)",
  "seat_number": "integer",
  "passenger_name": "string",
  "passenger_age": "integer",
  "status": "booked | cancelled",
  "created_at": "datetime"
}
```

### 🚀 Advanced Features

- ✅ Multi-passenger booking in single transaction
- ✅ Genre-based age restrictions (Horror +2 years)
- ✅ Consecutive seat allocation
- ✅ Database-level race condition prevention
- ✅ Comprehensive error messages
- ✅ Seat availability real-time calculation
- ✅ User-specific booking management
