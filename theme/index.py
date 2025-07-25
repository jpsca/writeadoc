from jx import Component

from .layout import Layout


class IndexPage(Component):
    components = [Layout]
    js = ("/assets/js/video.js", "/assets/js/code.js")

    def render(self) -> str:
        return self()
