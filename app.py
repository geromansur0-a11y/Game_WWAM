from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import random
import os

app = FastAPI(title="Who Wants to Be a Millionaire")

# Enable CORS for mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Questions database
QUESTIONS = [
    {
        "id": 1,
        "question": "Apa ibu kota Indonesia?",
        "options": ["Jakarta", "Bandung", "Surabaya", "Medan"],
        "correct_answer": 0,
        "level": 1,
        "prize": 500000
    },
    {
        "id": 2,
        "question": "Planet terdekat dari Matahari adalah?",
        "options": ["Venus", "Mars", "Merkurius", "Bumi"],
        "correct_answer": 2,
        "level": 1,
        "prize": 500000
    },
    {
        "id": 3,
        "question": "2 + 2 x 2 = ?",
        "options": ["6", "8", "4", "10"],
        "correct_answer": 0,
        "level": 2,
        "prize": 1000000
    },
    {
        "id": 4,
        "question": "Siapa penemu lampu pijar?",
        "options": ["Thomas Edison", "Nikola Tesla", "Alexander Graham Bell", "Albert Einstein"],
        "correct_answer": 0,
        "level": 2,
        "prize": 1000000
    },
    {
        "id": 5,
        "question": "Apa nama satelit alami Bumi?",
        "options": ["Phobos", "Deimos", "Bulan", "Titan"],
        "correct_answer": 2,
        "level": 3,
        "prize": 2000000
    },
    {
        "id": 6,
        "question": "Berapa jumlah provinsi di Indonesia saat ini?",
        "options": ["34", "33", "32", "35"],
        "correct_answer": 0,
        "level": 3,
        "prize": 2000000
    },
    {
        "id": 7,
        "question": "Apa simbol kimia untuk Emas?",
        "options": ["Ag", "Fe", "Au", "Cu"],
        "correct_answer": 2,
        "level": 4,
        "prize": 5000000
    },
    {
        "id": 8,
        "question": "Siapa presiden pertama Indonesia?",
        "options": ["Soeharto", "Soekarno", "BJ Habibie", "Megawati"],
        "correct_answer": 1,
        "level": 1,
        "prize": 500000
    },
    {
        "id": 9,
        "question": "Apa warna campuran biru dan kuning?",
        "options": ["Ungu", "Coklat", "Hijau", "Oranye"],
        "correct_answer": 2,
        "level": 2,
        "prize": 1000000
    },
    {
        "id": 10,
        "question": "Berapa banyak sisi yang dimiliki heksagon?",
        "options": ["5", "6", "7", "8"],
        "correct_answer": 1,
        "level": 3,
        "prize": 2000000
    }
]

# Lifelines
LIFELINES = {
    "50_50": {
        "name": "50:50",
        "used": False,
        "description": "Menghilangkan 2 jawaban salah"
    },
    "phone_friend": {
        "name": "Telepon Teman",
        "used": False,
        "description": "Konsultasi dengan teman"
    },
    "ask_audience": {
        "name": "Tanya Penonton",
        "used": False,
        "description": "Melihat persentase pilihan penonton"
    }
}

# Prize levels
PRIZE_LEVELS = [
    500000,    # Level 1
    1000000,   # Level 2
    2000000,   # Level 3
    5000000,   # Level 4
    10000000,  # Level 5
    25000000,  # Level 6
    50000000,  # Level 7
    100000000, # Level 8
    250000000, # Level 9
    500000000, # Level 10
    1000000000 # Level 11 - JACKPOT
]

class GameState(BaseModel):
    current_question: int = 0
    score: int = 0
    lifelines_used: List[str] = []
    game_over: bool = False
    questions_answered: List[int] = []
    guaranteed_prize: int = 0

# Game state storage (in production, use database)
game_state = GameState()

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/api/questions/{level}")
async def get_question(level: int):
    # Get questions for the specified level
    level_questions = [q for q in QUESTIONS if q["level"] == level]
    if not level_questions:
        raise HTTPException(status_code=404, detail="No questions found for this level")
    
    # Select a random question that hasn't been answered
    available_questions = [q for q in level_questions if q["id"] not in game_state.questions_answered]
    if not available_questions:
        available_questions = level_questions  # Reset if all questions used
    
    question = random.choice(available_questions)
    return question

@app.get("/api/game/start")
async def start_game():
    global game_state
    game_state = GameState()
    return {"message": "Game started", "prize_levels": PRIZE_LEVELS}

@app.get("/api/game/state")
async def get_game_state():
    return game_state

@app.post("/api/game/answer")
async def submit_answer(question_id: int, answer_index: int):
    # Find the question
    question = next((q for q in QUESTIONS if q["id"] == question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check answer
    if answer_index == question["correct_answer"]:
        game_state.score += question["prize"]
        game_state.current_question += 1
        game_state.questions_answered.append(question_id)
        
        # Update guaranteed prize
        if game_state.current_question <= len(PRIZE_LEVELS):
            game_state.guaranteed_prize = PRIZE_LEVELS[min(game_state.current_question - 1, 10)]
        
        response = {
            "correct": True,
            "prize_won": question["prize"],
            "total_score": game_state.score,
            "next_level": game_state.current_question
        }
    else:
        game_state.game_over = True
        response = {
            "correct": False,
            "correct_answer": question["correct_answer"],
            "prize_won": game_state.guaranteed_prize,
            "game_over": True
        }
    
    return response

@app.post("/api/game/quit")
async def quit_game():
    game_state.game_over = True
    return {
        "message": "Game ended",
        "prize_won": game_state.guaranteed_prize,
        "total_score": game_state.score
    }

@app.post("/api/lifelines/{lifeline_name}")
async def use_lifeline(lifeline_name: str, question_id: int):
    if lifeline_name not in LIFELINES:
        raise HTTPException(status_code=404, detail="Lifeline not found")
    
    if LIFELINES[lifeline_name]["used"]:
        raise HTTPException(status_code=400, detail="Lifeline already used")
    
    question = next((q for q in QUESTIONS if q["id"] == question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    LIFELINES[lifeline_name]["used"] = True
    game_state.lifelines_used.append(lifeline_name)
    
    response = {"lifeline": lifeline_name, "used": True}
    
    if lifeline_name == "50_50":
        # Remove 2 wrong answers
        wrong_indices = [i for i in range(4) if i != question["correct_answer"]]
        remove_indices = random.sample(wrong_indices, 2)
        response["remaining_options"] = [question["correct_answer"]] + [
            i for i in range(4) if i not in remove_indices
        ]
    
    elif lifeline_name == "phone_friend":
        # Simulate friend's suggestion (80% chance correct)
        if random.random() < 0.8:
            response["suggestion"] = question["correct_answer"]
        else:
            wrong_indices = [i for i in range(4) if i != question["correct_answer"]]
            response["suggestion"] = random.choice(wrong_indices)
    
    elif lifeline_name == "ask_audience":
        # Simulate audience poll
        correct_weight = 0.6
        weights = [0.1, 0.1, 0.1, 0.1]
        weights[question["correct_answer"]] = correct_weight
        
        # Distribute remaining weight
        remaining = 1 - correct_weight
        for i in range(4):
            if i != question["correct_answer"]:
                weights[i] = remaining / 3
        
        response["audience_poll"] = [int(w * 100) for w in weights]
    
    return response

@app.get("/api/lifelines")
async def get_lifelines():
    return LIFELINES

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
