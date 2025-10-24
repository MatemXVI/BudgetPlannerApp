# Budget Planner – Backend + statyczny frontend (JWT + Google Login)

Aplikacja do zarządzania budżetem domowym (FastAPI + SQLite/MySQL) z prostym, statycznym frontendem serwowanym przez FastAPI. 
Zaimplementowano pełną autentykację JWT (rejestracja/logowanie) oraz logowanie przez konto Google (OAuth2/OpenID Connect – Authlib). 
UI wyświetla e‑mail zalogowanego użytkownika obok przycisku „Wyloguj”.

## Funkcje

- Rejestracja i logowanie na e‑mail/hasło (JWT w localStorage)
- Logowanie przez Google (przekierowanie do Google, powrót na `/api/auth/google/callback` i wydanie lokalnego JWT)
- Kategorie: tworzenie, lista, edycja, usuwanie
- Transakcje: tworzenie, lista z filtrami, usuwanie, szybki podgląd ostatnich
- Raporty: bilans oraz zestawienie wg kategorii
- Statyczny frontend (HTML + JS) serwowany z aplikacji

## Struktura repozytorium

- app/
  - main.py — konfiguracja aplikacji, CORS, SessionMiddleware, serwowanie statycznego frontendu
  - api/ — moduły API (auth, google_auth, categories, transactions, reports, debug)
  - core/ — konfiguracja (`config.py`), bezpieczeństwo/JWT (`security.py`)
  - database.py — inicjalizacja bazy SQLAlchemy (SQLite domyślnie)
  - models.py, schemas.py — modele ORM i schematy Pydantic
  - static/ — pliki frontendu (index.html, login.html, register.html, main.js)
- requirements.txt — zależności
- README.md — ten plik

## Wymagania

- Python 3.11+
- Pip/virtualenv

## Instalacja i uruchomienie (Windows PowerShell)

1. (Opcjonalnie) środowisko wirtualne
   python -m venv .venv
   .venv\Scripts\Activate.ps1

2. Instalacja zależności
   pip install -r requirements.txt

3. Konfiguracja środowiska (plik .env w katalogu głównym repo)
   Przykład minimalny do pracy lokalnej przy adresie 127.0.0.1:8000:

   SECRET_KEY=change-me-in-env
   # (opcjonalnie) Jeżeli nie ustawisz, użyty zostanie SECRET_KEY
   SESSION_SECRET_KEY=another-strong-secret
   # Baza (domyślnie SQLite w pliku)
   DATABASE_URL=sqlite:///./budget_planner.db
   # Adres serwera używany do budowy redirect_uri w OAuth Google
   SERVER_BASE_URL=http://127.0.0.1:8000
   # Dane klienta Google OAuth (z Google Cloud Console)
   GOOGLE_CLIENT_ID=...twoj_client_id...
   GOOGLE_CLIENT_SECRET=...twoj_client_secret...

   Uwaga: nie umieszczaj prawdziwych sekretów w repozytorium. 
   SECRET_KEY jest używany do podpisywania JWT, a SESSION_SECRET_KEY — przez SessionMiddleware.

4. Start aplikacji (dev)
   uvicorn app.main:app --reload

5. Wejdź w przeglądarce:
   - http://127.0.0.1:8000/ — aplikacja (wymaga zalogowania)
   - http://127.0.0.1:8000/login — logowanie (e‑mail/hasło lub „Zaloguj przez Google”)
   - http://127.0.0.1:8000/register — rejestracja
   - Swagger/OpenAPI: http://127.0.0.1:8000/docs

## Konfiguracja logowania przez Google

1. Google Cloud Console → APIs & Services → Credentials → utwórz OAuth 2.0 Client ID (Web application).
2. Authorized redirect URIs dodaj dokładnie adres(y) powrotu, np. dla pracy lokalnej:
   - http://127.0.0.1:8000/api/auth/google/callback
   (opcjonalnie) dodaj też wariant z „localhost”:
   - http://localhost:8000/api/auth/google/callback
3. (Opcjonalnie) Authorized JavaScript origins:
   - http://127.0.0.1:8000
   - http://localhost:8000
4. Wstaw GOOGLE_CLIENT_ID i GOOGLE_CLIENT_SECRET do pliku .env. 
5. Upewnij się, że SERVER_BASE_URL w .env jest zgodny z tym, czego używasz w przeglądarce (np. 127.0.0.1 vs localhost). 
   Mismatch spowoduje błąd 400 redirect_uri_mismatch.

## Jak korzystać (frontend)

- Wejdź na /register i utwórz konto lub na /login i zaloguj się.
- Aby użyć logowania Google, kliknij „Zaloguj przez Google”; po powrocie token JWT zostanie zapisany w localStorage, a aplikacja przekieruje na „/”.
- Po zalogowaniu w nagłówku obok „Wyloguj” zobaczysz swój adres e‑mail.
- W aplikacji możesz dodawać kategorie i transakcje, filtrować, kasować oraz przeglądać szybkie raporty.

## API – najważniejsze endpointy

Uwierzytelnianie (JWT):
- POST /api/auth/register — body JSON: {"email","password"} → tworzy konto
- POST /api/auth/login — form-urlencoded: username, password → zwraca {access_token}
- GET /api/auth/me — dane bieżącego użytkownika (Authorization: Bearer <token>)
- GET /api/auth/google/login — przekierowanie do Google (przeglądarka)
- GET /api/auth/google/callback — punkt powrotu z Google (generuje lokalny JWT)

Zasoby (wymagają Bearer token):
- /api/categories — GET, POST, GET/{id}, PUT/{id}, DELETE/{id}
- /api/transactions — GET (filtry: type, category_id, date_from, date_to, q, limit), POST, GET/{id}, PUT/{id}, DELETE/{id}
- /api/reports/balance — GET
- /api/reports/monthly — GET
- /api/reports/by-category — GET

Nagłówek autoryzacji dla żądań zabezpieczonych:
Authorization: Bearer <JWT_TOKEN>

Przykład (PowerShell, pobranie bilansu):
$Headers = @{ Authorization = "Bearer $env:ACCESS_TOKEN" }
Invoke-WebRequest -Uri http://127.0.0.1:8000/api/reports/balance -Headers $Headers

## Rozwiązywanie problemów

- 400 redirect_uri_mismatch: 
  - Upewnij się, że redirect_uri wysyłane przez aplikację (SERVER_BASE_URL + /api/auth/google/callback) jest literalnie takie samo jak wpis w Google Console. 
  - 127.0.0.1 i localhost traktowane są jako różne hosty — dodaj oba, jeśli korzystasz z obu.
- „SessionMiddleware must be installed…”: 
  - Aplikacja ma włączony SessionMiddleware; zrestartuj serwer po instalacji zależności i zmianach .env.
- 401 Unauthorized: 
  - Brak/niepoprawny Bearer token w nagłówku Authorization albo wygasły JWT — zaloguj się ponownie.
- ImportError: Authlib/pydantic-settings: 
  - Upewnij się, że wykonałeś `pip install -r requirements.txt`.

## Uwagi

- Domyślnie używane jest SQLite. Możesz podać `DATABASE_URL` (np. MySQL przez `mysql+pymysql://user:pass@host:3306/db`).
- W produkcji korzystaj z HTTPS i silnych kluczy w .env.


## Testy

Aplikacja ma zestaw testów oparty na pytest, obejmujący najważniejsze ścieżki backendu.

Jak uruchomić testy:

1. Zainstaluj zależności (uwzględnia pytest):
   pip install -r requirements.txt
2. Z katalogu głównego repo uruchom:
   pytest -q

Informacje o środowisku testowym:
- Testy używają niezależnej, w pamięci (in-memory) bazy SQLite i nadpisują zależność get_db w FastAPI, więc nie modyfikują lokalnego pliku budget_planner.db.
- Nie musisz konfigurować .env do testów – testy nie korzystają z Google OAuth end-to-end.
- Testy uruchamiają FastAPI w TestClient, więc nie jest potrzebny działający serwer uvicorn.

Zakres testów (skrót):
- Autoryzacja: rejestracja, logowanie, /api/auth/me, obsługa duplikatu e‑maila, brak autoryzacji.
- Kategorie: tworzenie, lista, usuwanie; weryfikacja odłączania transakcji (category_id=NULL) zamiast ich kasowania.
- Transakcje i raporty: filtry, raport bilansu, raport miesięczny, raport wg kategorii.
- Debug: /api/debug/clear kasuje tylko dane bieżącego użytkownika (izolacja użytkowników).
