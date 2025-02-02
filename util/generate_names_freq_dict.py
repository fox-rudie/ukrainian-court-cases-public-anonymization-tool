import csv
import urllib.request
import os
import zipfile


# if there is no ubertext_freq.csv, 
# download it from https://lang.org.ua/static/downloads/ubertext2.0/dicts/ubertext_freq.csv.xz and extract it
if not os.path.exists('dict/ubertext_freq.csv'):
    url = 'https://lang.org.ua/static/downloads/ubertext2.0/dicts/ubertext_freq.csv.xz'
    urllib.request.urlretrieve(url, 'dict/ubertext_freq.csv.xz')
    with zipfile.ZipFile('dict/ubertext_freq.csv.xz', 'r') as zip_ref:
        zip_ref.extractall('dict')
    os.remove('dict/ubertext_freq.csv.xz')


def load_ignore_list(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        ignore_list = [line.strip() for line in file]
    return ignore_list


def load_freq_dict(filename):
    freq_dict = {}
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["pos"] == "PROPN":
                freq_dict[row["lemma"]] = row
    return freq_dict


def get_word_freq(word, freq_dict):
    return freq_dict.get(word)


def freq_dict_contains(word, freq_dict):
    return word in freq_dict


def get_names_from_file(filename, ignore_list):
    with open(filename, 'r', encoding='utf-8') as file:
        names = [line.strip() for line in file if not line.startswith(' ')]
    return [name.split()[0] for name in names if name not in ignore_list]


def normalize_freq(freq_dict):
    sum_freq = sum(float(freq['freq_in_corpus']) for freq in freq_dict.values())
    for name in freq_dict:
        freq_dict[name]['freq_in_corpus'] = float(freq_dict[name]['freq_in_corpus']) / sum_freq
    return freq_dict

def get_names_freq(filename, freq_dict, ignore_list):
    names = get_names_from_file(filename, ignore_list)
    print(f'Loaded {len(names)} names from file')

    names_freq_dict = {}

    for name in names:
        if freq_dict_contains(name, freq_dict):
            names_freq_dict[name] = get_word_freq(name, freq_dict)

    # Normalize the frequency
    names_freq_dict = normalize_freq(names_freq_dict)

    # Sort the names_freq_dict by freq_in_corpus
    names_freq_dict = sorted(names_freq_dict.items(), key=lambda x: x[1]['freq_in_corpus'], reverse=True)

    return names_freq_dict

    
def save_names_freq_dict(names_freq_dict, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'freq_in_corpus'])
        writer.writeheader()
        for name in names_freq_dict:
            writer.writerow({'name': name[0], 'freq_in_corpus': name[1]['freq_in_corpus']})

os.makedirs('dict/generated', exist_ok=True)

ignore_list = load_ignore_list('dict/ignore_list.txt')
freq_dict = load_freq_dict('dict/ubertext_freq.csv')

female_fname_freq_dict = get_names_freq('dict/wiki_person_female_fname.txt', freq_dict, ignore_list)
male_fname_freq_dict = get_names_freq('dict/wiki_person_make_fname.txt', freq_dict, ignore_list)

save_names_freq_dict(female_fname_freq_dict, 'dict/generated/female_fname_freq_dict.csv')
save_names_freq_dict(male_fname_freq_dict, 'dict/generated/male_fname_freq_dict.csv')

female_lname_freq_dict = get_names_freq('dict/person_female_lname.txt', freq_dict, ignore_list)
male_lname_freq_dict = get_names_freq('dict/person_male_lname.txt', freq_dict, ignore_list)
lname_freq_dict = {**dict(female_lname_freq_dict), **dict(male_lname_freq_dict)}
lname_freq_dict = normalize_freq(lname_freq_dict)
lname_freq_dict = sorted(lname_freq_dict.items(), key=lambda x: x[1]['freq_in_corpus'], reverse=True)
save_names_freq_dict(lname_freq_dict, 'dict/generated/lname_freq_dict.csv')

female_pname_freq_dict = get_names_freq('dict/person_female_pname.txt', freq_dict, ignore_list)
male_pname_freq_dict = get_names_freq('dict/person_male_pname.txt', freq_dict, ignore_list)
save_names_freq_dict(female_pname_freq_dict, 'dict/generated/female_pname_freq_dict.csv')
save_names_freq_dict(male_pname_freq_dict, 'dict/generated/male_pname_freq_dict.csv')
