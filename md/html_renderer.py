import mistune

from .highlight import HighlightMixin


class HTMLRenderer(
    HighlightMixin,
    mistune.HTMLRenderer
):
    pass