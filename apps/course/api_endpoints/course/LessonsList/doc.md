# Lessons List API Documentation

## Endpoint
`GET /api/v1/course/{course_id}/lessons/`

## Description
Retrieves a paginated list of all active lessons for a specific course. The lessons are ordered by their `order` field and include a `status` field that indicates lesson accessibility for group members.

## Authentication
- **Required**: Yes
- **Type**: Bearer Token

## Parameters

### Path Parameters
- `course_id` (integer, required): The ID of the course whose lessons you want to retrieve

### Query Parameters
- `search` (string, optional): Search lessons by title
- `page` (integer, optional): Page number for pagination (default: 1)
- `page_size` (integer, optional): Number of items per page

## Response

### Success Response (200 OK)
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Introduction to Medical Terminology",
      "slug": "introduction-to-medical-terminology",
      "order": 1,
      "parts_count": 3,
      "is_user_lesson_created": true,
      "user_lesson_id": 15,
      "user_course_id": 8,
      "progress_percent": 75.50,
      "status": "open"
    },
    {
      "id": 2,
      "title": "Basic Anatomy",
      "slug": "basic-anatomy",
      "order": 2,
      "parts_count": 4,
      "is_user_lesson_created": false,
      "user_lesson_id": null,
      "user_course_id": 8,
      "progress_percent": 0.00,
      "status": "lock"
    },
    {
      "id": 3,
      "title": "Physiology Fundamentals",
      "slug": "physiology-fundamentals",
      "order": 3,
      "parts_count": 5,
      "is_user_lesson_created": false,
      "user_lesson_id": null,
      "user_course_id": 8,
      "progress_percent": 0.00,
      "status": "lock"
    },
    {
      "id": 4,
      "title": "Advanced Pathology",
      "slug": "advanced-pathology",
      "order": 4,
      "parts_count": 6,
      "is_user_lesson_created": false,
      "user_lesson_id": null,
      "user_course_id": 8,
      "progress_percent": 0.00,
      "status": "loock"
    },
    {
      "id": 5,
      "title": "Clinical Practice",
      "slug": "clinical-practice",
      "order": 5,
      "parts_count": 7,
      "is_user_lesson_created": false,
      "user_lesson_id": null,
      "user_course_id": 8,
      "progress_percent": 0.00,
      "status": "loock"
    }
  ]
}
```

## Status Field Explanation

The `status` field indicates the accessibility of each lesson for group members. This field only applies to users who are **group members** of the course. For other users (non-group members, purchased course users), this field will be `null`.

### Status Values

#### `"open"`
- **Meaning**: Lesson is accessible and can be started
- **When**: 
  - First lesson (order = 1) is always "open"
  - Any lesson that has been unlocked through completion of prerequisite lessons

#### `"lock"`
- **Meaning**: Lesson is locked but can be unlocked by completing prerequisite lessons
- **When**:
  - Initial state for lessons 2-3 (if no lessons completed)
  - Lessons that are within 2 positions after the last completed lesson
  - These lessons become accessible once prerequisite lessons are completed with passing grades

#### `"loock"`
- **Meaning**: Lesson is locked and cannot be unlocked yet
- **When**:
  - Initial state for lessons 4+ (if no lessons completed)
  - Lessons that are more than 2 positions after the last completed lesson
  - These lessons will change to "lock" status as more lessons are completed

#### `null`
- **Meaning**: Status field does not apply to this user
- **When**:
  - User is not a group member
  - User has purchased the course (has full access regardless of status)
  - User is not authenticated

## Lesson Unlocking Logic

### For Group Members Only

The lesson unlocking system works as follows:

1. **Initial State** (no lessons completed):
   - Lesson 1: `"open"` (always accessible)
   - Lessons 2-3: `"lock"` (can be unlocked)
   - Lessons 4+: `"loock"` (cannot be unlocked yet)

2. **After completing Lesson 1** (with passing grades):
   - Lesson 1: `"open"` (completed)
   - Lessons 2-3: `"lock"` (can be unlocked)
   - Lesson 4: `"lock"` (now unlocked! changed from "loock")
   - Lesson 5+: `"loock"` (still cannot be unlocked)

3. **After completing Lesson 2** (with passing grades):
   - Lesson 1: `"open"` (completed)
   - Lesson 2: `"open"` (completed)
   - Lessons 3-4: `"lock"` (can be unlocked)
   - Lesson 5: `"lock"` (now unlocked! changed from "loock")
   - Lesson 6+: `"loock"` (still cannot be unlocked)

### Passing Grade Requirements

For a lesson to be considered "completed", the group member must have:
- **Theoretical ball** ≥ lesson's `theoretical_pass_ball`
- **Practical ball** ≥ lesson's `practical_pass_ball`

Both conditions must be met for the lesson to count as completed.

### Access Window

Group members can access lessons within a **2-lesson window** after their last completed lesson:
- If last completed lesson is order N, they can access lessons up to order N+2
- Lessons beyond N+2 remain "loock" until more lessons are completed

## Field Descriptions

### Lesson Fields
- `id`: Unique identifier for the lesson
- `title`: Title of the lesson
- `slug`: URL-friendly identifier (only returned for accessible lessons)
- `order`: Display order of the lesson within the course
- `parts_count`: Number of active lesson parts in this lesson
- `is_user_lesson_created`: Whether the user has started this lesson
- `user_lesson_id`: ID of the user's lesson progress record (if exists)
- `user_course_id`: ID of the user's course enrollment record
- `progress_percent`: Percentage completion of the lesson (0.00-100.00)
- `status`: Lesson accessibility status for group members

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Examples

### Example 1: Group Member with No Completed Lessons
```json
{
  "results": [
    {"id": 1, "title": "Lesson 1", "status": "open"},
    {"id": 2, "title": "Lesson 2", "status": "lock"},
    {"id": 3, "title": "Lesson 3", "status": "lock"},
    {"id": 4, "title": "Lesson 4", "status": "loock"},
    {"id": 5, "title": "Lesson 5", "status": "loock"}
  ]
}
```

### Example 2: Group Member After Completing Lesson 1
```json
{
  "results": [
    {"id": 1, "title": "Lesson 1", "status": "open"},
    {"id": 2, "title": "Lesson 2", "status": "lock"},
    {"id": 3, "title": "Lesson 3", "status": "lock"},
    {"id": 4, "title": "Lesson 4", "status": "lock"},
    {"id": 5, "title": "Lesson 5", "status": "loock"}
  ]
}
```

### Example 3: Non-Group Member or Purchased Course User
```json
{
  "results": [
    {"id": 1, "title": "Lesson 1", "status": null},
    {"id": 2, "title": "Lesson 2", "status": null},
    {"id": 3, "title": "Lesson 3", "status": null},
    {"id": 4, "title": "Lesson 4", "status": null},
    {"id": 5, "title": "Lesson 5", "status": null}
  ]
}
```

## Notes

- The status system only applies to **group members** of the course
- Users who have **purchased the course** have full access to all lessons regardless of status
- The status field helps group members understand which lessons they can access based on their progress
- Lesson parts are also restricted based on lesson accessibility for group members
- The system encourages sequential learning by requiring completion of prerequisite lessons
