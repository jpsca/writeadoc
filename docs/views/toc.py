from jx import Component


class Toc(Component):

    def render(self, show_pages: bool = False) -> str:
        return self(
            show_pages=show_pages,
        )
