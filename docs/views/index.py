from jx import Component

from .layout import Layout


class IndexPage(Component):
    components = [Layout]
    css = ("/assets/css/index.css", )

    def render(self) -> str:
        return self()
