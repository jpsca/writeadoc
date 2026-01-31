import argparse
import datetime
import json
import re
import shutil
import signal
import typing as t
from multiprocessing import Process
from pathlib import Path
from tempfile import mkdtemp

# from textwrap import dedent
import jx
from markupsafe import Markup

from . import utils
from .pages import PagesProcessor
from .types import PageData, SiteData
from .utils import get_random_messages, logger


class Docs:
    pages: list[str | dict[str, t.Any]]
    site: SiteData
    prefix: str = ""
    variants: "dict[str, Docs]"
    is_main: bool = True
    skip_home: bool = False

    strings: dict[str, str]
    catalog: jx.Catalog

    root_dir: Path
    content_dir: Path
    assets_dir: Path
    views_dir: Path
    build_dir: Path

    debug: bool = False

    def __init__(
        self,
        root: str,
        /,
        *,
        pages: list[str | dict[str, t.Any]],
        site: dict[str, t.Any] | None = None,
        prefix: str = "",
        variants: "dict[str, Docs] | None" = None,
        skip_home: bool = False,
    ):
        """
        Initialize the Docs object.

        Arguments:
            root: The root folder of the documentation project.
            pages: The user-defined pages structure.
            site: The site metadata.
            prefix: The URL prefix for the documentation.
            variants: A dictionary of documentation variants.
            skip_home: Whether to skip generating the home page.

        """
        root_dir = Path(root).resolve()
        if root_dir.is_file():
            root_dir = root_dir.parent
        if not root_dir.exists():
            raise FileNotFoundError(f"Path {root} does not exist.")
        self.root_dir = root_dir
        self.content_dir = root_dir / "content"
        self.assets_dir = root_dir / "assets"
        self.views_dir = root_dir / "views"
        self.archive_dir = root_dir / "archive"
        self.build_dir = root_dir / "build"

        self.pages = pages
        self.site = SiteData(**(site or {}))
        self.prefix = prefix.strip("/").strip()
        self.skip_home = skip_home

        variants = variants or {}
        for prefix, variant in variants.items():
            variant.content_dir = self.content_dir / prefix
            variant.prefix = f"{self.prefix}/{prefix}" if self.prefix else prefix
            variant.is_main = False
        self.variants = variants

        self.pages_processor = PagesProcessor(self)

        self.catalog = jx.Catalog(
            site=self.site,
            docs=self,
            _=self.translate,
            _now=datetime.datetime.now(tz=datetime.timezone.utc),
            _insert_asset=self.insert_asset,
        )

    def init_catalog(self):
        strings_file = self.views_dir / "strings.json"
        if strings_file.exists():
            strings_data = json.loads(strings_file.read_text())
            self.strings = strings_data.get(self.site.lang, {})
        else:
            self.strings = {}

        self.catalog.add_folder(self.views_dir)

    def cli(self):
        print()
        parser = argparse.ArgumentParser(description="WriteADoc CLI")
        subparsers = parser.add_subparsers(dest="command")

        subparsers.add_parser("run", help="Run and watch for changes")

        build_parser = subparsers.add_parser("build", help="Build the documentation for deployment")
        build_parser.add_argument(
            "--archive",
            action="store_true",
            default=False,
            help="Build the current version as an archived documentation"
        )
        build_parser.add_argument(
            "--llm",
            action="store_true",
            default=False,
            help=f"Generate a `{self.site.name}.txt` file with all the markdown content",
        )

        args = parser.parse_args()

        if args.command == "build":
            self.cli_build(archive=args.archive, llm=args.llm)
        elif args.command in (None, "run"):
            self.cli_run()
        else:
            parser.print_help()

    def cli_run(self) -> None:
        """Run the documentation server and watch for changes.
        """
        self.build_dir = Path(mkdtemp(prefix="wad-"))
        for variant in self.variants.values():
            variant.build_dir = self.build_dir

        self.build()  # Initial build
        p = Process(
            target=utils.start_server,
            args=(str(self.build_dir),),
            daemon=True
        )
        p.start()
        utils.start_observer(self.root_dir, self.build)

        def shutdown(*args):
            p.terminate()
            p.join()
            exit(0)

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

    def cli_build(self, *, archive: bool, llm: bool = False) -> None:
        """Build the documentation for deployment.
        """
        if archive:
            self.build_dir = self.archive_dir
            self.prefix = f"{self.prefix}/{self.site.version}" if self.prefix else self.site.version
            self.site.archived = True
        else:
            self.build_dir = self.root_dir / "build"

        for prefix, variant in self.variants.items():
            variant.build_dir = self.build_dir
            variant.prefix = f"{self.prefix}/{prefix}" if self.prefix else prefix

        self.build(devmode=False, llm=llm)
        print("\nDocumentation built successfully.")
        if archive:
            print(f"Archived documentation is available in the `archive/{self.site.version}` folder.")
        else:
            print("Documentation is available in the `build` folder.")

    def build(self, *, devmode: bool = True, llm: bool = False) -> None:
        messages = get_random_messages(3)
        print(f"{messages[0]}...")

        for variant in self.variants.values():
            variant.build(devmode=devmode, llm=llm)

        self.init_catalog()

        print("Processing pages...")
        nav, pages = self.pages_processor.run(self.pages)
        print(f"{messages[1]}...")

        self.site.nav = nav
        self.site.pages = pages

        if self.prefix and not self.site.base_url.endswith(f"/{self.prefix}"):
            self.site.base_url = f"{self.site.base_url}/{self.prefix}"

        print("Rendering pages...")
        for page in pages:
            self._render_page(page)
        print(f"{messages[2]}...")

        if llm:
            print(f"Building {self.site.name}.txt...")
            self._render_llm_file()

        self._render_search_page()
        self._render_redirect_pages()
        self._add_prefix_to_urls()

        if self.is_main:
            self._render_extra()
            if devmode:
                self._symlink_assets()
            else:
                print("Copying assets...")
                self._copy_assets()
                print("Fingerprinting assets URLs...")
                self._fingerprint_assets()

    def translate(self, key: str, **kwargs) -> str:
        """
        Translate a key using the strings dictionary.
        If the key does not exist, return the key itself.
        """
        string = self.strings.get(key, key)
        return string.format(**kwargs)

    def insert_asset(self, asset: str) -> str:
        """
        Read the asset and return the content
        """
        asset_path = self.assets_dir / asset
        if asset_path.exists():
            return Markup(asset_path.read_text(encoding="utf-8").strip())
        return ""

    def log(self, *args: t.Any) -> None:
        if self.debug:
            print(" ".join(str(arg) for arg in args))

    # Private

    def _render_page(self, page: PageData) -> None:
        outpath = self.build_dir / str(page.url).strip("/") / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)

        try:
            html = self.catalog.render(
                page.view,
                globals={"page": page}
            )
        except jx.JxException as err:
            raise RuntimeError(f"Error rendering {page.filepath}") from err
        outpath.write_text(html, encoding="utf-8")
        self.log(outpath)

    def _render_search_page(self) -> None:
        if not (self.views_dir / "search.jinja").exists():
            logger.warning("No search.jinja view found.")
            return None

        outpath = self.build_dir / self.prefix / "search" / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        url = f"/{self.prefix}/search/" if self.prefix else "/search/"

        page = PageData(
            url=url,
            meta={
                "id": "search",
                "title": "Search",
                "view": "search.jinja",
            },
        )
        search_data = {}
        for p in self.site.pages:
            search_data.update(p.search_data or {})

        try:
            html = self.catalog.render(
                page.view,
                search_data=search_data,
                globals={"page": page}
            )
        except jx.JxException as err:
            raise RuntimeError("Error rendering search page") from err
        outpath.write_text(html, encoding="utf-8")
        self.log(outpath)

    def _render_redirect_pages(self) -> None:
        if len(self.site.pages) < 2:
            # The "first" page is the next one after the index page, if any
            return

        # Use the first page as the redirect target
        url = self.site.pages[1].url
        html = (
            '<!DOCTYPE html><html><head><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0; url={url}">'
            "<title></title></head><body></body></html>"
        )

        outpath = self.build_dir / self.prefix / "docs" / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        outpath.write_text(html, encoding="utf-8")
        self.log(outpath)

        if self.skip_home:
            outpath = self.build_dir / self.prefix / "index.html"
            outpath.write_text(html, encoding="utf-8")
            self.log(outpath)

    def _render_extra(self) -> None:
        for file in (
            "sitemap.xml",
            "robots.txt",
            "humans.txt"
        ):
            outpath = self.build_dir / self.prefix / file
            outpath.parent.mkdir(parents=True, exist_ok=True)
            try:
                body = self.catalog.render(f"{file}.jinja")
            except jx.ImportError:
                logger.info("No view found for %s, skipping...", file)
                continue
            outpath.write_text(body, encoding="utf-8")
            self.log(outpath)

    def _render_llm_file(self) -> None:
        outpath = self.build_dir / self.prefix / f"{self.site.name}.txt"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        try:
            body = self.catalog.render("llm.jinja")
        except jx.JxException as err:
            raise RuntimeError(f"Error rendering {self.site.name}.txt") from err
        outpath.write_text(body, encoding="utf-8")
        self.log(outpath)

    def _add_prefix_to_urls(self) -> None:
        """Update URLs in the site data for archived documentation."""
        if not self.prefix:
            return

        folders = "docs|assets|search" if self.is_main else "docs|search"
        rx_urls = re.compile(fr"""(href|src|action|poster|data|srcset|data-src)=("|')/({folders})/""")

        build_dir = self.build_dir / self.prefix
        for html_file in build_dir.rglob("*.html"):
            content = html_file.read_text()

            def replace_url(match: re.Match) -> str:
                attr = match.group(1)
                quote = match.group(2)
                url = match.group(3)
                return f"{attr}={quote}/{self.prefix}/{url}/"

            new_content = rx_urls.sub(replace_url, content)
            html_file.write_text(new_content)

    def _symlink_assets(self) -> None:
        if not self.assets_dir.exists():
            return
        target_path = self.build_dir / self.prefix / "assets"
        if target_path.is_symlink():
            target_path.unlink()
        elif target_path.exists():
            shutil.rmtree(target_path)

        target_path.symlink_to(self.assets_dir)

    def _copy_assets(self) -> None:
        if not self.assets_dir.exists():
            return
        target_path = self.build_dir / self.prefix / "assets"
        shutil.copytree(
            self.assets_dir,
            target_path,
            dirs_exist_ok=True,
        )

    def _fingerprint_assets(self) -> None:
        """Add fingerprinting to asset files for cache busting."""
        assets_path = self.build_dir / self.prefix / "assets"
        if not assets_path.exists():
            return

        fingerprints = {}

        for asset_file in assets_path.rglob("*.*"):
            if asset_file.is_file():
                mtime = int(asset_file.stat().st_mtime)
                fingerprint = f"{mtime:x}"
                old_name = asset_file.relative_to(assets_path)
                new_name = f"{old_name}?v={fingerprint}"
                fingerprints[old_name] = new_name
                print(f"Fingerprinting {old_name} -> {new_name}")

        # Update references in HTML files
        for html_file in (self.build_dir / self.prefix).rglob("*.html"):
            html_content = html_file.read_text()
            for old_name, new_name in fingerprints.items():
                html_content = (
                    html_content
                    .replace(f'href="/assets/{old_name}"', f'href="/assets/{new_name}"')
                    .replace(f'src="/assets/{old_name}"', f'src="/assets/{new_name}"')
                )
            html_file.write_text(html_content)
