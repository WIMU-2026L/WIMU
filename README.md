# FMD jako narzędzie ewaluacji kontrolowalności modeli generatywnych

## Design Proposal

**WIMU**  
Marcin Kowalczyk 318677  
Oskar Gorgis  
Paweł Kutyła  

---

# Opis projektu

Modele generatywne muzyki symbolicznej coraz częściej oferują kontrolę nad atrybutami wyjścia (gatunek, nastrój, instrumentacja). Projekt polega na użyciu FMD do zbadania, czy generacje warunkowane danym atrybutem rzeczywiście trafiają w rozkład odpowiedniego podzbioru referencyjnego. Dla wybranego modelu należy wygenerować próbki dla każdej klasy i porównać FMD względem odpowiednich i nieodpowiednich podzbiorów. Wyniki warto odnieść do klasyfikacji zero-shot z CLaMP 3 jako niezależnej metody weryfikacji.

---

# Harmonogram

| Tydzień | Postęp | Status |
|---|---|---|
| 18.03-22.03 | przygotowanie środowiska<br>pobranie i uruchomienie modelu MuseCoCo<br>wczytanie datasetu | |
| 23.03-29.03 | implementacja FMD<br>dodanie funkcji pomocniczych do przekształcania danych<br>dodanie podstawowego pipeline’u (model -> wygenerowana próbka -> porównanie z datasetem przy pomocy FMD)<br>przygotowanie prototupy | |
| 30.03-05.04 | refaktoryzacja kodu propotypu<br>poprawienie skalowalności pipeline’u<br>zapisywanie wyników do pliku | |
| 06.04-12.04 | dodanie drugiego modelu | |
| 13.04-19.04 | implementacja CLAMP<br>obliczanie i zapis embeddingów | |
| 20.04-26.04 | pierwsze eksperymenty na większej ilości próbek testowanie metryk porównawczych | |
| 27.04-03.05 | automatyzacja eksperymentów<br>napisanie testów integracyjnych | |
| 04.05-10.05 | przygotowanie wyników i statystyk<br>analiza wyników | |
| 11.05-17.05 | refaktoryzacja kodu projektu<br>poprawienie błędów | |
| 18.05-24.05 | przygotowanie raportu i prezentacji | |

---

# Stack technologiczny

Głównym językiem wykorzystywanym do tworzenia systemu będzie Python. Dodatkowo planowane jest wykorzystanie narzędzia make w celu automatyzacji poszczególnych kroków w przetwarzaniu danych, zachowując przy tym wysoką czytelność i łatwość pracy w stworzonym środowisku. Eksperymenty wykonywane, a szczególnie te związane z wykorzystaniem modeli generatywnym będą częściowo przeprowadzane z wykorzystaniem narzędzia Jupyter Notebook.  

---

# Funkcjonalność programu

System przygotowany przez nas będzie składał się z poniższych funkcjonalności:

- przygotowanie i filtrowanie zbioru wejściowego na podstawie atrybutów np. genre,
- generowania utworów na podstawie zadanych warunków z wykorzystaniem modeli generatywnych,
- obliczania wartości FMD między wygenerowanymi utworami a zbiorami referencyjnymi,
- uruchamianie ewaluacji przez CLaMP 3,
- otrzymanie i zebranie wyników i przedstawienie ich w postaci niewielkiego raportu lub czytelnego logu zapisanego do pliku.

Przygotowanie zbioru danych zależnie od wykorzystanego zbioru może obejmować takie kroki jak:

- filtrowanie poszczególnych gatunków (w przypadku dużych zbiorów danych rozwiązanie może dotyczyć kilku wybranych gatunków na podstawie kryteriów jak np. liczebności utworów lub naszej wiedzy na ich temat),
- przygotowanie zbiorów referencyjnych w odpowiedniej strukturze katalogów np. `data/reference`

Następnie wykorzystując modele generatywne będziemy generować utwory na podstawie warunków wejściowych. Przykładowo mogą być to parametry:

- model - w przypadku integracji kilku modeli parametr ten pozwoli na wybranie jednego z nich,
- typ atrybutu - np. `genre=jazz`,
- liczbę próbek,
- dodatkowe parametry opcjonalne np. seed w celu zapewnienia powtarzalności eksperymentów.

Kolejnym z kroków w tym pipeline jest ekstrakcja embeddingów. Wczytywane będą pliki MIDI, a następnie po wstępnym przetworzeniu obliczane będa embeddingi. Ostatnim krokiem będzie ich zapisanie do plików, co pozwoli na ograniczenie czasu niezbędnego do policzenia ich po raz kolejny raz zapewniając cachowanie.

Na podstawie wygenerowanych utworów i odpowiednich podzbiorów referencyjnych obliczane będzie FMD.

Następnym etapem jest ewaluacja z wykorzystaniem CLaMP3 przyjmująca wygenerowane utwory oraz zestaw instrukcji warunkowych i zwracająca takie statystyki jak dokładność czy wykorzystując macierz pomyłek w celu lepszej wizualizacji.

Ostatecznym krokiem potoku jest zebranie danych z procesu i wizualizacja ich np. wykorzystując raport z wcześniej zdefiniowanym szablonem lub zebranie czytelnych logów w pliku.

Poszczególne etapy będą mogły być wywoływane z wykorzystaniem narzędzia make i przyjmowały formę np:
