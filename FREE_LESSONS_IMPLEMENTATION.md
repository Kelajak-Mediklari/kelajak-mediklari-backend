# Free Lessons Implementation

## Overview
This document describes the implementation of the free lessons feature that allows users to watch the first 3 lessons of any course and receive coin/point awards without purchasing the course.

## Changes Made

### 1. Database Changes

#### UserCourse Model (`apps/course/models.py`)
- **Added field**: `is_free_trial` (BooleanField)
  - `default=False`
  - Indicates whether the user is accessing free lessons without payment
  - When `True`: User has access only to the first 3 lessons
  - When `False`: User has paid and has full access to all lessons

#### Migration
- Created migration: `apps/course/migrations/0028_add_is_free_trial_to_user_course.py`
- Adds the `is_free_trial` field to the `UserCourse` model

### 2. API Endpoint Changes

#### UserLessonCreate API (`apps/course/api_endpoints/course/UserLessonCreate/serializers.py`)
**Changes:**
- Made `user_course_id` optional (`required=False, allow_null=True`)
- Updated validation logic:
  - If `user_course_id` is not provided, validates that the lesson is in the first 3 lessons (ordered by `order` field)
  - If lesson is in first 3, automatically creates a free trial `UserCourse` with `is_free_trial=True`
  - If lesson is not in first 3 and no `user_course_id` provided, returns validation error
- Updated `create()` method to handle free trial UserCourse creation

**Usage:**
```json
// For free lessons (no user_course_id needed)
{
    "lesson_id": 1
}

// For paid lessons (user_course_id required)
{
    "user_course_id": 123,
    "lesson_id": 5
}
```

#### UserLessonPartCreate API (`apps/course/api_endpoints/course/UserLessonPartCreate/serializers.py`)
**Changes:**
- Added validation in `validate()` method to check if user is on free trial
- If `user_lesson.user_course.is_free_trial` is `True`:
  - Validates that the lesson is in the first 3 lessons
  - Prevents access to non-free lessons
- Coins and points are awarded for completing free lesson parts (handled by existing signal)

#### LessonPartDetail API (`apps/course/api_endpoints/course/LessonPartDetail/views.py`)
**Changes:**
- Updated `_check_lesson_access()` method:
  - First checks for paid UserCourse (`is_free_trial=False`)
  - If no paid UserCourse exists, checks if lesson is in first 3 lessons (ordered by `order` field)
  - Grants access to first 3 lessons regardless of payment status
  - Raises `PermissionDenied` for lessons beyond the first 3 if user hasn't paid

#### TestStart API (`apps/course/api_endpoints/course/TestStart/views.py`)
**Changes:**
- Updated UserCourse creation logic:
  - First checks if user has a paid UserCourse (`is_free_trial=False`)
  - If not, checks if the lesson is in the first 3 free lessons
  - Creates free trial UserCourse (`is_free_trial=True`) for free lessons
  - Properly handles test-taking for both free and paid lessons

### 3. Payment Integration

#### Transaction Model (`apps/payment/models.py`)
**Changes:**
- Updated `success_process()` method:
  - When a payment is successful, sets `is_free_trial=False` in the UserCourse
  - If a free trial UserCourse exists, it will be updated to a paid UserCourse
  - Ensures users get full access after payment

### 4. Signals (No Changes Needed)

#### UserLessonPart Signal (`apps/course/signals.py`)
- Existing signal already handles coin/point awards correctly
- Awards coins and points to all users (both free trial and paid)
- No changes needed

## How It Works

### Free Trial Flow

1. **User accesses a lesson (first 3 lessons)**:
   - User calls `UserLessonCreate` API without `user_course_id`
   - System validates lesson is in first 3
   - System creates/gets free trial `UserCourse` with `is_free_trial=True`
   - System creates `UserLesson` linked to the free trial UserCourse

2. **User watches lesson parts**:
   - User accesses lesson parts through `LessonPartDetail` API
   - Access is granted because lesson is in first 3
   - User completes lesson parts via `UserLessonPartCreate` API
   - System awards coins and points for completion

3. **User tries to access lesson 4+**:
   - System checks if user has paid UserCourse
   - If not, checks if lesson is in first 3
   - Returns `PermissionDenied` error with message to purchase course

### Paid User Flow

1. **User purchases course**:
   - Transaction completes successfully
   - `Transaction.success_process()` is called
   - Creates or updates UserCourse with `is_free_trial=False`
   - If free trial UserCourse exists, it's converted to paid

2. **User accesses any lesson**:
   - System checks for paid UserCourse (`is_free_trial=False`)
   - Grants access to all lessons
   - User can complete all lesson parts and earn coins/points

## Key Features

### ✅ Free Trial Benefits
- Access to first 3 lessons (ordered by `order` field)
- Full coin and point awards for completing free lesson parts
- Progress tracking within free lessons
- Can take tests in free lessons

### ✅ Seamless Upgrade
- Free trial UserCourse automatically upgraded to paid on purchase
- All progress and earnings retained
- No data loss or duplication

### ✅ Access Control
- Clear separation between free and paid content
- Consistent validation across all endpoints
- Proper error messages for unauthorized access

## Testing Recommendations

1. **Free Trial Tests**:
   - Test creating UserLesson for first 3 lessons without user_course_id
   - Test completing free lesson parts and receiving coins/points
   - Test accessing lesson 4+ without payment (should fail)

2. **Paid User Tests**:
   - Test purchasing course upgrades free trial to paid
   - Test accessing all lessons after payment
   - Test that paid users retain all progress from free trial

3. **Edge Cases**:
   - User with free trial tries to access non-free lesson
   - User purchases course after completing some free lessons
   - Multiple courses with different lesson counts

## Migration Instructions

1. **Run the migration**:
   ```bash
   python manage.py migrate course
   ```

2. **Optional: Update existing UserCourses**:
   ```python
   from apps.course.models import UserCourse
   from apps.payment.models import Transaction
   
   # Mark all existing UserCourses as paid (not free trial)
   # since they were created before this feature
   for uc in UserCourse.objects.all():
       # Check if user has a successful transaction for this course
       has_paid = Transaction.objects.filter(
           user=uc.user,
           course=uc.course,
           status='success'
       ).exists()
       
       uc.is_free_trial = not has_paid
       uc.save(update_fields=['is_free_trial'])
   ```

## Notes

- The "first 3 lessons" are determined by the `order` field in the Lesson model
- Coins and points are awarded equally for free and paid lesson completions
- Free trial UserCourses are automatically upgraded on payment
- The `is_free_trial` flag is the single source of truth for access control
