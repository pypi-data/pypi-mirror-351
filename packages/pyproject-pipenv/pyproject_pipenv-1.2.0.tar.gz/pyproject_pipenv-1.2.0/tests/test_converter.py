import unittest
from pathlib import Path

from pyproject_pipenv import converter

DATA = Path(__file__).parent / 'data'


class Test(unittest.TestCase):
    def test_star(self):
        # FIXME: throw warning and require "--force" when there's a "star" requirement, these are not good for packages!
        c = converter.Converter(DATA / 'Pipfile.1', DATA / 'pyproject.1.toml')
        d = c.diff()
        self.assertIsNone(d.deps)
        self.assertIsNone(d.version)

    def test_other(self):
        c = converter.Converter(DATA / 'Pipfile.2', DATA / 'pyproject.2.toml')
        d = c.diff()
        self.assertEqual(d.deps.extra, {'requests'})
        self.assertEqual(d.deps.missing, {'requests>=2.0.0'})
        self.assertIsNone(d.version)

    # TODO: skip for now - diff version in the future to make sure it's within range
    def skip_test_version(self):
        c = converter.Converter(DATA / 'Pipfile.3', DATA / 'pyproject.3.toml')
        d = c.diff()
        self.assertIsNone(d.deps)
        self.assertEqual(d.version.pipfile, '>=3.10,<4')
        self.assertEqual(d.version.pyproject, '>=3.9')

    def test_markers(self):
        c = converter.Converter(DATA / 'Pipfile.5', DATA / 'pyproject.5.toml')
        d = c.diff()
        self.assertIsNone(d.deps)
        self.assertIsNone(d.version)
