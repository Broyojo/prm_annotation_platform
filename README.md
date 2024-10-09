Current plan:
1. Make annotation platform first (with hardcoded users and api key login) - just make enough for the demo on Thursday
2. Then, add OAuth2 sign in with Huggingface or Github 

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
3. As an engineer, there should be comprehensive error handling.