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
