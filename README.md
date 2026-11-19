# AI Mystery Quest

An interactive detective game built with Python, Flask, HTML, CSS, JavaScript, and the Groq API. Investigate cases, review suspects and clues, solve puzzles, ask for hints, chat with Detective AI, and track completed cases.

## Features
- Two mystery cases with suspects, motives, alibis, clues, and puzzles
- Detective AI chat and spoiler-light hints using Groq
- Demo Mode works when `GROQ_API_KEY` is missing or the API is unavailable
- Score tracking, progress bar, and saved game history
- Responsive dark theme for desktop and mobile

## Requirements
- Python 3.9 or newer
- Internet connection for Groq AI mode (Demo Mode works offline after installation)

## Install and run (Windows PowerShell)

1. Extract the ZIP and open PowerShell in the `ai-mystery-quest` folder.
2. Create a virtual environment:
   ```powershell
   python -m venv venv
   ```
3. Activate it:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run this once in the same terminal:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
   .\venv\Scripts\Activate.ps1
   ```
4. Install packages:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copy the example environment file:
   ```powershell
   Copy-Item .env.example .env
   ```
6. Open `.env` and add your Groq API key after `GROQ_API_KEY=`. Keep the key private. If you leave it blank, the game runs in Demo Mode.
7. Start the app:
   ```powershell
   python app.py
   ```
8. Open **http://127.0.0.1:5000** in your browser. Press `Ctrl+C` in PowerShell to stop the server.

## Run on macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your Groq API key to .env (optional)
python app.py
```

## Groq API
Create an API key in the Groq console and place it in `.env`. The key is read only by the Flask server; it is not sent to the browser. If the key is missing or the API request fails, hint/chat responses fall back to Demo Mode.

## Project structure

```text
ai-mystery-quest/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── game_history.json   # created automatically after solving a case
├── templates/
│   └── index.html
└── static/
    ├── app.js
    └── style.css
```

## Notes
- This is a learning/demo project. Flask's development server is not intended for production.
- The score is awarded once per successful solve attempt; history records completed cases.
- Never upload your real `.env` file or API key to GitHub.
