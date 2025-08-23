# Send Forget Password Code API

## Overview
This endpoint sends an OTP (One-Time Password) code to the user's phone number for password reset verification. The user must provide their registered phone number, and they will receive a 4-digit verification code via SMS.

## Endpoint
- **URL:** `/api/users/auth/send-forget-password-code/`
- **Method:** `POST`
- **Authentication:** Not required

## Request Body
```json
{
    "phone": "+998945552233"
}
```

## Field Descriptions
- `phone` (string, required): User's phone number in E164 format (e.g., "+998945552233")

## Rate Limiting
- Maximum 5 requests per phone number within 2 minutes
- Cooldown period: 2 minutes after reaching the limit

## Response

### Success Response (200 OK)
```json
{
    "session": "A1B2C3D4E5F6G7H8"
}
```

### Field Descriptions
- `session`: 16-character session key required for the ForgetPassword API

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

#### 400 Bad Request - Rate Limit Exceeded
```json
{
    "send_forget_password_code": ["You have reached the limit of sending forget password code. Try again later."]
}
```

## Example Usage

### Valid Request
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"phone": "+998945552233"}' \
  https://api.example.com/api/users/auth/send-forget-password-code/
```

### Response
```json
{
    "session": "A1B2C3D4E5F6G7H8"
}
```

## Workflow
1. User provides their registered phone number
2. System validates the phone number format and checks if user exists
3. If valid, system generates a 4-digit OTP code
4. SMS is sent to the provided phone number with the verification code
5. System returns a session key for the next step (ForgetPassword API)
6. The OTP code expires after 2 minutes

## Security Notes
- OTP codes are valid for 2 minutes only
- Rate limiting prevents spam and abuse
- Session keys are unique for each request
- Phone number must be registered in the system
- In production, real SMS is sent; in development/test mode, a static code "7777" is used

## Next Step
After receiving the session key, use the ForgetPassword API with:
- The phone number
- The OTP code received via SMS
- The session key from this response
- The new password
