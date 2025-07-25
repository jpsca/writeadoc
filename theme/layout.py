from jx import Component

from .toc import Toc


class Layout(Component):
    components = [Toc]

    def render(self) -> str:
        return self()
