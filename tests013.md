## Opis testów

Przeprowadzono pełne testy funkcjonalne nowego systemu quizów.  
Zakres testów obejmował weryfikację poprawności działania:

- tworzenia quizu,
- edycji quizu,
- rozwiązywania quizu,
- prezentacji wyniku,
- walidacji danych wejściowych i komunikatów błędów,
- integracji frontend ↔ backend.

## Kryteria akceptacji – realizacja

### Scenariusze testowe
- [x] Opracowano manualne scenariusze testowe obejmujące pełny proces:
  **„stwórz → edytuj → rozwiąż → zobacz wynik”**.

### Formularze
- [x] Zweryfikowano poprawność działania formularza tworzenia quizu.
- [x] Zweryfikowano poprawność działania formularza edycji quizu.

### Rozwiązywanie quizu
- [x] Zweryfikowano poprawność wyświetlania quizów i pytań podczas rozwiązywania.
- [x] Zweryfikowano możliwość wyboru odpowiedzi oraz przebieg quizu.

### Logika oceny
- [x] Sprawdzono logikę oceny odpowiedzi.
- [x] Potwierdzono, że prezentowany wynik jest zgodny z danymi zwracanymi przez backend.

### Walidacje i błędy
- [x] Przetestowano walidacje formularzy (puste pola, błędne dane).
- [x] Przetestowano scenariusze braku uprawnień użytkownika.
- [x] Przetestowano obsługę błędów API w interfejsie użytkownika.

### Zarządzanie błędami
- [x] Każdy znaleziony błąd został zgłoszony jako issue w GitHub.

## Podsumowanie

Przeprowadzono testy funkcjonalne nowego systemu quizów, obejmujące zarówno
weryfikację komunikacji frontend–backend, jak i poprawność działania kluczowych
funkcjonalności aplikacji po stronie interfejsu użytkownika.

Testami objęto pełny przepływ użytkownika: tworzenie i edycję quizu,
rozwiązywanie quizu oraz prezentację wyniku końcowego. Zweryfikowano poprawność
przesyłania danych pomiędzy frontendem a backendem oraz zgodność logiki oceny
odpowiedzi z wynikami zwracanymi przez backend.

Sprawdzono walidacje danych wejściowych, obsługę błędów API oraz scenariusze
brzegowe, w tym brak uprawnień i niepoprawne dane. Nie zidentyfikowano
krytycznych niespójności pomiędzy frontendem a backendem.

Na podstawie przeprowadzonych testów uznano, że testowany zakres funkcjonalny
spełnia założone kryteria akceptacji.

