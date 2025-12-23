from fastapi import FastAPI
from fastapi.responses import FileResponse
import json

app = FastAPI()

# Simple in-memory questions
questions = [
    {
        "id": 1,
        "question": "Apa ibu kota Indonesia?",
        "options": ["Jakarta", "Bandung", "Surabaya", "Medan"],
        "correct": 0,
        "prize": 500000
    },
    {
        "id": 2,
        "question": "Planet terdekat dari Matahari?",
        "options": ["Venus", "Mars", "Merkurius", "Bumi"],
        "correct": 2,
        "prize": 1000000
    }
]

prizes = [500000, 1000000, 2000000, 5000000, 10000000]

@app.get("/")
async def home():
    return FileResponse("index.html")

@app.get("/api/questions")
async def get_questions():
    return questions

@app.get("/api/prizes")
async def get_prizes():
    return prizes

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
