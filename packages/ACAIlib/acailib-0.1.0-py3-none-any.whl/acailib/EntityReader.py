"""Read ACAI data into a dict.

>>> from acai.util import EntityReader
>>> peoplerd = EntityReader.PeopleReader()
# return a list of entities whose preferred label matches a given string
>>> peoplerd.eng_preferred_label_dict["John"]
['person:John.3', 'person:John', 'person:John.2', 'person:John.5', 'person:John.4']
# likewise for other EntityReader subclasses

"""

from collections import UserDict, defaultdict
from collections.abc import Callable
import json
from pathlib import Path
from typing import Optional

from acailib import ACAIROOT
from acailib.shared_classes import AcaiDeity, AcaiGroup, AcaiPerson, AcaiPlace


class EntityReader(UserDict):
    """Base class for reading entity data."""

    acaidir: str = ""
    jsondir: Path = Path()
    # typing here needs help
    entryclass: Optional[Callable] = None
    repodata: str = "https://github.com/Clear-Bible/ACAI/tree/main/data"

    def __init__(self, upcase: bool = False) -> None:
        """Initialize an instance.

        With upcase = True (default is False), convert names to all
        upper-case. This is useful for matching TynBD headwords that
        are all upper-case.

        """
        super().__init__()
        for jsonfile in self.jsondir.glob("*.json"):
            with jsonfile.open() as f:
                jdict = json.load(f)
            try:
                if self.entryclass:
                    self.data[jdict["id"]] = self.entryclass(**jdict)
            except Exception as e:
                print(f"Failed on {jsonfile}\n{e}")
        self.eng_preferred_label_dict: defaultdict = defaultdict(list)
        self.eng_alternate_label_dict: defaultdict = defaultdict(list)
        for entityid in self.data:
            # split is a hack to dropo post-name qualifiers
            preflabel = self[entityid].localizations["eng"]["preferred_label"].split(" ")[0]
            altlabels = self[entityid].localizations["eng"].get("alternate_labels", [])
            if upcase:
                preflabel = preflabel.upper()
                altlabels = [label.upper() for label in altlabels]
            self.eng_preferred_label_dict[preflabel].append(entityid)
            for label in altlabels:
                self.eng_alternate_label_dict[label].append(entityid)

    def acai_uri(self, identifier: str) -> str:
        """Return a string for the Github repo location for identifier."""
        nsp, name = identifier.split(":")
        return f"{self.repodata}/{self.acaidir}/json/acai/{name}.json"

    def acai_md_link(self, identifier: str) -> str:
        """Return a Markdown link to the JSON file for identifier."""
        uri = self.acai_uri(identifier)
        return f"[{identifier}]({uri})"

    def references_by_type(self, identifier: str) -> dict[str, list[str]]:
        """Return all the references for an entity, grouped by type."""
        reftypes = [
            # note these overlap with other reference types
            "key_references",
            "references",
            "explicit_instances",
            "pronominal_referents",
            "subject_referents",
        ]
        return {reftype: getattr(self[identifier], reftype) for reftype in reftypes}

    def word_references_by_type(self, identifier: str) -> dict[str, list[str]]:
        """Return all the word-level references for an entity, grouped by type."""
        bcvwpreftypes = [
            "explicit_instances",
            "pronominal_referents",
            "subject_referents",
        ]
        return {
            reftype: references
            for reftype, references in self.references_by_type(identifier).items()
            if reftype in bcvwpreftypes
        }


class DeitiesReader(EntityReader):
    """Read Deities data."""

    acaidir = "deities"
    jsondir = ACAIROOT / acaidir / "json"
    entryclass = AcaiDeity


class GroupsReader(EntityReader):
    """Read Groups data."""

    acaidir = "groups"
    jsondir = ACAIROOT / acaidir / "json"
    entryclass = AcaiGroup


class PeopleReader(EntityReader):
    """Read People data."""

    acaidir = "people"
    jsondir = ACAIROOT / acaidir / "json"
    entryclass = AcaiPerson


class PlacesReader(EntityReader):
    """Read Places data."""

    acaidir = "places"
    jsondir = ACAIROOT / acaidir / "json"
    entryclass = AcaiPlace


# class FaunaReader(EntityReader):
#     """Read Places data."""

#     acaidir = "fauna"
#     jsondir = ACAIROOT / acaidir / "json"
#     entryclass = AcaiFaunaEntry
