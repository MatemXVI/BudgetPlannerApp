# Budget Planner – Szkielet aplikacji (Etap 1)

Ten repozytorium zawiera minimalny szkielet aplikacji zgodny z założeniami z pliku „Budget Planner – Stack Technologiczny i Założenia Projektowe”. Dodano prosty frontend zintegrowany z backendem – bez tworzenia osobnego katalogu „frontend”.

## Struktura

- app/
  - main.py — punkt wejściowy backendu (FastAPI), CORS, serwowanie frontendu, endpoint /api/ping
  - api/__init__.py — prosty router API z endpointem GET /api/ping
  - core/config.py — podstawowa konfiguracja aplikacji (ENV, DATABASE_URL, CORS)
  - database.py — inicjalizacja bazy przez SQLAlchemy (domyślnie SQLite, możliwość MySQL przez env)
  - static/
    - index.html — prosty frontend serwowany przez FastAPI (integracja z /api/ping)
    - main.js — logika wywołania API z frontendu
- requirements.txt — zależności Python

Uwaga: Zgodnie z wymaganiem backend i frontend znajdują się w katalogu `app` (bez osobnego folderu „frontend”).

## Szybki start (uruchomienie)

1. Stwórz i aktywuj wirtualne środowisko (opcjonalnie):
   - Windows (PowerShell):
     python -m venv .venv
     .venv\\Scripts\\Activate.ps1

2. Zainstaluj zależności:
   pip install -r requirements.txt

3. Uruchom serwer (FastAPI + Uvicorn):
   uvicorn app.main:app --reload

4. Otwórz przeglądarkę i przejdź do frontendu:
   - http://localhost:8000/ — strona główna (frontend) z przyciskiem sprawdzającym połączenie
   - Po kliknięciu powinieneś zobaczyć odpowiedź z API: {"message": "pong"}
   - Dokumentacja API (Swagger): http://localhost:8000/docs

## Konfiguracja bazy danych

- Domyślnie używane jest lokalne SQLite: `sqlite:///./budget_planner.db`.
- Aby użyć MySQL zgodnie z założeniami projektu, ustaw zmienną środowiskową:
  - Przykład: `DATABASE_URL=mysql+pymysql://user:password@localhost:3306/budget_planner`

## Notatki

- CORS jest włączony dla lokalnego dev (np. `http://localhost:5173`), jednak w obecnej integracji frontend jest serwowany z tego samego hosta/portu, więc nie jest wymagany do działania.
- Struktura jest gotowa do rozbudowy o modele, schematy, usługi i autentykację (JWT) w kolejnych etapach.
