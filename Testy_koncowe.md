## Opis
Przeprowadzenie całościowej weryfikacji działania aplikacji z perspektywy użytkownika końcowego.  
Task obejmuje sprawdzenie wszystkich głównych przepływów funkcjonalnych aplikacji w środowisku docelowym.

---

## Kryteria akceptacji – status

| Kryterium akceptacji | Status |
|---|---|
| Zweryfikowano proces logowania (Google SSO oraz rejestracja tradycyjna). | Zaliczone |
| Zweryfikowano rozwiązywanie quizów oraz wyświetlanie wyników. | Zaliczone |
| Zweryfikowano poprawność wyświetlania poprawnych i błędnych odpowiedzi. | Zaliczone |
| Zweryfikowano ranking i statystyki użytkownika. | Zaliczone |
| Sprawdzono historię rozwiązań quizów (jeśli dostępna). | Zaliczone |
| Aplikacja działa stabilnie bez krytycznych błędów w głównych przepływach. | Zaliczone |

---

## Scenariusze testowe (E2E)

| ID | Obszar | Scenariusz | Kroki (skrót) | Oczekiwany rezultat | Status |
|---:|---|---|---|---|---|
| TC-01 | Logowanie | Google SSO | Wejście → Logowanie Google → Autoryzacja → Powrót do aplikacji | Użytkownik zalogowany, aktywna sesja, dostęp do funkcji konta | Zaliczone |
| TC-02 | Rejestracja | Rejestracja tradycyjna | Rejestracja → Podanie danych → Utworzenie konta | Konto utworzone, możliwość zalogowania | Zaliczone |
| TC-03 | Logowanie | Logowanie tradycyjne | Logowanie → Podanie danych → Zalogowanie | Użytkownik zalogowany, aktywna sesja | Zaliczone |
| TC-04 | Quizy | Rozpoczęcie i przejście quizu | Lista quizów → Start → Odpowiedzi → Nawigacja po pytaniach | Quiz działa płynnie, brak błędów nawigacji | Zaliczone |
| TC-05 | Wyniki | Wyświetlenie wyniku | Zakończenie quizu → Ekran wyników | Widoczne podsumowanie i wynik (punkty/poprawne odpowiedzi) | Zaliczone |
| TC-06 | Odpowiedzi | Poprawne/błędne odpowiedzi | Mieszane odpowiedzi → Podsumowanie | Poprawne oznaczenie odpowiedzi poprawnych i błędnych | Zaliczone |
| TC-07 | Ranking | Wyświetlenie rankingu | Wejście w ranking → Weryfikacja listy | Ranking wyświetla się poprawnie, dane spójne | Zaliczone |
| TC-08 | Statystyki | Statystyki użytkownika | Profil/Statystyki → Sprawdzenie po quizie | Statystyki widoczne i aktualizowane po zakończeniu quizu | Zaliczone |
| TC-09 | Historia | Historia rozwiązań quizów | Wejście w historię → Weryfikacja wpisów | Historia dostępna (jeśli funkcja występuje) i zawiera poprawne dane | Zaliczone |
| TC-10 | Stabilność | Stabilność głównych przepływów | Logowanie → Quiz → Wyniki → Ranking/Statystyki | Brak błędów krytycznych, aplikacja działa stabilnie | Zaliczone |

---

## Podsumowanie
Wszystkie główne przepływy użytkownika końcowego zostały zweryfikowane i działają poprawnie.  
Nie zidentyfikowano błędów krytycznych blokujących korzystanie z aplikacji.