"""Compute an importance score for ACAI entities.

This is a simple heuristic based on the number of times an entity is
mentioned, the distribution of those mentions, and other type-specific
factors.

The importance score is a floating point number between 0.0 and 1.0,
where 1.0 means maximally important. Scores are normalized within
entity type, but it is explicitly not guaranteed that the same
importance score for two different entity types means the same
thing. For example, a score of 0.5 for a person may not be comparable
to a score of 0.5 for a place.

>>> from acai.core import importance
"""

from collections import UserDict
from pathlib import Path
from typing import Sized

import numpy as np
import pandas as pd

from acailib import DATAPATH

from acailib.shared_classes import AcaiEntity


class BaseImportance(UserDict):
    """Base class for importance scores.

    This class is not intended to be used directly. Instead, use one of
    the subclasses for a specific entity type.

    """

    # a list of functions and the weights they contribute to the
    # overall score. Weights must sum to 1.0.
    factors: dict[str, float] = {}
    # the type of entity this importance score is for, e.g. "people",
    type: str = "UNDEFINED"

    def __init__(self) -> None:
        """Initialize the importance scores for a set of entities."""
        super().__init__()

    def __post_init__(self) -> None:
        """Check values after initialization."""
        assert (
            sum(self.factors.values()) == 1.0
        ), f"Weights must sum to 1.0, not {sum(self.factors.values())}."
        self.basepath: Path = DATAPATH / "adjunct" / self.type
        self.basepath.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _decrement_length_weight(
        items: Sized,
        # base_weight: float = 1.0, decrement: float = 0.2
    ) -> float:
        """Decrement the length weight of a list of items.

        The more items there are, the less important each additional one is.
        """
        total = 0.0
        for i in range(len(items)):
            # weight = max(base_weight - i * decrement, 0.0)
            # try an exponential decrement
            # weight = max(base_weight - i * decrement, 0.0)
            total += 1 / (i + 1)
        return total

    @staticmethod
    def normalize_to_unit_range(arr: np.ndarray) -> np.ndarray:
        """Normalize a numpy array to the range [0, 1].

        This is done by subtracting the minimum value and dividing by
        the range (max - min). If all values are the same, return an
        array of zeros.

        """
        arr = np.asarray(arr)
        min_val = np.min(arr)
        max_val = np.max(arr)
        if max_val == min_val:
            return np.zeros_like(arr)
        return (arr - min_val) / (max_val - min_val)

    # these methods are common to most entity types

    # not sure this is actually useful
    def biblical(self, entry: AcaiEntity) -> float:
        """Return 1.0 if non_biblical is False, else 0.0."""
        assert hasattr(entry, "non_biblical"), f"Entry {entry} must have 'non_biblical' attribute."
        return 1.0 if entry.non_biblical is False else 0.0

    def is_nt(self, entry: AcaiEntity) -> float:
        """Return 1.0 if referenced in the New Testament, else 0.0."""
        assert hasattr(entry, "references"), f"Entry {entry!r} must have 'references' attribute."
        bookrefset: set[int] = {int(ref[:2]) for ref in entry.references}
        if bookrefset:
            return 1.0 if (max({int(ref[:2]) for ref in entry.references}) >= 40) else 0.0
        else:
            return 0.0

    # not sure this is actually useful
    def nonapochryphal(self, entry: AcaiEntity) -> float:
        """Return 1.0 if only_mentioned_in_apocrypha is False, else 0.0."""
        assert hasattr(
            entry, "only_mentioned_in_apocrypha"
        ), f"Entry {entry!r} must have 'only_mentioned_in_apocrypha' attribute."
        return 1.0 if entry.only_mentioned_in_apocrypha is False else 0.0

    def n_book_references(self, entry: AcaiEntity) -> int:
        """Compute the number of book references for a person."""
        # if entry.id not in self.is_primary:
        #     allids = self.aliases[self.aliases[entry.id][0]]
        aliased_entries = self._get_aliased_entries(entry)
        return len({ref[:2] for ent in aliased_entries for ref in ent.references})

    def n_chapter_references(self, entry: AcaiEntity) -> int:
        """Compute the number of chapter references for a person."""
        aliased_entries = self._get_aliased_entries(entry)
        return len({ref[:4] for ent in aliased_entries for ref in ent.references})

    def n_key_references(self, entry: AcaiEntity) -> int:
        """Return the number of key references for a person."""
        aliased_entries = self._get_aliased_entries(entry)
        return len({ref for ent in aliased_entries for ref in ent.key_references})

    def n_verse_references(self, entry: AcaiEntity) -> int:
        """Compute the number of verse references for a person."""
        aliased_entries = self._get_aliased_entries(entry)
        return len({ref for ent in aliased_entries for ref in ent.references})
        # maybe i don't need this complexity
        # def _bcv(ref):
        #     """Convert a word-level reference to a book-chapter-verse string."""
        #     bcv = ref.split(".")
        #     if re.match(r"^[n|o]", ref):
        #         bcv = bcv[1:]
        #     return bcv[:8]

        # return len(
        #     set(
        #         entry.references
        #         + [_bcv(ref) for reflist in entry.pronominal_referents for ref in reflist]
        #         + [_bcv(ref) for reflist in entry.subject_referents for ref in reflist]
        #     )
        # )

    def compute_importance(self, row: pd.Series) -> float:
        """Compute the importance score for an entity.

        This is done by summing the weighted factors for the entity.

        """
        score = 0.0
        for factor, weight in self.factors.items():
            score += getattr(row, factor) * weight
        return score

    def write_tsv(self) -> None:
        """Write the importance scores to a TSV file.

        The file will contain the entity ID and the importance score.

        """
        outpath = self.basepath / f"{self.type}_importance.tsv"
        # sort by importance score
        self.entitydf = self.entitydf.sort_values("importance", ascending=False)
        self.entitydf.to_csv(outpath, sep="\t", index=True, header=True)
