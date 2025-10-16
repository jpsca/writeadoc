import pytest


@pytest.fixture
def tmp_root(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "content").mkdir()
    (tmp_path / "views").mkdir()
    (tmp_path / "views" / "page.jinja").write_text("""
<h1>{{ page.title }}</h1>
{{ page.content or content }}
""")
    return tmp_path
