"""
The README for consumers works as written: its files of an application
(the Python blocks starting with ``# app/<path>``) make one, its commands
(``uv run python -m app ...``) run it, and its table of configs lists the
configs of the addon with their defaults (a secret's is not shown).
"""

import os
import pathlib
import re
import shlex
import subprocess
import sys
import tempfile
import typing as t
import unittest

README = pathlib.Path(__file__).parent.parent / "README.md"
FILE = re.compile(r"^```python\n# (app/\S+)\n(.*?)^```$", re.M | re.S)
COMMAND = re.compile(r"^uv run python -m app ([^#\n]*?) *(?:#.*)?$", re.M)
CONFIG_ROW = re.compile(r"^\| `(MONGODB_\w+)` \| (?:`([^`]*)`)? *\|", re.M)
CONFIG_LINE = re.compile(r"^(MONGODB_\w+) = (.*)$", re.M)


class ReadmeTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.readme = README.read_text()
        tmp = self.enterContext(tempfile.TemporaryDirectory())
        self.root = pathlib.Path(tmp)
        (self.root / "app").mkdir()
        (self.root / "app" / "__init__.py").touch()
        for path, code in FILE.findall(self.readme):
            (self.root / path).write_text(f"# {path}\n{code}")

    def run_app(self, *argv: str) -> str:
        env = {k: v for k, v in os.environ.items() if not k.startswith("APP_")}
        done = subprocess.run(
            [sys.executable, "-m", "app", *argv],
            cwd=self.root,
            env={**env, "APP_IS_PRINT_CONFIGS": "off"},
            capture_output=True,
            text=True,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def test_the_application_files_are_given(self) -> None:
        paths = [path for path, _ in FILE.findall(self.readme)]
        self.assertEqual(paths, ["app/project.py", "app/__main__.py"])

    def test_the_commands_run(self) -> None:
        commands = COMMAND.findall(self.readme)
        self.assertTrue(commands)
        for command in commands:
            with self.subTest(command):
                self.run_app(*shlex.split(command))

    def test_the_table_lists_the_configs_of_the_addon(self) -> None:
        table = dict(CONFIG_ROW.findall(self.readme))
        listed = dict(CONFIG_LINE.findall(self.run_app("settings", "list")))
        # a secret is listed as ***, whatever its default
        secrets = {name for name, value in listed.items() if value == "***"}
        self.assertEqual(table.keys(), listed.keys())
        for name in listed.keys() - secrets:
            with self.subTest(name):
                self.assertEqual(table[name], listed[name])
