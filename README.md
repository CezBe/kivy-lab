# Aplikacja do rezerwacji kortu tenisowego

## 1. Opis ogólny

Aplikacja jest desktopową aplikacją napisaną w języku Python z wykorzystaniem frameworka **Kivy**. Służy do zarządzania rezerwacjami kortu tenisowego, umożliwiając użytkownikom tworzenie rezerwacji oraz przeglądanie i anulowanie istniejących terminów.

Aplikacja działa w oparciu o lokalną bazę danych i oferuje prosty, czytelny interfejs użytkownika oparty na systemie ekranów (`ScreenManager`).

---

## 2. Funkcjonalności

### 2.1. Ekran główny (HomeScreen)

- Wyświetlenie logo aplikacji
- Przejście do:
    - formularza rezerwacji
    - grafiku rezerwacji

---

### 2.2. Rezerwacja kortu (ReservationScreen)

Formularz umożliwia wprowadzenie następujących danych:

- Imię klienta
- Nazwisko klienta
- Data rezerwacji (wybór z listy dostępnych dat)
- Godzina rozpoczęcia (format HH:MM)
- Czas trwania rezerwacji:
    - 30 minut
    - 60 minut
    - 90 minut

Walidacje:
- pola imię i nazwisko są wymagane
- rezerwacja nie może rozpocząć się wcześniej niż godzinę od bieżącego czasu
- klient może mieć maksymalnie dwie aktywne rezerwacje w danym tygodniu
- sprawdzana jest dostępność terminu

Po poprawnym utworzeniu rezerwacji:
- użytkownik zostaje przeniesiony do ekranu głównego
- wyświetlany jest komunikat potwierdzający

Formularz jest automatycznie czyszczony przy każdym wejściu na ekran.

---

### 2.3. Grafik rezerwacji (ScheduleScreen)

Ekran umożliwia:

- wybór zakresu dat „od – do”
- filtrowanie rezerwacji na podstawie wybranego zakresu
- wyświetlenie rezerwacji w formie tabeli
- anulowanie pojedynczej rezerwacji
- eksport danych (CSV / JSON – UI przygotowane)

Tabela zawiera kolumny:
- Imię i nazwisko
- Start rezerwacji
- Koniec rezerwacji
- Akcja (anulowanie)

Dane są automatycznie odświeżane przy każdym wejściu na ekran.

---

## 3. Architektura aplikacji

### 3.1. ScreenManager

Aplikacja korzysta z `ScreenManager` do zarządzania widokami:

- `HomeScreen`
- `ReservationScreen`
- `ScheduleScreen`

Każdy ekran dziedziczy po klasie bazowej `DefaultScreen`.

---

### 3.2. DefaultScreen

Klasa bazowa wspólna dla wszystkich ekranów.

Odpowiedzialności:
- przechowywanie referencji do bazy danych
- wspólny layout główny
- obsługa nawigacji pomiędzy ekranami
- globalny system alertów (komunikaty sukcesu i błędu)

Alerty:
- wyświetlane są jako etykieta
- automatycznie znikają po określonym czasie
- dostępne na każdym ekranie

---

### 3.3. Odświeżanie ekranów

Aplikacja wykorzystuje lifecycle hooki Kivy:

- `on_pre_enter`

Zastosowanie:
- czyszczenie formularza rezerwacji
- automatyczne ładowanie danych do tabeli grafiku

Dzięki temu:
- `__init__` odpowiada tylko za budowę UI
- dane są zawsze aktualne
- unika się ponownego tworzenia widgetów

---

## 4. Warstwa danych

Aplikacja korzysta z klasy `Database`, odpowiedzialnej za:

- tworzenie tabel
- zarządzanie klientami
- zapisywanie rezerwacji
- sprawdzanie dostępności terminów
- anulowanie rezerwacji
- pobieranie danych do grafiku

Dane klientów reprezentowane są przez obiekt `Customer`.

Logika biznesowa (walidacje, limity, dostępność) jest oddzielona od warstwy UI.

---

## 5. Interfejs użytkownika

### 5.1. Layout

- `BoxLayout` – główna struktura ekranów
- `AnchorLayout` – pozycjonowanie logo i elementów centralnych
- `GridLayout` + `ScrollView` – tabela rezerwacji

Tabela:
- dynamiczna
- dostosowuje wysokość do liczby rekordów
- obsługuje przewijanie

---

### 5.2. Styl

- jasne tło
- czytelna typografia
- spójna kolorystyka przycisków
- brak plików `.kv`, całość w Pythonie

---

## 6. Rozszerzalność

Aplikacja została zaprojektowana w sposób umożliwiający łatwą rozbudowę, m.in. o:

- eksport danych do CSV i JSON
- blokadę anulowania przeszłych rezerwacji
- sortowanie grafiku
- paginację
- autoryzację użytkowników
- wersję mobilną

---

## 7. Uruchamianie aplikacji

Wymagania:
- Python 3.10+
- Kivy
- lokalna baza danych

Uruchomienie:

```bash
python main.py
