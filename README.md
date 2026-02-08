# 📸 TripSort AI

AI-powered photo organization assistant that uses location, weather, and time data to curate travel photos.

## Features

- Multi-turn conversations with context memory
- GPS → Location names (Nominatim API)
- Historical weather data (Open-Meteo API)
- Time categorization (Morning/Afternoon/Evening/Night)
- Hallucination prevention (validates AI responses)
- Web UI + CLI interface

## Quick Start

### 1. Install

pip install -r requirements.txt

### 2. Setup

Create `.env` file:
OPENAI_API_KEY=your_key_here

### 3. Run

Open **2 terminals** in project directory:

**Terminal 1** - Enrich data (run once):
PYTHONPATH=. python3 src/main.py

**Terminal 2** - Start web app:
PYTHONPATH=. streamlit run src/app.py

## Tech Stack

- OpenAI GPT-4o-mini
- Nominatim (geocoding)
- Open-Meteo (weather)
- Streamlit (UI)

## Troubleshooting

**Import errors?** Always run with `PYTHONPATH=.` from project root

**Missing data?** Run enrichment: `PYTHONPATH=. python3 src/logic/coordinator.py`