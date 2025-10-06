# User Dashboard API

## Overview
This endpoint provides comprehensive dashboard data for authenticated users, including their recent courses, study progress, and reading tempo analytics.

## Endpoint
- **URL:** `/api/users/dashboard/`
- **Method:** `GET`
- **Authentication:** Required (Bearer Token)

## Response

### Success Response (200 OK)
```json
{
    "last_courses": [
        {
            "id": 1,
            "title": "Kimyo",
            "cover": "https://example.com/media/courses/chemistry.jpg",
            "progress_percent": 75.50,
            "total_lessons": 10,
            "completed_lessons": 8,
            "last_accessed": "2024-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "title": "Biologiya", 
            "cover": "https://example.com/media/courses/biology.jpg",
            "progress_percent": 45.00,
            "total_lessons": 12,
            "completed_lessons": 5,
            "last_accessed": "2024-01-14T15:20:00Z"
        }
    ],
    "reading_tempo": [
        {
            "date": "2024-01-01",
            "points_earned": 25,
            "study_hours": 2.5
        },
        {
            "date": "2024-01-02", 
            "points_earned": 0,
            "study_hours": 0.0
        },
        {
            "date": "2024-01-03",
            "points_earned": 40,
            "study_hours": 4.0
        }
    ],
    "total_coins": 150,
    "total_points": 320,
    "total_courses_started": 5,
    "total_courses_completed": 2
}
```

## Field Descriptions

### Last Courses
- `id`: Course ID
- `title`: Course title
- `cover`: Course cover image URL
- `progress_percent`: Progress percentage (0.00 to 100.00)
- `total_lessons`: Total number of lessons in the course
- `completed_lessons`: Number of completed lessons
- `last_accessed`: Last time the user accessed this course

### Reading Tempo
- `date`: Date in YYYY-MM-DD format
- `points_earned`: Points earned on that date from completed lesson parts
- `study_hours`: Study hours calculated from points (10 points = 1 hour)

### User Statistics
- `total_coins`: User's current coin balance
- `total_points`: User's current point balance  
- `total_courses_started`: Total number of courses the user has started
- `total_courses_completed`: Total number of courses the user has completed

## Features

### Progress Calculation
- Progress is calculated based on completed lessons vs total lessons
- Only active lessons are counted
- Progress percentage is rounded to 2 decimal places

### Reading Tempo
- Shows last 30 days of study activity
- Missing dates are filled with 0 values
- Study hours are calculated as: `points_earned / 10`
- Data is ordered chronologically

### Last Courses
- Returns last 3 most recently accessed courses
- Ordered by last access time (updated_at)
- Only includes active courses

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```
