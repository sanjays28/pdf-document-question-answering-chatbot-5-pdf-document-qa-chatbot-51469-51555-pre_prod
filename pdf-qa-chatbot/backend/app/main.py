from fastapi import FastAPI

app = FastAPI(title="PDF QA Chatbot")

@app.get("/")
async def root():
    return {"message": "Welcome to PDF QA Chatbot API"}