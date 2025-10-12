# User Test Results API

## Overview
The User Test Results API allows authenticated users to retrieve detailed information about their test attempts, including questions, answers, scores, and awards.

## Endpoint
**GET** `/api/course/user-test-results/{user_test_id}/`

## Authentication
- **Required**: Yes
- **Type**: Token/Session Authentication

## Path Parameters
- `user_test_id` (integer, required): The ID of the UserTest record to retrieve results for

## Response

### Success Response (200 OK)
```json
{
    "id": 15,
    "test_title": "Mathematics Basic Test",
    "test_type": "regular_test",
    "total_questions": 10,
    "attempts_count": 3,
    "award_coins": 50,
    "award_points": 25,
    "user_correct_answers": 7,
    "score_percentage": 70.0,
    "is_passed": true,
    "is_submitted": true,
    "start_date": "2024-01-15T10:30:00Z",
    "finish_date": "2024-01-15T10:45:00Z",
    "questions": [
        {
            "id": 101,
            "question_text": "What is 2 + 2?",
            "user_answer_status": "correct"
        },
        {
            "id": 102,
            "question_text": "What is 5 * 3?",
            "user_answer_status": "incorrect"
        },
        {
            "id": 103,
            "question_text": "What is 10 / 2?",
            "user_answer_status": "not_answered"
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

### Main Fields
- `id`: Unique identifier for the user test attempt
- `test_title`: Title of the test
- `test_type`: Type of test (regular_test, true_false, matching, book_test)
- `total_questions`: Total number of questions in the test
- `attempts_count`: Total number of attempts by this user for this test
- `award_coins`: Number of coins awarded for completing this test
- `award_points`: Number of points awarded for completing this test
- `user_correct_answers`: Number of questions the user answered correctly
- `score_percentage`: User's score as a percentage (0-100)
- `is_passed`: Whether the user passed the test (typically 70% or higher)
- `is_submitted`: Whether the test has been submitted
- `start_date`: When the user started the test
- `finish_date`: When the user finished the test (null if not finished)

### Questions Array
Each question object contains:
- `id`: Unique identifier for the question
- `question_text`: The text of the question
- `user_answer_status`: User's answer status for this question
  - `"correct"`: User answered correctly
  - `"incorrect"`: User answered incorrectly
  - `"not_answered"`: User did not answer this question

## Security
- Users can only access their own test results
- The API validates that the UserTest belongs to the authenticated user

## Business Logic

### Score Calculation
- Score percentage is calculated as: (correct_answers / total_questions) * 100
- Passing threshold is typically 70%

### Awards
- Coins and points are retrieved from the associated LessonPart
- Awards are only given when the test is passed

### Attempts Tracking
- The API shows the total number of attempts for this specific test by the user
- Each attempt creates a separate UserTest record

## Usage Examples

### Get test results for a specific attempt
```bash
GET /api/course/user-test-results/15/
Authorization: Bearer your-token-here
```

This will return detailed results for UserTest with ID 15, including all questions and the user's performance on each question.
