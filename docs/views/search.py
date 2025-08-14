import json

from jx import Component
from writeadoc import TSearchData

from .layout import Layout
from .toc import Toc


class SearchPage(Component):
    components = [Layout, Toc]

    def render(self, search_data: TSearchData) -> str:
        return self(
            search_data=json.dumps(search_data, ensure_ascii=False, indent=2),
        )