# Mujahid API Authentication Documentation

This documentation outlines the user account and authentication flows for the Mujahid API. The system supports traditional email/password registration, as well as social authentication via **Google** and **Apple**.

---

## 1. Traditional Sign-Up (Username & Password)

This flow is for users creating a new account using a username, email, and password.

- **Endpoint**: `POST /account/register/`
- **Request Body**:
  ```json
  {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "deviceId": "unique-device-id",
    "gender": "male",
    "pushNotificationToken": "optional-token"
  }
  ```
- **Process**:
  1. Validates that `username` and `email` are unique.
  2. Ensures `password` and `password_confirm` match.
  3. Creates a new user with status `not activated`.
  4. Generates and sends a 4-digit OTP to the user's email for verification.
- **Success Response**: Returns JWT `access` and `refresh` tokens.

---

## 2. Google Authentication (Email only, no Username required)

Allows users to sign up or sign in using their Google account. The system automatically handles account creation if the user doesn't exist.

- **Endpoint**: `POST /account/google_auth/`
- **Request Body**:
  ```json
  {
    "token": "google-id-token",
    "email": "user@gmail.com",
    "pushNotificationToken": "optional-token"
  }
  ```
- **Process**:
  - **Existing User**: If a user with this email exists, they are logged in. Their account is linked to Google if it wasn't already.
  - **New User**: If no user exists with this email, a new account is created. A unique, random username is automatically generated (e.g., `goldenwolf42`).
- **Response**:
  ```json
  {
      "refresh": "...",
      "access": "...",
      "data": { ...user_profile... },
      "message": "Sign-in successful",
      "newUser": false
  }
  ```
  _Note: `newUser` will be `true` if a new account was created._

---

## 3. Apple Authentication (No Email or Username required)

Allows users to sign up or sign in using Apple ID. This is designed to handle Apple's "Hide My Email" feature where the email might not be shared.

- **Endpoint**: `POST /account/apple_auth/`
- **Request Body**:

  ```json
  {
    "token": "apple-identity-token",
    "email": "user@example.com",
    "pushNotificationToken": "optional-token"
  }
  ```

  _Note: `email` is optional here as Apple might not provide it on subsequent logins._

- **Process**:
  - **Identification**: The system first tries to find the user by `email`. If not found (or not provided), it searches by the `apple_auth_token`.
  - **New User**: If no matching user is found, a new account is created with a generated unique username (e.g., `bravemujahid15`) and `is_apple_signin` set to `true`.
- **Response**: Similar to Google Auth, includes JWT tokens and user profile data.

---

## 4. Post-Social Login: Updating Username

Since social logins (Google/Apple) generate a random username (e.g., `silenthunter88`), users can update their username later once they've authenticated.

- **Endpoint**: `POST /account/update_username/`
- **Authentication**: Required (JWT Bearer Token)
- **Request Body**:
  ```json
  {
    "username": "my_new_preferred_username"
  }
  ```

---

## 5. Standard Login (Username and Password)

For users who registered via the traditional flow.

- **Endpoint**: `POST /account/login/`
- **Request Body**:
  ```json
  {
    "username": "johndoe",
    "password": "securepassword123"
  }
  ```
- **Response**: Returns standard JWT tokens (`refresh`, `access`).

---

## Key Technical Details

- **Token Type**: JWT (JSON Web Token).
- **Authentication Header**: For protected endpoints, use `Authorization: Bearer <access_token>`.
- **Unique Username Generation**: Social logins use a pool of 20 adjectives and 20 nouns combined with a random number to ensure uniqueness without user input.
- **Account Status**:
  - `not activated`: Default for email registration (requires OTP verification).
  - `activated`: Default for social logins or after OTP verification.
  - `suspended`: User cannot login.
