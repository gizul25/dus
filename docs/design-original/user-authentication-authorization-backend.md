# AA Page: backend design #31

## High-level design

## Module features

- User accounts allow for the user to be able to change their desk preferences
  - They can change the height, velocity and set specific settings as a profile
    for their needs
- User can choose a desk of choice which they want to work on
  - To do that they can interact with the map interface
  - If a desk is occupied the map interface will inform them that the desk in
    question is busy
- User can log into their account by providing the right credentials such as
  first and last name and password
- The interface allows users to report issues with their desk

### Maybe?

- Users can put in comments on the desks they are using for co-workers to see
  - Could be useful if they are not at their desk currently and want to notify
    others on a certain matter
- The users can view the amount of time they had spent while working on the desk

## Module handling

- Authorization
  - User can only log into their account by inputting the right data
- Error handling
  - Deny request if wrong or empty information is used
- Testing - Vitest, Playwright, manual

## Use cases

- User logs into their account
- User selects a desk to use
- User sets up their profile for work
- User changes their preferences in their settings
- User sends an error report
- User makes a comment(From the Maybe? section)
- User views time spent on desk(From the Maybe? section)

## Test cases

- User successfully logs into their account
- User successfully sets their preferences for the desk
- User is unable to send an error report(insufficient)
- User sends an error report successfully
- User leaves a comment successfully
- User is unable to leave a comment(insufficient)
- User is able to select a desk to work on
- User is unable to select a desk(busy or already chosen)

## Dependencies

### Module

- Data visualization
- Office map system
- Frontend
  - Web interface
- Databases
  - Error logs
  - User accounts

### External

- N/A

## JWT

```YAML
openapi: 3.0.0 # or whatever we're using
info:
  title: Authentication API (JWT)

  version: 1.0.0

servers:
  - url: # our server

paths:
 /auth/login:
  post:
   summary: Log in
   operationId: loginUser
   
   requestBody:
    required: true
    content:
     application/json:
      schema: 
       type: object
       required:
         - email
         - password
       properties:
        email: 
         type: string
         format: email
        password:
         type: string
        remember_me:
         type: boolean
         default: false
   responses:
    "200":
     description: successful login. If remember_me is true, the server sets a reftesh-token cookie.
     headers:
      Set-Cookie:
       description: onlt when remember_me is true
       schema: 
        type: string
     content:
      application/json:
       schema:
        type: object
        required:
         - access_token
         - token_type
         - expires_in
        properties:
         access_token:
          type: string
          description: a signed JWT
         token_type:
          type: string
          enum:
           - Bearer
         expires_in:
          type: integer
          description: lifetime in seconds
    "401":
     description: Invalid email or password
    
 /auth/account:
  get:
   description: returns the current account
   operationId: getCurrentAccount
   security:
    - bearerAuth: []
   responses:
    "200":
     description: current account returned with success
     content:
      application/json:
       schema:
        $ref: "#/components/schemas/User"
    "401":
     description: missing, invalid or expired token
     
 /auth/refresh:
  post:
   description: refresh access token
   operationId: refreshAccessToken
   security:
    - refreshCookie: []
   responses:
    "200":
     description: access token refreshed
     headers:
      Set-Cookie:
       schema:
        type: string
       description: sets the replacement refresh token cookie
     content:
      application/json:
       schema:
        type: object
        required:
         - access_token
         - token_type
         - expires_in
        properties:
         access_toke:
           type: string
         token_type:
          type: string
          enum:
           - Bearer
         expires_in:
          type: integer
    "401":
     description: missing, invalid, expired or revoked refresh token
   
  
 /auth/logout:
  post: 
   description: ends current login
   operationId: logoutUser
   security:
    - bearerAuth: []
   responses:
    "204":
     description: successful logout. Server revokes the associated refresh token and clears the refresh-token cookie, if present
    "401":
     description: missing, invalid or expired access token
         
         
components:
 securitySchemes:
  bearerAuth:
   type: http
   scheme: bearer
   bearerFormat: JWT
  refreshCookie:
   type: apiKey
   in: cookie
   name: refresh_token
   
 schemas:
  User:
   type: object
   required:
    - id
    - email
    - role
   properties:
    id:
     type: integer
    email:
     type: string
     format: email
    role:
     type: string
     enum:
      - user
      - admin
     
```

### Flow

**On login:**

1. Receive email and password
2. Find the user and verify the stored password hash
3. Create a signed JWT with claims such as
   - `sub`: user ID
   - `iat`: issued-at time
   - `exp`: expiration time (Unix timestamp)
   - `iss`: issuer
4. Return the token and its lifetime to the client **On requests:**
5. Client sends `Authorization: Bearer <access_token>`
6. Validate JWT signature with `HS256` algorithm and a securely stored key
7. Validates expiry and claims (`exp`, `iss`)
8. If invalid/expired => 401 Unauthorized
9. If valid => identify user (by user ID) and check their permissions (role)
10. If invalid role => 403 Forbidden On logout:
11. Validate access JWT
12. Identify the user and current login session
13. Revoke refresh token by setting `revoked_at`
14. Clear `refresh_token` cookie
15. Frontend deletes stored access token and updates

### JWT

- **Header**: contains metadata (ex. signing algorithm)
- **Payload**: contains claims
- **Signature**: verifies the token's integrity using a secret or private key

### Remember Me

For that we may need access token and a refresh token. **Access token**:
short-lived token sent with API requests.

- validated before granting access
- typically 30-90 minutes or few hours **Refresh token**: obtains new access
  tokens without the user needing to login again.
- issued only when "Remember me" is selected
- stored in `HttpOnly`, `Secure`, `SameSite=Lax` cookies
- set expiration time and invalidate expired tokens
- issue a new refresh token each time the old one is used and invalidate the
  previous one
- allow refresh tokens to be revoked (on logout)

```JSON
// Refresh Token in DB
{
 "id": "...",
 "user_id": "...",
 "token_hash": "...",
 "created_at": "...",
 "expires_at": "...",
 "revoked_at": "..."
}
```

## Hashing

Passwords:

- need to be stored as hashed, which should be done with `bcrypt`
- can be verified using the library's verification functions

## Database

```JSON
{
 "user_id": "...",
 "email": "...@gmail.com",  // unique
 "password_hash": "...",
 "role": "admin"
}
```
