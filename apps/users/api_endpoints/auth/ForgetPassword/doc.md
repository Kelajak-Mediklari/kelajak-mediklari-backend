# Forget Password API

## Overview
This endpoint allows users to reset their password using OTP verification. Users must first use the SendForgetPasswordCode API to receive an OTP code, then use this endpoint to set a new password.

## Endpoint
- **URL:** `/api/users/auth/forget-password/`
- **Method:** `POST`
- **Authentication:** Not required

## Request Body
```json
{
    "phone": "+998945552233",
    "code": "1234",
    "session": "A1B2C3D4E5F6G7H8",
    "password": "new_secure_password",
    "confirm_password": "new_secure_password"
}
```

## Field Descriptions
- `phone` (string, required): User's phone number in E164 format (same as used in SendForgetPasswordCode)
- `code` (string, required): 4-digit OTP code received via SMS
- `session` (string, required): 16-character session key from SendForgetPasswordCode API
- `password` (string, required): New password (must meet security requirements)
- `confirm_password` (string, required): Password confirmation (must match password)

## Password Requirements
- Minimum 8 characters
- Cannot be too common (e.g., "password123")
- Cannot be too similar to user information
- Cannot be entirely numeric
- Must pass Django's built-in password validation

## Response

### Success Response (200 OK)
```json
{
    "message": "Password has been reset successfully.",
    "success": true
}
```

### Error Responses

#### 400 Bad Request - Invalid Phone Format
```json
{
    "phone": ["Enter a valid phone number."]
}
```

#### 400 Bad Request - User Not Found
```json
{
    "phone": ["User with this phone number does not exist."]
}
```

#### 400 Bad Request - Invalid OTP Code
```json
{
    "code": ["Wrong code!"]
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

#### 400 Bad Request - Invalid Code Length
```json
{
    "code": ["Ensure this field has exactly 4 characters."]
}
```

#### 400 Bad Request - Invalid Session Length
```json
{
    "session": ["Ensure this field has exactly 16 characters."]
}
```

## Example Usage

### Valid Request
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+998945552233",
    "code": "1234",
    "session": "A1B2C3D4E5F6G7H8",
    "password": "new_secure_password",
    "confirm_password": "new_secure_password"
  }' \
  https://api.example.com/api/users/auth/forget-password/
```

### Response
```json
{
    "message": "Password has been reset successfully.",
    "success": true
}
```

## Complete Workflow

### Step 1: Send OTP Code
```bash
# Request OTP code
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998945552233"}' \
  https://api.example.com/api/users/auth/send-forget-password-code/

# Response
{
    "session": "A1B2C3D4E5F6G7H8"
}
```

### Step 2: Reset Password
```bash
# Reset password with OTP
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+998945552233",
    "code": "1234",
    "session": "A1B2C3D4E5F6G7H8",
    "password": "new_secure_password",
    "confirm_password": "new_secure_password"
  }' \
  https://api.example.com/api/users/auth/forget-password/

# Response
{
    "message": "Password has been reset successfully.",
    "success": true
}
```

## Security Features
- ✅ OTP verification required
- ✅ Session-based verification
- ✅ Password strength validation
- ✅ Password confirmation matching
- ✅ OTP expires after 2 minutes
- ✅ One-time use OTP (deleted after successful verification)
- ✅ User existence validation
- ✅ Secure password hashing

## Error Handling
- Invalid OTP codes are rejected
- Expired sessions return validation errors
- Non-existent users are handled gracefully
- Weak passwords are rejected with detailed feedback
- All user inputs are properly validated

## Notes
- The OTP code and session are single-use and expire after successful password reset
- In development/test mode, the static code "7777" can be used
- The user can immediately log in with the new password after successful reset
