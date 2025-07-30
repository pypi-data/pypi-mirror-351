"""Common code for rendering user displays of ACAI entity data (people, places, deities, groups).

This assumes the dataclasses in shared/shared_classes.
"""

from dataclasses import dataclass, field
import regex as re
from typing import Any

from biblelib.word import bcvwpid


@dataclass
class Entity:
    """A base class for rendering ACAI entities.

    This abstracts the shared_classes dataclasses for rendering via
    Flask and Jinja2 templates. The display is organized for English.

    """

    entity: Any
    id: str
    # pointer to primary id. If this *is* the primary, it matches the id field
    primary_id: str
    type: str
    subtype: str = ""
    preferred_label: str = ""
    alternate_labels: list = field(default_factory=list)
    # a list of acai_id pointing to respective entries
    referred_to_as: list = field(default_factory=list)
    # "apocrypha" == NRSV apocrypha only
    only_mentioned_in_apocrypha: bool = False
    # "non-biblical" == not in the Bible at all
    non_biblical: bool = False
    # key is description source, value is the description string
    descriptions: dict[str, str] = field(default_factory=dict)
    hebrew_lemmas: list = field(default_factory=list)
    greek_lemmas: list = field(default_factory=list)
    ubsdgnt: list = field(default_factory=list)
    ubsdbh: list = field(default_factory=list)
    key_references: list = field(default_factory=list)
    references: list = field(default_factory=list)
    # type-specific additional fields, as label/value pairs
    # must be formatted here so the template doesn't have to know about them
    extensions: dict[str, str] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Return a printed representation."""
        return f"<Entity: '{self.id}'>"

    @staticmethod
    def from_dataclass(entity: Any) -> "Entity":
        """Return an Entity instance from an ACAI dataclass."""

        # core functionality here ought to live in Biblelib
        def to_usfm(reflist: list[str]) -> list[str]:
            """Return references in USFM format."""
            return [bcvwpid.make_id(ref).to_usfm() for ref in reflist]

        def clean_description(description: str) -> str:
            """Return a cleaned-up description string.

            Removes HTML tags and special characters.

            """
            # regex to remove <..>
            clean_description: str = re.sub(r"<[^>]+>", "", description)
            clean_description = re.sub(r"\{[A-Z]+:([^}]+)}", r"\1", clean_description)
            clean_description = re.sub(r" *[◄►] *", " ", clean_description)
            clean_description = re.sub(r"\.\s*$", "", clean_description)
            return clean_description

        # doesn't look liek this gets the second level of
        # interpretation by Flask: probably another way
        # Also needs to handle _lists_ of identifiers.
        # def url_if_identifier(string: str) -> str:
        #     """Return an a element if string is an ACAI identifier.

        #     Otherwise just the string value.

        #     """
        #     entitytypes = {"deity", "group", "person", "place"}
        #     if ":" in string:
        #         typestr, _ = string.split(":")
        #         if typestr in entitytypes:
        #             urlforstr: str = f"url_for('identifierlookup', identifier='{string}')"
        #             return '<a href="{{  ' + urlforstr + '}}">'
        #         else:
        #             return string
        #     else:
        #         return string

        eng_localizations = entity.localizations.get("eng", {})
        eng_preferred_label: str = ""
        eng_alternate_labels: list[str] = []
        if eng_localizations:
            eng_descriptions = {
                desc["source"]: clean_description(desc["description"])
                for desc in eng_localizations.get("descriptions", {})
            }
            eng_preferred_label = eng_localizations.get("preferred_label", "")
            eng_alternate_labels = eng_localizations.get("alternate_labels", [])
        # add any type-specific extensions. Key is formatted for
        # display: values is used to retrieve the entity attribute.
        extensionsmap: dict[str, dict[str, str]] = {
            "deity": {
                "Related places": "related_places",
            },
            "group": {
                "Group origin": "group_origin",
            },
            "person": {
                "Gender": "gender",
                "Birthplace": "birth_place",
                "Death place": "death_place",
                "Father": "father",
                "Mother": "mother",
                "Partners": "partners",
                "Offspring": "offspring",
                "Siblings": "siblings",
                "Roles": "roles",
                "Related places": "related_places",
                "Possibly same as": "possibly_same_as",
            },
            "place": {
                "Possibly same as": "possibly_same_as",
                "Associated places": "associated_places",
                "Nearby places": "nearby_places",
                "Subregion of": "subregion_of",
            },
        }
        extensions: dict[str, str] = {
            label: attrval
            for label, attr in extensionsmap.get(entity.type, {}).items()
            if (attrval := getattr(entity, attr))
            if attrval
        }
        # need more to capture speeches for People
        subtype: str = ""
        if entity.type == "deity":
            subtype = entity.deity_type
        elif entity.type == "group":
            subtype = entity.group_type
        elif entity.type == "place":
            subtype = entity.place_types.get("acai", "")
        # elif entity.type == "person":
        #     subtype = entity.place_types.get("acai", "")
        return Entity(
            entity=entity,
            id=entity.id,
            primary_id=entity.primary_id,
            type=entity.type,
            subtype=subtype,
            # subtype=entity.subtype,
            preferred_label=eng_preferred_label,
            alternate_labels=eng_alternate_labels,
            referred_to_as=entity.referred_to_as,
            only_mentioned_in_apocrypha=entity.only_mentioned_in_apocrypha,
            non_biblical=entity.non_biblical,
            descriptions=eng_descriptions,
            hebrew_lemmas=entity.lemmas.get("he", {}),
            greek_lemmas=entity.lemmas.get("el", {}),
            ubsdbh=entity.ubsdbh,
            ubsdgnt=entity.ubsdgnt,
            key_references=to_usfm(entity.key_references),
            references=to_usfm(entity.references),
            extensions=extensions,
        )
