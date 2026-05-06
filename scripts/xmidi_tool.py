import os
import sys
from tqdm import tqdm
import json

try:
    import mido
except ImportError:
    print("Błąd: Biblioteka 'mido' nie jest zainstalowana.")
    print("Zainstaluj ją wpisując w terminalu: pip install mido")
    sys.exit(1)

genres_dict = {}

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

def get_midi_length(file_path):
    """Próbuje odczytać długość pliku MIDI w sekundach."""
    try:
        mid = mido.MidiFile(file_path)
        return mid.length
    except Exception:
        # Zwraca 0 w przypadku problemu z odczytem pliku
        return 0

def group_files(target_dir, duration_analysis):
    if not os.path.isdir(target_dir):
        print(f"Błąd: Ścieżka '{target_dir}' nie jest folderem.")
        return

    # Lista wszystkich plików w folderze
    files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]

    print("GROUPPING FILES\n")

    for file_name in tqdm(files):
        # Rozdzielamy nazwę na części. 
        # Zamiast rsplit używamy split, by sprawdzić wszystkie 4 segmenty
        # XMIDI_warm_pop_V1UFY7EF.midi -> ['XMIDI', 'warm', 'pop', 'V1UFY7EF.midi']
        parts = file_name.split('_')
        
        if len(parts) != 4 or parts[0] != 'XMIDI':
            stats['skipped_files'] += 1
            continue

        mood = parts[1]
        genre = parts[2]
        

        file_path = os.path.join(target_dir, file_name)
        duration = 1
        if duration_analysis:
            duration = get_midi_length(file_path)
        
        add_to_dict(file_name, genre, mood, duration)
        
        # Aktualizacja ogólnych statystyk (tylko dla poprawnych plików MIDI)
        if duration > 0:
            stats['total_files'] += 1
            stats['total_duration'] += duration
            
            if duration > stats['longest']:
                stats['longest'] = duration
                stats['longest_name'] = file_name
                
            if duration < stats['shortest']:
                stats['shortest'] = duration
                stats['shortest_name'] = file_name

def add_to_dict(file_name, genre, mood, duration):
    if genre not in genres_dict:
        genres_dict[genre] = {}
    
    if mood not in genres_dict[genre]:
        genres_dict[genre][mood] = []
    
    # Zamiast przypisywać, DODAJEMY do listy, żeby nie nadpisywać poprzednich plików.
    # Przechowujemy też długość pliku, aby łatwiej wyliczać statystyki nastrojów
    genres_dict[genre][mood].append({'name': file_name, 'duration': duration})

def print_dict(duration_analysis):
    print("\n" + "=" * 60)
    print(" PODSUMOWANIE PLIKÓW MIDI")
    print("=" * 60)

    if stats['total_files'] == 0:
        print("Nie znaleziono żadnych plików MIDI o poprawnym formacie,")
        print("lub wystąpił problem z ich odczytem.")
        return

    # Ogólne statystyki
    print("📌 STATYSTYKI OGÓLNE:")
    print(f" • Poprawne pliki MIDI : {stats['total_files']}")
    print(f" • Pominięte pliki     : {stats['skipped_files']} (zła nazwa)")
    
    if duration_analysis:
        avg_total_dur = stats['total_duration'] / stats['total_files']
        print(f" • Średnia dł. utworu  : {avg_total_dur:.2f} sek")
        
        if stats['longest_name']:
            print(f" • Najdłuższy plik     : {stats['longest_name']} ({stats['longest']:.2f} sek)")
            print(f" • Najkrótszy plik     : {stats['shortest_name']} ({stats['shortest']:.2f} sek)")

    print("\n STRUKTURA (GATUNKI i NASTROJE):")
    print("-" * 60)

    # Statystyki szczegółowe ze słownika
    print("CALCULATING STATS\n")
    j = 0
    for genre, moods in genres_dict.items():
        j+=1
        # Liczymy sumę plików dla danego gatunku
        genre_count = sum(len(files) for files in moods.values())
        print(f"{j:2} Gatunek: {genre.upper()} (Łącznie plików: {genre_count})")
        i = 0
        for mood, files in moods.items():
            i+=1
            mood_count = len(files)
            mood_total_dur = sum(f['duration'] for f in files)
            avg_mood_dur = mood_total_dur / mood_count if mood_count > 0 else 0
            
            print(f"  {i:2}└── Nastrój: {mood:<10} | Plików: {mood_count:<3} | Średnia dł: {avg_mood_dur:.2f} sek")

    print("=" * 60 + "\n")

def generate_prompts(prompt_example_path, out_dir):

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

def merge_jsons(dir_path):
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

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Użycie: python grouper.py <sciezka_do_folderu_xmidi> <duration_analysis 0 or 1>")
    else:
        folder_path = sys.argv[1]
        duration_analysis = int(sys.argv[2])
        group_files(folder_path, duration_analysis)
        print_dict(duration_analysis)
        #generate_prompts('data/prompts/prompt_example.txt', 'data/prompts')
        merge_jsons("data/prompts")