"""Common Pydantic classes for language support.

>>> from acai import LangEnum
>>> from acai.util import Language
>>> lstr = Language.Locstr(lang=LangEnum("grc"), value="foo")
>>> lstr.lang
<LangEnum.greek: 'grc'>
>>> lstr.lang.value
'grc'
>>> lset = Language.LanguageSet(lang="grc", lemma="Ἰησοῦς", transliteration="Iēsŏus", references=["n41001001004"])
>>> lset.lang
<LangEnum.greek: 'grc'>
>>> lset.lemma
'Ἰησοῦς'
>>> ld = Language.LocDict({"eng": "dog", "spa": "perro"})
>>> ld.get_value("eng")
'dog'
# language code must exist and have data
>>> ld.get_value("fra")
AssertionError: No data for fra


For ingestion, it may be best to collate values from several fields
together for a single language, so you can e.g. retrieve all the
English values without worrying about the others.

PROBLEM: switching from Pydantic to ordinary dataclasses because of a
problem with downstream Pydantic classes using them.

"""

from collections import UserDict
from dataclasses import dataclass
from typing import Any, Mapping

# from pydantic import BaseModel

from acailib import LangEnum, TargetLanguageCodes


# class Locstr(BaseModel):
@dataclass
class Locstr:
    """Defines an instance of a localized string for a biblical language."""

    # string value
    value: str
    # language code
    lang: LangEnum = LangEnum.greek

    def __post_init__(self) -> None:
        """Compute values after initialization."""
        assert isinstance(self.lang, LangEnum), f"lang must be a LangEnum instance: {self.lang}"


class _LocBase(UserDict):
    """Base for collections of localized strings."""

    targetlangcodes = {tlc.value for tlc in TargetLanguageCodes.__members__.values()}

    def __init__(self, initialdata: Mapping[str, Any] = {}) -> None:
        """Initialize a LocDict instance.

        Checks the validity of keys, but not values.
        """
        for pair in initialdata.items():
            self._check_mapping(*pair)
        super().__init__(initialdata)

    def _check_mapping(self, code: str, value: Any) -> None:
        """Check that mapping is valid: return False if not."""
        self._check_langcode(code)
        self._check_value(value)

    def _check_langcode(self, code: str) -> None:
        """Check that language code is valid: return False if not."""
        assert code in self.targetlangcodes, f"Invalid language code: {code}"

    def _check_value(self, value: Any) -> None:
        """Check to ensure value is valid."""
        assert isinstance(value, str), f"Value must be a string: {value}"

    # typing complaints here about incompatible signatures: beyond my
    # understanding
    def update(self, m: Mapping[str, str]) -> None:
        """Update, with key checking."""
        # unlike parent, doesn't allow empty m
        for code, val in m.items():
            self._check_mapping(code, val)
            self[code] = val

    def get_value(self, code: Any) -> Any:
        """Return the value for code, a language code.

        It is an error if there is no localization for code.
        """
        self._check_langcode(code)
        assert code in self, f"No data for {code}"
        return self[code]


class LocDict(_LocBase):
    """Defines a collection of localized strings.

    Assumes the various strings are translations of each
    other. Languages must either be valid source or target codes.

    """

    def __init__(self, initialdata: Mapping[str, str]) -> None:
        """Initialize a LocDict instance."""
        super().__init__(initialdata)


class LocDictSet(_LocBase):
    """Defines a collection of localizations, with a set for each language.

    This is typically used for alternate labels. There is no
    correspondence between labels across languages.

    """

    def __init__(self, initialdata: Mapping[str, set]) -> None:
        """Initialize a LocDict instance."""
        super().__init__(initialdata)

    # override
    def _check_value(self, value: set) -> None:
        """Check to ensure value is valid.

        Value must be a non-empty set.
        """
        assert isinstance(value, set), f"Value must be a set: {value}"
        assert value, "Set must not be empty"


# class LanguageSet(BaseModel):
@dataclass
class LanguageSet:
    """Defines a lemma and references for a dataset instance."""

    # language code
    lang: LangEnum
    lemma: str
    transliteration: str
    # list of BCVWP IDs
    # must be at least one: needs validation
    references: list[str]

    def __post_init__(self) -> None:
        """Compute values after initialization."""
        assert isinstance(self.lang, LangEnum), f"lang must be a LangEnum instance: {self.lang}"
