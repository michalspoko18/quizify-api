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
python -m venv venv
source venv/bin/activate
pip install django djangorestframework drf-spectacular django-cors-headers
python quizify/manage.py migrate
python quizify/manage.py runserver
```

Serwer startuje pod `http://localhost:8000`.

**Swagger / OpenAPI**
- OpenAPI schema: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`
- ReDoc: `GET /api/redoc/`

**Autoryzacja**
- API uzywa sesji Django (cookies).
- `POST /api/auth/login` zwraca `token: "session"` jako placeholder dla frontendu.

**Endpointy**

Auth:
- `POST /api/auth/login` - logowanie (email, password)
- `POST /api/auth/register` - rejestracja (email, password, nick?)
- `POST /api/auth/google` - logowanie/registracja Google (sub, email, name?, picture?, nick?)
- `POST /api/auth/logout` - wylogowanie (wymaga zalogowania)
- `GET /api/auth/profile` - profil aktualnego uzytkownika (wymaga zalogowania)
- `PUT /api/auth/profile` - aktualizacja profilu (nick lub username)
- `POST /api/auth/refresh` - odswiezenie tokenu (zwraca "session")
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

Tworzenie quizu (gdy brak sesji, wymagany ownerId lub ownerGoogleId):
```json
{
  "ownerId": 1,
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
  "passed": true,
  "userId": "external-id"
}
```
