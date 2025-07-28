# Collaborative Text Editor

A **Collaborative Text Editor** built with Django and Django Channels, enabling real-time collaborative editing of documents. This application allows multiple users to edit the same document simultaneously, manage version history, share documents with others, and utilize rich text formatting features.

---

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Contact](#contact)

---

## Features

- **Real-Time Collaboration**: Multiple users can edit the same document simultaneously with updates reflected in real-time using WebSockets.
- **User Authentication**: Secure login and signup functionality leveraging Django's built-in authentication system.
- **Document Sharing**: Share documents with other registered users to collaborate on editing.
- **Version Control**: Maintain a history of document versions with the ability to view and revert to previous versions.
- **Rich Text Formatting**: Utilize formatting options such as bold, italic, underline, strikethrough, text alignment, and list creation.
- **Download Options**: Export documents in various formats including HTML, TXT, and DOC.
- **Autosave**: Automatically save document changes at regular intervals to prevent data loss.
- **Responsive Design**: User-friendly interface optimized for both desktop and mobile devices.
- **Theme Toggle**: Switch between dark and light themes for personalized viewing.

---

## Technologies Used

- **Backend**:
  - [Django](https://www.djangoproject.com/) - Web framework for Python.
  - [Django Channels](https://channels.readthedocs.io/en/stable/) - Extends Django to handle WebSockets and background tasks.
  - [Daphne](https://github.com/django/daphne) - ASGI server for deploying Django Channels applications.
  - [Redis](https://redis.io/) - In-memory data structure store used as a channel layer backend.
  
- **Frontend**:
  - [Bootstrap 5](https://getbootstrap.com/) - Frontend component library for responsive design.
  - [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) - Client-side scripting for interactive features.
  
- **Others**:
  - [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) - Protocol for real-time communication.
  - [SQLite](https://www.sqlite.org/index.html) - Lightweight relational database for development.

---

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.11+**: Make sure Python is installed on your system. You can download it from [here](https://www.python.org/downloads/).
- **Redis**: Required for handling WebSocket connections. Installation instructions can be found [here](https://redis.io/download).
- **Daphne** Required for use with ASGI.
- **pip**: Python package installer. It typically comes bundled with Python.
- **Virtual Environment (optional but recommended)**: Tools like `venv` or `virtualenv` help manage project dependencies.

---
## Project Structure

```plaintext
collaborative-text-editor/
├── web_project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── hello/
│   ├── migrations/
│   ├── static/
│   │   └── hello/
│   │       ├── editor.js
│   │       ├── scripts.js
│   │       └── styles2.css
│   ├── templates/
│   │   └── hello/
│   │       ├── base.html
│   │       ├── create_document.html
│   │       ├── delete_document.html
│   │       ├── document_list.html
│   │       ├── editor.html
│   │       ├── error.html
│   │       ├── login.html
│   │       ├── revert_version.html
│   │       ├── share_document.html
│   │       ├── signup.html
│   │       ├── version_history.html
│   │       └── view_version.html
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── forms.py
│   ├── models.py
│   ├── routing.py
│   ├── tests.py
│   └── views.py
├── manage.py
├── requirements.txt
└── README.md
```



## Installation

1. **Create and activate a virtual environment**
    python3 -m venv venv
    source .venv/bin/activate 
    On Windows, use venv\Scripts\activate

2. **Install dependencies**
    pip install -r requirements.txt


##  Configuration

1. **Set up Redis**
    Ensure Redis is installed and running on your machine. By default, the application expects Redis to be accessible at 127.0.0.1:6379. If Redis is running elsewhere, update the CHANNEL_LAYERS configuration in settings.py accordingly.

2. **Apply database migrations to set up the SQLite database.**
    python manage.py migrate

3. **To access the Django admin interface, create a superuser account.**
    python manage.py createsuperuser


## Running the application

1. **Start redis server**
    redis-server

2. **Run Django Development Server with Daphne in a separate terminal**
    daphne web_project.asgi:application

3. **Navigate to localhost or 127.0.0.1:8000**


## Usage

   - **Sign Up**
        Navigate to the signup page to create a new account.
        Provide a unique username and password to register.

   - **Login**
        Use your credentials to log in to the application.
        Upon successful login, you'll be redirected to your document list.

   - **Manage_Documents**
        Create Document: Click on "Create New Document" to start a new text document.
        Edit Document: Click on "Edit" to open the collaborative editor for a specific document.
        Share Document: Share your document with other users to collaborate.
        Delete Document: Remove documents you no longer need.
        Version History: View and manage different versions of your documents.

   - **Collaborative Editing**
        When multiple users are editing the same document, changes will be reflected in real-time.
        Typing indicators show when other users are actively editing.

   -  **Formatting and Downloading**
        Use the toolbar to apply text formatting such as bold, italic, underline, and more.
        Download your document in various formats like HTML, TXT, or DOC.

   - **Theme Toggle**
        Switch between dark and light themes using the toggle button in the navigation bar.


## Contact

For any inquiries or feedback, please contact **ansh.madan_ug25@ashoka.edu.in**