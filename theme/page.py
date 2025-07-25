from jx import Component

from .layout import Layout
from .toc import Toc


class Page(Component):
    components = [Layout, Toc]
    js = ("/assets/js/code.js", )

    def render(self) -> str:
        return self()
