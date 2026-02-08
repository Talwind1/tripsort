import json
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from src.services.llm_service import LLMService
from src.logic.coordinator import TripCoordinator
from src.services.geo_service import GeoService
from src.services.weather_service import WeatherService


console = Console()

def main():
    console.print(Panel("Welcome to TripSort AI-Your Personal Photo Curator"))
    # load data
    enriched_path = 'data/enriched_photos.json'
    
    if not os.path.exists(enriched_path):
        console.print("Enriched data not found. Processing photos first...")
        with open('data/mock_photos.json', 'r') as f:
            mock_data = json.load(f)

        coordinator = TripCoordinator(GeoService(), WeatherService())
        enriched_data = coordinator.enrich_trip_data(mock_data)
        coordinator.save_enriched_data(enriched_data)
    else:
        with open(enriched_path, 'r') as f:
            enriched_data = json.load(f)

    llm = LLMService()

    chat_history = []
    # 2. לולאת הצ'אט
    while True:
        user_query = Prompt.ask("\n[bold green]How would you like to organize your trip photos today?[/bold green] (type 'exit' to quit)")
        
        if user_query.lower() in ['exit', 'quit']:
            console.print("[bold red]Goodbye! Happy traveling! ✈️[/bold red]")
            break

        with console.status("[bold blue]AI is analyzing your photos and weather data...[/bold blue]"):
            suggestion = llm.get_album_suggestions(enriched_data, user_query, chat_history=chat_history)

        console.print("\n[bold magenta]AI Suggestions:[/bold magenta]")
        console.print(Panel(suggestion, border_style="green"))

        chat_history.append({"role": "user", "content": user_query})
        chat_history.append({"role": "assistant", "content": suggestion})

if __name__ == "__main__":
    main()