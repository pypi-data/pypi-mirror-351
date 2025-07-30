"""Utilities for working with ACAI data."""

import re

from .TSVReader import TSVReader
from .Language import Locstr, LocDict, LocDictSet, LanguageSet
from .marble import is_prot_marbleid, from_marbleid, from_marbleid_range, get_from_marbleids

from .strongs import normalize_strongs


__all__ = [
    #
    "makeuri",
    # Language
    "Locstr",
    "LocDict",
    "LocDictSet",
    "LanguageSet",
    # TSVReader
    "TSVReader",
    # marble
    "is_prot_marbleid",
    "from_marbleid",
    "from_marbleid_range",
    "get_from_marbleids",
    # strongs
    "normalize_strongs",
]


def makeuri(prefLabel: str, namespaceprefix: str) -> str:
    """Return a URI for an ACAI item based on the preferred label.

    This replaces and strips characters from the title to make a URI.
    """
    assert prefLabel, "Empty prefLabel is not allowed."
    assert namespaceprefix.endswith(":"), f"'{namespaceprefix}' must end in a colon"
    uri = re.sub(r"[ ~/-]", "_", prefLabel)
    cleanuri = re.sub(r"[“”’():]", "", uri)
    return f"{namespaceprefix}{cleanuri}"
