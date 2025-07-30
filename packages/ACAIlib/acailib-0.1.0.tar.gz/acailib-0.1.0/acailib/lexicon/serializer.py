"""Serialize UBS DGNT data to files for other uses.

>>> from acai.lexicon import serializer
>>> serializer.Serializer(outpath=(ROOT.parent / "TyndaleBibleDictionary/notebooks/ubsdgnt.tsv"))
"""

from csv import DictWriter
from pathlib import Path

from . import ubsdgnt, ROOT


class Serializer:
    """Serialize UBS DGNT data to files for other uses.

    This is a simple serializer that writes the data to a TSV file.
    """

    ubsprs = ubsdgnt.UBSParser()
    fieldnames = ["entryCode", "lemma", "glosses", "definitionShort", "lexDomains", "lexSubDomains"]

    def __init__(self, outpath: Path) -> None:
        """Initialize the serializer."""
        with outpath.open("w", encoding="utf-8", newline="") as f:
            writer = DictWriter(f, fieldnames=self.fieldnames, delimiter="\t")
            writer.writeheader()
            for meaning in self.ubsprs.meaning_iterator():
                _ = writer.writerow(meaning.serialize_text())
