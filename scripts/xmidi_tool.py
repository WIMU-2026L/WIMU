import os
import sys
from tqdm import tqdm
import json
from pathlib import Path
import tempfile
from midiprocessor.midi_decoding import MidiDecoder
midi_decoder = MidiDecoder("REMIGEN2")
from dataclasses import dataclass

from frechet_music_distance import FrechetMusicDistance

try:
    import mido
except ImportError:
    print("Błąd: Biblioteka 'mido' nie jest zainstalowana.")
    print("Zainstaluj ją wpisując w terminalu: pip install mido")
    sys.exit(1)



def calculate_fmd(reference_path: str, test_path: str) -> float:
    metric = FrechetMusicDistance(verbose=True)
    score = metric.score(
        reference_path=reference_path,
        test_path=test_path
    )
    return score


def calculate_fmd_inf(reference_path: str, test_path: str, steps=25, min_n=5):
    metric = FrechetMusicDistance(verbose=True)
    score = metric.score_inf(
        reference_path=reference_path,
        test_path=test_path,
        steps=steps,
        min_n=min_n
    )
    return score


@dataclass
class MusicCluster:
    genres_dict = {}
    duration_analysis = False
    # Globalne statystyki
    stats = {
    'total_files': 0,
    'total_duration': 0,
    'shortest': float('inf'),
    'longest': 0,
    'shortest_name': '',
    'longest_name': '',
    'skipped_files': 0
    }

    def set_duration_analysis(self, bool_value):
        self.duration_analysis = bool_value

    def add(self, file_path, genre, mood):
        
        duration = 0
        if duration_analysis:
            duration = get_midi_length(file_path)

        if genre not in self.genres_dict:
            self.genres_dict[genre] = {}
        
        if mood not in self.genres_dict[genre]:
            self.genres_dict[genre][mood] = []
        
        # Zamiast przypisywać, DODAJEMY do listy, żeby nie nadpisywać poprzednich plików.
        # Przechowujemy też długość pliku, aby łatwiej wyliczać statystyki nastrojów
        self.genres_dict[genre][mood].append({'name': file_path, 'duration': duration})

        # Aktualizacja ogólnych statystyk (tylko dla poprawnych plików MIDI)
        if not self.duration_analysis or duration > 0 :
            self.stats['total_files'] += 1
            self.stats['total_duration'] += duration
            
            if duration > self.stats['longest']:
                self.stats['longest'] = duration
                self.stats['longest_name'] = file_path
                
            if duration < self.stats['shortest']:
                self.stats['shortest'] = duration
                self.stats['shortest_name'] = file_path
    
    def get_grouped_by_moods(self):
        moods = {}
        for genre, moods_dict in self.genres_dict.items():
            for mood, file_datas in moods_dict.items():
                paths =  moods.get(moods, [])
                for data in file_datas:
                    paths.append(data["name"])
                moods[mood] = paths
        return moods
    
    def get_grouped_by_genres(self):
        genres = {}
        for genre, moods_dict in self.genres_dict.items():
            for mood, file_datas in moods_dict.items():
                paths =  genres.get(genre, [])
                for data in file_datas:
                    paths.append(data["name"])
                genres[genre] = paths
        return genres
     

    def __str__(self):
        output = ""
        output += "\n" + "=" * 60 + "\n"
        output += " PODSUMOWANIE PLIKÓW MIDI\n" 
        output += "=" * 60 + "\n"

        if self.stats['total_files'] == 0:
            output += "Nie znaleziono żadnych plików MIDI o poprawnym formacie,\n" 
            output += "lub wystąpił problem z ich odczytem.\n" 
            return

        # Ogólne statystyki
        output += "📌 STATYSTYKI OGÓLNE:\n" 
        output += f" • Poprawne pliki MIDI : {self.stats['total_files']}\n" 
        output += f" • Pominięte pliki     : {self.stats['skipped_files']} (zła nazwa)\n" 
        
        if self.duration_analysis:
            avg_total_dur = self.stats['total_duration'] / self.stats['total_files']
            output += f" • Średnia dł. utworu  : {avg_total_dur:.2f} sek\n" 
            
            if self.stats['longest_name']:
                output += f" • Najdłuższy plik     : {self.stats['longest_name']} ({self.stats['longest']:.2f} sek)\n" 
                output += f" • Najkrótszy plik     : {self.stats['shortest_name']} ({self.stats['shortest']:.2f} sek)\n" 

        output += "\n STRUKTURA (GATUNKI i NASTROJE):\n" 
        output += "-" * 60 + "\n"

        # Statystyki szczegółowe ze słownika
        output += "CALCULATING STATS\n\n" 
        j = 0
        for genre, moods in self.genres_dict.items():
            j+=1
            # Liczymy sumę plików dla danego gatunku
            genre_count = sum(len(files) for files in moods.values())
            output += f"{j:2} Gatunek: {genre.upper()} (Łącznie plików: {genre_count})\n" 
            i = 0
            for mood, files in moods.items():
                i+=1
                mood_count = len(files)
                mood_total_dur = sum(f['duration'] for f in files)
                avg_mood_dur = mood_total_dur / mood_count if mood_count > 0 else 0
                
                output += f"  {i:2}└── Nastrój: {mood:<10} | Plików: {mood_count:<3} | Średnia dł: {avg_mood_dur:.2f} sek\n" 

        output += "=" * 60 + "\n\n" 
        return output



def get_midi_length(file_path):
    """Próbuje odczytać długość pliku MIDI w sekundach."""
    try:
        mid = mido.MidiFile(file_path)
        return mid.length
    except Exception:
        # Zwraca 0 w przypadku problemu z odczytem pliku
        return 0

def group_xmidi_files(target_dir, duration_analysis):
    if not os.path.isdir(target_dir):
        print(f"Błąd: Ścieżka '{target_dir}' nie jest folderem.")
        return
    music_cluster = MusicCluster()
    music_cluster.set_duration_analysis(duration_analysis)
    
    # Lista wszystkich plików w folderze
    files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]

    print("GROUPPING FILES\n")

    for file_name in tqdm(files):
        # Rozdzielamy nazwę na części. 
        # Zamiast rsplit używamy split, by sprawdzić wszystkie 4 segmenty
        # XMIDI_warm_pop_V1UFY7EF.midi -> ['XMIDI', 'warm', 'pop', 'V1UFY7EF.midi']
        parts = file_name.split('_')
        
        if len(parts) != 4 or parts[0] != 'XMIDI':
            music_cluster.stats['skipped_files'] += 1
            continue

        mood = parts[1]
        genre = parts[2]
    
        file_path = os.path.join(target_dir, file_name)

        music_cluster.add(file_path, genre, mood)

    return music_cluster

def retrive_recursive_all_midi(path):
    midi_filepaths = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            if file_path.endswith((".mid", ".midi")):
                midi_filepaths.append(file_path)
        elif os.path.isdir(file_path):
            inner_midis = retrive_recursive_all_midi(file_path)
            midi_filepaths += inner_midis
    return midi_filepaths

def group_musecoco_files(target_dir, duration_analysis):
    if not os.path.isdir(target_dir):
        print(f"Błąd: Ścieżka '{target_dir}' nie jest folderem.")
        return
    music_cluster = MusicCluster()
    music_cluster.set_duration_analysis(duration_analysis)
    
    # Lista wszystkich plików w folderze
    genres = []
    for genre in os.listdir(target_dir):
        genre_path = os.path.join(target_dir, genre)
        if os.path.isdir(genre_path):
            genres.append((genre, genre_path))
            for mood in os.listdir(genre_path):
                mood_path = os.path.join(genre_path, mood)
                if os.path.isdir(mood_path):
                    midi_files = retrive_recursive_all_midi(mood_path)
                    for file in midi_files:
                        music_cluster.add(file, genre, mood)
                else:
                    raise Exception(f"Unexpected file which is not dir, investigate: {mood_path}")

        else:
            raise Exception(f"Unexpected file which is not dir, investigate: {genre_path}")

    return music_cluster

def generate_prompts(prompt_example_path, out_dir, music_cluster):
    genres_dict = music_cluster.genres_dict

    with open(prompt_example_path, 'r') as fp:
        prompt_example_text = fp.readline()
    prompt_text = ""
    for genre in genres_dict.keys():
        for mood in genres_dict[genre].keys():
            prompt_text = prompt_example_text.replace("{MOOD}", mood)
            prompt_text = prompt_text.replace("{GENRE}", genre)
            directory = out_dir + "/" + genre + "/generate"
            file_name =f"{mood}_{genre}_gemini_prompt.txt"
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(directory + "/" + file_name, 'w') as fp:
                fp.write(prompt_text)

def merge_jsons(dir_path, music_cluster):
    genres_dict = music_cluster.genres_dict
    merged_prompts = {}
    for genre in genres_dict.keys():
        merged_prompts[genre] = {}
        dir_path_genre  = dir_path + "/" + genre
        for mood in genres_dict[genre].keys():
            file_name = mood + "_" + genre + "_prompts.json"  
            with open(dir_path_genre + "/" + file_name, 'r') as fp:
                mood_json = json.load(fp)
                merged_prompts[genre][mood] = mood_json
    with open(dir_path + "/all_prompts.json", 'w') as fp:
        json.dump(merged_prompts, fp)


def process_all_remi_to_midi(root_directory):
    """
    Przeszukuje strukturę katalogów w poszukiwaniu plików txt w folderach 'remi',
    konwertuje je na MIDI i zapisuje w odpowiednich folderach 'midi'.
    """
    root_path = Path(root_directory)
    
    # Używamy rglob do znalezienia wszystkich plików .txt w jakimkolwiek folderze 'remi'
    remi_files = list(root_path.rglob('remi/*.txt'))
    
    if not remi_files:
        print("Nie znaleziono żadnych plików .txt w folderach 'remi'. Sprawdź ścieżkę root_directory.")
        return

    print(f"Znaleziono {len(remi_files)} plików do przetworzenia.")

    e_files = []
    e_cnt = 0
    c_cnt = 0
    for txt_file in remi_files:
        print(f"\nPrzetwarzanie: {txt_file}")
        
        # Ustalanie ścieżek
        # txt_file.parent to folder 'remi'
        # txt_file.parent.parent to nadrzędny folder z ID (np. '0', '1')
        id_folder = txt_file.parent.parent
        midi_dir = id_folder / 'midi'
        
        # Tworzenie folderu 'midi', jeśli jeszcze nie istnieje
        midi_dir.mkdir(parents=True, exist_ok=True)
        
        # Docelowa ścieżka pliku MIDI (ta sama nazwa, ale rozszerzenie .mid)
        midi_file_path = midi_dir / f"{txt_file.stem}.mid"
        
        try:
            generate_midi_from_remi(txt_file, midi_file_path)
            c_cnt+=1
        except Exception as e:
            print(f"  [Błąd] Wystąpił problem z plikiem {txt_file.name}: {e}")
            e_files.append(txt_file)
            e_cnt +=1
    
    print("Przetwarzanie zakończone.")
    print("\nPODSUMOWANIE\n")
    print(f"Ilość znalezionych plików: {len(remi_files)}\n")
    print(f"Ilość poprawnie przetworzonych plików: {c_cnt}\n")
    print(f"Ilość plików nie możliwych do przetworzenia: {e_cnt}\n")
    print(f"Scieżki do plików:")
    for p in e_files:
        print("\t", p)



def generate_midi_from_remi(remi_path, midi_path):
    # 1. Wczytanie pliku tekstowego
    with open(remi_path, 'r', encoding='utf-8') as f:
        remi_text = f.read().strip()
        
    if not remi_text:
        print(f"  [Pominięto] Plik jest pusty.")
        return
        
    # 2. Podział na tokeny i czyszczenie
    tokens = remi_text.split(" ")
    
    # Zastosowanie filtra odrzucającego nagłówki/metadane przed <sep>
    if '<sep>' in tokens:
        sep_index = tokens.index('<sep>')
        tokens = tokens[sep_index + 1:]
    else:
        # Zapasowy filtr: zostaw tylko tokeny zawierające myślnik (np. p-60, d-12)
        tokens = [t for t in tokens if '-' in t]
        
    if not tokens:
        print(f"  [Pominięto] Brak prawidłowych tokenów po wyczyszczeniu.")
        return

    # 3. Dekodowanie do struktury MIDI
    midi_obj = midi_decoder.decode_from_token_str_list(tokens)
    
    # 4. Zapisanie pliku na dysku
    # miditoolkit.MidiFile posiada metodę dump() do zapisu
    midi_obj.dump(str(midi_path))
    print(f"  [Sukces] Zapisano do: {midi_path}")

def calculate_fmd_for_custom_group(reference_file_paths, test_file_paths, fmd_function):
    """
    file_paths_list: Lista ścieżek do plików xmidi, np. ['folderA/plik1.mid', 'folderB/plik2.mid']
    """
    
    # Tworzymy tymczasowy folder, który sam się usunie po wyjściu z bloku 'with'
    with tempfile.TemporaryDirectory() as ref_dir, tempfile.TemporaryDirectory() as test_dir:
        ref_path = Path(ref_dir)
        test_path = Path(test_dir)
        
        for i, file_path in enumerate(reference_file_paths):
            oryginal_path = Path(file_path).resolve() # resolve() daje pełną ścieżkę absolutną
            
            # Dodajemy indeks 'i' do nazwy symlinka. 
            # To zabezpiecza przed błędem, gdybyś grupował pliki z różnych 
            # folderów, które mają dokładnie taką samą nazwę.
            symlink_name = f"{i}_{oryginal_path.name}"
            symlink_path = ref_path / symlink_name
            
            # Tworzymy wirtualny skrót w folderze tymczasowym wskazujący na oryginalny plik
            os.symlink(oryginal_path, symlink_path)
            
        for i, file_path in enumerate(test_file_paths):
            oryginal_path = Path(file_path).resolve() # resolve() daje pełną ścieżkę absolutną
            
            # Dodajemy indeks 'i' do nazwy symlinka. 
            # To zabezpiecza przed błędem, gdybyś grupował pliki z różnych 
            # folderów, które mają dokładnie taką samą nazwę.
            symlink_name = f"{i}_{oryginal_path.name}"
            symlink_path = test_path / symlink_name
            
            # Tworzymy wirtualny skrót w folderze tymczasowym wskazujący na oryginalny plik
            os.symlink(oryginal_path, symlink_path)

        
        # Wywołujemy funkcję podając jej ścieżkę do naszego tymczasowego folderu
        score = fmd_function(ref_path, test_path)
        
        return score


def calculate_fmd_genres(reference_music_cluster, test_music_cluster):
    pass


def calculate_fmd_genres(reference_music_cluster, test_music_cluster):
    pass

def calculate_fmd_genres_moods(reference_music_cluster, test_music_cluster):
    pass

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Użycie: python xmidi_tool.py <sciezka_do_folderu_xmidi> <duration_analysis 0 or 1>")
    else:
        folder_path = sys.argv[1]
        duration_analysis = int(sys.argv[2])
        # cluster= group_xmidi_files(folder_path, duration_analysis)
        cluster = group_musecoco_files(folder_path, duration_analysis)
        print(cluster)
        # print(cluster.genres_dict)
        genres = cluster.get_grouped_by_genres()
        print(calculate_fmd_for_custom_group(genres["jazz"], genres["rock"], calculate_fmd))
        # generate_prompts('data/prompts/prompt_example.txt', 'data/prompts')
        # merge_jsons("data/prompts", music_cluster)
        #process_all_remi_to_midi(folder_path)