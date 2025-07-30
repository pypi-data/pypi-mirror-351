"""Parse UBSGNT into dataclasses.

The combination of an entryCode and a lemma makes for a unique
sense/meaning record (which also has an identifier, but it's opaque).

>>> from acai.lexicon import UBSParser
>>> ubsprs = UBSParser()
# these are Lexicon_Entry instances
>>> len(ubsprs)
5507
# these are LEXSense instances: 1-1 with LEXMeaning instances
>>> len(list(ubsprs.sense_iterator()))
9166


# lookup from a lemma
>>> pagis = ubsprs.get_lemma_entries("παγίς")
>>> pagis
<Lexicon_Entry: 003707000000000>
>>> pagis.get_meanings()
[<LEXMeaning: 003707001001000>, <LEXMeaning: 003707001002000>, <LEXMeaning: 003707001003000>]

# lookup from a Louw-Nida code
>>> trapsnare = ubsprs.get_entryCode_meanings("6.23")
>>> trapsnare
<LEXMeaning: 003707001001000>
>>> trapsnare.asdict()
{'identifier': '003707001001000', 'isBiblicalTerm': 'M', 'entryCode': '6.23', 'lexDomains': ['Artifacts'], 'lexSubDomains': ['Traps, Snares']}
# Dictionary for serialization
>>> trapsnare.serialize()
{'identifier': '003707001001000', 'isBiblicalTerm': 'M', 'lexDomains': 'Artifacts', 'lexSubDomains': 'Traps, Snares', 'entryCode': '6.23', 'lemma': 'παγίς', 'glosses': 'trap;snare', 'definitionShort': 'a device used for trapping or snaring, principally birds', 'lexReferences': 'LUK 21:35!2;ROM 11:9!9'}

# lookup from a strongs number: only one lemma for this one
>>> strongs_lemmas["G3803"]
[<Lexicon_Entry: 003707000000000>]

See LexiconEntry.py for additional details on the dataclasses.

# Aggregate data elements
>>> from acai.lexicon import Aggregator
>>> agg = Aggregator(ubsprs)
# mapping of domain names to subdomain names
>>> agg.domain_subdomains['Military Activities']
{'Soldiers, Officers', 'Prisoners of War', 'To Fight', 'Army', 'To Arm'}
# text attribute for lexSenses in a subdomain: default attribute is definitionShort
>>> agg.subdomain_words('To Fight')
['to go to war against', '(figurative extension of meaning of {L:μάχαιρα<SDBG:μάχαιρα:000000>}[a] ‘sword,’ {D:6.33})', 'to engage in open warfare', 'act of engaging in open warfare', '(figurative extension of meaning of {L:ῥομφαία<SDBG:ῥομφαία:000000>}[a] ‘broad sword,’ {D:6.32})', 'act of engaging in war or battle as a soldier', 'to engage in war or battle as a soldier', 'to oppose in battle']
# or the entryCode attribute (on the parten LexMeaning)
>>> agg.subdomain_words('To Fight', strfun=lambda lm: lm.lexSenses[0].parent.entryCode)
['55.2', '55.6', '55.5', '55.5', '55.6', '55.4', '55.4', '55.3']
# or the glosses
>>> agg.subdomain_words('To Fight', strfun=lambda lm: lm.lexSenses[0].glosses)
[['to rise up in arms against', 'to make war against'], ['war', 'fighting', 'conflict'], ['to wage war', 'war', 'fighting'], ['war', 'fighting'], ['war', 'fighting', 'conflict'], ['war', 'warfare'], ['to battle', 'to fight', 'to engage in war', 'warfare'], ['to meet in battle', 'to face in battle']]

"""

from collections import UserDict, defaultdict
from csv import DictWriter
from pathlib import Path
from typing import Any, Callable, Generator
import unicodedata

import requests
from lxml import etree

from biblelib.word import fromubs

from acai import DATAPATH

from .LexiconEntry import LEXSense, LEXMeaning, BaseForm, Lexicon_Entry


def get_ubsdgnt(langcode: str = "eng") -> str:
    """Return a string for the readable content from Github."""
    pathprefix: str = (
        "https://github.com/ubsicap/ubs-open-license/raw/main/dictionaries/greek/XML/UBSGreekNTDic-v1.0"
    )
    langcodes = {
        "eng": "en",
        "fra": "fr",
        "spa": "sp",
        # not ISO 639-3
        "zhs": "zhs",
        "zht": "zht",
    }
    return f"{pathprefix}-{langcodes[langcode]}.XML"


class UBSParser(UserDict):
    """Manage data read from UBSGNT."""

    # for lookup methods
    lemma_entries: dict[str, Lexicon_Entry] = {}
    entryCode_meanings: dict[str, LEXMeaning] = {}
    # sometimes multiple meanings for a word-level reference
    reference_meanings: dict[str, list[LEXMeaning]] = defaultdict(list)
    # for filtering: these domain codes are grammatical markers whose
    # semantics we may not care about
    grammatical_domains = {"90", "91", "92", "93"}

    def __init__(self, langcode: str = "eng"):
        """Initialize the parser."""
        super().__init__()
        # these store _elements_ for debugging
        # unfollowed import problem, so values are Any
        self.lexicon_entries: dict[str, Any] = {}
        self.baseform_elements: dict[str, Any] = {}
        self.lexmeaning_elements: dict[str, Any] = {}
        self.dicturi = get_ubsdgnt(langcode)
        r = requests.get(self.dicturi)
        assert r.status_code == 200, f"Failed to get content from {self.dicturi}"
        # normalize everything so matching works
        self.root = etree.fromstring(r.text)
        # iterate over Lexicon_Entry elements
        # for Greek, each Lexicon_Entry.lemma is unique, so could use
        # lemma for keys rather than identifier. Not sure about Hebrew though
        self.data = {
            thislexe.identifier: thislexe
            for lexentry in self.root.xpath("//Lexicon_Entry")
            if (thislexe := self._do_lexicon_entry(lexentry))
        }

    @staticmethod
    def _first_if(xpathexpr: str) -> str:
        """Return first string value in the xpath result, or empty string."""
        return xpathexpr[0] if len(xpathexpr) > 0 else ""

    # type complaint with this
    #    def _do_senses(self, lexmean: etree._Element) -> list[LEXSense]:
    def _do_senses(self, lexmean: Any) -> list[LEXSense]:
        """Process LEXSense content.

        Returns a list with a single LEXSense instance. This leaves
        room for other data that might have multiple.

        """
        # only ever one LEXSense for Greek
        lexsense = lexmean.xpath("LEXSenses/LEXSense")[0]
        lsdict = dict(
            languageCode=lexsense.xpath("@LanguageCode")[0],
            glosses=lexsense.xpath("Glosses/Gloss/text()"),
            definitionShort=self._first_if(lexsense.xpath("DefinitionShort/text()")),
            definitionLong=self._first_if(lexsense.xpath("DefinitionLong/text()")),
            comments=lexsense.xpath("Comments/text()"),
        )
        return [LEXSense(**lsdict)]

    # def _do_meaning(self, lexmean: etree._Element) -> LEXMeaning:
    def _do_meaning(self, lexmean: Any) -> LEXMeaning:
        """Process LEXMeaning contents."""
        # stash for debugging
        lexmean_id: str = lexmean.xpath("@Id")[0]
        self.lexmeaning_elements[lexmean_id] = lexmean
        try:
            lexsenses = self._do_senses(lexmean)
        except Exception as e:
            print(f"Failed on {lexmean}, {lexmean_id}\n{e}")
            lexsenses = []
        try:
            lexReferences = [
                ubsref.get_id()
                for ref in lexmean.xpath("LEXReferences/LEXReference/text()")
                for ubsref in fromubs(ref)
            ]
        except Exception as e:
            print(f"Failed on references for {lexmean}, {lexmean_id}\n{e}")
            lexReferences = []
        lexmeaning = LEXMeaning(
            identifier=lexmean_id,
            isBiblicalTerm=self._first_if(lexmean.xpath("@IsBiblicalTerm")),
            entryCode=self._first_if(lexmean.xpath("@EntryCode")),
            # does this capture multiple values correctly?
            lexDomains=lexmean.xpath("LEXDomains/LEXDomain/text()"),
            lexSubDomains=lexmean.xpath("LEXSubDomains/LEXSubDomain/text()"),
            lexSenses=lexsenses,
            lexReferences=lexReferences,
        )
        for lexs in lexsenses:
            lexs.parent = lexmeaning
        return lexmeaning

    def _do_baseform(self, baseformel: Any) -> BaseForm:
        """Process BaseForm contents."""
        # stash for debugging
        baseform_id: str = baseformel.xpath("@Id")[0]
        self.baseform_elements[baseform_id] = baseformel
        baseform = BaseForm(
            identifier=baseform_id,
            partsofspeech=baseformel.xpath("PartsOfSpeech/PartOfSpeech/text()"),
            lexMeanings=[
                self._do_meaning(lm)
                for lm in baseformel.xpath("LEXMeanings/LEXMeaning")
                if self._first_if(lm.xpath("@IsBiblicalTerm")) != "N"
            ],
        )
        for lm in baseform.lexMeanings:
            lm.parent = baseform
        return baseform

    def _do_lexicon_entry(self, lexentry: Any) -> Lexicon_Entry:
        """Process Lexicon_Entry contents."""
        lexentry_id: str = lexentry.xpath("@Id")[0]
        self.lexicon_entries[lexentry_id] = lexentry
        # PROCESS _do_baseform here
        thislexe = Lexicon_Entry(
            identifier=lexentry_id,
            lemma=unicodedata.normalize("NFKC", lexentry.xpath("@Lemma")[0]),
            strongCodes=lexentry.xpath("StrongCodes/Strong/text()"),
            # this assumes a single BaseForm per lexentry
            baseforms=[self._do_baseform(bf) for bf in lexentry.xpath("BaseForms/BaseForm")],
        )
        for bf in thislexe.baseforms:
            bf.parent = thislexe
        return thislexe

    # accessors
    # only build these on demand

    # just make lemma the key for self.data?
    def get_lemma_entries(self, lemma: str) -> Lexicon_Entry:
        """Return the Lexicon_Entry instance for lemma."""
        if not self.lemma_entries:
            self.lemma_entries = {entry.lemma: entry for entry in self.data.values()}
        return self.lemma_entries[lemma]

    def get_entryCode_meanings(self, entryCode: str) -> LEXMeaning:
        """Return the LEXMeaning instance for an entryCode."""
        if not self.entryCode_meanings:
            self.entryCode_meanings = {
                meaning.entryCode: meaning
                for entry in self.data.values()
                for baseform in entry.baseforms
                for meaning in baseform.lexMeanings
            }
        return self.entryCode_meanings[entryCode]

    def get_reference_meanings(self, reference: str) -> list[LEXMeaning]:
        """Return the LEXMeaning instances for an reference."""
        if not self.reference_meanings:
            for entry in self.data.values():
                for baseform in entry.baseforms:
                    for meaning in baseform.lexMeanings:
                        for ref in meaning.lexReferences:
                            self.reference_meanings[ref].append(meaning)
        return self.reference_meanings[reference]

    def get_strongs_lemmas(self) -> dict[str, list[Lexicon_Entry]]:
        """Return a mapping from strongs to lemmas."""
        strongs_lemmas: dict[str, list[Lexicon_Entry]] = defaultdict(list)
        for entry in self.data.values():
            for strong in entry.strongCodes:
                strongs_lemmas[strong].append(entry)
        return strongs_lemmas

    def get_strongs_meanings(self) -> dict[str, list[LEXMeaning]]:
        """Return a mapping from strongs to lexMeanings."""
        strongs_lemmas: dict[str, list[LEXMeaning]] = defaultdict(list)
        for entry in self.data.values():
            for baseform in entry.baseforms:
                for meaning in baseform.lexMeanings:
                    for strong in entry.strongCodes:
                        strongs_lemmas[strong].append(meaning)
        return strongs_lemmas

    def meaning_iterator(self) -> Generator[LEXMeaning, None, None]:
        """Return a generator over senses."""
        for lexent in self.values():
            for baseform in lexent.baseforms:
                for lexmean in baseform.lexMeanings:
                    yield lexmean

    def sense_iterator(self) -> Generator[LEXSense, None, None]:
        """Return a generator over senses.

        Note these are 1-1 with meanings for DGNT.
        """
        for lexmean in self.meaning_iterator():
            for lexsense in lexmean.lexSenses:
                yield lexsense

    def sense_references(self) -> dict[str, list[str]]:
        """Return a dict of sense identifiers and their references."""
        return {
            parent.identifier: parent.lexReferences
            for sense in self.sense_iterator()
            if (parent := sense.parent)
        }

    def write_sense_data(self, outpath: Path = DATAPATH / "lexicon/sensedata.tsv") -> None:
        """Write out sense data as TSV."""
        self.definitionShort = {}
        self.comments = {}
        self.glosses = {}
        fieldnames = [
            "LEXMeaningID",
            "LEXMeaningEntryCode",
            "glosses",
            "definitionShort",
            "comments",
        ]
        with outpath.open("w", encoding="utf-8", newline="") as f:
            writer = DictWriter(
                f,
                fieldnames=fieldnames,
                delimiter="\t",
            )
            writer.writeheader()
            for lexsense in self.sense_iterator():
                sensedict = lexsense.asdict()
                del sensedict["languageCode"]
                del sensedict["definitionLong"]
                parent = lexsense.parent
                lexmeaningid = parent.identifier
                sensedict.update({"LEXMeaningID": lexmeaningid})
                sensedict.update({"LEXMeaningEntryCode": parent.entryCode})
                writer.writerow(sensedict)
                self.definitionShort[lexmeaningid] = lexsense.definitionShort
                self.comments[lexmeaningid] = lexsense.comments
                self.glosses[lexmeaningid] = lexsense.glosses


# ordering here may be suboptimal
class Aggregator:
    """Aggregate various data elements."""

    def __init__(self, parser: UBSParser) -> None:
        """Initialize the aggregator."""
        self.parser = parser
        # maps domain strings to their subdomain strings
        # might be nicer to also capture the number?
        self.domain_subdomains: dict[str, set[str]] = defaultdict(set)
        # maps subdomain strings to their LEXMeaning instances
        self.subdomain_meanings: dict[str, list[LEXMeaning]] = defaultdict(list)
        for meaning in self.parser.meaning_iterator():
            # there's really only one for DGNT
            for subdomain in meaning.lexSubDomains:
                self.subdomain_meanings[subdomain].append(meaning)
            for domain in meaning.lexDomains:
                self.domain_subdomains[domain].add(subdomain)

    def subdomain_words(
        self, subdomain: str, strfun: Callable = lambda lm: lm.lexSenses[0].definitionShort
    ) -> list[list[str]]:
        """Return a list of lists of words for a subdomain.

        strfun is a function that takes a LEXMeaning and returns a
        string. Default is to return definitionShort for the first
        (only) lexSense.

        """
        return [strfun(meaning) for meaning in self.subdomain_meanings[subdomain]]
