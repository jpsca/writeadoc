from jx import Component


class ColorScheme(Component):
    js = ("/assets/js/color-scheme.js",)

    def render(self) -> str:
        return self()
