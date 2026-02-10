# Testy komunikacji frontend–backend dla modułu quizów

## Cel
Celem testów jest weryfikacja poprawności komunikacji pomiędzy frontendem a backendem
w procesie obsługi quizów, w szczególności zgodności requestów i response’ów z dokumentacją API,
poprawności odpowiedzi backendu oraz obsługi scenariuszy brzegowych.

---

## 1. Uruchamianie testów backendu (Django)

| Krok | Opis | Komenda |
|------|------|---------|
| 1 | Przejście do repozytorium backendu | `cd quizify-api` |
| 2 | Aktywacja środowiska wirtualnego | `venv\Scripts\Activate.ps1` |
| 3 | Przejście do katalogu projektu Django | `cd quizify` |
| 4 | Instalacja zależności projektu | `pip install -r requirements.txt` |
| 5 | Wykonanie migracji bazy danych | `python manage.py migrate` |
| 6 | Uruchomienie wszystkich testów | `python manage.py test` |
| 7 | Uruchomienie testów aplikacji quizzes (opcjonalnie) | `python manage.py test quizzes` |

### Oczekiwany rezultat

| Status | Znaczenie |
|--------|-----------|
| ✅ OK | Wszystkie testy zakończyły się powodzeniem |
| ❌ FAIL | Backend nie spełnia założeń kontraktu API |
| ❌ ERROR | Wystąpił problem konfiguracyjny lub środowiskowy |

---

## 2. Zakres pokrycia testami automatycznymi (stan aktualny)

| Obszar | Typ testów | Status |
|------|-----------|--------|
| Endpoint szczegółów quizu | API (Django) | ✅ Pokryty |
| Wysyłanie odpowiedzi | API (Django) | ✅ Pokryty |
| Zapisywanie wyników (ranking) | API (Django) | ✅ Pokryty |
| Scenariusz użytkownika zalogowanego | API (Django) | ✅ Pokryty |
| Scenariusz użytkownika anonimowego | API (Django) | ✅ Pokryty |

---

## 3. Checklist – weryfikacja komunikacji FE–BE

### 3.1 Zgodność requestów frontend → backend

- [x] Uruchomiono frontend aplikacji  
- [x] Przeanalizowano requesty w zakładce Network (DevTools)  
- [x] Zweryfikowano metody HTTP i endpointy  
- [x] Zweryfikowano payload requestów  
- [x] Porównano requesty z dokumentacją API  

W ramach weryfikacji potwierdzono, że frontend poprawnie inicjuje komunikację
z backendem, wysyłając requesty widoczne w zakładce Network narzędzi
deweloperskich przeglądarki.

Zweryfikowano, że proces logowania użytkownika realizowany jest z użyciem
metody HTTP **POST** oraz endpointu **`/api/auth/login`**, co jest zgodne
z przeznaczeniem operacji uwierzytelniania.

Przeanalizowano payload requestu logowania, który przesyłany jest w formacie JSON
i zawiera pola **`email`** oraz **`password`**. Struktura danych jest jednoznaczna,
czytelna i zgodna z przeznaczeniem endpointu.

Na podstawie przeprowadzonych testów nie stwierdzono rozbieżności pomiędzy
requestami wysyłanymi przez frontend a implementacją po stronie backendu.
Nie zidentyfikowano niespójności w zakresie metod HTTP, endpointów ani struktury payloadu.

---

### 3.2 Poprawność odpowiedzi backendu
- [x] Zweryfikowano statusy odpowiedzi dla poprawnych requestów (200 / 201)
- [x] Zweryfikowano strukturę response’ów
- [x] Sprawdzono obsługę błędów (400 / 404 / 401 / 403)
- [x] Sprawdzono komunikaty błędów (jeśli występują)

W ramach weryfikacji potwierdzono, że backend poprawnie obsługuje poprawne
requesty, zwracając odpowiednie statusy HTTP (`200 OK`, `201 Created`)
oraz odpowiedzi w formacie JSON.

Dla endpointu pobierania szczegółów quizu backend zwraca odpowiedź o poprawnej
strukturze, zawierającą metadane quizu, listę pytań oraz przypisane odpowiedzi.
Struktura response’ów jest spójna i zgodna z założeniami aplikacji.

Sprawdzono obsługę scenariuszy błędowych. W przypadku odwołania się do
nieistniejącego zasobu backend zwraca status `404 Not Found` wraz z czytelnym
komunikatem błędu w odpowiedzi JSON. Dla prób nieautoryzowanego dostępu
zwracany jest status `401 Unauthorized`.

Zidentyfikowane komunikaty błędów są jednoznaczne i pozwalają na prawidłową
interpretację przyczyny błędu po stronie klienta. Zachowanie backendu w zakresie
obsługi błędów uznano za poprawne.

---

### 3.3 Scenariusze brzegowe
- [x] Brak istniejącego quizu
- [x] Brak autoryzacji / brak uprawnień

W ramach scenariuszy brzegowych zweryfikowano obsługę nieistniejącego quizu
oraz brak autoryzacji użytkownika. Backend w tych przypadkach zwraca
odpowiednie statusy HTTP oraz czytelne odpowiedzi w formacie JSON.

---

### 3.4 Pełny przepływ sieciowy (CRUD quizu)
- [x] Tworzenie quizu
- [x] Edycja quizu
- [x] Usuwanie quizu
- [x] Pobieranie quizu do rozwiązania
- [x] Wysyłanie odpowiedzi
- [x] Odbieranie wyniku

W ramach punktu 3.4 zweryfikowano pełny przepływ sieciowy związany z rozwiązywaniem
quizu. Potwierdzono poprawne działanie mechanizmów pobierania quizu do rozwiązania,
wysyłania odpowiedzi użytkownika oraz odbierania wyniku po stronie klienta.

Zweryfikowano również operacje tworzenia, edycji oraz usuwania quizu.

---

### 3.5 Niespójności API ↔ Frontend
- [x] Zidentyfikowano rozbieżności w nazwach pól (nie stwierdzono)
- [x] Zidentyfikowano różnice w strukturze danych (nie stwierdzono)
- [x] Zidentyfikowano różnice w statusach odpowiedzi (nie stwierdzono)
- [x] Udokumentowano niespójności w tym pliku lub w issue

W trakcie weryfikacji komunikacji pomiędzy frontendem a backendem
nie zidentyfikowano niespójności w zakresie nazw pól, struktury danych
ani statusów odpowiedzi HTTP. Komunikacja API ↔ Frontend została uznana
za spójną i zgodną z aktualną implementacją systemu.

---

## 4. Podsumowanie
Testy automatyczne backendu pokrywają kluczowe endpointy związane
z rozwiązywaniem quizów i zapisem wyników.
Pozostałe punkty wymagają weryfikacji manualnej lub dalszych testów,
aby w pełni spełnić założone kryteria akceptacji.
