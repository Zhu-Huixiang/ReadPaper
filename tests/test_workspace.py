"""Observable safety and portability checks for workspace initialization."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('scaffold', ROOT / 'readpaper/scripts/init_workspace.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / '中文 paper space'

    def init(self, **kwargs):
        return MODULE.scaffold(self.root, **kwargs)

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def test_new_workspace_is_complete_and_rerun_is_lossless(self):
        self.init(slug='example-2603.12345', title='A | B\nC')
        for rel in ('paper/example-2603.12345', 'analyse/example-2603.12345/notes',
                    'analyse/example-2603.12345/figures', 'analyse/example-2603.12345/tmp', 'ideas', 'archive'):
            self.assertTrue((self.root / rel).is_dir())
        pdf = self.root / 'paper/example-2603.12345/original.pdf'
        pdf.write_bytes(b'%PDF test sentinel\x00\xff')
        notes = self.root / 'analyse/example-2603.12345/README.md'
        notes.write_text(notes.read_text() + '\n用户自写内容。\n')
        ledger = self.root / 'README.md'
        ledger.write_text(ledger.read_text().replace('| 待读 |', '| 已验收 |'))
        before = self.snapshot()
        self.init(slug='example-2603.12345', title='Different title')
        self.assertEqual(before, self.snapshot())
        self.assertIn('A &#124; B C', ledger.read_text())

    def test_adding_paper_preserves_existing_data(self):
        self.init(slug='one-2603.12345')
        old = (self.root / 'analyse/one-2603.12345/README.md').read_bytes()
        self.init(slug='two-2604.12345')
        self.assertEqual(old, (self.root / 'analyse/one-2603.12345/README.md').read_bytes())
        text = (self.root / 'README.md').read_text()
        self.assertEqual(text.count('| one-2603.12345 |'), 1)
        self.assertEqual(text.count('| two-2604.12345 |'), 1)

    def test_existing_project_instructions_and_nonledger_stay_untouched(self):
        self.root.mkdir()
        (self.root / 'AGENTS.md').write_text('Existing rules.\n')
        (self.root / 'README.md').write_text('# Software project\nDo not replace.\n')
        result = self.init(slug='example-2603.12345')
        self.assertTrue(result['warnings'])
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'Existing rules.\n')
        self.assertEqual((self.root / 'README.md').read_text(), '# Software project\nDo not replace.\n')

    def test_traversal_and_conflicts_fail_before_writes(self):
        for slug in ('../escape', '/tmp/escape', 'UPPER-2603.12345'):
            with self.assertRaises(ValueError):
                self.init(slug=slug)
            self.assertFalse(self.root.exists())
        self.root.mkdir()
        (self.root / 'analyse').write_text('sentinel')
        with self.assertRaises(ValueError):
            self.init(slug='example-2603.12345')
        self.assertEqual(set(p.name for p in self.root.iterdir()), {'analyse'})

    def test_symlink_cannot_redirect_outputs(self):
        self.root.mkdir()
        outside = Path(self.tmp.name) / 'outside'
        outside.mkdir()
        (self.root / 'analyse').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.init(slug='example-2603.12345')
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.root / 'AGENTS.md').exists())

    def test_empty_workspace_and_explicit_nonarxiv_slug(self):
        self.init(focus='蛋白质结构预测')
        self.assertEqual(list((self.root / 'analyse').iterdir()), [])
        self.assertIn('蛋白质结构预测', (self.root / 'AGENTS.md').read_text())
        self.init(slug='classic-paper', allow_custom_slug=True)
        self.assertTrue((self.root / 'analyse/classic-paper/README.md').exists())


if __name__ == '__main__':
    unittest.main()
