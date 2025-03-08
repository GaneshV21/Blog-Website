# Blog Website

A simple blog website built using Flask and SQLAlchemy.

## Demo
[Click here to visit the blog website](https://blog-website-hzj2.onrender.com/)

## Features
- User authentication (Signup/Login)
- Create, Read, Update, and Delete blog posts
- Commenting system
- Responsive UI

## Technology Stack
- **Backend:** Flask, SQLAlchemy
- **Frontend:** HTML, CSS, JavaScript (if applicable)
- **Database:** SQLite / PostgreSQL
- **Deployment:** Render

## Installation

### Prerequisites
- Python 3.x
- Virtual Environment (recommended)

### Steps to Setup
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd blog-website
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```sh
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

5. Run the Flask application:
   ```sh
   flask run
   ```

## Folder Structure
```
blog-website/
│── app/
│   │── static/             # CSS, JS, Images
│   │── templates/          # HTML templates
│   │── __init__.py         # App initialization
│   │── models.py           # Database models
│   │── routes.py           # Routes and views
│   │── forms.py            # Flask-WTF Forms
│── migrations/             # Database migrations
│── venv/                   # Virtual environment
│── config.py               # Configuration settings
│── requirements.txt        # Python dependencies
│── run.py                  # Flask entry point
│── README.md               # Project documentation
```

## Environment Variables
Create a `.env` file and add:
```
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///site.db
```

## Deployment
1. Push the code to a Git repository.
2. Connect the repository to Render.
3. Set up environment variables in Render.
4. Deploy the application.

## Contributing
Feel free to fork this repository and contribute!

## License
MIT License
