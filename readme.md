# Scorch Tracker API

A FastAPI-based backend for the Accountability Challenge system with WhatsApp integration and AI-powered roasting.

## Features

- **User Management**: Registration, authentication, and profile updates
- **Routine Tracking**: Create and manage daily routines and tasks
- **Progress Monitoring**: Track task completions and view statistics
- **WhatsApp Integration**: Reminders, roasts, and progress reports via WhatsApp
- **AI-Powered Roasting**: Customizable roast intensity for missed goals
- **Gamification**: Points system, achievements, and leaderboards

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Scheduler**: APScheduler
- **AI Integration**: Google Gemini API
- **Messaging**: WhatsApp Business API
- **Containerization**: Docker

## Project Structure

The project follows a clean, maintainable structure:

- `app/`: Main application package
  - `api/`: API routes and dependencies
  - `core/`: Core functionality like security and scheduling
  - `db/`: Database models and connection
  - `schemas/`: Pydantic models for validation
  - `services/`: Business logic and external services

## Getting Started

### Prerequisites

- Docker and Docker Compose
- WhatsApp Business API credentials
- Google Gemini API key

### Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your credentials
3. Start the application with Docker Compose:

```bash
docker-compose up -d
```

4. The API will be available at http://localhost:8000
5. API documentation is available at http://localhost:8000/docs

## API Endpoints

### Authentication

- `POST /api/v1/auth/login`: Log in and get access token

### Users

- `POST /api/v1/users/`: Create a new user
- `GET /api/v1/users/me`: Get current user information
- `PUT /api/v1/users/me`: Update current user

### Routines

- `POST /api/v1/routines/`: Create a new routine
- `GET /api/v1/routines/`: Get all user routines
- `GET /api/v1/routines/{routine_id}`: Get a specific routine
- `PUT /api/v1/routines/{routine_id}`: Update a routine
- `DELETE /api/v1/routines/{routine_id}`: Delete a routine

### Tasks

- `POST /api/v1/routines/{routine_id}/tasks`: Create a task
- `PUT /api/v1/routines/{routine_id}/tasks/{task_id}`: Update a task
- `DELETE /api/v1/routines/{routine_id}/tasks/{task_id}`: Delete a task

### Progress

- `POST /api/v1/progress/tasks/{task_id}/complete`: Mark a task as complete
- `GET /api/v1/progress/tasks/{task_id}/completions`: Get task completions
- `GET /api/v1/progress/completions`: Get all user completions

### WhatsApp

- `GET /api/v1/whatsapp/webhook`: Verify webhook
- `POST /api/v1/whatsapp/webhook`: Process webhook messages

## WhatsApp Commands

Users can interact with the system via WhatsApp using the following commands:

- Send a task number to mark it complete
- `tasks`: See your tasks for today
- `stats`: View your progress report
- `help`: Show available commands

## Development

To run the application in development mode:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export DATABASE_URL=postgresql://user:password@localhost:5432/scorch-tracker
export SECRET_KEY=your-secret-key
# Set other required environment variables

# Run the application
uvicorn app.main:app --reload
```

## License

This project is proprietary and confidential.
