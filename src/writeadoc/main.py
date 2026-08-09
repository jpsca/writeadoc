import argparse
import datetime
import json
import re
import shutil
import signal
import typing as t
import warnings
from collections.abc import Sequence
from functools import partial
from multiprocessing import Process
from pathlib import Path
from tempfile import mkdtemp

# from textwrap import dedent
import jx
from jx.tools import check_all
from markupsafe import Markup

from .devserver import start_observer, start_server
from .links import get_prefixed_folders, validate_links
from .pages import PagesProcessor
from .types import Build, PageData, SiteData
from .utils import get_random_messages, logger


def warn_moved(old: str, new: str) -> None:
    """Warn that a `Docs` attribute moved onto the build object.

    `FutureWarning` rather than `DeprecationWarning` on purpose: the reader is
    running `python docs.py build`, and a `DeprecationWarning` raised from inside
    a template render is silent under the default filters, which would make the
    warning useless.
    """
    warnings.warn(
        f"`docs.{old}` is deprecated and will be removed in 0.29."
        f" Use `{new}` in a view, or `docs.build_target.{new.split('.')[1]}`"
        " in Python.",
        FutureWarning,
        stacklevel=3,
    )


class Docs:
    pages: Sequence[str | dict[str, t.Any]]
    site: SiteData
    build_target: Build
    variants: "dict[str, Docs]"
    is_main: bool = True
    skip_home: bool = False

    strings: dict[str, str]
    catalog: jx.Catalog

    root_dir: Path
    content_dir: Path
    assets_dir: Path
    views_dir: Path
    archive_dir: Path

    debug: bool = False

    def __init__(
        self,
        root: str,
        /,
        *,
        pages: Sequence[str | dict[str, t.Any]],
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

        self.pages = pages
        self.site = SiteData(**(site or {}))
        self.skip_home = skip_home

        self.variants = variants or {}
        for name, variant in self.variants.items():
            variant.content_dir = self.content_dir / name
            variant.is_main = False

        self.pages_processor = PagesProcessor(self)

        self.catalog = jx.Catalog(
            site=self.site,
            docs=self,
            _=self.translate,
            _now=datetime.datetime.now(tz=datetime.timezone.utc),
            _insert_asset=self.insert_asset,
        )
        self._set_build_target(
            build_dir=root_dir / "build",
            prefix=prefix.strip("/").strip(),
        )
        self.init_catalog()
        self.check_catalog()

    def _set_build_target(self, *, build_dir: Path, prefix: str) -> None:
        """Point this documentation, and its variants, at a build target.

        Variants are written into the same folder as their parent, under a prefix
        nested below the parent's. This is the only place that composes prefixes,
        so `_add_prefix_to_urls` and the views stay in agreement.
        """
        variants = {}
        for name, variant in self.variants.items():
            variant._set_build_target(
                build_dir=build_dir,
                prefix=f"{prefix}/{name}" if prefix else name,
            )
            variants[name] = variant.build_target

        self.build_target = Build(dir=build_dir, prefix=prefix, variants=variants)
        self.catalog.jinja_env.globals["build"] = self.build_target

    # Deprecated, removed in 0.29

    @property
    def prefix(self) -> str:
        """Deprecated. Use `build.prefix` in a view, `build_target.prefix` in Python."""
        warn_moved("prefix", "build.prefix")
        return self.build_target.prefix

    @prefix.setter
    def prefix(self, value: str) -> None:
        warn_moved("prefix", "build.prefix")
        self._set_build_target(build_dir=self.build_target.dir, prefix=value)

    @property
    def build_dir(self) -> Path:
        """Deprecated. Use `build.dir` in a view, `build_target.dir` in Python."""
        warn_moved("build_dir", "build.dir")
        return self.build_target.dir

    @build_dir.setter
    def build_dir(self, value: Path) -> None:
        warn_moved("build_dir", "build.dir")
        self._set_build_target(build_dir=value, prefix=self.build_target.prefix)

    def init_catalog(self):
        strings_file = self.views_dir / "strings.json"
        if strings_file.exists():
            strings_data = json.loads(strings_file.read_text())
            self.strings = strings_data.get(self.site.lang, {})
        else:
            self.strings = {}
        self.catalog.add_folder(self.views_dir)

    def check_catalog(self):
        print("\nValidating views...")
        errors, checked = check_all(self.catalog)
        for error in errors:
            print(f"{error.file}:{error.line} - {error.message}")

    def cli(self):
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
            help="Generate a `llms.txt` file with all the markdown content",
        )
        build_parser.add_argument(
            "--boring",
            action="store_true",
            default=False,
            help="Remove the random messages from the log output"
        )

        args = parser.parse_args()

        if args.command == "build":
            self.cli_build(archive=args.archive, llm=args.llm, boring=args.boring)
        elif args.command in (None, "run"):
            self.cli_run()
        else:
            parser.print_help()

    def cli_run(self) -> None:
        """Run the documentation server and watch for changes.
        """
        self._set_build_target(
            build_dir=Path(mkdtemp(prefix="wad-")),
            prefix=self.build_target.prefix,
        )

        self.build(devmode=True)  # Initial build
        print()
        p = Process(
            target=start_server,
            args=(str(self.build_target.dir),),
            daemon=True
        )
        p.start()
        start_observer(self.root_dir, partial(self.build, devmode=True))

        def shutdown(*args):
            p.terminate()
            p.join()
            exit(0)

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

    def cli_build(self, *, archive: bool, llm: bool = False, boring: bool = False) -> None:
        """Build the documentation for deployment.
        """
        if archive:
            version = self.site.version
            self._set_build_target(
                build_dir=self.archive_dir,
                prefix=f"{self.build_target.prefix}/{version}" if self.build_target.prefix else version,
            )
            self.site.archived = True
        else:
            self._set_build_target(
                build_dir=self.root_dir / "build",
                prefix=self.build_target.prefix,
            )

        self.build(devmode=False, llm=llm, boring=boring)
        print("\nDocumentation built successfully.")
        if archive:
            print(f"Archived documentation is available in the `archive/{self.site.version}` folder.")
        else:
            print("Documentation is available in the `build` folder.")

    def build(self, *, devmode: bool = True, llm: bool = False, boring: bool = False) -> None:
        if not boring:
            messages = get_random_messages(3)
            print(f"{messages[0]}...")

        for variant in self.variants.values():
            variant.build(devmode=devmode, llm=llm, boring=boring)

        print("Processing pages...")
        nav, pages = self.pages_processor.run(self.pages)
        if not boring:
            print(f"{messages[1]}...")

        self.site.nav = nav
        self.site.pages = pages

        if self.build_target.prefix and not self.site.base_url.endswith(f"/{self.build_target.prefix}"):
            self.site.base_url = f"{self.site.base_url}/{self.build_target.prefix}"

        print("Rendering pages...")
        for page in pages:
            self._render_page(page)
        if not boring:
            print(f"{messages[2]}...")

        if llm:
            print("Building llms.txt...")
            self._render_llm_file()

        self._render_search_page()
        self._render_redirect_pages()
        self._add_prefix_to_urls()
        self._validate_links()

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

    def _write(self, outpath: Path, content: str) -> None:
        """Write a generated file, creating its parent folders."""
        outpath.parent.mkdir(parents=True, exist_ok=True)
        outpath.write_text(content, encoding="utf-8")
        self.log(outpath)

    def _render_page(self, page: PageData) -> None:
        try:
            html = self.catalog.render(
                page.view,
                globals={"page": page}
            )
        except Exception as err:
            raise RuntimeError(f"Error rendering {page.filepath}") from err

        self._write(self.build_target.dir / str(page.url).strip("/") / "index.html", html)

    def _render_search_page(self) -> None:
        if not (self.views_dir / "search.jx").exists():
            logger.warning("No search.jx view found.")
            return None

        url = f"{self.build_target.base_url}search/"

        page = PageData(
            url=url,
            meta={
                "id": "search",
                "title": "Search",
                "view": "search.jx",
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

        self._write(self.build_target.out_dir / "search" / "index.html", html)

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

        self._write(self.build_target.out_dir / "docs" / "index.html", html)

        if self.skip_home:
            self._write(self.build_target.out_dir / "index.html", html)

    def _render_extra(self) -> None:
        for file in (
            "not_found.html",
            "sitemap.xml",
            "robots.txt",
            "humans.txt"
        ):
            url = f"{self.build_target.base_url}{file}"
            page = PageData(
                url=url,
                meta={
                    "id": file.split(".")[0],
                    "title": file.replace("_", " ").title(),
                },
            )
            try:
                body = self.catalog.render(
                    f"{file}.jx",
                    globals={"page": page}
                )
            except jx.ComponentNotFoundError:
                logger.info("No view found for %s, skipping...", file)
                continue

            self._write(self.build_target.out_dir / file, body)

    def _render_llm_file(self) -> None:
        try:
            body = self.catalog.render("llm.jx")
        except jx.JxException as err:
            raise RuntimeError("Error rendering llms.txt") from err

        self._write(self.build_target.out_dir / "llms.txt", body)

    def _add_prefix_to_urls(self) -> None:
        """Update URLs in the site data for archived documentation."""
        if not self.build_target.prefix:
            return

        folders = "|".join(get_prefixed_folders(prefix=self.build_target.prefix, is_main=self.is_main))
        rx_urls = re.compile(fr"""(href|src|action|poster|data|srcset|data-src)=("|')/({folders})/""")

        build_dir = self.build_target.out_dir
        for html_file in build_dir.rglob("*.html"):
            content = html_file.read_text()

            def replace_url(match: re.Match) -> str:
                attr = match.group(1)
                quote = match.group(2)
                url = match.group(3)
                return f"{attr}={quote}/{self.build_target.prefix}/{url}/"

            new_content = rx_urls.sub(replace_url, content)
            html_file.write_text(new_content)

    def _validate_links(self) -> None:
        warnings = validate_links(
            self.site.pages,
            content_root=self.root_dir / "content",
            assets_dir=self.assets_dir,
            build_dir=self.build_target.dir,
            root_dir=self.root_dir,
            prefix=self.build_target.prefix,
            is_main=self.is_main,
        )
        if not warnings:
            return

        print("\n⚡ WARNING:")
        for warning in warnings:
            print(f"  {warning.filename}:{warning.lineno} - {warning.message}")
        print()

    def _symlink_assets(self) -> None:
        if not self.assets_dir.exists():
            return
        target_path = self.build_target.out_dir / "assets"
        if target_path.is_symlink():
            target_path.unlink()
        elif target_path.exists():
            shutil.rmtree(target_path)

        target_path.symlink_to(self.assets_dir)

    def _copy_assets(self) -> None:
        if not self.assets_dir.exists():
            return
        target_path = self.build_target.out_dir / "assets"
        shutil.copytree(
            self.assets_dir,
            target_path,
            dirs_exist_ok=True,
        )

    def _fingerprint_assets(self) -> None:
        """Add fingerprinting to asset files for cache busting."""
        assets_path = self.build_target.out_dir / "assets"
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
        prefixes = ("",)
        if self.build_target.prefix:
            prefixes = (f"/{self.build_target.prefix}", "")

        for html_file in (self.build_target.out_dir).rglob("*.html"):
            html_content = html_file.read_text()
            for old_name, new_name in fingerprints.items():
                for prefix in prefixes:
                    html_content = (
                        html_content
                        .replace(
                            f'href="{prefix}/assets/{old_name}"',
                            f'href="{prefix}/assets/{new_name}"',
                        )
                        .replace(
                            f'src="{prefix}/assets/{old_name}"',
                            f'src="{prefix}/assets/{new_name}"',
                        )
                    )
            html_file.write_text(html_content)
