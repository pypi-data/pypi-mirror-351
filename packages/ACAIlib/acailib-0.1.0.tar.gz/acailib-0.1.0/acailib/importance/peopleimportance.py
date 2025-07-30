"""Compute importance scores for people.

>>> from acai.core import peopleimportance
# this uses a magic formula to compute the importance score
>>> peoplei = peopleimportance.PeopleImportance()
>>> peoplei.entitydf.loc["person:Mary"]
family                  0.572278
is_nt                   1.000000
n_book_references       0.085106
n_chapter_references    0.049180
n_key_references        0.115385
n_verse_references      0.007761
roles                   0.093750
importance              0.131374
Name: person:Mary, dtype: float64

# write out the scores to a TSV file for easy access. If you upgrade
# the magic formula, you should probably rewrite the TSV
>>> peoplei.write_tsv()


"""

# other ideas:
# - a person is more important if their family members are important
#   (e.g. "person:Mary")

from collections import defaultdict

import numpy as np
import pandas as pd

from acailib.shared_classes import AcaiPerson
from acailib.util import EntityReader

from .baseimportance import BaseImportance


class PeopleImportance(BaseImportance):
    """Compute importance scores for people."""

    reader = EntityReader.PeopleReader()
    type = "people"

    def __init__(self) -> None:
        """Initialize the importance score."""
        super().__init__()
        self.factors = {
            # probably don't want to even consider entities that aren't biblical at all
            # "biblical": 0.05,
            "family": 0.05,
            "is_nt": 0.05,
            # ditto for biblical
            # "nonapochryphal": 0.05,
            "n_book_references": 0.15,
            # would be nice to have pericope references but chapters are easier to compute
            "n_chapter_references": 0.15,
            "n_key_references": 0.10,
            "n_verse_references": 0.30,
            "roles": 0.20,
        }
        self.__post_init__()
        # person:Simeon -> person:Peter (but not vice versa)
        self.directed_aliases: dict[str, str] = {}
        # person:Peter -> {person:Simeon, person:Peter, etc.}: all the aliases
        self.aliases: dict[str, set[str]] = defaultdict(set)
        for ent in self.reader.values():
            if ent.primary_id != ent.id:
                if ent.id in self.directed_aliases:
                    print(f"Duplicate alias {ent.id} for {ent.primary_id}")
                self.directed_aliases[ent.id] = ent.primary_id
                # this will collect _all_ the aliases for a given entity
                self.aliases[ent.primary_id].add(ent.primary_id)
                self.aliases[ent.primary_id].add(ent.id)
        # only work with the primary record: in theory we're
        # collecting all the related data for aliases below
        self.primarykeys = [k for k in self.reader.keys() if k not in self.directed_aliases]
        self.entitydf = pd.DataFrame(index=self.primarykeys)
        # add all the factors to the dataframe, normalizing the range
        for factor in self.factors:
            self.entitydf[factor] = self.normalize_to_unit_range(
                np.asarray([getattr(self, factor)(self.reader[pid]) for pid in self.entitydf.index])
            )
        # compute the overall importance score
        self.entitydf["importance"] = self.entitydf.apply(self.compute_importance, axis=1)

    def _get_aliased_entries(self, entry: AcaiPerson) -> list[AcaiPerson]:
        """Get all the entries for a given entity."""
        primaryid: str = entry.primary_id
        if entry.id in self.directed_aliases:
            primaryid = self.directed_aliases[entry.id]
        if primaryid in self.aliases:
            return [self.reader[alias] for alias in self.aliases[primaryid]]
        else:
            return [entry]

    # this might overemphasize OT people with extensive family mentions
    def family(self, entry: AcaiPerson) -> float:
        """Compute the weighted number of known family members.

        The intuition is that the number of family members mentioned
        for a person indicates something about their importance.

        Parents and offspring are weighted more heavily than siblings.

        """
        weight: float = 0.0
        # this assumes that all aliased entries have the same family attributes
        for close_relative in ["father", "mother", "partners", "tribe"]:
            if getattr(entry, close_relative):
                weight += 1
        if entry.siblings:
            # the decremented weight of the number of siblings
            weight += self._decrement_length_weight(entry.siblings) / 2
        if entry.offspring:
            # the decremented weight of the number of offspring
            weight += self._decrement_length_weight(entry.offspring) / 2
        return weight

    def roles(self, entry: AcaiPerson) -> float:
        """Compute the aggregate weight for the number of roles for a person.

        The more roles a person has, the more important they are.
        """
        roleweights = {
            "Angel": 5,
            "Apostle": 5,
            "Army Commander": 2,
            "Carpenter": 3,
            "Church Leader": 4,
            "Concubine": 1,
            "Deity": 5,
            "Disciple": 4,
            "Emperor": 3,
            "Evangelist": 3,
            "Fisher": 4,
            "Fisherman": 4,
            "God": 5,
            "Governor": 3,
            "High Priest": 3,
            "Hunter": 1,
            "Judge": 3,
            "King": 4,
            "Lawgiver": 1,
            "Lawyer": 1,
            "Leader": 2,
            "Martyr, ": 3,
            "Matriarch": 1,
            "Member of the Royal Family": 2,
            "Messiah": 5,
            "Military Commander": 2,
            "Missionary": 3,
            "Official": 3,
            "Patriarch": 3,
            "Priest": 3,
            "Prisoner": 2,
            "Prophet": 4,
            "Queen": 4,
            "Relative of Jesus": 3,
            "Royal Family Member": 3,
            "Ruler": 3,
            "Ruler of the Synagogue": 2,
            "Scribe": 2,
            "Servant": 2,
            "Shepherd": 1,
            "Singer": 1,
            "Slave": 1,
            "Son of Adam": 3,
            "Tax Collector": 2,
            "Teacher": 3,
            "Tent Maker": 1,
            "Tribal Chief": 3,
            "Warrior": 2,
            "Wife": 1,
        }
        aliased_entries = self._get_aliased_entries(entry)
        allroles = {role for ent in aliased_entries for role in ent.roles}
        return sum(roleweights.get(role, 0) for role in allroles)
