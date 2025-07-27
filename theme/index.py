from jx import Component

from .layout import Layout


class IndexPage(Component):
    components = [Layout]
    css = ("/assets/css/index.css", )
    js = ("/assets/js/video.js", "/assets/js/code.js")

    def render(self) -> str:
        return self()
