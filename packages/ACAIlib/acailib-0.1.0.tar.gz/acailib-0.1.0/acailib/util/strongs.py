"""Utilities for working with Strong's numbers.

This duplicates functionality in
internal-alignments/src/util/strong.py. Should eventually refactor
into a single library to avoid this, but until then, keep in sync

Obligatory disclaimer: Strong's numbers are a mess, and we shouldn't
rely on them. Nevertheless, some data comes with them, so we should
maintain them, and (when forced) use them.

"""

import re


def normalize_strongs(strongs: str | int, prefix: str = "") -> str:
    """Return a normalized Strongs id."""
    _strongsre: re.Pattern = re.compile(r"[AGH]?\d{1,4}[a-d]?")
    specials: dict[str, str] = {
        "1537+4053": "G4053b",
        "5228+1537+4053": "G4053c",
        "1417+3461": "G3461b",
    }
    # special case for uW KeyTerms data: some like G29620. It appears
    # the last digit is always zero
    if isinstance(strongs, str) and strongs.startswith("G") and len(strongs) == 6:
        if strongs.endswith("0"):
            strongs = strongs[:-1]
        else:
            raise ValueError(f"6-char Strong's code: {strongs}")
    # some special cases for SBLGNT data
    if strongs in specials:
        normed = specials[str(strongs)]
    elif isinstance(strongs, int):
        assert prefix, f"prefix is required for a bare int: {strongs}"
        normed = f"{prefix}{strongs:0>4}"
    elif _strongsre.fullmatch(strongs):
        # check for initial prefix: save if available
        if re.match(r"[AGH]", strongs):
            if prefix:
                print(f"Overwriting prefix parameter {prefix} for {strongs}")
            prefix = strongs[:1]
        base = re.sub(r"\D", "", strongs)
        # final letter
        if re.search("[a-d]$", strongs):
            suffix = strongs[-1]
        else:
            suffix = ""
        # might need other tests here
        # may leave prefix unspecified
        assert prefix, f"prefix must be specified: {strongs}"
        normed = f"{prefix}{base:0>4}{suffix}"
    else:
        raise ValueError(f"Invalid Strong's code: {strongs}")
    return normed
