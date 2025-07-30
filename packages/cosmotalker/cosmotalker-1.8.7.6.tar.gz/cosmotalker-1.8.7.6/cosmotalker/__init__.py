from .image import image
from .get import get
from .spacex import spacex
from .search import search
from .apod import apod
from .celestrak import celestrak
from .feedback import feedback
from .chat import chat
from .wiki import wiki
try:
    from cosmotalker.img_db import img
except ImportError:
    raise ImportError("cosmotalker.img_db is required. Please upgrade to cosmotalker >= 1.8.7.5")
