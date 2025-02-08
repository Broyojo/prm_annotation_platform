# PRM Annotation Platform

Some useful links:
- [Annotation Platform](https://prm.duckai.org)
- [Video on how to use the platform](https://youtu.be/3XettEOoCZw)
- [Main PRM github repo](https://github.com/TheDuckAI/prm)

## Developement
Setup instructions:

### Installation
You may either use pip or uv.

**With pip:**
```bash
$ python3 -m venv .venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
```

**With uv:**
```bash
$ uv sync
```

### Launch
The launch consists of a frontend session and a backend session.

**Backend Session**
```bash
$ cd backend
$ fastapi dev server.py # debug
# OR
$ fastapi run server.py # release
```

If the above commands fail, you can also run FastAPI as a module:
```bash
$ python -m fastapi run server.py
```

**Frontend Session**

There are two equivalent approach, bun or npm.

With npm:

installation
- For MacOS system, install node/npm/bun in brew.

```bash
$ cd frontend
$ npm install # one-time install
$ npm run start
```

With bun:
```bash
$ cd frontend
$ bun install # one-time install
$ bun run start
```

if success, the login in page can be accessed in http://localhost:3000/login.

#### Loading the database
Place database file (*.db) under `/backend`.

## Format of Database Export

```json
{
    "datasets": [
        {
            "name": "<dataset name>",
            "domain": "<dataset domain>",
            "problems": [
                {
                    "question": "...",
                    "answer": "...",
                    // ...
                    "annotations": [
                        {
                            "user": "<annotation author>",
                            "step_labels": {
                                "0": "Good",
                                "1": "Bad",
                                "5": "Error Realization",
                                // ...
                            }
                        },
                        // ...
                    ]
                },
                // ...
            ],
        },
        // ...
    ]
}
```

<!-- # Things that need to be done still:

1. save and load annotations for users

# Some old stuff:

Current plan:
1. Make annotation platform first with no user login system - just for the demo on friday
2. add user login system with API key and hardcoded users
3. add OAuth2 sign in with Huggingface or Github 

## Functional Requirements

1. Get unannotated questions from database
    - Call API to retrieve 
    - Use SQLite 
2. User System
    - Manually create API keys and distribute to annotator team
    - Store API key in cookies so relogin doesn't need to happen often
  
## User Stories

Annotators:
1. As a user, I want to be able to log onto the system, select some questions based on the dataset, and then start working on them.
2. As a user, I want to be able to efficiently and easily see the question, answer, and model answer for the question. This includes good latex and markdown support as well as making a split-screen format where the question and anwer are on the left, and the model answer is on the right. The model answer is split into steps so I can easily label each step as good, bad, neutral, or error realization. 
3. As a user, I want to be able to mark questions with certain tags which can be filtered and searched by.

Researchers:
1. As a researcher, I want to be able to upload problems to the platform through some simple API client library (just upload some json objects)
2. As a researcher, I want to be able to view problems in the database and see responses to them easily. 

Engineers:
1. As an engineer, I want unit testing and the code should be easy to read and functional.
2. As an engineer, There should be decent documentation.
3. As an engineer, there should be comprehensive error handling. -->