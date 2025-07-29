import argparse
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cached_property
import logging
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import threading
from typing import Protocol

import jinja2
import jinjax


COMPONENTS_FOLDER = "_components"
BUILD_OUTPUT = "_build"
PYTHON_FILE = "__main__.py"
EXCLUDE_DIRS = [".git"]


class ProjectItem(Protocol):
    #: The project item for this
    project: "Project"
    #: The path relative to an abstract root
    relpath: Path
    #: The path data is being read from
    srcpath: Path
    #: The path data is being written to
    dstpath: Path
    #: Final URL (because Windows)
    url: str
    #: The contents of the file, before processing
    raw_contents: str|bytes
    #: The contents of the item, after processing
    contents: str|bytes

    def __eq__(self, other) -> bool: ...


@dataclass
class Asset:
    """
    A ProjectItem that is not modified--images and CSS and stuff
    """
    project: "Project"
    relpath: Path
    srcpath: Path
    dstpath: Path

    def __eq__(self, other):
        return self.srcpath == getattr(other, 'srcpath', None)

    @cached_property
    def url(self) -> str:
        url = '/' + str(self.relpath).replace('\\', '/')
        if self.relpath.name == "index.html":
            url = url.removesuffix("index.html")
        return url

    @cached_property
    def raw_contents(self) -> bytes:
        return self.srcpath.read_bytes()

    @cached_property
    def contents(self) -> bytes:
        return self.srcpath.read_bytes()


@dataclass
class JinjaFile:
    """
    A ProjectItem that is not modified--images and CSS and stuff
    """
    project: "Project"
    relpath: Path
    srcpath: Path
    dstpath: Path

    _render_lock: threading.Lock = field(default_factory=threading.Lock)

    def __eq__(self, other):
        return self.srcpath == getattr(other, 'srcpath', None)

    @cached_property
    def url(self) -> str:
        url = '/' + str(self.relpath).replace('\\', '/')
        if self.relpath.name == "index.html":
            url = url.removesuffix("index.html")
        return url

    @cached_property
    def raw_contents(self) -> bytes:
        return self.srcpath.read_text()

    @cached_property
    def contents(self) -> bytes:
        if self._render_lock.locked():
            raise RuntimeError("Recursive rendering; did you use .contents wrong?")
        with self._render_lock:
            return self.project.jinjax.render(
                str(self.relpath.with_suffix('')),
                # Falsey source counts as no source, so handle empty files
                _source=self.raw_contents or ' ',
                _file_ext=self.relpath.suffix,
                _globals={
                    'basicest': self.project,
                    'current_page': self,
                }
            )


ITEM_CLASSES = {
    ".html": JinjaFile,
    ".xml": JinjaFile,
    ...: Asset
}

@dataclass
class Project:
    root: Path
    dest: Path

    @cached_property
    def jinjax(self) -> jinjax.Catalog:
        cat = jinjax.Catalog()
        cat.add_folder(self.root / COMPONENTS_FOLDER)
        return cat

    @property
    def jinja(self) -> jinja2.environment.Environment:
        return self.jinjax.jinja_env

    def _mkitem(self, srcpath: Path) -> ProjectItem:
        relpath = srcpath.relative_to(self.root)
        dstpath = self.dest / relpath
        try:
            cls = ITEM_CLASSES[srcpath.suffix]
        except KeyError:
            cls = ITEM_CLASSES[...]
        return cls(project=self, relpath=relpath, srcpath=srcpath, dstpath=dstpath)

    @cached_property
    def pages(self):
        pages = []
        for dirpath, dirnames, filenames in self.root.walk():
            if COMPONENTS_FOLDER in dirnames:
                dirnames.remove(COMPONENTS_FOLDER)
            if dirpath == self.dest.parent and self.dest.name in dirnames:
                dirnames.remove(self.dest.name)
            for ex in EXCLUDE_DIRS:
                if ex in dirnames:
                    dirnames.remove(ex)
            for filename in filenames:
                if filename == PYTHON_FILE:
                    continue
                pages.append(self._mkitem(dirpath / filename))
        return pages

    def _import_python(self):
        entry = self.root / PYTHON_FILE
        if not entry.exists():
            return
        import __basicest__
        # Register ourselves as the current project
        __basicest__.project = self
        # Save sys.path because we're going to munge it
        oldpath = sys.path[:]
        try:
            sys.path.insert(0, str(self.root.absolute()))
            code = compile(entry.read_text(), str(entry), 'exec')
            exec(code, {})
        finally:
            sys.path[:] = oldpath
            del __basicest__.project

    def do_the_build(self):
        self._import_python()
        existing_files = set(self.dest.glob('**'))
        for page in self.pages:
            print(f"{page.relpath}")
            existing_files -= {page.dstpath, *page.dstpath.parents}
            page.dstpath.parent.mkdir(parents=True, exist_ok=True)
            contents = page.contents
            if isinstance(contents, bytes):
                page.dstpath.write_bytes(contents)
            elif isinstance(contents, str):
                page.dstpath.write_text(contents)
            elif hasattr(contents, "__bytes__"):
                page.dstpath.write_bytes(bytes(contents))
            else:
                # This always succeeds
                page.dstpath.write_text(str(contents))

        # existing_files is now all the files/directories that were not generated

        print("Cleaning up output directory...")
        # First, remove the files (and file-likes)
        for file in existing_files:
            if not file.is_dir(follow_symlinks=False):
                file.unlink(missing_ok=True)
        # Then remove the directories. These should be empty, since they weren't
        # the ancestor to anything that was generated, and the stale files were
        # removed.
        for file in existing_files:
            if file.is_dir(follow_symlinks=False):
                file.rmdir()



def _venv_bin(venv, cmd):
    if platform.system() == "Windows":
        return venv / "Scripts" / f"{cmd}.exe"
    else:
        return venv / "bin" / cmd


@contextmanager
def mkvenv(reqsfile):
    """
    Make a temporary venv
    """
    with tempfile.TemporaryDirectory() as vdir:
        vdir = Path(vdir)
        subprocess.run(
            [sys.executable, '-m', 'venv', str(vdir)],
            check=True
        )

        python = _venv_bin(vdir, "python")

        subprocess.run(
            [python, '-m', 'pip', "install", "basicest", "-r", reqsfile],
            check=True
        )        

        yield vdir


def bounce(venv: Path, indir: Path, outdir: Path):
    b = _venv_bin(venv, "basicest")

    subprocess.run(
        [b, "--out", str(outdir.absolute()), str(indir.absolute())],
        check=True
    )        


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Minimal Static Site Generator")
    parser.add_argument("root", help="Project root directory", type=Path)
    parser.add_argument('-o', '--out', help="Output directory (Default: PROJECT/_build)", type=Path)
    parser.add_argument(
        '-r', '--requirements', help="Requirements file (also enables creating a venv)",
        type=Path, nargs="?", const="requirements.txt", default=None)
    args = parser.parse_args()
    if not args.out:
        args.out = args.root / BUILD_OUTPUT

    if args.requirements is None:
        # Run immediately
        project = Project(root=args.root, dest=args.out)
        project.do_the_build()
    else:
        # Create a venv and trampoline into it
        with mkvenv(args.requirements) as venv:
            bounce(venv, args.root, args.out)