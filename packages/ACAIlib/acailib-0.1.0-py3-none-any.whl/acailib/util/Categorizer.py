"""Categorize according to content type, based on name matching.


>>> from acai.util import TyndaleReader
>>> tynrd = TyndaleReader.Reader()
>>> len(tynrd)
5027
>>> list(tynrd.items())[23]
('AbelShittim', Article(identifier='AbelShittim', headword='ABEL-SHITTIM', paragraphs=['Alternate name for Shittim, a place on\xa0the plains of Moab, in bref^Num_33_49. See art^ShittimPlace.'], wordcount=14, isredirect=True, contenttype=''))
>>> from acai.util import Categorizer
>>> ctgr = Categorizer.Categorizer()
# fil in the contenttype attribute
>>> for art in tynrd.values():
...   art.contenttype = ctgr.categorize_tynbd(art.clean_headword)
...
>>> tynrd["AbelShittim"]
Article(identifier='AbelShittim', headword='ABEL-SHITTIM', paragraphs=['Alternate name for Shittim, a place on\xa0the plains of Moab, in bref^Num_33_49. See art^ShittimPlace.'], wordcount=14, isredirect=True, contenttype='place')

"""

from collections import defaultdict

from acai.util import EntityReader


class Categorizer:
    """Match names to heuristically determine content types."""

    default_type: str = "acai"
    upcase: bool = True
    entitytypes: list = ["deity", "group", "person", "place"]

    def __init__(self) -> None:
        """Initialize an instance."""
        self.readers: dict[str, EntityReader.EntityReader] = {
            "deity": EntityReader.DeitiesReader(self.upcase),
            "group": EntityReader.GroupsReader(self.upcase),
            "person": EntityReader.PeopleReader(self.upcase),
            "place": EntityReader.PlacesReader(self.upcase),
        }

    @staticmethod
    def clean_asterisk(string: str) -> str:
        """Drop a final asterisk if present."""
        if string.endswith("*"):
            return string[:-1]
        else:
            return string

    def categorize_string(self, string: str) -> str:
        """Return a content type string given a Tyndale headword.

        This uses a sequence of heuristics: the categorization is not
        guaranteed to be correct.

        If nothing matches, return the default_type.

        """
        # special cases for TynBD headwords
        if string.endswith(" (Person )"):
            return "person"
        elif string.endswith(" (Place )"):
            return "place"
        elif string in self.readers["person"].eng_preferred_label_dict:
            return "person"
        elif string in self.readers["place"].eng_preferred_label_dict:
            return "place"
        elif string in self.readers["group"].eng_preferred_label_dict:
            return "group"
        elif string in self.readers["deity"].eng_preferred_label_dict:
            return "deity"
        elif string in self.readers["person"].eng_alternate_label_dict:
            return "person"
        elif string in self.readers["place"].eng_alternate_label_dict:
            return "place"
        else:
            return self.default_type

    def categorize_tynbd(self, headword: str) -> str:
        """Return a content type string given a Tyndale headword.

        This uses a sequence of heuristics: the categorization is not
        guaranteed to be correct.

        If nothing matches, return the default_type.

        """
        if ", " in headword:
            types: list[str] = [
                self.categorize_string(self.clean_asterisk(string))
                for string in headword.split(", ")
            ]
            realtypes = [t for t in types if t != self.default_type]
            if realtypes:
                return realtypes[0]
            else:
                return self.default_type
        else:
            return self.categorize_string(self.clean_asterisk(headword))


"""Incremental development:

- Simple entity name matching gets 2105 categories
- Adding headword cleanup for trailing asterisk: 2575
- clean_headword splits commas: 2868
- adding checking of alternate labels: 3225

Additional patterns not yet implemented:

- comma inversions like "ARABAH*, Brook of the"
- books: variety of string matches, 66+
- art.headword.endswith("Tribe of"): 12
- Hebrew months: 12
- Gates
"""
