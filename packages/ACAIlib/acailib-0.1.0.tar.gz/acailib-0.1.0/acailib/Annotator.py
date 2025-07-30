"""The Annotator delivers ACAI entities for verses and words.

>>> from acai.core import Annotator
>>> ann = Annotator.Annotator()
# no annotations for the first word of MRK 1:4
>>> ann.get("n41001004001")
# second word is an explicit reference to John (the Baptist)
>>> ann.get("n41001004002")
[('person:John', 'explicit_instances')]
# fourth word has John as implicit subject
>>> ann.get("n41001004004")
[('person:John', 'subject_referents')]

"""

from collections import UserDict
from typing import Any

from biblelib.word import bcvwpid

from acai.util import EntityReader
from acai.images import Reader


# def imagereflookup(refstr: str) -> Any:
#     try:
#         # try parsing as USFM
#         bcvid = bcvwpid.fromusfm(refstr).get_id()
#         # usfm = refstr
#     except Exception as _:
#         # otherwise treat as BCV
#         bcvid = refstr
#         # usfm = bcvwpid.make_id(refstr).to_usfm()
#     return set(READER.get_images(bcvid))


class Annotator(UserDict):

    reader = Reader()

    readers: dict[str, EntityReader.EntityReader] = {
        "deity": EntityReader.DeitiesReader(),
        "group": EntityReader.GroupsReader(),
        "person": EntityReader.PeopleReader(),
        "place": EntityReader.PlacesReader(),
    }

    # ntrefs = {ref: data for ref, data in ann.items() if int(ref[1:3]) > 39}
    def __init__(self) -> None:
        """Initialize an instance."""
        super().__init__(self)
        # self.data maps BCVWP identifiers to a list of (entityid,
        # referencetype) tuples
        # data: dict[str, list[tuple[str, str]]] = {}
        for readertype, reader in self.readers.items():
            for entityid, entityrec in reader.items():
                entityrefdict = reader.word_references_by_type(entityid)
                for reftype in entityrefdict:
                    # this 'flattens' sequences of tokens: that may be wrong
                    for canon, allrefs in entityrefdict[reftype].items():
                        for reflist in allrefs:
                            for ref in reflist:
                                if ref not in self.data:
                                    self.data[ref] = []
                                self.data[ref].append((entityid, reftype))
        # also need to capture ref -> image, but this is verse-level,
        # not word-level (until associated with ACAI entities)
