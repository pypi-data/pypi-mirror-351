"""Utilities for working with MARBLE data."""

import re
from typing import Any
from warnings import warn


from biblelib.word import BCVID, BCVIDRange, BCVWPID, fromubs, simplify
from biblelib.unit import unitrange


def is_prot_marbleid(marbleid: str) -> bool:
    """Return True if a Marble ID from the Protestant canon."""
    if re.match("[A|G|H|L]", marbleid):
        # strip a leading language code if present
        marbleid = marbleid[1:]
    # check book indices
    bookindex = marbleid[:3]
    return (bookindex <= "039") or ("066" >= bookindex >= "040")


def from_marbleid(marbleid: str, omitdc: bool = True, verbose: bool = False) -> list[str]:
    """Return a list of BCVWP ID from a Marble ID like H00501900500034.

    With omitdc = True (the default), silently drop references outside
    the Protestant canon. With verbose = True (default is False), warn
    about these.

    """
    if re.match("[A|G|H|L]", marbleid):
        # strip a leading language code if present
        marbleid = marbleid[1:]
    # TODO: rehydrate a range into a sequence
    try:
        if omitdc and not is_prot_marbleid(marbleid):
            # drop references outside the Protestant canon
            if verbose:
                warn(f"Dropping DC reference: {marbleid}")
            return []
        else:
            return [bcv.ID for bcv in fromubs(marbleid)]
    except Exception as e:
        print(f"Failed on {marbleid}: {e}")
        return []


def from_marbleid_range(ref: str, verbose: bool = False) -> list[Any]:
    """Return a list of BCV(WP) IDs from a Marble ID that might be a range.

    If a range, it may produce a list of BCVID instances: Hebrew
    references may return multiple BCVWPID instances when MARBLE
    tokenization a word together that Macula splits. So items in the
    results list can be heterogeneous as to reference level.

    With verbose = True (default is False), warn about Deuterocanon
    references: otherwise drop them silently.

    """
    bcvlist: list[Any] = []
    # bcvlist: list[BCVID | BCVWPID] = []
    if "-" in ref:
        # range reference: rehydrate into a sequence
        # probably fragile assumptions here
        startmid, endmid = ref.split("-")
        start_bcvwpids = fromubs(startmid)
        end_bcvwpids = fromubs(endmid)
        try:
            if start_bcvwpids[0].chapter_ID == end_bcvwpids[0].chapter_ID:
                # this silently assumes the range is contiguous
                refrange = BCVIDRange(start_bcvwpids[0], end_bcvwpids[-1])
                bcvlist = refrange.enumerate()
            else:
                vrange = unitrange.VerseRange(start_bcvwpids[0], end_bcvwpids[-1])
                bcvlist = vrange.enumerate_ids()
            return bcvlist
        except Exception as e:
            print(f"Cannot process range {ref}, dropping\n{e}")
            return []
        # return unitrange.VerseRange(start=start_bcvwpid, end=end_bcvwpid)
    else:
        # silently drop DC references
        if is_prot_marbleid(ref):
            bcvwpref: list = fromubs(ref)
            # don't simplify. empty string if in DC
            return bcvwpref if bcvwpref else []
        else:
            if verbose:
                warn(f"Dropping {ref}")
            return []


def get_from_marbleids(seq: list, verbose: bool = False) -> list[str]:
    """Return a list of normalized BCV references from MARBLE ids.

    Map ranges to their enumerated items. Throughout convert to
    Biblelib-style BCVWPID token ids.

    """
    return [
        # no prefix: with part_index because Hebrew
        item.get_id()
        for marbleid in seq
        for item in from_marbleid_range(marbleid, verbose)
        if item
    ]
