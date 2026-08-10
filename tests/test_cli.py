"""How `docs.py <command>` maps onto the build methods."""

import pytest

from writeadoc import Docs


@pytest.fixture
def docs(tmp_root):
    (tmp_root / "views" / "index.jx").write_text("<h1>Home</h1>")
    (tmp_root / "content" / "one.md").write_text("---\ntitle: One\n---\n\nHi.")
    return Docs(tmp_root, pages=["one.md"])


@pytest.fixture
def dispatch(docs, monkeypatch):
    """Run `docs.cli()` with the given argv, reporting what it called."""
    calls = []
    monkeypatch.setattr(docs, "cli_build", lambda **kw: calls.append(("build", kw)))
    monkeypatch.setattr(docs, "cli_run", lambda: calls.append(("run", {})))

    def run(*argv):
        monkeypatch.setattr("sys.argv", ["docs.py", *argv])
        docs.cli()
        return calls

    return run


def test_no_command_runs_the_server(dispatch):
    assert dispatch() == [("run", {})]


def test_run(dispatch):
    assert dispatch("run") == [("run", {})]


def test_build_defaults_to_a_plain_release(dispatch):
    assert dispatch("build") == [
        ("build", {"archive": False, "llm": False, "boring": False})
    ]


@pytest.mark.parametrize(
    ("flag", "key"),
    [("--archive", "archive"), ("--llm", "llm"), ("--boring", "boring")],
)
def test_each_build_flag_reaches_cli_build(dispatch, flag, key):
    (_, kwargs), = dispatch("build", flag)

    assert kwargs[key] is True


def test_the_build_flags_combine(dispatch):
    (_, kwargs), = dispatch("build", "--archive", "--llm", "--boring")

    assert kwargs == {"archive": True, "llm": True, "boring": True}


def test_an_unknown_command_is_rejected(dispatch):
    """argparse exits rather than falling through to a build."""
    with pytest.raises(SystemExit):
        dispatch("nonsense")


class TestProjectRoot:

    def test_a_missing_root_is_rejected(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="does not exist"):
            Docs(tmp_path / "nope", pages=[])

    def test_a_file_root_uses_its_folder(self, tmp_root):
        """`Docs(__file__, ...)` is how every `docs.py` calls it."""
        (tmp_root / "views" / "index.jx").write_text("<h1>Home</h1>")
        (tmp_root / "docs.py").write_text("")

        docs = Docs(tmp_root / "docs.py", pages=[])

        assert docs.root_dir == tmp_root
        assert docs.content_dir == tmp_root / "content"
