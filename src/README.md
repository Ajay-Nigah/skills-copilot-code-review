# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Display active, date-limited announcements
- Manage announcements while signed in as a teacher

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements/active`                                           | Get announcements currently within their start and expiration dates |
| GET    | `/announcements`                                                  | List all announcements (teacher sign-in required)                   |
| POST   | `/announcements`                                                  | Create an announcement (teacher sign-in required)                    |
| PUT    | `/announcements/{id}`                                             | Update an announcement (teacher sign-in required)                    |
| DELETE | `/announcements/{id}`                                             | Delete an announcement (teacher sign-in required)                    |

`/auth/login` sets a Secure, HttpOnly, SameSite=Strict session cookie. Each
announcement has a message and required expiration date; its start date is
optional. Set
`SCHOOL_TIMEZONE` to the school's IANA timezone (defaults to
`America/New_York`) so date-based visibility uses the school calendar. Set
`INITIAL_ANNOUNCEMENT_MESSAGE` to seed an initial announcement when the
announcements collection is empty; without it, no announcement is seeded.

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Activities, teachers, announcements, and login sessions are stored in MongoDB.
