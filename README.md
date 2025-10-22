# Budget Planner – Szkielet aplikacji (Etap 1)

Ten repozytorium zawiera minimalny szkielet aplikacji zgodny z założeniami z pliku „Budget Planner – Stack Technologiczny i Założenia Projektowe”.

## Struktura

- app/
  - main.py — punkt wejściowy backendu (FastAPI), CORS, endpoint /api/ping
  - api/__init__.py — prosty router API z endpointem GET /api/ping
  - core/config.py — podstawowa konfiguracja aplikacji (ENV, DATABASE_URL, CORS)
  - database.py — inicjalizacja bazy przez SQLAlchemy (domyślnie SQLite, możliwość MySQL przez env)
- requirements.txt — zależności Python

Uwaga: Zgodnie z wymaganiem backend znajduje się bezpośrednio w katalogu `app` (bez osobnego folderu „backend”).

## Szybki start (backend)

1. Stwórz i aktywuj wirtualne środowisko (opcjonalnie):
   - Windows (PowerShell):
     python -m venv .venv
     .venv\\Scripts\\Activate.ps1

2. Zainstaluj zależności:
   pip install -r requirements.txt

3. Uruchom backend (FastAPI + Uvicorn):
   uvicorn app.main:app --reload

4. Sprawdź endpoint testowy:
   - GET http://localhost:8000/api/ping → {"message": "pong"}
   - Swagger UI: http://localhost:8000/docs

## Konfiguracja bazy danych

- Domyślnie używane jest lokalne SQLite: `sqlite:///./budget_planner.db`.
- Aby użyć MySQL zgodnie z założeniami projektu, ustaw zmienną środowiskową:
  - Przykład: `DATABASE_URL=mysql+pymysql://user:password@localhost:3306/budget_planner`

## Frontend (kolejny krok)

- W tym etapie dostarczony jest szkielet backendu i podstawowy endpoint integracyjny.
- Frontend (React, Vite) może zostać dodany w kolejnym kroku w katalogu `app/frontend` lub jako osobny moduł, przy zachowaniu integracji z `http://localhost:8000/api`.

## Notatki

- Włączone CORS dla lokalnego dev (`http://localhost:5173`).
- Struktura przygotowana do rozbudowy o modele, schematy, usługi i autentykację (JWT) w kolejnych etapach.
