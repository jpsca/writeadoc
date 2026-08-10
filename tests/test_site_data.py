import jx
import pytest
from jinja2 import UndefinedError

from writeadoc.types import NavItem, SiteData


class TestDeclaredAttributes:

    def test_defaults(self):
        site = SiteData()

        assert site.name == "WriteADoc"
        assert site.version == "1.0"
        assert site.lang == "en"
        assert site.base_url == ""
        assert site.description == ""
        assert site.source_code == ""

    def test_given_values_win(self):
        site = SiteData(name="Docs", version="2.5", lang="es")

        assert site.name == "Docs"
        assert site.version == "2.5"
        assert site.lang == "es"

    def test_trailing_slash_is_stripped_from_base_url(self):
        assert SiteData(base_url="https://example.test/").base_url == "https://example.test"

    def test_archived_is_build_state_not_configuration(self):
        """It is set by `cli_build`, so a value passed here is ignored."""
        assert SiteData(archived=True).archived is False

    def test_pages_and_nav_start_empty(self):
        site = SiteData()

        assert site.pages == []
        assert site.nav == []


class TestCustomAttributes:
    """Any other key is kept, which the docs describe as custom site metadata."""

    def test_custom_keys_are_readable(self):
        site = SiteData(name="Docs", twitter="@example", analytics_id="ABC123")

        assert site.twitter == "@example"
        assert site.analytics_id == "ABC123"

    def test_underscored_keys_are_ignored(self):
        site = SiteData(_private="nope")

        assert not hasattr(site, "_private")


class TestUnsetAttributes:
    """Reading something never set must fail, so typos surface at build time."""

    def test_reading_an_unset_attribute_raises(self):
        site = SiteData(name="Docs")

        with pytest.raises(AttributeError):
            site.nmae  # noqa: B018

    def test_hasattr_reports_it_missing(self):
        assert not hasattr(SiteData(), "whatever")

    def test_a_typo_in_a_view_fails_the_render(self):
        catalog = jx.Catalog()
        site = SiteData(name="Docs")

        rendered = catalog.render_string("{{ site.name }}", globals={"site": site})
        assert str(rendered) == "Docs"

        with pytest.raises(UndefinedError, match="no attribute 'nmae'"):
            catalog.render_string("{{ site.nmae }}", globals={"site": site})


class TestNavItem:

    def test_dict_serializes_the_tree(self):
        child = NavItem(title="Child", url="/docs/parent/child/")
        parent = NavItem(title="Parent", url="/docs/parent/", pages=[child])

        assert parent.dict() == {
            "id": "parent",
            "title": "Parent",
            "url": "/docs/parent/",
            "icon": "",
            "pages": [
                {
                    "id": "parent-child",
                    "title": "Child",
                    "url": "/docs/parent/child/",
                    "icon": "",
                    "pages": [],
                }
            ],
        }

    def test_an_item_without_a_url_gets_a_generated_id(self):
        item = NavItem(title="Section")

        assert len(item.id) == 32
