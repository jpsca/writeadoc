import argparse
import os
import shutil
import time
import types
import typing as t
import webbrowser
from pathlib import Path
from uuid import uuid4

import jinja2
import markdown
from markupsafe import Markup
from watchdog.observers import Observer

from . import helpers, utils, search
from .types import PageData, PageRef, SectionRef, SiteData


TPages = dict[str, list[str]]
TProcPages = list[tuple[SectionRef, list[PageData]]]


class Docs:
    pages: TPages
    site: SiteData
    theme: types.ModuleType
    build_folder: Path

    def __init__(
        self,
        pages: TPages,
        *,
        theme: types.ModuleType,
        name: str = "WriteADoc",
        description: str = "",
        image: str = "/assets/images/opengraph.png",
        version: str = "0.1.0",
        base_url: str = "",
        source_url: str = "",
        help_url: str = "",
        md_extensions: list[str] = utils.DEFAULT_MD_EXTENSIONS,
        md_config: dict[str, dict[str, t.Any]] = utils.DEFAULT_MD_CONFIG,
    ):
        self.pages = pages
        self.site = SiteData(
            name=name,
            description=description,
            image=image,
            version=version,
            base_url=base_url.rstrip("/"),
            source_url=source_url,
            help_url=help_url,
        )
        self.theme = theme
        self.build_folder = Path("build")
        self.renderer = markdown.Markdown(
            extensions=md_extensions,
            extension_configs=md_config,
            output_format="html",
            tab_length=2,
        )
        self.jinja_env = jinja2.Environment(
            extensions=[
                "jinja2.ext.loopcontrols",
            ],
            undefined=jinja2.StrictUndefined,
        )
        self.jinja_env.filters.update({
            "widont": helpers.widont,
        })

    def build(self, relativize_urls: bool = True) -> None:
        print("Building documentation...")

        proc_pages = self._process_pages()
        self.site.pages = [
            (
                section,
                [
                    PageRef(id=page.id, title=page.title, url=page.url)
                    for page in sec_pages
                    if len(sec_pages) > 1
                ],
            )
            for section, sec_pages in proc_pages
        ]

        self._render_pages(proc_pages, relativize_urls=relativize_urls)
        self._render_search_page(proc_pages, relativize_urls=relativize_urls)
        self._render_index_page(relativize_urls=relativize_urls)
        self._render_docs_redirect_page()
        if False and relativize_urls:
            self._symlink_assets()
        else:
            self._copy_assets()

    def cli(self):
        parser = argparse.ArgumentParser(description="WriteADoc CLI")
        subparsers = parser.add_subparsers(dest="command")

        subparsers.add_parser("run", help="Run and watch for changes")
        subparsers.add_parser("build", help="Build the documentation for deployment")

        args = parser.parse_args()

        if args.command == "build":
            self.build(relativize_urls=False)
            print("Documentation built successfully.")
            print("You can now copy the 'build' folder to your web server.")

        elif args.command in (None, "run"):
            self.build()  # Initial run
            event_handler = utils.ChangeHandler(self.build)
            observer = Observer()
            # Watch current directory and all subfolders
            observer.schedule(event_handler, os.getcwd(), recursive=True)
            observer.start()
            print("Watching for changes. Press Ctrl+C to exit.\n")
            webbrowser.open("./build/index.html")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
        else:
            parser.print_help()

    ## Private

    def _process_pages(self) -> TProcPages:
        proc_pages = []

        for section_name, files in self.pages.items():
            section = SectionRef(
                id=uuid4().hex,
                title=section_name,
                url="",
            )
            sec_pages = []
            for filename in files:
                filepath = Path(filename)
                meta, html = self._process_file(filepath)
                url = f"/docs/{filepath.with_suffix('').as_posix().strip('/')}/"

                page = PageData(
                    section=section,
                    title=meta.pop("title", filepath.name),
                    description=meta.pop("description", ""),
                    url=url,
                    meta=meta,
                    content=html,
                )
                sec_pages.append(page)

            if sec_pages:
                section["url"] = sec_pages[0].url
            proc_pages.append((section, sec_pages))

        # --- Add prev/next navigation links ---

        pages_list = [page for _, sec_pages in proc_pages for page in sec_pages]
        last_index_with_next = len(pages_list) - 1

        for i, page in enumerate(pages_list):
            if i > 0:
                page.prev = PageRef(
                    id=pages_list[i - 1].id,
                    title=pages_list[i - 1].title,
                    url=pages_list[i - 1].url,
                )
            else:
                page.prev = None

            if i < last_index_with_next:
                page.next = PageRef(
                    id=pages_list[i + 1].id,
                    title=pages_list[i + 1].title,
                    url=pages_list[i + 1].url,
                )
            else:
                page.next = None

        return proc_pages

    def _process_file(self, filepath: Path) -> tuple[dict[str, t.Any], str]:
        if not filepath.exists():
            raise FileNotFoundError(f"File {filepath} does not exist.")

        source = filepath.read_text(encoding="utf-8")
        meta, source = utils.extract_metadata(source)
        html = self._render_markdown(source)
        return meta, Markup(html)

    def _render_markdown(self, source: str) -> str:
        html = self.renderer.convert(source).strip()
        html = html.replace("<pre><span></span>", "<pre>")
        return html

    def _render_pages(self, proc_pages: TProcPages, relativize_urls: bool) -> None:
        for _, sec_pages in proc_pages:
            for page in sec_pages:
                self._render_page(page, relativize_urls=relativize_urls)

    def _render_page(self, page: PageData, relativize_urls: bool) -> None:
        outpath = self.build_folder / str(page.url).strip("/") / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)

        co = self.theme.Page(
            jinja_env=self.jinja_env,
            site=self.site,
            page=page,
        )
        html = co.render()
        if relativize_urls:
            html = utils.relativize_urls(html, page.url)
        outpath.write_text(html, encoding="utf-8")

    def _render_search_page(self, proc_pages: TProcPages, *, relativize_urls: bool) -> None:
        outpath = self.build_folder / "search" / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        page = PageData(
            section=SectionRef(id="", title="Search", url="/search/"),
            title="Search",
            url="/search/",
        )
        co = self.theme.SearchPage(
            jinja_env=self.jinja_env,
            page=page,
            site=self.site,
        )
        search_data = search.extract_search_data(proc_pages)
        html = co.render(search_data=search_data)
        if relativize_urls:
            html = utils.relativize_urls(html, "/search/")
        outpath.write_text(html, encoding="utf-8")

    def _render_docs_redirect_page(self) -> None:
        section = self.site.pages[0]if self.site.pages else None
        if not section:
            return
        # Use the first page in the section or the section itself if no pages
        url = section[1][0]["url"] if section[1] else section[0]["url"]
        url = f"{url.removeprefix("/docs/")}index.html"

        outpath = self.build_folder / "docs" / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)
        html = (
            '<!DOCTYPE html><html><head><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0; url=./{url}">'
            "<title></title></head><body></body></html>"
        )
        outpath.write_text(html, encoding="utf-8")

    def _render_index_page(self, relativize_urls: bool) -> None:
        outpath = self.build_folder / "index.html"
        outpath.parent.mkdir(parents=True, exist_ok=True)

        md_index = Path("index.md")
        if md_index.exists():
            meta, html = self._process_file(md_index)
            page = PageData(
                section=SectionRef(id="", title=self.site.name, url="/"),
                title=meta.get("title", self.site.name),
                url="/",
                description=meta.get("description", ""),
                content=html,
            )
        else:
            # Just render the template page
            page = PageData(
                section=SectionRef(id="", title=self.site.name, url="/"),
                title=self.site.name,
                url="/",
            )

        co = self.theme.IndexPage(
            jinja_env=self.jinja_env,
            page=page,
            site=self.site,
        )
        html = co.render()
        if relativize_urls:
            html = utils.relativize_urls(html, "/")
        outpath.write_text(html, encoding="utf-8")

    def _symlink_assets(self) -> None:
        if not self.theme.__file__:
            return
        assets_folder = Path(self.theme.__file__).parent / "assets"
        if not assets_folder.exists():
            return
        target_path = self.build_folder / "assets"
        if target_path.exists():
            if target_path.is_symlink():
                target_path.unlink()
            else:
                shutil.rmtree(target_path)
        target_path.symlink_to(assets_folder, target_is_directory=True)

    def _copy_assets(self) -> None:
        if not self.theme.__file__:
            return
        assets_folder = Path(self.theme.__file__).parent / "assets"
        if not assets_folder.exists():
            return
        target_path = self.build_folder / "assets"
        shutil.copytree(
            assets_folder,
            target_path,
            dirs_exist_ok=True,
        )
