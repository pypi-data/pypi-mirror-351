import abc
import ast
import contextlib
import itertools
import json
import pathlib
import re

import more_itertools
import packaging.requirements
from coherent.deps import imports, pypi
from jaraco.context import suppress
from jaraco.functools import compose, pass_none

from .compat.py310 import tomllib

ValidRequirementString = compose(str, packaging.requirements.Requirement)

_unique = dict.fromkeys


class EllipsisFilter:
    found = False

    def __call__(self, item):
        is_ellipsis = item is Ellipsis
        self.found |= is_ellipsis
        return not is_ellipsis


class Dependencies(list):
    index_url = None

    def params(self):
        return ['--index-url', self.index_url] * bool(self.index_url) + self

    @classmethod
    def load(cls, items):
        """
        Construct self from items, validated as requirements.
        """
        ef = EllipsisFilter()
        deps = cls(map(ValidRequirementString, filter(ef, items)))
        deps.inferred = ef.found
        return deps


class DepsReader:
    """
    Given a Python script, read the dependencies it declares.
    Does not execute the script, so expects __requires__ to be
    assigned a static list of strings.
    """

    def __init__(self, script):
        self.script = script

    @classmethod
    def try_read(cls, script_path: pathlib.Path):
        results = (subclass._try_read(script_path) for subclass in cls.__subclasses__())
        return next(filter(None, results), Dependencies())

    @classmethod
    @suppress(Exception)
    def _try_read(cls, script_path: pathlib.Path):
        """
        Attempt to load the dependencies from the script,
        but return None if unsuccessful.
        """
        reader = cls.load(script_path)
        return reader.maybe_infer(reader.read())

    @classmethod
    @abc.abstractmethod
    def load(cls, script: pathlib.Path):
        """
        Construct a DepsReader from the script path.
        """

    @classmethod
    def search(cls, params):
        """
        Given a (possibly-empty) series of parameters to a
        Python interpreter, return any dependencies discovered
        in a script indicated in the parameters. Only honor the
        first file found.
        """
        safe_is_file = suppress(OSError)(pathlib.Path.is_file)
        files = filter(safe_is_file, map(pathlib.Path, params))
        return cls.try_read(next(files, None)).params()

    def maybe_infer(self, deps):
        if deps.inferred:
            deps[:] = _unique(itertools.chain(deps, self.infer()))
        return deps

    def infer(self):
        r"""
        >>> DepsReader('import sys\nimport cowsay\nimport jaraco.text.missing\n').infer()
        ['cowsay', 'jaraco.text']
        """
        return Dependencies(
            pypi.distribution_for(imp)
            for imp in imports.get_module_imports(self.script)
            if not imp.excluded()
        )

    def read(self):
        return self.read_toml() or self.read_python()

    def read_toml(self):
        r"""
        >>> DepsReader('# /// script\n# dependencies = ["foo", "bar"]\n# ///\n').read()
        ['foo', 'bar']
        >>> DepsReader('# /// pyproject\n# dependencies = ["foo", "bar"]\n# ///\n').read_toml()
        []
        >>> DepsReader('# /// pyproject\n#dependencies = ["foo", "bar"]\n# ///\n').read_toml()
        []
        >>> DepsReader('# /// script\n# dependencies = ["foo", "bar"]\n').read_toml()
        []
        >>> DepsReader('# /// script\n# ///\n\n# /// script\n# ///').read_toml()
        Traceback (most recent call last):
        ...
        ValueError: Multiple script blocks found
        """
        TOML_BLOCK_REGEX = (
            r'(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)*)^# ///$'
        )
        name = 'script'
        blocks = filter(
            lambda m: m.group('type') == name,
            re.finditer(TOML_BLOCK_REGEX, self.script),
        )
        block = more_itertools.only(
            blocks, too_long=ValueError(f'Multiple {name} blocks found')
        )
        return Dependencies.load(self._deps_from_toml(block) or [])

    @staticmethod
    @pass_none
    def _deps_from_toml(block):
        content = ''.join(
            line[2:] if line.startswith('# ') else line[1:]
            for line in block.group('content').splitlines(keepends=True)
        )
        return tomllib.loads(content).get("dependencies", [])

    def read_python(self):
        r"""
        >>> DepsReader("__requires__=['foo']").read()
        ['foo']
        >>> empty = DepsReader("").read()
        >>> empty
        []
        >>> empty.inferred
        True
        """
        reqs = suppress(ValueError)(self._read)('__requires__')
        if reqs is None:
            reqs = [...]
        deps = Dependencies.load(reqs)
        with contextlib.suppress(ValueError):
            deps.index_url = self._read('__index_url__')
        return deps

    def _read(self, var_name):
        """
        Read a variable from self.script by parsing the AST.

        Raises ValueError if the variable is not found or if it
        appears more than once.
        """
        mod = ast.parse(self.script)
        (node,) = (node for node in mod.body if self._is_assignment(node, var_name))
        return ast.literal_eval(node.value)

    @staticmethod
    def _is_assignment(node, var_name):
        """
        Does this AST node describe an assignment to var_name?
        """
        return (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == var_name
        )


class SourceDepsReader(DepsReader):
    @classmethod
    def load(cls, script: pathlib.Path):
        return cls(script.read_text(encoding='utf-8'))


def _load_json(path: pathlib.Path):
    with path.open(encoding='utf-8') as stream:
        return json.load(stream)


class NotebookDepsReader(DepsReader):
    @classmethod
    def load(cls, script: pathlib.Path):
        lines = (
            line
            for cell in _load_json(script)['cells']
            for line in cell['source'] + ['\n']
            if cell['cell_type'] == 'code' and not line.startswith('%')
        )
        return cls(''.join(lines))
