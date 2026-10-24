# DroneLearn — Drone Education and Training System

**CS 4500 — CIT Seminar | Fall 2026**  
**University:** William Paterson University of New Jersey  
**Instructor:** Professor Nan Wang

## Project Overview

DroneLearn is a web-based educational platform designed to help middle school students learn about drone technology, flight safety, and introductory programming.

The project was developed as an individual CS 4500 capstone project.

## Main Features

- Three educational lessons covering drone fundamentals, flight safety, and Blockly programming concepts.
- Interactive lesson knowledge checks.
- Five-question multiple-choice quiz with automatic scoring.
- Student lesson completion tracking.
- Instructor login and protected dashboard.
- Student quiz scores and progress reporting.
- CSV export of quiz results.

## Technologies Used

- Python
- Flask
- HTML, CSS, and JavaScript
- SQLite
- Werkzeug password hashing

## How to Run the Project

1. Download or clone the repository.
2. Open the project folder in Visual Studio Code.
3. Open the terminal.
4. Create a Python virtual environment:

   `python3 -m venv .venv`

5. Activate the environment:

   `source .venv/bin/activate`

6. Install the required dependencies:

   `python -m pip install Flask Werkzeug`

7. Create a local `.env` file containing a securely generated `SECRET_KEY` and an `INSTRUCTOR_PASSWORD_HASH` generated using Werkzeug.

8. Start the application:

   `python app.py`

9. Open the website in your browser:

   `http://127.0.0.1:5002`

## Project Structure

- `app.py` — Flask application, routes, authentication, and quiz processing.
- `database.py` — SQLite database initialization.
- `templates/` — Website HTML templates.
- `static/` — CSS, JavaScript, images, and other static resources.
- `.gitignore` — Excludes local configuration, database files, and temporary files.

## Testing

The application was manually tested for quiz submissions, lesson completion, instructor authentication, dashboard functionality, and CSV export.

## Current Limitations

DroneLearn is currently a locally runnable prototype and has not been verified as a publicly hosted application.

## Future Improvements

- Secure public deployment.
- Individual student accounts.
- Additional educational lessons.
- Improved instructor reporting.
- Automated testing and accessibility improvements.

## Privacy and Security

Private environment variables, passwords, student records, and local database files should not be committed to GitHub.

School images and videos should only be shared publicly with appropriate permission.

## Project Status

Completed capstone prototype with a local Flask application, student lessons, quiz functionality, and instructor dashboard.
