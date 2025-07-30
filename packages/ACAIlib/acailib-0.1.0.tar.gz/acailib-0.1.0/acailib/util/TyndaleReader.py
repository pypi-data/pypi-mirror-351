"""Read a plaintext TSV file produced by src/article2tsv.sh.

This clones/diverges from TyndaleBibleDictionary/tynbd/Reader.py: i
should make that or a derivative into a library.

>>> from acai.util import TyndaleReader
>>> tynrd = TyndaleReader.Reader()
>>> len(tynrd)
5027
>>> list(tynrd.items())[23]
('AbelShittim', Article(identifier='AbelShittim', headword='ABEL-SHITTIM', paragraphs=['Alternate name for Shittim, a place on\xa0the plains of Moab, in bref^Num_33_49. See art^ShittimPlace.'], wordcount=14, isredirect=True, contenttype=''))

"""

from collections import UserDict, Counter
from dataclasses import dataclass, field
from pathlib import Path
import re
from statistics import median

TYNDATAPATH = Path(__file__).parent.parent.parent.parent / "TyndaleBibleDictionary/plaintext"


@dataclass
class Article:
    identifier: str
    headword: str
    paragraphs: list[str] = field(default_factory=list)
    wordcount: int = 0
    isredirect: bool = False
    contenttype: str = ""

    def __post_init__(self) -> None:
        """Compute values after initialization."""
        # count 'words': space-delimited tokens
        self.wordcount = len([w for p in self.paragraphs for w in p.split(" ")])
        # Phrases like '(Alternate|Shortened) (name|form) (for|of)',
        # 'RSV rendering of', 'Name of ____ in', etc. These are redirects but it's also
        # worth capturing the alternate.
        # self.alternatename: str
        # could do more with this heuristic, which overgenerates a
        # bit: 'Ab' has little content but isn't a complete
        # redirect.
        self.isredirect = ("See art^" in self.paragraphs[0]) and len(self.paragraphs) == 1

    @property
    def clean_headword(self) -> str:
        """Return a cleaned up headword string."""
        cleaned = self.headword
        if cleaned.endswith("*"):
            cleaned = cleaned[:-1]
        return cleaned

    def write(self, outpath: Path) -> None:
        """Write article to outpath."""
        with outpath.open("w") as f:
            f.write(self.headword + "\n")
            for p in self.paragraphs:
                f.write(p + "\n")

    def numbered_paragraphs(self) -> list[str]:
        """Return any paragraphs that start with a number.

        This is a pattern for articles that need disambiguation.
        """
        expr = re.compile(" ?[1-9]+\\. ")
        return [para for para in self.paragraphs if expr.match(para)]

    def is_numbered(self, ratio: float = 0.5) -> bool:
        """Return True if more paragraphs are numbered than the ratio."""
        if len(self.paragraphs) == 0:
            return False
        else:
            return (len(self.numbered_paragraphs()) / len(self.paragraphs)) > ratio


class Reader(UserDict):
    """Read the articles from a TSV file."""

    filestems = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        # there's always one outlier :-/
        "XY",
        "Z",
    ]

    def __init__(self) -> None:
        """Initialize an instance."""
        super().__init__()
        for stem in self.filestems:
            filepath = TYNDATAPATH / f"{stem}.tsv"
            try:
                self.read_file(tsvpath=filepath)
            except Exception as e:
                print(f"Failed on {filepath}\n{e}")
        self.wordcount = sum(art.wordcount for art in self.values())
        self.median_wordcount = median

    def read_file(self, tsvpath: Path) -> None:
        """Read a TSV file into memory."""
        self.tsvpath = tsvpath
        with self.tsvpath.open() as f:
            lastid: str = ""
            headword: str = ""
            paragraphs: list[str] = []
            for line in f.readlines():
                try:
                    cleanline = line.strip()
                    # a handful don't have content: need to fix upstream
                    if "\t" not in cleanline:
                        continue
                    artid, paragraph = line.strip().split("\t")
                    if artid != lastid:
                        # new article: output previous data, reset
                        if lastid:
                            self.data[lastid] = Article(
                                identifier=lastid, headword=headword, paragraphs=paragraphs
                            )
                        # first line has the headword
                        headword = paragraph
                        paragraphs = []
                        lastid = artid
                    else:
                        # continue previous article
                        paragraphs.append(paragraph)
                except Exception as e:
                    print(f"Failed on {line}\n{e}")

    def wordcount_bins(self, binsize: int = 100) -> Counter:
        """Return a counter of article wordcounts by binsize."""
        return Counter(int(art.wordcount / binsize) for art in self.values())

    def numbered_paragraphs(self) -> list[Article]:
        """Return a list of numbered paragraphs."""
        return [art for art in self.values() if art.is_numbered()]
