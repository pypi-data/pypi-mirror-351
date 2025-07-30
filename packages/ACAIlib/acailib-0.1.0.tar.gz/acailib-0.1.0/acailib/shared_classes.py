"""Consolidate shared classes across entity types in acai/<entitytype>/shared/shared_classes.py.


The original code in acai/<entitytype>/shared/shared_classes.py has a
lot of duplication. This attempts to consolidate it into one place for
better maintainability.

This was constructed by copying the code from the various
entity-specific "shared/shared_classes.py" files into this file. I
checked people, places, deities, groups, and events, in that order. So
people/shared/shared_classes.py did most of the work. Note I did not
include the VizBible* classes or EntityDataEncode from that file.

Then i extracted common attributes into a base class AcaiEntity.

CAUTION: this means the original versions of these files could change,
until this gets synced with Rick's approach.

"""

from dataclasses import dataclass, field
import json as json
import re
from typing import Optional


# more preliminaries
@dataclass
class Localization:
    gloss: str
    short_definition: str = ""


@dataclass
class Identifier:
    identifier: str
    source: str


@dataclass
class LexicalSense:
    index: str
    source: str
    lemmas: list = field(default_factory=list)
    localizations: dict[str, Localization] = field(default_factory=dict)
    # glosses: list= field(default_factory=list)  # a list of LexicalGloss objects
    # short_definitions: list= field(default_factory=list) # a list of ShortDefinition objects


@dataclass
class EntityData:
    entity_class: str  # 'person' or 'place' or perhaps 'deity' (?)
    language: str  # but maybe a list because heb/aram?
    ubsdbh: str = ""
    ubsdgnt: str = ""
    lexical_sense: Optional[LexicalSense] = None
    lemmas: list = field(default_factory=list)
    segment_identifiers: dict[str, list] = field(default_factory=dict)  # a dict[edition, list<str>]
    pronominal_referents: dict[str, list] = field(
        default_factory=dict
    )  # a dict[edition, list<str>]
    subject_referents: dict[str, list] = field(default_factory=dict)  # a dict[edition, list<str>]


@dataclass
class AlternateSources:
    aquifer: list = field(default_factory=list)
    obi: list = field(default_factory=list)
    ubsdgnt: list = field(default_factory=list)
    ubsdbh: list = field(default_factory=list)
    ubsfauna: list = field(default_factory=list)
    ubsflora: list = field(default_factory=list)
    ubsrealia: list = field(default_factory=list)
    # biblemapper: list = field(default_factory=list)
    digital_atlas_roman_empire: list = field(default_factory=list)
    # using OBI factbook data does not work (logos changed schema?)
    # faithlife_factbook: list = field(default_factory=list)
    geonames: list = field(default_factory=list)
    pleiades: list = field(default_factory=list)
    tipnr: list = field(default_factory=list)
    vizbible: list = field(default_factory=list)
    wikidata: list = field(default_factory=list)
    wikipedia: list = field(default_factory=list)

    def __post_init__(self) -> None:
        """Ensure values are valid."""
        if self.aquifer:
            assert isinstance(self.aquifer, list), "aquifer must be a list"
            for item in self.aquifer:
                assert (
                    len(item.split("|")) == 3
                ), "aquifer items must be in the format 'id|name|source'"
        if self.ubsdgnt:
            assert isinstance(self.ubsdgnt, list), "ubsdgnt must be a list"
            for item in self.ubsdgnt:
                assert re.match(r"^\d+\.\d+[0-9]+$", item), "UBSDGNT code must match 'nn.nn' format"
        # others also need testing


@dataclass
class AcaiEntity:
    """Base class for all ACAI entities."""

    # type + identifier
    id: str
    # pointer to primary id. If this *is* the primary, it matches the id field
    primary_id: str
    alternate_sources: AlternateSources = field(default_factory=AlternateSources)
    # represents the entity class, e.g. "person", "place", "deity", "group", "event"
    # overwritten in subclasses
    type: str = ""
    # list of UBS DGNT identifiers
    ubsdgnt: list[str] = field(default_factory=list)
    # list of UBS DBH identifiers
    ubsdbh: list[str] = field(default_factory=list)
    # key is lang, dict inside has up to three entries: preferred label, alt labels, and description
    localizations: dict[str, dict[str, list]] = field(default_factory=dict)
    # list of ids for entities that are possible the same as this one
    possibly_same_as: list[str] = field(default_factory=list)
    # list of ids pointing to respective entries
    referred_to_as: list[str] = field(default_factory=list)
    # True if only mentioned in the NRSV apocrypha
    only_mentioned_in_apocrypha: bool = False
    # True if not mentioned in the Bible
    non_biblical: bool = False
    # short list of the most important BCVID string references in ORG versification
    key_references: list = field(default_factory=list)
    # exhaustive list of BCVID string references in ORG versification
    references: list = field(default_factory=list)
    # dict[edition, list<BCVWPID>]
    explicit_instances: dict[str, list] = field(default_factory=dict)
    # dict[edition, list<BCVWPID>] for pronominal references
    pronominal_referents: dict[str, list] = field(default_factory=dict)
    # dict[edition, list<BCVWPID>] for subject references
    subject_referents: dict[str, list] = field(default_factory=dict)
    # dict[edition, list<BCVWPID>] if there are any entities of this type that speak
    speeches: dict[str, list] = field(default_factory=dict)
    # lang: list<str> (list of lemmas in lang)
    lemmas: dict[str, list] = field(default_factory=dict)
    _valid_types: tuple[str, ...] = (
        "realia",
        "flora",
        "fauna",
        "person",
        "place",
        "deity",
        "group",
        "event",
    )

    def __post_init__(self) -> None:
        """Ensure values are valid."""
        if not isinstance(self.id, str):
            raise TypeError(f"id must be a string, got {type(self.id)}")
        if not isinstance(self.primary_id, str):
            raise TypeError(f"primary_id must be a string, got {type(self.primary_id)}")
        assert (
            self.type in self._valid_types
        ), f"type must be one of {self._valid_types}, got {self.type}"
        if self.ubsdgnt:
            assert isinstance(self.ubsdgnt, list), "ubsdgnt must be a list"
            for item in self.ubsdgnt:
                assert re.match(r"^\d+\.\d+[0-9]+$", item), "UBSDGNT code must match 'nn.nn' format"
        if self.localizations and "eng" in self.localizations:
            assert isinstance(
                self.localizations["eng"], dict
            ), "localizations['eng'] must be a dict"
            assert (
                "preferred_label" in self.localizations["eng"]
            ), "localizations['eng'] must contain 'preferred_label'"
        if self.referred_to_as:
            assert isinstance(self.referred_to_as, list), "referred_to_as must be a list"
            for item in self.referred_to_as:
                assert ":" in item, "referred_to_as items must be in the format 'type:id'"
        assert isinstance(
            self.only_mentioned_in_apocrypha, bool
        ), "only_mentioned_in_apocrypha must be a boolean"
        assert isinstance(self.non_biblical, bool), "non_biblical must be a boolean"

    def __repr__(self) -> str:
        """String representation of the entity."""
        return f"Acai{self.type.capitalize()}(id={self.id}, primary_id={self.primary_id})"


@dataclass(repr=False)
class AcaiRealia(AcaiEntity):
    type: str = "realia"
    realia_type: str = "other"


@dataclass(repr=False)
class AcaiFlora(AcaiEntity):
    type: str = "flora"
    flora_type: str = "other"


@dataclass(repr=False)
class AcaiFauna(AcaiEntity):
    type: str = "fauna"
    # save the fauna_type until UBS fauna dict becomes open
    fauna_type: str = "other"


@dataclass(repr=False)
class AcaiGroup(AcaiEntity):
    type: str = "group"
    group_type: str = (
        "other"  # default is 'other'; other values: 'residence', 'relation', or 'religious'
    )
    group_origin: str = ""  # id of person or place group derives from, when known


@dataclass(repr=False)
class AcaiDeity(AcaiEntity):
    type: str = "deity"
    deity_type: str = (
        "deity"  # could be 'angel' or 'demon' or 'deity' or 'other'. 'deity' is default
    )
    # gender: str = "" # 'male', 'female', 'deity'; # vizbible
    # birth_place: str = "" # vizbible
    # death_place: str = "" # vizbible
    # father: str = "" # vizbible 'father'
    # mother: str = "" # vizbible 'mother'
    # partners: list = field(default_factory=list) # vizbible 'partners'
    # offspring: list = field(default_factory=list) # vizbible 'children'
    # siblings: list = field(default_factory=list) # vizbible
    related_places: dict[str, list] = field(default_factory=dict)  # reason, list of place:id
    # mentioned_in_bible: bool = True # "bible" == entire NRSV (ot, nt, apocrypha)


@dataclass(repr=False)
class AcaiPerson(AcaiEntity):
    type: str = "person"
    gender: str = ""  # 'male', 'female', 'deity'; # vizbible
    birth_place: str = ""  # vizbible
    death_place: str = ""  # vizbible
    father: str = ""  # vizbible 'father'
    mother: str = ""  # vizbible 'mother'
    partners: list = field(default_factory=list)  # vizbible 'partners'
    offspring: list = field(default_factory=list)  # vizbible 'children'
    siblings: list = field(default_factory=list)  # vizbible
    roles: list = field(default_factory=list)  # curation
    tribe: str = ""  # tipnr 'tribe' mapped to ACAI group identifier
    related_places: dict[str, list] = field(default_factory=dict)  # reason, list of place:id
    # associated_places: list = field(default_factory=list) # list of acai_id
    # mentioned_in_bible: bool = True # "bible" == entire NRSV (ot, nt, apocrypha)
    # is_artifact: bool = False
    # is_person: bool = False
    # added_entry: bool = False
    # will there be person types? roles?
    # place_types: dict[str, list] = field(default_factory=dict) # key is source, list of types in source


@dataclass(repr=False)
class AcaiPlace(AcaiEntity):
    type: str = "place"
    tribal_area: str = ""
    associated_places: list = field(default_factory=list)  # list of acai_id
    nearby_places: list = field(default_factory=list)  # list of acai_id
    subregion_of: list = field(default_factory=list)  # list of acai_id
    mentioned_in_bible: bool = True  # "bible" == entire NRSV (ot, nt, apocrypha)
    is_artifact: bool = False
    is_person: bool = False
    added_entry: bool = False
    place_types: dict[str, list] = field(
        default_factory=dict
    )  # key is source, list of types in source
    geocoordinates: dict[str, dict[str, str]] = field(default_factory=dict)  # unsure of type


@dataclass
class LocationInfo:
    obi_id: str
    obi_friendly_id: str
    obi_names: list = field(default_factory=list)
    # obi = openbibleinfo
    obi_types: list = field(default_factory=list)
    obi_references: list = field(default_factory=list)
    # add possibly_same_as ? Are these even needed if there are SDBH and SDBG alternate entries?
    ubsdgnt: list = field(default_factory=list)
    ubsdbh: list = field(default_factory=list)
    # lists or objects?
    digital_atlas_roman_empire: list = field(default_factory=list)
    # using OBI factbook data does not work (logos changed schema?)
    # faithlife_factbook: list = field(default_factory=list)
    pleiades: list = field(default_factory=list)
    tipnr: list = field(default_factory=list)
    wikidata: list = field(default_factory=list)
    wikipedia: list = field(default_factory=list)
