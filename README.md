🤖 Personal AI Assistant (Python, ML, Voice Automation)

A voice & text–enabled Personal AI Assistant built with Python and Machine Learning for intent detection, permission-based app control, web search, notes, time/date, and fun responses (jokes/replies).
Designed to run safely with explicit user permissions and supports DEV mode (Codespaces/testing) and LOCAL mode (Windows system actions).

⚠️ System-level features (open/close apps, file access) require running locally on Windows.
GitHub Codespaces is used for development & testing logic (DEV mode).

------------------------------------------------------------------------------------------------------

✨ Features

🎤 Voice & Text Input

🧠 ML-based Intent Detection (TF-IDF + Logistic Regression)

🔐 Permission-based App Control (ask once, remember decisions)

🌐 Search the Web

📝 Notes (write/read with overwrite/append flow)

⏰ Time & Date

😂 Jokes & Smart Replies

🧪 DEV Mode (safe, no system calls)

🖥️ LOCAL Mode (Windows) for real app control

🧩 Modular Project Structure (core, actions, ml, security, tests, ui, voice)

------------------------------------------------------------------------------------------------------

🗂️ Project Structure
personal_ai/
├── actions/            # App actions (open/close/search/etc.)
├── core/               # Assistant routing, config
├── data/               # intents.csv (training data)
├── ml/                 # training pipeline
├── models/             # trained models (.pkl) [gitignored]
├── security/           # permissions logic
├── tests/              # tester scripts
├── ui/                 # future UI
├── voice/              # voice I/O
├── main.py             # entry point
├── requirements.txt
└── README.md

------------------------------------------------------------------------------------------------------

🚀 Getting Started
1️⃣ Setup (Local / Codespaces)
python -m venv .venv
source .venv/bin/activate        # Linux/Mac/Codespaces
# OR
.venv\Scripts\activate           # Windows

pip install -r requirements.txt

2️⃣ Train the Model
python ml/train.py
This creates:
models/intent_model.pkl
Model files are ignored by Git (models/*.pkl) and will update locally after each training.

3️⃣ Run the Assistant
python main.py
You’ll see:
🔧 Running in DEV mode
Personal AI ready.

------------------------------------------------------------------------------------------------------

⚙️ Modes (DEV vs LOCAL)

Set mode in:
core/config.py
MODE = "dev"    # safe testing (Codespaces)
# MODE = "local"  # real app control (Windows only)
DEV → prints what would happen
LOCAL → actually opens/closes apps (with permission)

------------------------------------------------------------------------------------------------------

🔐 Security & Permissions

On first use, the assistant asks:
“Do you allow me to open Chrome in the future?”
✅ If allowed → saved to app_permissions.json
❌ If denied → action blocked
🔁 Permissions are reused next time
The assistant only scans approved locations and never acts without consent.

------------------------------------------------------------------------------------------------------

🧪 Testing

Run intent tests:
python tests/tester.py
Example output:
✅ PASS | 'open chrome' → open_app
❌ FAIL | 'exit' → close_app

------------------------------------------------------------------------------------------------------

🧠 ML Model

Features: word + char n-grams
Classifier: Logistic Regression
Balanced class weights
Confidence gating for noisy inputs
Active-learning ready (can log corrections for retraining)
You can keep improving accuracy by adding more examples to data/intents.csv.

------------------------------------------------------------------------------------------------------

📌 Notes

Codespaces = dev/testing only
Windows = required for real system actions
Trained models are local artifacts (not pushed to GitHub)

------------------------------------------------------------------------------------------------------

🚀 Future Enhancements

Planned improvements to make the assistant more powerful, accurate, and user-friendly:

🔁 Auto-Learning Pipeline
Collect real user voice/text inputs → clean noisy data → retrain model nightly → deploy new model only if accuracy improves.

🧠 Advanced NLP Understanding
Support compound commands like:

“Open Chrome and search Python tutorials”
“Type hello in notes and save it”

🧩 Entity & Slot Extraction
Detect app names, search queries, and file names separately from intent.

🗣️ Better Voice Recognition
Improve handling of accents, typos, and Hinglish (e.g., “bhai open chrome”).

🖼️ Desktop UI
Simple window UI with:

Mic button

Text input

Conversation history

📊 Model Versioning & Rollback
Maintain:

current_model.pkl

candidate_model.pkl

backup_model.pkl
Automatically rollback if accuracy drops.

🔐 Granular Permissions
Per-app and per-action permissions (open, close, read, write separately).

🧪 Automated Test Suite
CI tests for intent accuracy and regression checks on every update.

🌐 Plugin System
Allow adding new skills (weather, reminders, email, music) as plug-and-play modules.

------------------------------------------------------------------------------------------------------

👤 Author
Sahil Rathod
GitHub: https://github.com/developershahil



