"""What the file watcher decides to rebuild for.

`start_server` and `start_observer` are loops that never return, so they are not
covered here; `ChangeHandler` holds the decision they exist to serve.
"""

from types import SimpleNamespace

import pytest

from writeadoc.devserver import ChangeHandler


@pytest.fixture
def rebuilds(tmp_path, monkeypatch):
    """Report the paths a handler rebuilt for, with `tmp_path` as the cwd."""
    monkeypatch.chdir(tmp_path)
    calls = []

    def build(*, path_filter=("content", "views")):
        handler = ChangeHandler(lambda: calls.append(True), path_filter)

        def fire(relative, *, as_bytes=False):
            before = len(calls)
            src = str(tmp_path / relative)
            handler.on_any_event(
                SimpleNamespace(
                    src_path=src.encode() if as_bytes else src,
                    event_type="modified",
                )
            )
            return len(calls) > before

        return fire

    return build


class TestWhatTriggersARebuild:

    @pytest.mark.parametrize(
        "path",
        ["content/page.md", "views/page.jx", "content/docs.py", "views/deep/x.md"],
    )
    def test_watched_folders_and_extensions(self, rebuilds, path):
        assert rebuilds()(path) is True

    @pytest.mark.parametrize(
        "path",
        [
            "assets/style.css",  # outside the watched folders
            "build/index.html",
            "elsewhere/page.md",
        ],
    )
    def test_unwatched_folders_are_ignored(self, rebuilds, path):
        assert rebuilds()(path) is False

    @pytest.mark.parametrize("path", ["content/notes.txt", "content/image.png"])
    def test_unwatched_extensions_are_ignored(self, rebuilds, path):
        assert rebuilds()(path) is False

    def test_hidden_folders_are_ignored(self, rebuilds):
        """Editors keep swap files in dot folders, which would loop the build."""
        assert rebuilds()("content/.hidden/page.md") is False

    def test_hidden_files_are_ignored(self, rebuilds):
        assert rebuilds()("content/.page.md") is False

    def test_a_bytes_path_is_decoded(self, rebuilds):
        """watchdog reports bytes when the watched path was given as bytes."""
        assert rebuilds()("content/page.md", as_bytes=True) is True

    def test_the_watched_folders_are_configurable(self, rebuilds):
        fire = rebuilds(path_filter=("guides",))

        assert fire("guides/page.md") is True
        assert fire("content/page.md") is False

    def test_an_empty_filter_watches_nothing(self, rebuilds):
        """`str.startswith(())` is False, so the default `path_filter` is inert.

        `start_observer` always passes `("content", "views")`, so this only bites
        a caller that builds a `ChangeHandler` itself and relies on the default.
        """
        assert rebuilds(path_filter=())("anywhere/page.md") is False
