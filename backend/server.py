from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
rough plan:
- store data in sqlite db
- backend hands problems over to the fronend, frontend gives responses to problems and we store those. 
- make a client-side code to allow people to use the api from python code. they can upload problems that way too.
- each new dataset they add, a new dataset shows up on the front page of the annotation website
- also we need to have a user system (just manually make users since we don't want random people signing up)
"""
