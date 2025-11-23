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

#### Regular Test Response
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
            "question_image": null,
            "video_url": null,
            "instructions": null,
            "question_type": "text_choice",
            "user_answer_status": "correct",
            "choices": [
                {
                    "id": 1,
                    "choice_text": "4",
                    "choice_image": null,
                    "choice_label": "A",
                    "is_correct": true,
                    "is_user_selected": true,
                    "order": 1
                },
                {
                    "id": 2,
                    "choice_text": "3",
                    "choice_image": null,
                    "choice_label": "B",
                    "is_correct": false,
                    "is_user_selected": false,
                    "order": 2
                }
            ],
            "user_selected_choice_id": 1,
            "matching_pairs": null,
            "user_matching_answer": null,
            "book_questions_data": null,
            "correct_answer": null,
            "user_boolean_answer": null
        }
    ]
}
```

#### Matching Test Response
```json
{
    "id": 16,
    "test_title": "Vocabulary Matching",
    "test_type": "matching",
    "total_questions": 1,
    "attempts_count": 2,
    "award_coins": 30,
    "award_points": 15,
    "user_correct_answers": 1,
    "score_percentage": 100.0,
    "is_passed": true,
    "is_submitted": true,
    "start_date": "2024-01-15T11:00:00Z",
    "finish_date": "2024-01-15T11:10:00Z",
    "questions": [
        {
            "id": 201,
            "question_text": "Match the words with their definitions",
            "question_image": null,
            "video_url": null,
            "instructions": "Drag and drop to match",
            "question_type": "matching",
            "user_answer_status": "correct",
            "choices": null,
            "user_selected_choice_id": null,
            "matching_pairs": [
                {
                    "id": 1,
                    "left_item": "Apple",
                    "right_item": "A fruit",
                    "user_matched_right_item": "A fruit",
                    "is_correct_match": true,
                    "order": 1
                },
                {
                    "id": 2,
                    "left_item": "Car",
                    "right_item": "A vehicle",
                    "user_matched_right_item": "A vehicle",
                    "is_correct_match": true,
                    "order": 2
                }
            ],
            "user_matching_answer": {
                "Apple": "A fruit",
                "Car": "A vehicle"
            },
            "book_questions_data": null,
            "correct_answer": null,
            "user_boolean_answer": null
        }
    ]
}
```

#### Book Test Response
```json
{
    "id": 17,
    "test_title": "Chapter 5 Book Test",
    "test_type": "book_test",
    "total_questions": 1,
    "attempts_count": 1,
    "award_coins": 40,
    "award_points": 20,
    "user_correct_answers": 1,
    "score_percentage": 100.0,
    "is_passed": true,
    "is_submitted": true,
    "start_date": "2024-01-15T12:00:00Z",
    "finish_date": "2024-01-15T12:15:00Z",
    "questions": [
        {
            "id": 301,
            "question_text": "Complete the exercises from page 45",
            "question_image": null,
            "video_url": null,
            "instructions": "Answer all questions from the book",
            "question_type": "book_test",
            "user_answer_status": "correct",
            "choices": null,
            "user_selected_choice_id": null,
            "matching_pairs": null,
            "user_matching_answer": null,
            "book_questions_data": [
                {
                    "question_number": 1,
                    "expected_answer": "A",
                    "user_answer": "A",
                    "is_correct": true
                },
                {
                    "question_number": 2,
                    "expected_answer": "B",
                    "user_answer": "B",
                    "is_correct": true
                },
                {
                    "question_number": 3,
                    "expected_answer": "C",
                    "user_answer": "D",
                    "is_correct": false
                }
            ],
            "correct_answer": null,
            "user_boolean_answer": null
        }
    ]
}
```

#### True/False Test Response
```json
{
    "id": 18,
    "test_title": "Quick True/False Quiz",
    "test_type": "true_false",
    "total_questions": 5,
    "attempts_count": 1,
    "award_coins": 20,
    "award_points": 10,
    "user_correct_answers": 4,
    "score_percentage": 80.0,
    "is_passed": true,
    "is_submitted": true,
    "start_date": "2024-01-15T13:00:00Z",
    "finish_date": "2024-01-15T13:05:00Z",
    "questions": [
        {
            "id": 401,
            "question_text": "The Earth is flat",
            "question_image": null,
            "video_url": null,
            "instructions": null,
            "question_type": "true_false",
            "user_answer_status": "correct",
            "choices": null,
            "user_selected_choice_id": null,
            "matching_pairs": null,
            "user_matching_answer": null,
            "book_questions_data": null,
            "correct_answer": false,
            "user_boolean_answer": false
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
Each question object contains common fields plus test-type-specific fields:

#### Common Fields (All Test Types)
- `id`: Unique identifier for the question
- `question_text`: The text of the question
- `question_image`: Image associated with the question (if any)
- `video_url`: Video URL for the question (if any)
- `instructions`: Special instructions for the question
- `question_type`: Type of question (matches test_type for non-regular tests)
- `user_answer_status`: User's answer status for this question
  - `"correct"`: User answered correctly
  - `"incorrect"`: User answered incorrectly
  - `"not_answered"`: User did not answer this question

#### Regular Test Specific Fields
- `choices`: Array of answer choices with detailed information
  - `id`: Choice identifier
  - `choice_text`: Text of the choice
  - `choice_image`: Image for the choice (if any)
  - `choice_label`: Label (A, B, C, D, etc.)
  - `is_correct`: Whether this is the correct answer
  - `is_user_selected`: Whether the user selected this choice
  - `order`: Display order
- `user_selected_choice_id`: ID of the choice selected by the user
- Other fields will be `null`

#### Matching Test Specific Fields
- `matching_pairs`: Array of matching pairs with user's answers
  - `id`: Pair identifier
  - `left_item`: The left side item (question)
  - `right_item`: The correct right side item (answer)
  - `user_matched_right_item`: The right item the user matched with this left item
  - `is_correct_match`: Whether the user's match is correct
  - `order`: Display order
- `user_matching_answer`: Dictionary of user's complete matching answer `{left_item: right_item}`
- Other fields will be `null`

#### Book Test Specific Fields
- `book_questions_data`: Array of individual book questions with results
  - `question_number`: The question number from the book
  - `expected_answer`: The correct answer
  - `user_answer`: The answer provided by the user
  - `is_correct`: Whether the user's answer is correct
- Other fields will be `null`

#### True/False Test Specific Fields
- `correct_answer`: The correct boolean answer (true or false)
- `user_boolean_answer`: The user's boolean answer
- Other fields will be `null`

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
