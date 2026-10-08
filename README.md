Btw, it's a partial commit ....................
The main code is not completely here ................

# Bialk

Bialk is a Flask-based social microblogging platform inspired by lightweight community networks. It includes user authentication, profile management, post creation, follower/following relationships, private messaging, notifications, search, translation, and background task support.

## Features

- User registration and login
- Profile editing and user pages
- Follow / unfollow functionality
- Timeline of posts from followed users
- Explore page for public content discovery
- Search across indexed posts
- Messaging between users
- Notifications for unread messages and events
- Post language detection and translation support
- Background job/task queue integration with Redis/RQ
- REST-like API endpoints for users and posts
- Flask admin-style app structure with blueprints

## Tech Stack

- Python
- Flask
- SQLAlchemy
- Flask-Login
- Flask-WTF
- Redis
- RQ (task queue)
- Elasticsearch integration
- Flask-Babel for localization
- PostgreSQL/MySQL compatible SQLAlchemy database backend

## Project Structure

```text
Bialk/
├── app/
│   ├── api/
│   ├── auth/
│   ├── errors/
│   ├── main/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── cli.py
│   ├── models.py
│   ├── search.py
│   ├── tasks.py
│   ├── translate.py
│   └── translations/
├── .flaskenv
├── .gitignore
├── babel.cfg
├── microblog.py
├── requirements.txt
├── tests.py
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- pip
- Redis server (required for background tasks and queue functionality)
- A supported database (configured through Flask app settings)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/bhivourdevnath-stack/Bialk.git
cd Bialk
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
# or
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment settings.

The repository includes a `.flaskenv` file with the default Flask app configuration:

```env
FLASK_APP=microblog.py
FLASK_DEBUG=1
```

If your local setup requires additional environment variables or a custom configuration class, add them before running the app.

## Running the Application

Start the development server:

```bash
flask run
```

Or run the app directly:

```bash
python microblog.py
```

The app should be available at:

```text
http://localhost:5000
```

## Database setup

If database migrations are enabled in your environment, initialize and apply them as needed:

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

If your project uses a different setup than the default Flask-Migrate configuration, adjust these commands to match your environment.

## Usage

Once running, users can:

- Create an account and sign in
- Publish posts on their feed
- Follow other users
- View a personalized timeline
- Send messages and inspect notifications
- Search posts and browse public content
- Use the translation feature on supported posts

## Testing

The repository includes a test file:

```bash
python tests.py
```

## Notes

This project follows the structure of a typical Flask microblogging application and is well-suited for learning, extending, and customizing social web features.

## License

This project does not currently declare a license in the repository metadata. If you plan to distribute or publish it, consider adding an appropriate open-source license.
