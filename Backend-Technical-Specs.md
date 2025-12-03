# Backend Server Technical Sepcs

## Business Goal:
A language learning school wants to build a prototype of learning portal which will act as three things: 
-Inventory of possible vocabulary that can be learned
-Act as a Learning record store (LRS), providing correctand wrong score on practice vocabulary
-A unified launchpad to launch different learning apps


## Technical Requirements:
 - The backend will be built using python and flask framework
 - Invoke is a task runner for Python.
 - The database will be sqlite3
 - The api endpoints will be RESTful
 - The api will always return json responses
 - There will be no authentication or authorization
 - Everything will be treated as a single user

## Directory Structure

``` text
backend_go/
├── app.py                 # Flask application entry point
├── words.db              # SQLite database
├── db/                   # Database folder
│   ├── migrations/       # SQL migration files
│   └── seeds/           # JSON seed data files
├── models/              # Database models
├── routes/              # API endpoint handlers
├── tasks.py             # Invoke task runner configuration
└── requirements.txt     # Python dependencies
```

## Database Schema:
Our database will be a single sqlite database called `words.db` that will be in the root of the project folder of `backend_go`

The database will have the following tables:
- words: store vocabulary words
    - id integer
    - japasese string
    - romaji string
    - english string
    - parts json

- words_groups: many-to-many relationship between words and groups
    - id integer
    - word_id integer
    - group_id integer

- groups: thematic groups of words
    - id integer
    - name string

- study_seeions: records of study sessions grouping word_review_items
    -id integer
    -group_id integer
    -created_at datetime
    -study_activity_id integer

- study_activities: a specifc study activity, linking a study session to group
    -id integer
    -study_session_id integer
    -group_id integer
    -created_at datetime

- words_review-items: a record of word practice determining if the word was correct or not
    -word_id integer
    -study_session_id integer
    -correct boolean
    -created_at datetime


### API Endpoints

### GET /api/dashboard/last_study_session
**Response:**
```json
{
  "id": 1,
  "study_activity_id": 5,
  "activity_name": "Hiragana Practice",
  "group_id": 2,
  "group_name": "Basic Characters",
  "created_at": "2025-01-15T10:30:00Z",
  "correct_count": 18,
  "wrong_count": 2,
  "total_reviews": 20
}
```

### GET /api/dashboard/-study_progress
**Response:**
```json
{
  "total_words_studied": 45,
  "total_words_available": 500,
  "mastery_percentage": 9.0,
  "last_studied_date": "2025-01-15T10:30:00Z"
}
```

### GET /api/dashboard/quick-stats
**Response:**
```json
{
  "success_rate": 80.5,
  "total_study_sessions": 12,
  "total_active_groups": 5,
  "study_streak_days": 4
}
```

### GET /api/api/study_activities/:id
**Response:**
```json
{
  "id": 1,
  "name": "Hiragana Quiz",
  "description": "Practice hiragana characters",
  "thumbnail_url": "/images/hiragana.png",
  "activity_type": "quiz",
  "launch_url": "https://external-app.com/hiragana",
  "created_at": "2025-01-01T00:00:00Z"
}
```

### GET /api/api/study_activities/:id/study_sessions
**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "activity_name": "Hiragana Quiz",
      "group_name": "Basic Characters",
      "start_time": "2025-01-15T10:30:00Z",
      "end_time": "2025-01-15T10:45:00Z",
      "review_item_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 42
  }
}
```


### POST /api/study_activities
       - required params: group_id, study_activity_type
**Request:**
```json
{
  "group_id": 2,
  "study_activity_type": "quiz"
}
```
**Response:**
```json
{
  "id": 25,
  "study_session_id": 1,
  "group_id": 2,
  "created_at": "2025-01-15T10:30:00Z"
}
```


### GET /api/words
        - pagination with 100 items per page
**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "japanese": "あ",
      "romaji": "a",
      "english": "a",
      "correct_count": 10,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total_pages": 5,
    "total_items": 500
  }
}
```

### GET /api/words/:id
**Response:**
```json
{
  "id": 1,
  "japanese": "あ",
  "romaji": "a",
  "english": "a",
  "parts": ["consonant", "vowel"],
  "correct_count": 10,
  "wrong_count": 2,
  "groups": [
    {
      "id": 1,
      "name": "Hiragana"
    },
    {
      "id": 2,
      "name": "Basic Characters"
    }
  ]
}
```

### GET /api/groups
        - pagination with 100 items per page
**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Hiragana",
      "word_count": 46
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total_pages": 2,
    "total_items": 150
  }
}
```

### GET /api/groups/:id
**Response:**
```json
{
  "id": 1,
  "name": "Hiragana",
  "total_word_count": 46,
  "created_at": "2025-01-01T00:00:00Z"
}
```

### GET /api/groups/:id/words
**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "japanese": "あ",
      "romaji": "a",
      "english": "a",
      "correct_count": 10,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total_pages": 1,
    "total_items": 46
  }
}
```

### GET /api/groups/:id/study_sessions

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "activity_name": "Hiragana Quiz",
      "group_name": "Hiragana",
      "start_time": "2025-01-15T10:30:00Z",
      "end_time": "2025-01-15T10:45:00Z",
      "review_item_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total_pages": 2,
    "total_items": 150
  }
}
```

### GET /api/study_sessions
       - pagination with 100 items per page
**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "activity_name": "Hiragana Quiz",
      "group_name": "Basic Characters",
      "start_time": "2025-01-15T10:30:00Z",
      "end_time": "2025-01-15T10:45:00Z",
      "review_item_count": 20
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total_pages": 3,
    "total_items": 250
  }
}
```

### GET /api/study_sessions/:id
**Response:**
```json
{
  "id": 1,
  "activity_name": "Hiragana Quiz",
  "group_name": "Basic Characters",
  "start_time": "2025-01-15T10:30:00Z",
  "end_time": "2025-01-15T10:45:00Z",
  "review_item_count": 20,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### GET /api/study_sessions/:id/words
**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "word_id": 5,
      "japanese": "あ",
      "romaji": "a",
      "english": "a",
      "correct": true,
      "reviewed_at": "2025-01-15T10:31:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total_pages": 1,
    "total_items": 20
  }
}
```

### POST /api/reset_history
**Response:**
```json
{
  "message": "Study history reset successfully",
  "deleted_sessions": 25,
  "deleted_reviews": 500
}
```

### POST /api/full_reset
**Response:**
```json
{
  "message": "Database reset and reseeded successfully",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### POST /api/study_sessions/:id/words/:word_id/review
    - required params: correct
**Request:**
```json
{
  "correct": true
}
```
**Response:**
```json
{
  "id": 1,
  "word_id": 5,
  "study_session_id": 1,
  "correct": true,
  "created_at": "2025-01-15T10:31:00Z"
}
```

## Tasks Runner Tasks
Lets list out possible tasks we need for our lang portal.

### Initialize Database
This task will initialize the sqlite database called `words.db`

### Migrate Database
This task will run a series of migrations sal files on the database

Migrations live in the `db/migrations` folder.
The migration files will be run in order of their file name.
The file names should looks like this:

```sql
0001_init.sql
0002_create_words_table.sql 
```

### Seed Data
This task will import json files and transform them into target data for our database.
All seed files live in the `db/seeds` folder.
In our task we should have DSL to specific each seed file and its expected group word name.


```json
[
    {
        "kanji": "払う”,
        "romaji": "harau",
        "english": "to pay",
    },
    ...
]
```