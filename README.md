# quizify-api

Backend API dla aplikacji Quizify. Projekt oparty o Django + Django REST Framework.

**Stack**
- Django 5.x
- Django REST Framework
- drf-spectacular (OpenAPI/Swagger)
- django-cors-headers
- SQLite (domyslnie)

**Szybki start (lokalnie)**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GOOGLE_CLIENT_ID="twoj-google-client-id"
python3 quizify/manage.py migrate
python3 quizify/manage.py runserver
```

Serwer startuje pod `http://localhost:8000`.

**Swagger / OpenAPI**
- OpenAPI schema: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`
- ReDoc: `GET /api/redoc/`

**Autoryzacja**
- API uzywa JWT (access + refresh).
- `POST /api/auth/login` zwraca `accessToken` i `refreshToken`.

**Google login**
- Ustaw `GOOGLE_CLIENT_ID` w env backendu (musi odpowiadac client id z frontendu).
- Jesli masz `quizify-app/.env.local`, skopiuj wartosc `VITE_GOOGLE_CLIENT_ID`.
- Backend automatycznie laduje `quizify/.env` (np. `GOOGLE_CLIENT_ID=...`).

**Frontend (quizify-app)**
- `VITE_API_BASE_URL=http://127.0.0.1:8000/api`
- `VITE_GOOGLE_CLIENT_ID` musi pasowac do `GOOGLE_CLIENT_ID` w backendzie

**Endpointy**

Auth:
- `POST /api/auth/login` - logowanie (email, password)
- `POST /api/auth/register` - rejestracja (email, password, nick?)
- `POST /api/auth/google` - logowanie/registracja Google (credential, nick?)
- `POST /api/auth/logout` - wylogowanie (wymaga zalogowania)
- `GET /api/auth/profile` - profil aktualnego uzytkownika (wymaga zalogowania)
- `PUT /api/auth/profile` - aktualizacja profilu (nick lub username)
- `POST /api/auth/refresh` - odswiezenie tokenu (refreshToken)
- `GET /api/auth/me` - alias profilu zalogowanego uzytkownika
- `GET /api/me` - to samo co `auth/me`

Quizzes:
- `GET /api/quizzes/` - lista quizow (id, title, description, questionsCount)
- `POST /api/quizzes/` - tworzenie quizu (wymaga ownera)
- `GET /api/quizzes/mine` - quizy konkretnego uzytkownika (auth lub ownerId/ownerGoogleId)
- `GET /api/quizzes/<quiz_id>` - szczegoly quizu (pytania + odpowiedzi)
- `PUT /api/quizzes/<quiz_id>` - aktualizacja quizu (tylko owner)
- `DELETE /api/quizzes/<quiz_id>` - usuniecie (owner lub ownerId/ownerGoogleId w query)
- `POST /api/quizzes/<quiz_id>/answer` - sprawdzenie odpowiedzi + zapis wyniku

Ranking:
- `GET /api/ranking` - rankingi (`type=global|me|popular`, `limit`, `userId`)
- `POST /api/ranking` - zapis wyniku (quizId, percentage/score, correctAnswers, totalQuestions, passed?)

**Przykladowe payloady**

Rejestracja:
```json
{
  "email": "user@example.com",
  "password": "haslo",
  "nick": "quizmaster"
}
```

Logowanie:
```json
{
  "email": "user@example.com",
  "password": "haslo"
}
```

Tworzenie quizu (wymaga JWT w Authorization):
```json
{
  "title": "Stolice Europy",
  "description": "Krotki test",
  "questions": [
    {
      "text": "Stolica Francji?",
      "answers": [
        { "text": "Paryz", "is_correct": true },
        { "text": "Lyon", "is_correct": false }
      ]
    }
  ]
}
```

Odpowiedzi do quizu:
```json
{
  "answers": [
    { "questionId": 10, "answerId": 55 },
    { "questionId": 11, "answerId": 60 }
  ]
}
```

Ranking (POST):
```json
{
  "quizId": 1,
  "percentage": 80,
  "correctAnswers": 8,
  "totalQuestions": 10,
  "passed": true
}
```
