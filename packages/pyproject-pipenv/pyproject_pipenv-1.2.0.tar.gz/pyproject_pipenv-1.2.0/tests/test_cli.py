import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pyproject_pipenv import __main__ as ppmain

DATA = Path(__file__).parent / 'data'


class Test(unittest.TestCase):
    def test_check_up_to_date(self):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.seek(0)
            tmpf = Path(tmp.name)
            source = DATA / 'pyproject.1.toml'
            tmpf.write_text(source.read_text())
            with mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                ppmain.main(['--pipfile', str(DATA / 'Pipfile.1'), '--pyproject', str(tmpf)])
            self.assertEqual(mock_stdout.getvalue(), 'pyproject.toml is up to date\n')
            # unmodified
            self.assertEqual(source.read_text(), tmpf.read_text())

    def test_check_needs_changes(self):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.seek(0)
            tmpf = Path(tmp.name)
            source = DATA / 'pyproject.2.toml'
            tmpf.write_text(source.read_text())
            with mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                try:
                    ppmain.main(['--pipfile', str(DATA / 'Pipfile.2'), '--pyproject', str(tmpf)])
                    self.fail('Expected exit code 1 but got 0')
                except SystemExit:
                    pass
            self.assertEqual(
                mock_stdout.getvalue(),
                'Dependencies out of sync:\n- requests\n+ requests>=2.0.0\npyproject.toml NEEDS UPDATE!\n',
            )
            # unmodified
            self.assertEqual(source.read_text(), tmpf.read_text())

    def test_fix_deps_need_changes(self):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.seek(0)
            tmpf = Path(tmp.name)
            source = DATA / 'pyproject.2.toml'
            tmpf.write_text(source.read_text())
            with mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                ppmain.main(['--pipfile', str(DATA / 'Pipfile.2'), '--pyproject', str(tmpf), '--fix'])
            self.assertEqual(
                mock_stdout.getvalue(),
                'Dependencies out of sync:\n- requests\n+ requests>=2.0.0\npyproject.toml UPDATED!\n',
            )
            # modified
            self.assertEqual((DATA / 'pyproject.2.fixed.toml').read_text(), tmpf.read_text())

    # TODO: skip for now - diff version in the future to make sure it's within range
    def skip_test_fix_version_needs_changes(self):
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.seek(0)
            tmpf = Path(tmp.name)
            source = DATA / 'pyproject.3.toml'
            tmpf.write_text(source.read_text())
            with mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                ppmain.main(['--pipfile', str(DATA / 'Pipfile.3'), '--pyproject', str(tmpf), '--fix'])
            self.assertEqual(
                mock_stdout.getvalue(),
                """Version out of sync: DiffVersion(pipfile='>=3.10,<4', pyproject='>=3.9')\npyproject.toml UPDATED!\n""",
            )
            # modified
            self.assertEqual((DATA / 'pyproject.3.fixed.toml').read_text(), tmpf.read_text())

    def test_fix_dep_without_operator(self):
        """https://github.com/fopina/pyproject-pipenv/issues/4"""
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.seek(0)
            tmpf = Path(tmp.name)
            source = DATA / 'pyproject.1.toml'
            tmpf.write_text(source.read_text())
            with mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                ppmain.main(['--pipfile', str(DATA / 'Pipfile.4'), '--pyproject', str(tmpf), '--fix'])
            self.assertEqual(
                mock_stdout.getvalue(),
                'Dependencies out of sync:\n- requests\n+ requests==2.0.0\npyproject.toml UPDATED!\n',
            )
            self.assertIn('requests==2.0.0', tmpf.read_text())
