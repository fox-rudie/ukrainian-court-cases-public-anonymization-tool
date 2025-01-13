import random


def generate_random_name(gender):
    files = {
        'male': {
            'fname': '../dict/person_male_fname.txt',
            'lname': '../dict/person_male_lname.txt',
            'pname': '../dict/person_male_pname.txt'
        },
        'female': {
            'fname': '../dict/person_female_fname.txt',
            'lname': '../dict/person_female_lname.txt',
            'pname': '../dict/person_female_pname.txt'
        }
    }

    name_map = {
        'v_naz': {},
        'v_rod': {},
        'v_dav': {},
        'v_zna': {},
        'v_oru': {},
        'v_mis': {},
        'v_kly': {}
    }

    # Randomly select a base name for each part (fname, lname, pname) and gather all its forms
    for part in ['fname', 'lname', 'pname']:
        filename = files[gender].get(part)
        if filename:
            with open(filename, 'r', encoding='utf-8') as file:
                entries = []
                current_base = None
                forms_dict = {form: None for form in name_map.keys()}
                for line in file:
                    if line.startswith(' '):  # Indented line (word form)
                        if current_base:
                            word, attributes = line.strip().split(maxsplit=1)
                            for form in forms_dict.keys():
                                if form in attributes:
                                    forms_dict[form] = word
                    else:  # Base form
                        if current_base:  # Store completed entry
                            entries.append((current_base, forms_dict.copy()))
                        current_base = line.strip().split(maxsplit=1)[0]
                        forms_dict = {form: None for form in name_map.keys()}

                # Add the last entry if it exists
                if current_base:
                    entries.append((current_base, forms_dict.copy()))

                if entries:
                    selected_base, selected_forms = random.choice(entries)
                    for form in name_map.keys():
                        if selected_forms[form]:
                            name_map[form][part] = selected_forms[form]
                        else:
                            name_map[form][part] = selected_base  # Use base as fallback

    return name_map
