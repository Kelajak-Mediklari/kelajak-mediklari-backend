# Lesson Part Detail API

## Endpoint
`GET /api/v1/course/parts/{id}/`

## Description
Retrieves detailed information about a specific lesson part including all fields, associated test details, galleries, and attached files.

## Authentication
- **Required**: Yes
- **Type**: Bearer Token

## Parameters

### Path Parameters
- `id` (integer, required): The ID of the lesson part to retrieve

## Response

### Success Response (200 OK)
```json
{
  "id": 1,
  "title": "Introduction to Medical Terminology",
  "description": "This lesson part covers the basic medical terminology that every medical student should know. We will explore common prefixes, suffixes, and root words used in medical practice.",
  "type": "video",
  "order": 1,
  "award_coin": 10,
  "award_point": 5,
  "video_url": "https://example.com/videos/medical-terminology-intro.mp4",
  "test": {
    "id": 2,
    "title": "Medical Terminology Quiz",
    "description": "Test your knowledge of basic medical terminology",
    "type": "regular_test",
    "test_duration": 15
  },
  "galleries": [
    {
      "id": 1,
      "image": "/media/galleries/medical-chart-example.jpg"
    },
    {
      "id": 2,
      "image": "/media/galleries/terminology-diagram.png"
    }
  ],
  "attached_files": [
    {
      "id": 1,
      "file": "/media/files/medical-terminology-reference.pdf"
    },
    {
      "id": 2,
      "file": "/media/files/practice-exercises.docx"
    }
  ],
  "lesson_id": 5,
  "lesson_title": "Medical Fundamentals",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z",
  "is_active": true
}
```

### Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## Field Descriptions

### Main Fields
- `id`: Unique identifier for the lesson part
- `title`: Title of the lesson part
- `description`: Detailed description of the lesson part content
- `type`: Type of lesson part (video, theory, matching, true_false, book_test, regular_test, assignment)
- `order`: Display order of the lesson part within the lesson
- `award_coin`: Number of coins awarded upon completion
- `award_point`: Number of points awarded upon completion
- `video_url`: URL to the video content (null if not a video type)
- `lesson_id`: ID of the parent lesson
- `lesson_title`: Title of the parent lesson
- `created_at`: Timestamp when the lesson part was created
- `updated_at`: Timestamp when the lesson part was last updated
- `is_active`: Whether the lesson part is currently active

### Test Object Fields (null if no test is associated)
- `id`: Unique identifier for the test
- `title`: Title of the test
- `description`: Description of what the test covers
- `type`: Type of test (true_false, matching, book_test, regular_test)
- `test_duration`: Duration of the test in minutes

### Gallery Array Fields
- `id`: Unique identifier for the gallery item
- `image`: URL to the image file

### Attached Files Array Fields
- `id`: Unique identifier for the file
- `file`: URL to the attached file

## Usage Examples

### Get lesson part details
```bash
curl -H "Authorization: Bearer your_token_here" \
     "https://api.example.com/api/v1/course/parts/1/"
```

### Example with JavaScript/Fetch
```javascript
fetch('https://api.example.com/api/v1/course/parts/1/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Lesson Part Types

The API supports the following lesson part types:

- **video**: Video-based lesson content
- **theory**: Text-based theoretical content
- **matching**: Matching exercise
- **true_false**: True/False questions
- **book_test**: Book-based test questions
- **regular_test**: Regular quiz/test
- **assignment**: Assignment or homework

## Notes

- Only active lesson parts (`is_active=True`) are accessible
- The API includes complete test information when a test is associated
- All related data (galleries, attached_files, test) is included to minimize additional API calls
- The response includes parent lesson information for context
- Timestamps are provided in ISO 8601 format
- If no test is associated with the lesson part, the `test` field will be `null`
- Gallery and attached files arrays will be empty if no media is associated

## Related APIs

- **Lesson Parts List**: `GET /api/v1/course/lessons/{lesson_id}/parts/` - Get all parts for a lesson (summary view)
- **Lessons List**: `GET /api/v1/course/{course_id}/lessons/` - Get all lessons for a course
