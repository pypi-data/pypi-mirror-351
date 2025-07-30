"""Use SpaCy to lemmatize English words."""

from collections import UserDict
from csv import DictWriter
from dataclasses import dataclass
from pathlib import Path

import spacy

from acai import DATAPATH
from acai.util import TSVReader


BBEWORDS = DATAPATH / "lexicon/uniqueWordsBBE.tsv"


@dataclass
class LemmatizedWord:
    """Represents a word and its lemmatized form."""

    word: str
    lemma: str = ""

    def diff_lemma(self) -> bool:
        """Return True if lemma is diferent from word."""
        return not self.word == self.lemma


class WordReader(TSVReader):
    """Read BBE words."""

    tsvpath = BBEWORDS
    # identity element from the TSV
    idattr = "word"
    # model to represent the data from each row
    model = LemmatizedWord


class Lemmatizer(UserDict):
    """Lemmatize English words."""

    # reads the data
    words = WordReader()
    nlp = spacy.load("en_core_web_sm")

    def __init__(self) -> None:
        """Initialize an instance."""
        super().__init__(self)
        for word, lword in self.words.items():
            # this does _all_ the analysis: speed it up by omitting
            # parts of the pipeline?
            doc = self.nlp(word)
            lword.lemma = doc[0].lemma_
        # mapping from lowercased word to true-case: for correction of
        # lemmatized forms
        self.lcasewords = {word.lower(): word for word in self.words.keys()}
        # map lemmatized forms to a list of their words
        for lword in self.words.values():
            if lword.lemma not in self.data:
                self.data[lword.lemma] = set()
            self.data[lword.lemma].add(lword.word)

    def write(self, outpath: Path) -> None:
        """Write out lemmatized forms."""
        fieldnames = ["lemma", "words"]
        with outpath.open("w") as f:
            writer = DictWriter(f, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            for lemma, wordset in self.items():
                # capitalize the lemma if there's a case-insensitive
                # matched word
                caplemma = self.lcasewords.get(lemma, lemma)
                writer.writerow({"lemma": caplemma, "words": "; ".join(wordset)})
