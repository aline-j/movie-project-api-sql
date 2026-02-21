# 🎬 My Movies Database

A command-line application for managing a personal movie database.
Movies are stored in a SQLite database and enriched with data from the OMDb API.

## Features

- Add movies via OMDb API
- Update and delete movies
- Search (fuzzy matching)
- Statistics (average, median, best/worst)
- Filter and sort movies
- Generate a static HTML website

## Tech Stack

- Python 3.10+
- SQLite
- SQLAlchemy
- OMDb API

## Setup

⚠️ IMPORTANT: Before starting, the environment variable OMDB_API_KEY must be set!

### 1. Obtain your OMDb API key

• Go to omdbapi.com
• Register for free and receive your API key
• Max. 1,000 requests/day (free)

### 2. Clone repository

```bash
git clone <repo-url>
cd movie-project-api-sql
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set OMDb API Key as Environment Variable

Using a .env file (recommended):

1. Install python-dotenv: `pip install python-dotenv`

2. Create a .env file in the project folder:
   OMDB_API_KEY=your_api_key_here

### 5. Start application

```bash
python app/main.py
```
