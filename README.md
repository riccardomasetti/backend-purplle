# PurpLLe

## Overview

is a learning management application designed to help students continuously 
test their knowledge through organized study projects, tracked 
learning sessions, document management, and progress evaluation. Built with Flask 
and SQLAlchemy, this API-driven rappresent the backend of the complete application.
## Features

- **Project Management**: Create and manage learning projects with metrics
- **Document Management**: Upload, organize, and retrieve study materials
- **Learning Sessions**: Track study time and set learning objectives
- **Question Management**: Create and evaluate test questions with reference tracking
- **Progress Tracking**: Monitor performance through various metrics and milestones

## Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy 3.1.1
- **API**: RESTful API with JSON responses
- **File Storage**: Local file system storage for documents

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
   ```bash
   git clone https://your-repository-url/purplle.git
   cd purplle
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following content:
   ```
   DATABASE_URI=sqlite:///instance/purplle.db
   SECRET_KEY=<your_secret_key>
   UPLOAD_FOLDER=uploads
   MAX_CONTENT_LENGTH=16777216  # 16MB max upload size
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## Running the Application

Start the application with:

```bash
python run.py
```
