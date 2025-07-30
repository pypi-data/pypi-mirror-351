"""Reader for Macula Greek data for SBLGNT.

This enables a variety of lookups.
"""

from collections import defaultdict, UserDict
import pandas as pd


def normalize_strongs(i: int, prefix: str = "G") -> str:
    """Return a normalized Strongs id for an int."""
    assert prefix in ["G", "H"], f"Prefix should be 'G' or 'H': {prefix}"
    istr = str(i)
    assert len(istr) <= 4, f"Too many digits: {istr}"
    return f"{prefix}{i:0>4}"


class _BaseReader(UserDict):
    """Base class for reading Macula TSV data from Github."""

    # placeholders
    macula_path = ""
    prefix = "X"
    # column label for Louw-Nida identifier
    senseattr = "ln"
    # column label for Strong's numbers
    strongattr = "strong"
    # pos not in this list are filtered out when reading
    keeppos = set(("adj", "adv, noun", "verb"))

    def __init__(self) -> None:
        """Initialize a Reader."""
        super().__init__()
        self.df = pd.read_csv(self.macula_path, delimiter="\t")
        self.strong_lemma = defaultdict(set)
        # maps a normalized strongs number to a set of LN sense ids
        # roughly 30% of strongs numbers have multiple senses
        # strongs numbers
        self.strong_ln = defaultdict(set)
        for index, row in self.df.iterrows():
            if getattr(row, "class") in self.keeppos:
                self.data[getattr(row, "xml:id")] = row
                strong = normalize_strongs(getattr(row, self.strongattr), prefix=self.prefix)
                self.strong_lemma[strong].add(row.lemma)
                self.strong_ln[strong].add(getattr(row, self.senseattr))


# Hebrew TSV is borked as of 2023-12-20: read Nodes data instead
# class HebrewReader(_BaseReader):
#     """Manage WLC TSV data read from Github."""

#     macula_path = "https://github.com/Clear-Bible/macula-hebrew/raw/main/TSV/macula-hebrew.tsv"
#     prefix = "H"
#     # column label for Strong's numbers
#     strongattr = "strongnumberx"


class GreekReader(_BaseReader):
    """Manage SBLGNT TSV data read from Github."""

    macula_path = (
        "https://github.com/Clear-Bible/macula-greek/raw/main/SBLGNT/tsv/macula-greek-SBLGNT.tsv"
    )
    prefix = "G"
