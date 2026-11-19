import os, json, random
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DATA_FILE = Path(__file__).with_name("game_history.json")

CASES = [
    {
        "id": "museum", "title": "The Missing Diamond", "difficulty": "Easy",
        "intro": "A priceless blue diamond vanished from the city museum during its evening gala. The display case is intact.",
        "suspects": [
            {"name":"Maya Reed","role":"Museum curator","motive":"She was worried about the museum's debts.","alibi":"She says she was giving a speech at 8:00 PM."},
            {"name":"Leo Grant","role":"Security guard","motive":"He recently received a large gambling debt.","alibi":"He says he was checking the east entrance."},
            {"name":"Nina Cole","role":"Event photographer","motive":"She wanted an exclusive story.","alibi":"She says she was photographing guests in the main hall."}
        ],
        "clues": [
            {"title":"A dusty footprint","detail":"A small muddy footprint was found beside the display. It points toward the staff corridor."},
            {"title":"The camera log","detail":"The east entrance camera was manually paused at 8:04 PM using a staff access card."},
            {"title":"A torn badge sleeve","detail":"A clear plastic badge sleeve was found near the staff corridor. It has the initials L.G."}
        ],
        "puzzle": {"question":"Which suspect is most strongly linked to the paused camera and the badge sleeve?","answer":"leo","explanation":"The camera was paused with staff access, and the sleeve marked L.G. links the evidence to Leo Grant."},
        "solution":"Leo Grant"
    },
    {
        "id": "library", "title": "The Silent Library", "difficulty": "Medium",
        "intro": "A rare handwritten manuscript disappeared from a locked library room. No window was broken and the room was quiet all night.",
        "suspects": [
            {"name":"Oliver Price","role":"Librarian","motive":"He feared the manuscript would be sold.","alibi":"He says he locked up at 9:00 PM."},
            {"name":"Sara Finch","role":"Researcher","motive":"She wanted to publish its contents first.","alibi":"She says she left before closing."},
            {"name":"Ben Morris","role":"Cleaner","motive":"He was recently dismissed.","alibi":"He says he cleaned the hallway at 10:00 PM."}
        ],
        "clues": [
            {"title":"The key register","detail":"The room's spare key was signed out under the librarian's name at 9:30 PM."},
            {"title":"Fresh paper dust","detail":"Paper dust was found on the librarian's desk, matching the manuscript shelf."},
            {"title":"The hallway clock","detail":"The clock stopped at 9:42 PM, but its battery was still working; it had been deliberately adjusted."}
        ],
        "puzzle": {"question":"Who had documented access to the spare key? Enter the first name.","answer":"oliver","explanation":"The key register records the spare key under Oliver Price's name."},
        "solution":"Oliver Price"
    }
]

def history():
    if not DATA_FILE.exists(): return []
    try: return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (ValueError, OSError): return []

def save_history(entry):
    items = history()
    items.insert(0, entry)
    DATA_FILE.write_text(json.dumps(items[:50], indent=2), encoding="utf-8")

@app.route("/")
def index():
    return render_template("index.html", cases=CASES, demo=not bool(GROQ_API_KEY))

@app.route("/api/case/<case_id>")
def get_case(case_id):
    case = next((c for c in CASES if c["id"] == case_id), None)
    if not case: return jsonify(error="Case not found"), 404
    return jsonify({k:v for k,v in case.items() if k != "solution"})

@app.route("/api/hint", methods=["POST"])
def hint():
    data = request.get_json(silent=True) or {}
    case = next((c for c in CASES if c["id"] == data.get("case_id")), None)
    if not case: return jsonify(error="Choose a valid case."), 400
    prompt = f"You are a helpful detective game hint assistant. Give one short, spoiler-light hint for this case. Case: {case['title']}. Clues: {case['clues']}. Puzzle: {case['puzzle']['question']}. Player progress: {data.get('progress', 'just started')}."
    answer = ask_groq(prompt) if GROQ_API_KEY else None
    if not answer:
        answer = "Compare each clue with the suspects' access and alibis. Look for a name or detail that appears in more than one piece of evidence."
    return jsonify(reply=answer, mode="AI" if GROQ_API_KEY else "Demo")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("message") or "").strip()
    case = next((c for c in CASES if c["id"] == data.get("case_id")), None)
    if not case or not question: return jsonify(error="Select a case and enter a question."), 400
    prompt = f"""You are Detective AI in a family-friendly mystery game. Help the player reason, but do not reveal the solution directly unless they explicitly ask.
Case: {case['title']}
Story: {case['intro']}
Suspects: {case['suspects']}
Clues: {case['clues']}
Puzzle: {case['puzzle']['question']}
Player asks: {question}
Answer in 2-4 concise sentences."""
    answer = ask_groq(prompt) if GROQ_API_KEY else None
    if not answer:
        q = question.lower()
        if any(w in q for w in ["who", "suspect", "culprit"]):
            answer = "I would not accuse anyone from motive alone. Match the physical evidence to access, initials, and each suspect's alibi."
        elif "hint" in q or "clue" in q:
            answer = "Start with the clue that gives a specific person or access method, then see whether another clue supports it."
        else:
            answer = "Good question, detective. Separate confirmed facts from claims in the alibis, then compare the timeline with the physical clues."
    return jsonify(reply=answer, mode="AI" if GROQ_API_KEY else "Demo")

@app.route("/api/solve", methods=["POST"])
def solve():
    data = request.get_json(silent=True) or {}
    case = next((c for c in CASES if c["id"] == data.get("case_id")), None)
    if not case: return jsonify(error="Case not found"), 404
    guess = (data.get("guess") or "").strip().lower()
    correct = guess == case["solution"].lower() or guess == case["solution"].split()[0].lower()
    score = 100 if correct else 0
    if correct:
        save_history({"case":case["title"], "result":"Solved", "score":score, "date":datetime.now().strftime("%Y-%m-%d %H:%M")})
    return jsonify(correct=correct, score=score, solution=case["solution"] if correct else None,
                   explanation=case["puzzle"]["explanation"] if correct else "Not quite. Review the clues and try again.")

@app.route("/api/history")
def get_history():
    return jsonify(history=history())

def ask_groq(prompt):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type":"application/json"},
            json={"model":GROQ_MODEL, "messages":[{"role":"user","content":prompt}], "temperature":0.6, "max_tokens":220},
            timeout=20
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, ValueError):
        return None

if __name__ == "__main__":
    app.run(debug=True)
