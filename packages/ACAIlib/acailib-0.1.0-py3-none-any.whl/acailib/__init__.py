"""Code for working with ACAI data."""

from enum import Enum
import os
from pathlib import Path

# the dotenv magic only works if your Python environment is running in
# the right directory
import dotenv

# use an environment variable if available
if not dotenv.load_dotenv():
    print("No .env file found")

# the root of Clear-Bible repositories
clearrootenvar = os.getenv("CLEARROOT")
if clearrootenvar:
    CLEARROOT = Path(clearrootenvar)
else:
    # guess if not defined in .env
    CLEARROOT = Path.home() / "git/Clear-Bible"
    print(f"No environment variable for CLEARROOT: assuming {CLEARROOT}")

# the root of a local copy of BibleAquifer/ACAI
# Currently you need this for loading data
acairootenvar = os.getenv("ACAIROOT")
if acairootenvar:
    ACAIROOT = Path(acairootenvar)
else:
    # guess if not defined in .env
    ACAIROOT = Path.home() / "git/BibleAquifer/ACAI"
    print(f"No environment variable for ACAIROOT: assuming {ACAIROOT}")


ROOT = Path(__file__).parent.parent
DATAPATH = ROOT / "data"


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class LangEnum(str, Enum):
    """Enumerate lang code values for biblical source languages."""

    aramaic = "arc"
    greek = "grc"
    hebrew = "hbo"


class TargetLanguageCodes(str, Enum):
    """Enumerate ISO-639-3 lang code values for target LWC languages."""

    ARABIC = "arb"
    BISLAMA = "bis"
    ENGLISH = "eng"
    FRENCH = "fra"
    HAUSA = "hau"
    HINDI = "hin"
    IGBO = "ibo"
    INDONESIAN = "ind"
    # Ethnologue lists several: is this the right one?
    MALAY = "pse"
    # not sure how to represent Traditional
    MANDARIN = "cmn"
    PORTUGUESE = "por"
    RUSSIAN = "rus"
    SPANISH = "spa"
    SWAHILI = "swa"
    TOK_PISIN = "tpi"
    VIETNAMESE = "vie"


class ContentType(str, Enum):
    """Enumerate types for images and other assets."""

    # from UBS Image data
    ILL = "illustration"
    IMG = "image"
    MAP = "map"
    # extensions
    PHOTO = "photo"


__all__ = [
    "LangEnum",
    "TargetLanguageCodes",
    "ContentType",
]

__all__ = [
    "CLEARROOT",
    "ACAIROOT",
    "ROOT",
    "DATAPATH",
    "OPENAI_API_KEY",
    "LangEnum",
    "TargetLanguageCodes",
    "ContentType",
]
