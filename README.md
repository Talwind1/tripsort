# tripsort structure
TripSort/
├── data/
│   ├── mock_photos.json       # המטא-דאטה הגולמי (ID, GPS, Timestamp)
│   └── geo_cache.json        # (נוצר בהרצה) מטמון למניעת קריאות API מיותרות
├── src/
│   ├── services/             # "הפועלים" - תקשורת עם העולם החיצוני
│   │   ├── geo_service.py     # Nominatim API
│   │   ├── weather_service.py # Open-Meteo API
│   │   └── llm_service.py     # OpenAI/Claude API
│   ├── logic/                # "המוח" - עיבוד וקבלת החלטות
│   │   ├── coordinator.py     # Orchestration, Data Fusion & Hallucination Logic
│   │   └── context_manager.py # שמירת היסטוריית השיחה (Multi-turn)
│   └── main.py               # ה-Entry Point וה-CLI (הממשק למשתמש)
├── .env                      # API Keys (OpenAI)
├── .gitignore                # להתעלם מ-venv ומה-.env
└── requirements.txt          # הספריות להתקנה