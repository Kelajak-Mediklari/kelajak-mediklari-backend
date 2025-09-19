# UserLessonCreate API

## Overview
The UserLessonCreate API allows authenticated users to create a UserLesson record, which tracks their progress through a specific lesson within a course they have paid for.

## Endpoint
**POST** `/api/course/user-lesson/create/`

## Authentication
- **Required**: Yes
- **Type**: Token/Session Authentication

## Request Body
```json
{
    "user_course_id": 1,
    "lesson_id": 2
}
```

### Parameters
- `user_course_id` (integer, required): The ID of the UserCourse record that proves the user has paid for the course
- `lesson_id` (integer, required): The ID of the lesson the user wants to start

## Response

### Success Response (201 Created)
```json
{
    "id": 5,
    "user_course_id": 1,
    "lesson_id": 2
}
```

### Error Responses

#### 400 Bad Request - Validation Errors
```json
{
    "user_course_id": ["User course not found or user has not paid for this course."],
    "lesson_id": ["Lesson not found or is not active."],
    "non_field_errors": ["Lesson does not belong to the specified course."]
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## Validation Rules

1. **Authentication Required**: User must be authenticated
2. **UserCourse Validation**: 
   - UserCourse must exist
   - UserCourse must belong to the authenticated user (ensures user has paid for the course)
3. **Lesson Validation**:
   - Lesson must exist and be active
   - Lesson must belong to the same course as the UserCourse
4. **Uniqueness**: UserLesson must not already exist for this user-lesson combination

## Business Logic

### Payment Verification
The API verifies that a user has paid for a course by checking if a `UserCourse` record exists for the authenticated user and the specified course. If no `UserCourse` exists, it means the user hasn't paid for the course and cannot access its lessons.

### Course-Lesson Relationship
The API ensures that the lesson belongs to the same course that the user has paid for, preventing users from accessing lessons from courses they haven't purchased.

### Progress Tracking
Once a UserLesson is created, it serves as the foundation for tracking the user's progress through that specific lesson, including completion status and progress percentage.

## Usage Example

```javascript
// Create a user lesson
const response = await fetch('/api/course/user-lesson/create/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Token your-auth-token-here'
    },
    body: JSON.stringify({
        user_course_id: 1,
        lesson_id: 2
    })
});

if (response.ok) {
    const userLesson = await response.json();
    console.log('UserLesson created:', userLesson);
} else {
    const errors = await response.json();
    console.error('Validation errors:', errors);
}
```

## Related Models

- **UserCourse**: Represents a user's enrollment in a course (indicates payment)
- **UserLesson**: Tracks user progress in a specific lesson
- **Lesson**: The lesson content within a course
- **Course**: The course that contains lessons

## Notes

- This endpoint only creates the UserLesson record; it doesn't mark the lesson as started or completed
- Progress tracking is handled by separate endpoints for lesson parts and completion
- The created UserLesson will have default values: `is_completed=False`, `progress_percent=0.00`
