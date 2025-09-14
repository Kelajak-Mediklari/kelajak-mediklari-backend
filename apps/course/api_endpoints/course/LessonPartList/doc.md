# Lesson Parts List API

## Endpoint
`GET /api/v1/course/lessons/{lesson_id}/parts/`

## Description
Retrieves a paginated list of all active lesson parts for a specific lesson. The lesson parts are ordered by their `order` field.

## Authentication
- **Required**: Yes
- **Type**: Bearer Token

## Parameters

### Path Parameters
- `lesson_id` (integer, required): The ID of the lesson whose parts you want to retrieve

### Query Parameters
- `search` (string, optional): Search lesson parts by title or description
- `page` (integer, optional): Page number for pagination (default: 1)
- `page_size` (integer, optional): Number of items per page

## Response

### Success Response (200 OK)
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Introduction Video",
      "description": "Learn the basics of the topic",
      "type": "video",
      "order": 1,
      "award_coin": 10,
      "award_point": 5,
      "video_url": "https://example.com/video.mp4",
      "test_id": 2,
      "galleries": [
        {
          "id": 1,
          "image": "/media/galleries/image1.jpg"
        }
      ],
      "attached_files": [
        {
          "id": 1,
          "file": "/media/files/document.pdf"
        }
      ]
    },
    {
      "id": 2,
      "title": "Theory Section",
      "description": "Read the theoretical background",
      "type": "theory",
      "order": 2,
      "award_coin": 15,
      "award_point": 8,
      "video_url": null,
      "test_id": null,
      "galleries": [],
      "attached_files": []
    }
  ]
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

### LessonPart Fields
- `id`: Unique identifier for the lesson part
- `title`: Title of the lesson part
- `description`: Detailed description of the lesson part content
- `type`: Type of lesson part (video, theory, matching, true_false, book_test, regular_test, assignment)
- `order`: Display order of the lesson part within the lesson
- `award_coin`: Number of coins awarded upon completion
- `award_point`: Number of points awarded upon completion
- `video_url`: URL to the video content (null if not a video type)
- `test_id`: ID of associated test (null if no test is associated)
- `galleries`: Array of associated gallery images
- `attached_files`: Array of associated files

### Gallery Fields
- `id`: Unique identifier for the gallery item
- `image`: URL to the image file

### File Fields
- `id`: Unique identifier for the file
- `file`: URL to the file

## Usage Examples

### Get all lesson parts for lesson ID 5
```bash
curl -H "Authorization: Bearer your_token_here" \
     "https://api.example.com/api/v1/course/lessons/5/parts/"
```

### Search lesson parts by title
```bash
curl -H "Authorization: Bearer your_token_here" \
     "https://api.example.com/api/v1/course/lessons/5/parts/?search=video"
```

### Get paginated results
```bash
curl -H "Authorization: Bearer your_token_here" \
     "https://api.example.com/api/v1/course/lessons/5/parts/?page=1&page_size=10"
```

## Notes
- Only active lesson parts (`is_active=True`) are returned
- Only active lessons (`is_active=True`) are accessible
- Results are automatically ordered by the `order` field
- The API includes related data (galleries, attached_files) to minimize additional requests
- Search functionality works on both title and description fields
