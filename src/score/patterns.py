from typing import List, Dict

from unidecode import unidecode

import pandas as pd

from config.settings import PATTERN_SHEETS


def refactor_pattern(pattern: str) -> str:
    # TODO: why can't we write this directly in the csv file?
    pattern = pattern.replace("\w+", "[^ ]+").lower()
    pattern = unidecode(pattern)
    return pattern


def get_shift_patterns(languages: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Load patterns for the Shift score.

    :param languages: Codes of languages for which patterns must be loaded.
    :return: Dictionary containing for each language code a dictionary associating patterns to weights.
    """
    patterns_dict = {}
    for language in languages:
        # Load a file where there must be a column containing patterns (named 'Patterns')
        #  and a column containing weights (named 'final weights'). # TODO: maybe change the names
        patterns_csv_fn = f"../../data/patterns/{PATTERN_SHEETS[language]['shift']}"
        language_patterns_df = pd.read_csv(patterns_csv_fn, header=0)
        language_patterns_df["patterns"] = language_patterns_df["patterns"].apply(refactor_pattern)
        patterns_dict[language] = language_patterns_df.patterns.values.tolist()
    return patterns_dict


def get_sdg_patterns(languages: List[str]) -> Dict[str, Dict[str, List[str]]]:
    """
    Load patterns for the SDG (Sustainable Development Goals) scores.

    :param languages: Codes of languages for which patterns must be loaded.
    :return: Dictionary containing for each language code a dictionary associating a list of patterns to each SDG.
    """
    patterns_dict = {}
    for language in languages:
        # Load a file where there must be one column per SDG whose header is the name of the SDG and the following lines
        #  specify patterns corresponding to this SDG
        patterns_csv_fn = f"../../data/patterns/{PATTERN_SHEETS[language]['sdg']}"
        language_patterns_df = pd.read_csv(patterns_csv_fn, header=0)

        # Build dictionary associating a list of patterns to each SDG
        sdg_patterns_dict = {}
        for sdg in language_patterns_df.columns:
            sdg_patterns_dict[sdg] = language_patterns_df[sdg].dropna().apply(refactor_pattern).tolist()
        patterns_dict[language] = sdg_patterns_dict

    return patterns_dict


def get_climate_patterns(languages):
    """
    Load patterns for the Climate scores. # TODO: what is the diff between climate and shift?

    :param languages: Codes of languages for which patterns must be loaded.
    :return: Dictionary containing for each language code a dictionary
    """
    patterns_dict = {}
    for language in languages:
        patterns_csv_fn = f"../../data/patterns/{PATTERN_SHEETS[language]['climate']}"
        print(patterns_csv_fn)
        tmp = pd.read_csv(patterns_csv_fn, header=None)
        patterns_dict[language] = tmp.iloc[:, 0].values.tolist()
    return patterns_dict