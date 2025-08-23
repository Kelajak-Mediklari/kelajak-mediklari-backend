# Register API

## Endpoint
`POST /users/register/`

## Description
Register a new user account with phone verification. This endpoint requires a valid OTP code that was sent via the `send-auth-verification-code/` endpoint.

## Request Body
```json
{
    "phone": "+998945552233",
    "full_name": "John Doe", 
    "password": "securepassword123",
    "device_id": "unique_device_identifier",
    "code": "123456",
    "session": "session_key_from_verification"
}
```

## Fields
- `phone` (string, required): Phone number in E164 format (e.g., "+998945552233")
- `full_name` (string, required): User's full name
- `password` (string, required): User's password (minimum 8 characters)
- `device_id` (string, required): Unique device identifier
- `code` (string, required): 6-digit verification code received via SMS
- `session` (string, required): Session key received from `send-auth-verification-code/` endpoint

## Response

### Success (201 Created)
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "full_name": "John Doe",
        "username": "john_doe",
        "phone": "+998945552233",
        "avatar": null
    },
    "created": true
}
```

### Error Responses

#### Invalid Code (400)
```json
{
    "code": ["Wrong code!"]
}
```

#### User Already Exists (400)
```json
{
    "phone": ["User with this phone number already exists."]
}
```

#### Validation Error (400)
```json
{
    "password": ["Password must be at least 8 characters long."],
    "full_name": ["Full name cannot be empty."]
}
```

## Usage Flow
1. Call `send-auth-verification-code/` with phone number to get OTP
2. Receive SMS with verification code and session key
3. Call `register/` with all required fields including the verification code and session
4. Use returned tokens for authenticated requests

## Notes
- Phone number must be unique in the system
- Password is automatically hashed before storage
- Username is auto-generated from full name
- Device ID is stored for session management
- Tokens include device ID for multi-device support
