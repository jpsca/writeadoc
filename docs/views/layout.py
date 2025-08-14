from jx import Component

from .color_scheme import ColorScheme
from .language_popover import LanguagePopover
from .toc import Toc
from .version_popover import VersionPopover


class Layout(Component):
    components = [ColorScheme, Toc, LanguagePopover, VersionPopover]

    def render(self) -> str:
        return self()
