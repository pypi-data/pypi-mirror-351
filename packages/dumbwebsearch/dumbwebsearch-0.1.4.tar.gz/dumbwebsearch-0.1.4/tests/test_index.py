
import dumbwebsearch.index

import subprocess


def run(args):
    return subprocess.check_output([dumbwebsearch.index.__file__, *args], encoding="utf8")


def test_basic(tmp_path):
    (tmp_path / "foo.md").write_text("some text")

    run(["--database", str(tmp_path / "db"), "--docroot", str(tmp_path), "index"])

    result = run(["--database", str(tmp_path / "db"), "--docroot", str(tmp_path), "search", "failure"])
    assert result == ""

    result = run(["--database", str(tmp_path / "db"), "--docroot", str(tmp_path), "search", "text"])
    assert result.strip().split("\n") == ["= foo.md ==============================", "some [text]"]

