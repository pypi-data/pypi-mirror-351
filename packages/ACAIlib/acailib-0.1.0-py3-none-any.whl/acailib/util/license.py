"""Load external license data.

Not much validation required since this is a simple input file.

>>> from acai.util import license
>>> rd = license.TSVReader
>>> rd["CC0"]
License(license_id='CC0', license_url='https://creativecommons.org/publicdomain/zero/1.0/',
  attribution=False, sharealike=False, noderivs=False, noncommercial=False)
>>> [lic.license_id for lic in rd.values() if not lic.noncommercial]
['CC0', 'CC BY 1.0', 'CC BY-SA 1.0', 'CC BY-ND 1.0', ...]

"""

from pathlib import Path

from pydantic import BaseModel  # type: ignore

from acai import DATAPATH
from .TSVReader import TSVReader as tsvr


class License(BaseModel):
    """Manage data that is read in from file on a license.

    This should stay in sync with license.tsv.
    """

    license_id: str
    license_url: str
    attribution: bool
    sharealike: bool
    noderivs: bool
    noncommercial: bool


class TSVReader(tsvr):
    """Read TSV data into a dict.

    This is generalized for use where the source data is in TSV, with
    column headers that match a BaseModel instance, and a designated
    identity element.

    """

    # subs must define these
    tsvpath: Path = DATAPATH / "license.tsv"
    idattr: str = "license_id"
    model: BaseModel = License
