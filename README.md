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

## Informacja o sposobie użytkowania modeli LLM w projekcie
### Marcin Kowalczyk
Model: Gemini 3.1 Pro 
Sposób użycia: szybsze prototypowanie krótkich programów do analizy danych oraz wywołania funkcji. Debugowanie kodu oraz ogarniczony research.
Narzędzia: Nie korzystam ze środowiska ze zintegorwanym LLM'em, zazwyczaj korzystam z wersji dostępnej przez stronę internetową.

### Oskar Gorgis
Ja wykorzystuje generatywne AI do pisania mniejszych funkcji w kodzie. Używam Clauda modelu Sonnet 4.6. Poza pisaniem funkcji wykorzystuje go do planowania architektury, zadaje pytania i proszę o wytłumaczenie rozwiązań oraz podanie źródeł, z którch mogę zobaczyć jak ktoś na jakimś przykładzie je implementuje.


## Instrukcja uruchomienia projektu

### 1. Sklonowanie repozytorium

```bash
git clone --recurse-submodules [<URL_TWOJEGO_REPO>](https://github.com/WIMU-2026L/WIMU)
cd WIMU
```

---

### 2. Konfiguracja środowiska (głównego projektu)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

### 3. Konfiguracja MIDI-LLM (submodule)

Przejdź do repo modelu:

```bash
cd external/midi-llm
```

Utwórz środowisko (zgodnie z repo MIDI-LLM, zwykle conda):

```bash
conda create -n midi-llm python=3.10
conda activate midi-llm
pip install -r requirements.txt
```

### 4. Konfiguracja MuseCoco (submodule)

Przejdź do repo modelu:

```bash
cd muzic/musecoco
```

Utwórz środowisko (zgodnie z repo MuseCoco, zwykle conda):

```bash
conda create -n MuseCoco python=3.8
conda activate MuseCoco
conda install pytorch=1.11.0 -c pytorch
pip install -r requirements.txt
```
Additionally our machine should be provided with appropriate gcc and nvidia toolkit for CUDA usage.

To run test sample generation, we should download model from the link [https://huggingface.co/XinXuNLPer/MuseCoco_attribute2music/tree/main], put it in 2-attribute2music_model/checkpoint... dircetory.

Now, we can run the script form 2-attribute2musci_model dir with `bach interactive_1bilion.sh 0 10`, this will generate 20 samples (10 prompts x 2 batch size) in the new generate directory.

---

## Konfiguracja projektu

Wszystkie ścieżki i ustawienia modeli są przechowywane w **`config.yaml`** w korzeniu repozytorium. Edytuj wartości `models.midillm.python`, `models.clamp3.python` i `models.clamp3.env_dir`, aby wskazywały na lokalne środowiska conda.

Dla logowania do Weights & Biases ustaw `wandb.entity` na nazwę swojego konta/zespołu i wykonaj raz `wandb login`.

---

## Uruchamianie pipeline'u (CLI)

Wszystkie komendy uruchamiane są z korzenia repozytorium:

```bash
# Reorganizacja surowego datasetu XMIDI
python src/main.py organize

# Generacja MIDI przez MIDI-LLM (3 pliki na prompt)
python src/main.py generate --model midillm --n_outputs 3

# Ewaluacja CLaMP3 – oba modele, wszystkie granularności
python src/main.py evaluate --model all --mode all

# Ewaluacja tylko MIDI-LLM, tylko per gatunek
python src/main.py evaluate --model midillm --mode by_genre
```

### Granularności ewaluacji CLaMP3

| Tryb | Opis | Plik wynikowy |
|------|------|---------------|
| `genre_vibe` | Każda para (gatunek, nastrój) osobno | `{model}_genre_vibe_clamp3.txt` |
| `by_genre`   | Wszystkie nastroje danego gatunku razem | `{model}_by_genre_clamp3.txt` |
| `by_vibe`    | Wszystkie gatunki danego nastroju razem | `{model}_by_vibe_clamp3.txt` |

---

## Testy automatyczne

```bash
PYTHONPATH=src python -m pytest tests/ -v
```

21 testów jednostkowych pokrywa: parsowanie JSON z promptami, reorganizację datasetu, parsowanie wyników CLaMP3 oraz kopiowanie plików MIDI.

---

## Jakość kodu

```bash
# Formatowanie
black src/ tests/

# Linting
ruff check src/ tests/
```

Oba narzędzia skonfigurowane są w `pyproject.toml` z limitem linii 100 znaków (PEP 8 z rozszerzonym limitem).

---

## Struktura projektu

```
WIMU/
├── config.yaml              # Konfiguracja ścieżek i modeli
├── pyproject.toml           # Konfiguracja black / ruff / pytest
├── src/
│   ├── main.py              # CLI (argparse)
│   ├── config.py            # Ładuje config.yaml, eksportuje stałe
│   ├── data/
│   │   ├── data_loader.py
│   │   ├── dataset_processing.py
│   │   └── midisample_class.py
│   ├── model/midillm/
│   │   ├── generator.py
│   │   └── pipeline.py
│   └── metrics/
│       ├── clamp3.py
│       ├── fmd.py
│       └── wandb_logger.py  # Logowanie wyników do W&B
├── tests/
│   ├── test_dataset_processing.py
│   ├── test_clamp3_parsing.py
│   └── test_prompts.py
├── data/
│   ├── prompts/             # Pliki tekstowe z promptami
│   ├── XMIDI_Organized/     # Dane referencyjne (tylko do odczytu)
│   └── generated/           # Wygenerowane MIDI
│       ├── midi-llm/
│       └── musecoco/
├── results/                 # Wyniki ewaluacji CLaMP3
└── external/                # Submoduły git
    ├── midi-llm/
    ├── clamp3/
    └── muzic/
```
