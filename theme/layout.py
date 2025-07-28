from jx import Component

from .color_scheme import ColorScheme
from .toc import Toc


class Layout(Component):
    components = [ColorScheme, Toc]

    def render(self) -> str:
        return self()
