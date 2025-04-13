import pandas as pd
import numpy as np
from pathlib import Path
import re
import logging
import pickle
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NormalizationStrategy(Enum):
    RAW = "raw"
    LOG = "log"
    CLIP = "clip"
    DROP_TOP = "drop_top"

@dataclass
class NormalizationConfig:
    strategy: NormalizationStrategy = NormalizationStrategy.RAW
    clip_quantile: float = 0.98          # for CLIP
    drop_top_n: int = 3                  # for DROP_TOP

class NameGenerator:
    def __init__(self, dict_base_path: Path = Path("dict"),
                 seed_state_path: Path = Path("rng_state.pkl"), 
                 normalization_config: NormalizationConfig = NormalizationConfig()):
        self.normalization_config = normalization_config
        
        self.base_path = dict_base_path / "generated"
        self.case_path = dict_base_path
        self.rng_state_path = seed_state_path

        self.fname_freq: Dict[str, pd.DataFrame] = {}
        self.pname_freq: Dict[str, pd.DataFrame] = {}
        self.lname_freq: Optional[pd.DataFrame] = None

        self.fname_cases: Dict[str, dict] = {}
        self.pname_cases: Dict[str, dict] = {}
        self.lname_cases: Dict[str, dict] = {}

        self._load_rng_state()
        self._load_all_data()

    def _load_rng_state(self):
        if self.rng_state_path.exists():
            with open(self.rng_state_path, 'rb') as f:
                np.random.set_state(pickle.load(f))

    def save_rng_state(self):
        with open(self.rng_state_path, 'wb') as f:
            pickle.dump(np.random.get_state(), f)

    def _load_case_dict(self, file_path: Path) -> dict:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return {}
        
        case_dict = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if not line:
                        i += 1
                        continue
                    if not line.startswith(' '):
                        parts = line.split()
                        if not parts:
                            i += 1
                            continue
                        base_form = parts[0]
                        cases = {'v_naz': base_form}
                        j = i + 1
                        while j < len(lines) and lines[j].startswith(' '):
                            case_line = lines[j].strip()
                            case_parts = case_line.split()
                            if case_parts:
                                case_word = case_parts[0]
                                case_info = ' '.join(case_parts[1:])
                                case_match = re.search(r'v_([a-z]+)', case_info)
                                if case_match:
                                    case_type = f"v_{case_match.group(1)}"
                                    cases[case_type] = case_word
                            j += 1
                        case_dict[base_form] = cases
                        i = j
                    else:
                        i += 1
        except Exception as e:
            logger.error(f"Error loading case dictionary from {file_path}: {e}")
        return case_dict

    def _load_all_data(self):
        for gender in ['male', 'female']:
            self.fname_freq[gender] = self._load_freq_df(f"{gender}_fname_freq_dict.csv")
            self.pname_freq[gender] = self._load_freq_df(f"{gender}_pname_freq_dict.csv")

            self.fname_cases[gender] = self._load_case_dict(self.case_path / f"person_{gender}_fname.txt")
            self.pname_cases[gender] = self._load_case_dict(self.case_path / f"person_{gender}_pname.txt")

            lname_path = self.case_path / f"person_{gender}_lname.txt"
            if lname_path.exists():
                self.lname_cases[gender] = self._load_case_dict(lname_path)

        self.lname_freq = self._load_freq_df("lname_freq_dict.csv")
        if not self.lname_cases:
            self.lname_cases["default"] = self._load_case_dict(self.case_path / "person_lname.txt")

    def _load_freq_df(self, filename: str) -> pd.DataFrame:
        df = pd.read_csv(self.base_path / filename)

        strat = self.normalization_config.strategy

        if strat == NormalizationStrategy.LOG:
            df['freq_in_corpus'] = np.log1p(df['freq_in_corpus'])

        elif strat == NormalizationStrategy.CLIP:
            q = self.normalization_config.clip_quantile
            cap = df['freq_in_corpus'].quantile(q)
            df['freq_in_corpus'] = np.minimum(df['freq_in_corpus'], cap)

        elif strat == NormalizationStrategy.DROP_TOP:
            n = self.normalization_config.drop_top_n
            df = df.sort_values(by='freq_in_corpus', ascending=False).iloc[n:]

        # Else use RAW

        df['prob'] = df['freq_in_corpus'] / df['freq_in_corpus'].sum()
        return df

    def generate(self, gender: str, seed: Optional[int] = None) -> dict:
        if gender not in ['male', 'female']:
            raise ValueError("Gender must be either 'male' or 'female'")
        if seed is not None:
            np.random.seed(seed)

        fname_df = self.fname_freq[gender]
        pname_df = self.pname_freq[gender]
        lname_df = self.lname_freq

        first_name = np.random.choice(fname_df['name'], p=fname_df['prob'])
        patronymic = np.random.choice(pname_df['name'], p=pname_df['prob'])
        last_name = np.random.choice(lname_df['name'], p=lname_df['prob'])

        fname_cases = self.fname_cases[gender].get(first_name, {})
        pname_cases = self.pname_cases[gender].get(patronymic, {})
        lname_cases = self.lname_cases.get(gender, self.lname_cases.get("default", {})).get(last_name, {})

        case_map = {
            'v_naz': 'nominative',
            'v_rod': 'genitive',
            'v_dav': 'dative',
            'v_zna': 'accusative',
            'v_oru': 'instrumental',
            'v_mis': 'locative',
            'v_kly': 'vocative'
        }

        result = {}
        for uk_case, en_case in case_map.items():
            lname_case = lname_cases.get(uk_case, last_name)
            fname_case = fname_cases.get(uk_case, first_name)
            pname_case = pname_cases.get(uk_case, patronymic)
            result[en_case] = f"{lname_case} {fname_case} {pname_case}"

        result['original'] = {
            'last_name': last_name,
            'first_name': first_name,
            'patronymic': patronymic
        }

        return result

if __name__ == "__main__":
    name_generator = NameGenerator()
    print(name_generator.generate("male", seed=1))
    print(name_generator.generate("male", seed=1))
    print(name_generator.generate("male", seed=1))
