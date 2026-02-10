# QA Raport – Testy E2E / Manualne – Quizify (etap: logowanie)

**Tester:** Andrzej Jur 
**Data:** 26.10.2025  
**Projekt:** Quizify (frontend + backend Django)  
**Zakres:** Logowanie użytkownika (Google OAuth + komunikacja frontend–backend)

---

## Środowisko testowe
| Komponent | Opis |
|------------|------|
| **Frontend** | `quizify-app` uruchomiony lokalnie przez VS Code / Live Server (`http://127.0.0.1:5500/index.html`) |
| **Backend** | `quizify-api` (Django 5.2) uruchomiony komendą `python manage.py runserver` |
| **Adres backendu** | `http://127.0.0.1:8000/` |
---

## Test Cases

| **ID** | **Nazwa testu** | **Cel testu** | **Kroki** | **Oczekiwany rezultat** | **Wynik** | **Uwagi / Przyczyna błędu** |
|--------|------------------|---------------|------------|--------------------------|------------|-----------------------------|
| **TC-01** | Uruchomienie backendu | Sprawdzić, czy serwer Django działa | 1. Aktywować `venv`  <br> 2. Uruchomić `python manage.py runserver`  <br> 3. Wejść na `http://127.0.0.1:8000/` | Widoczna strona Django *“The install worked successfully!”* | ✅ **POZYTYWNY** | Serwer działa, brak błędów w logach |
| **TC-02** | Uruchomienie frontendu | Sprawdzić, czy aplikacja frontendowa działa lokalnie | 1. Uruchomić `index.html` przez Live Server  <br> 2. Sprawdzić widok strony | Strona ładuje się, widać logo i przycisk “Zaloguj się przez Google” | ✅ **POZYTYWNY** | UI działa|
| **TC-03** | Widoczność elementów logowania / wylogowania | Sprawdzić, czy interfejs poprawnie ukrywa lub pokazuje elementy logowania w zależności od stanu użytkownika | 1. Uruchomić frontend `index.html`  <br> 2. Sprawdzić widoczność przycisków po starcie  <br> 3. Symulować zalogowanie użytkownika (np. przez `sessionStorage`) | Po zalogowaniu widoczny tylko przycisk **„Wyloguj się”**, po wylogowaniu tylko **„Zaloguj się”** | ❌ **NEGATYWNY** | Jednocześnie widoczne przyciski logowania i wylogowania |
| **TC-04** | Logowanie Google OAuth | Sprawdzić działanie przycisku logowania | 1. Kliknąć “Zaloguj się przez Google”  <br> 2. Spróbować zalogować się kontem Google | Użytkownik zalogowany, zwrócony token JWT | ❌ **NEGATYWNY** | *Błąd 400 invalid_request* – OAuth zablokowany dla localhost (brak konfiguracji domeny w Google Cloud). |

---

## Wnioski końcowe

- Środowisko lokalne (frontend + backend) działa poprawnie technicznie.  
- Backend Django uruchamia się bez błędów, ale nie ma skonfigurowanych endpointów API.  
- Frontend poprawnie się ładuje, jednak logika widoczności przycisków logowania/wylogowania wymaga poprawy.  
- Logowanie przez Google OAuth nie działa lokalnie — konieczna konfiguracja *Authorized origins* w Google Cloud Console.  


