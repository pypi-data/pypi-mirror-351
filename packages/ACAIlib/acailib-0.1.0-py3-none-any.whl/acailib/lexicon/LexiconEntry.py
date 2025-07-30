"""Read the UBS dictionaries into lookup dicts.

The dataclass reflect the XML hierarchy (selectively):
Lexicon_Entry.baseforms ->
BaseForm.lexMeanings ->
LEXMeaning.lexSenses ->
LEXSense

# iterate over all the senses
>>> senses = [lexsense for lexent in ubsprs.values()
 for baseform in lexent.baseforms
 for lexmean in baseform.lexMeanings
 for lexsense in lexmean.lexSenses]
>>> len(senses)
9166
>>> senses[23].asdict()
{'languageCode': 'en', 'glosses': ['good', 'goodness', 'good act'], 'definitionShort': 'positive moral qualities of the most general nature', 'definitionLong': '', 'comments': []}

"""

from dataclasses import dataclass, field
from typing import Any, Optional

from biblelib.word import bcvwpid


@dataclass
class LEXSense:
    """Represents the same element from UBSGNT as a Python dataclass."""

    # no distinct identifier: 1-1 with LEXMeaning for Greek
    # the language of the definition
    languageCode: str
    glosses: list[str]
    definitionShort: str
    definitionLong: str
    comments: list[str]
    # link upward: beware recursion
    parent: Optional["LEXMeaning"] = field(init=False, default=None)

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"<LEXSense: {';'.join(self.glosses)}>"

    def asdict(self) -> dict[str, Any]:
        """Return content as dict, minus the parent to avoid infinite recursion."""
        fields = ["languageCode", "glosses", "definitionShort", "definitionLong", "comments"]
        return {f: getattr(self, f) for f in fields}


@dataclass
class LEXMeaning:
    """Represents the same element from UBSGNT as a Python dataclass."""

    identifier: str
    isBiblicalTerm: str
    entryCode: str
    # only a single value for DGNT
    lexDomains: list[str]
    # only a single value for DGNT
    lexSubDomains: list[str]
    # appears to only be one LEXSense per LEXMeaning? But the
    # structure allows for more
    lexSenses: list[LEXSense]
    # using MARBLE-style references
    # this includes the deuterocanon, which seems to often have
    # multiple meanings for a single reference
    # some unusual ones like '04500900300002{N:002}'
    lexReferences: list[str]
    # link upward: beware recursion
    parent: Optional["BaseForm"] = field(init=False, default=None)

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"<LEXMeaning: {self.identifier}>"

    def __hash__(self) -> int:
        """Return a hash value."""
        return hash(self.identifier)

    def asdict(self) -> dict[str, Any]:
        """Return content as dict, minus the parent to avoid infinite recursion."""
        fields = ["identifier", "isBiblicalTerm", "entryCode", "lexDomains", "lexSubDomains"]
        return {f: getattr(self, f) for f in fields}

    def serialize(self) -> dict[str, str]:
        """Return content as dict for serialization.

        Flattens single-value lists into strings, and omits references and parent.
        """
        refs: list[str] = []
        # the first three should be enough
        for ref in self.lexReferences[:3]:
            try:
                if len(ref) == 12:
                    refs.append(bcvwpid.BCVWPID(ref).to_usfm(with_word=True))
                else:
                    refs.append(bcvwpid.BCVID(ref).to_usfm())
            except Exception as e:
                print(f"Error processing reference {ref} from {self.identifier}: {e}")
                refs.append(ref)
        return {
            "identifier": self.identifier,
            "isBiblicalTerm": self.isBiblicalTerm,
            "lexDomains": ";".join(self.lexDomains),
            "lexSubDomains": ";".join(self.lexSubDomains),
            "entryCode": self.entryCode,
            "lemma": self.parent.parent.lemma,
            "glosses": ";".join(self.lexSenses[0].glosses),
            "definitionShort": self.lexSenses[0].definitionShort,
            "lexReferences": ";".join(refs),
        }

    def serialize_text(self) -> dict[str, str]:
        """Return textual content as dict for serialization.

        Flattens single-value lists into strings, and omits references and parent.
        """
        return {
            "entryCode": self.entryCode,
            "lemma": self.parent.parent.lemma,
            "glosses": ";".join(self.lexSenses[0].glosses),
            "definitionShort": self.lexSenses[0].definitionShort,
            "lexDomains": ";".join(self.lexDomains),
            "lexSubDomains": ";".join(self.lexSubDomains),
        }


@dataclass
class BaseForm:
    """Represents the same element from UBSGNT as a Python dataclass."""

    identifier: str
    partsofspeech: list[str]
    lexMeanings: list[LEXMeaning]
    # FUTURE: incorporate RelatedLemmas.L
    # link upward: beware recursion
    parent: Optional["Lexicon_Entry"] = field(init=False, default=None)

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"<BaseForm: {self.identifier}>"

    def __hash__(self) -> int:
        """Return a hash value."""
        return hash(self.identifier)

    def asdict(self) -> dict[str, Any]:
        """Return content as dict, minus the parent to avoid infinite recursion."""
        selfdict = {f: getattr(self, f) for f in ["identifier", "partsofspeech"]}
        # if self.parent:
        #     # need to populate these for testing
        #     selfdict["lemma"] = self.parent.lemma
        #     # yuck but ...
        #     selfdict["strongCodes"] = self.parent.strongCodes
        return selfdict


@dataclass
class Lexicon_Entry:
    """Represents the same element from UBSGNT as a Python dataclass."""

    identifier: str
    lemma: str
    strongCodes: list[str]
    # FUTURE: capture Notes (see Lexicon_Entry Id="003076000000000")
    # multiple values if different parts of speech,
    # e.g. <Lexicon_Entry: 000266000000000>
    baseforms: list[BaseForm]

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return f"<Lexicon_Entry: {self.identifier}>"

    def __hash__(self) -> int:
        """Return a hash value."""
        return hash(self.identifier)

    def get_meanings(self) -> list[LEXMeaning]:
        """Return a list of of LEXMeanings for this entry."""
        return [lm for bf in self.baseforms for lm in bf.lexMeanings]
