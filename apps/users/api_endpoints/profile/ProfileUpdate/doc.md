# Profile Update API

## Overview
This endpoint allows authenticated users to update their profile information including full name, avatar, and password.

## Endpoint
- **URL:** `/api/users/profile/update/`
- **Method:** `PATCH` or `PUT`
- **Authentication:** Required (Bearer Token)

## Request Body
All fields are optional. Include only the fields you want to update.

```json
{
    "full_name": "John Doe",
    "avatar": "base64_encoded_image_or_file",
    "password": "new_password",
    "confirm_password": "new_password", 
    "current_password": "current_password"
}
```

## Field Descriptions

### Profile Fields
- `full_name` (string, optional): User's full name
- `avatar` (file/image, optional): User's profile picture

### Password Fields
- `password` (string, optional): New password
- `confirm_password` (string, optional): Confirmation of new password (required if password is provided)
- `current_password` (string, optional): Current password (required if password is provided)

## Password Update Rules
1. To update password, you must provide:
   - `password`: The new password
   - `confirm_password`: Must match the new password
   - `current_password`: Must be the user's current password

2. Password validation includes:
   - Current password verification
   - New password and confirmation must match
   - Django's built-in password validation (strength, length, etc.)

## Response

### Success Response (200 OK)
```json
{
    "id": 1,
    "full_name": "John Doe",
    "avatar": "https://example.com/media/users/2024/01/avatar.jpg",
    "phone": "+1234567890",
    "email": "john@example.com"
}
```

### Error Responses

#### 400 Bad Request - Current Password Required
```json
{
    "current_password": ["Current password is required to update password."]
}
```

#### 400 Bad Request - Invalid Current Password
```json
{
    "current_password": ["Current password is incorrect."]
}
```

#### 400 Bad Request - Password Mismatch
```json
{
    "confirm_password": ["Password and confirm password do not match."]
}
```

#### 400 Bad Request - Weak Password
```json
{
    "password": [
        "This password is too short. It must contain at least 8 characters.",
        "This password is too common."
    ]
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## Example Usage

### Update Full Name Only
```bash
curl -X PATCH \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John Smith"}' \
  https://api.example.com/api/users/profile/update/
```

### Update Password
```bash
curl -X PATCH \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "new_secure_password",
    "confirm_password": "new_secure_password",
    "current_password": "old_password"
  }' \
  https://api.example.com/api/users/profile/update/
```

### Update Multiple Fields
```bash
curl -X PATCH \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "password": "new_secure_password",
    "confirm_password": "new_secure_password",
    "current_password": "old_password"
  }' \
  https://api.example.com/api/users/profile/update/
```

## Security Notes
- Password fields are write-only and will not be returned in responses
- Current password verification is mandatory for password updates
- All password validations follow Django's built-in security standards
- Passwords are automatically hashed using Django's secure password hashing
