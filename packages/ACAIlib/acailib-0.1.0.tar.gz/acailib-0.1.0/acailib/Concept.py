"""Base class for ACAI entities (people, places, etc.)"""

from dataclasses import asdict, dataclass, field
from enum import Enum

# TODO: enumerate a set of ACAI types


@dataclass
class Localization:
    """Localization data for an ACAI entity."""

    # values should be in acai.TargetLanguageCodes
    langcode: str
    preferred_label: str
    description: str
    alternate_labels: list = field(default_factory=list)
    # optional: where this information came from
    source: str = ""
    # optional: English gloss
    eng_gloss: str = ""


@dataclass
class LexicalRelation:
    """Manages a link to lexical content like UBSDGH/GNT."""

    # what kind of relation: Greek, Hebrew, other?
    # this should probably be an enumeration
    type: str
    # identifier for the lexical content
    lexicaluri: str


@dataclass
class EquivalenceRelation:
    """Manages a link to equivalent content describing this entity."""

    # what kind of relation: article, definition,
    # this should probably be an enumeration
    type: str
    # identifier for the lexical content
    # the namespace identifies the article source, like tynbd
    equivalenceuri: str


# To be deprecated
class ImageRelationType(str, Enum):
    """Enumerate types for image relations.

    Don't confuse this with the _subject_ of an image. This captures
    the image medium or type. Unlike e.g. Dublin Core `Image`, this
    does not include videos. The vast majority of UBS images are
    'photograph' or 'drawing', with an occaional 'painting'.

    Incorporates ideas from Schema.org's CreativeWork type, though not
    identical.

    """

    # "A picture or diagram made with a pencil, pen, or crayon rather than paint."
    DRAWING = "drawing"
    INFOGRAPHIC = "infographic"
    MAP = "map"
    PAINTING = "painting"
    PHOTOGRAPH = "photograph"
    # a la Logos
    FAMILYDIAGRAM = "family tree diagram"


class ImageType(str, Enum):
    """Enumerate types for image relations.

    Don't confuse this with the _subject_ of an image. This captures
    the image medium or type. Unlike e.g. Dublin Core `Image`, this
    does not include videos. The vast majority of UBS images are
    'photograph' or 'drawing', with an occaional 'painting'.

    Incorporates ideas from Schema.org's CreativeWork type, though not
    identical.

    """

    # "A picture or diagram made with a pencil, pen, or crayon rather than paint."
    DRAWING = "drawing"
    INFOGRAPHIC = "infographic"
    MAP = "map"
    PAINTING = "painting"
    PHOTOGRAPH = "photograph"
    # a la Logos
    FAMILYDIAGRAM = "family tree diagram"
    # also
    # TIMELINE
    # TABLE
    # SCULPTURE
    # WOODCUT
    # CARTOON: a drawing in a particular style
    # maybe later
    # 3D model
    # POSTER


# To be deprecated
@dataclass
class ImageRelation:
    """Manages a link to an image depicting this entity."""

    # what kind of image: photo, map, infographic, art, line drawing, family tree diagram
    # site plan, timeline
    # this should probably be an enumeration
    type: ImageRelationType
    # identifier for the lexical content
    # the namespace identifies the article source, like tynbd
    imageuri: str

    def asdict(self) -> dict:
        return {
            "type": self.type.value,
            "imageuri": self.imageuri,
        }


@dataclass
class BaseRecord:
    """Base class with common attributes for ACAI data records, including concepts.

    Other code should subclass this. This should not include type-specific attributes.
    """

    # <namespace>:<identifier>
    id: str
    # defined
    type: str = ""
    subtype: str = ""
    localizations: list[Localization] = field(default_factory=list)
    equivalence_relations: list[LexicalRelation] = field(default_factory=list)
    # list of BCVID/BCVWPID strings: select a few references that are
    # most important for the concept
    key_references: list = field(default_factory=list)
    # comprehensive list of references
    references: list = field(default_factory=list)


@dataclass
class Concept(BaseRecord):
    """Base class with common attributes for ACAI entities.

    Other code should subclass this. This doesn't include type-specific attributes.
    """

    # pointer to primary id. If this *is* the primary, it matches the
    # id field. This is for collecting several records together under
    # a main identifier.
    primary_id: str = ""
    # defined
    type: str = "person"  # for places, the only type is "place"
    lexical_relations: list[LexicalRelation] = field(default_factory=list)
    image_relations: list[ImageRelation] = field(default_factory=list)

    # # links to other entites or concepts that are fundamentally the same
    # same_as: list = field(default_factory=list)
    # possibly_same_as: list = field(default_factory=list)
    # # not sure about this
    # # referred_to_as: list = field(default_factory=list) # a list of acai_id pointing to respective entries
    # only_mentioned_in_apocrypha: bool = False  # "apocrypha" == NRSV apocrypha only
    # non_biblical: bool = False
    # lemmas: dict[str, list] = dataclasses.field(
    #     default_factory=dict
    # )  # lang: list<str> (list of lemmas in lang)
    # # will there be person types? roles?
    # # place_types: dict[str, list] = dataclasses.field(default_factory=dict) # key is source, list of types in sou

    def asdict(self) -> dict:
        """Return a dict for serialization."""
        return {
            "id": self.id,
            "primary_id": self.primary_id,
            "type": self.type,
            "localizations": [asdict(obj) for obj in self.localizations],
            "lexical_relations": [asdict(obj) for obj in self.lexical_relations],
            "equivalence_relations": [asdict(obj) for obj in self.equivalence_relations],
            "image_relations": [obj.asdict() for obj in self.image_relations],
            "key_references": self.key_references,
            "references": self.references,
        }
