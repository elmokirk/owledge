from __future__ import annotations

import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from owledge_adapters.cli import main


def run_cli(*args, answer=''):
    output = io.StringIO()
    status = main(list(args), input_stream=io.StringIO(answer), output_stream=output)
    return status, output.getvalue()


class WorkspaceArchiveTests(unittest.TestCase):
    def test_native_single_archive_exact_preview_and_closed_stdin(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            workspace, archive, restored = base / 'workspace', base / 'single.zip', base / 'restored'
            self.assertEqual(run_cli('setup', str(workspace), '--profile', 'knowledge', '--yes', '--json')[0], 0)
            code, preview_raw = run_cli('backup', '--workspace', str(workspace), '--archive', str(archive), '--json')
            self.assertEqual(code, 0, preview_raw)
            preview = json.loads(preview_raw)
            self.assertEqual(run_cli('backup', '--workspace', str(workspace), '--archive', str(archive),
                '--expected-sha256', preview['expected_sha256'], '--yes', '--json')[0], 0)
            code, restore_raw = run_cli('restore', '--archive', str(archive), '--target', str(restored), '--json')
            self.assertEqual(code, 0, restore_raw)
            expected = json.loads(restore_raw)['expected_sha256']
            self.assertEqual(run_cli('restore', '--archive', str(archive), '--target', str(restored),
                '--expected-sha256', expected, '--yes', '--json')[0], 0)
            self.assertEqual(json.loads(run_cli('status', '--workspace', str(restored), '--json')[1])['status'], 'healthy')

    def test_changed_input_and_failed_publication_leave_no_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / 'source'
            source.mkdir()
            (source / 'original.md').write_text('Original', encoding='utf8')
            workspace = base / 'workspace'
            self.assertEqual(run_cli('setup', '--workspace', str(workspace), '--source', str(source),
                '--profile', 'knowledge', '--json', '--yes')[0], 0)
            archive = base / 'backup.zip'
            class ChangedInput(io.StringIO):
                def readline(self, *args):
                    (workspace / 'new.md').write_text('Changed after preview', encoding='utf8')
                    return 'apply\n'
            output = io.StringIO()
            args = ['maintain', '--workspace', str(workspace), '--action', 'backup', '--archive', str(archive)]
            self.assertEqual(main(args, input_stream=ChangedInput(), output_stream=output), 1)
            self.assertIn('changed since preview', output.getvalue())
            self.assertFalse(archive.exists())
            with patch('owledge_adapters.workspace_archive.os.link', side_effect=OSError('Disk unavailable')):
                result = run_cli(*args, answer='apply\n')
            self.assertEqual(result[0], 1, result)
            self.assertFalse(archive.exists())
            self.assertEqual(list(base.glob('.owledge-backup-*')), [])
            self.assertEqual((source / 'original.md').read_text(), 'Original')
            self.assertIn('"status": "healthy"', run_cli('doctor', '--workspace', str(workspace))[1])

    def test_invalid_archive_and_cancel_do_not_create_or_overwrite_targets(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            archive = base / 'bad.zip'
            archive.write_bytes(b'not a zip')
            target = base / 'restored'
            result = run_cli('maintain', '--workspace', str(target), '--action', 'restore',
                             '--archive', str(archive), answer='apply\n')
            self.assertEqual(result[0], 1, result)
            self.assertFalse(target.exists())
            with zipfile.ZipFile(archive, 'w') as output:
                output.writestr('manifest.json', json.dumps({'schema':'owledge.private-workspace-backup/1',
                    'files': {'workspace.json': {'size': 2, 'sha256': '0'*64, 'readonly':False}}}))
                output.writestr('files/workspace.json', '{}')
            result = run_cli('maintain', '--workspace', str(target), '--action', 'restore',
                             '--archive', str(archive), answer='apply\n')
            self.assertEqual(result[0], 1, result)
            self.assertFalse(target.exists())
            with zipfile.ZipFile(archive, 'a') as output:
                output.writestr('../escaped.md', 'escape')
            result = run_cli('maintain', '--workspace', str(target), '--action', 'restore',
                             '--archive', str(archive), answer='apply\n')
            self.assertEqual(result[0], 1, result)
            self.assertFalse((base / 'escaped.md').exists())
            target.mkdir()
            (target / 'mine.md').write_text('Do not overwrite', encoding='utf8')
            self.assertEqual(run_cli('maintain', '--workspace', str(target), '--action', 'restore',
                             '--archive', str(archive), answer='apply\n')[0], 1)
            self.assertEqual((target / 'mine.md').read_text(), 'Do not overwrite')

    def test_reviewed_lesson_survives_backup_restore_and_fresh_read(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / 'source'
            source.mkdir()
            (source / 'original.md').write_text('Preserved original.\n', encoding='utf-8')
            workspace = base / 'workspace'
            self.assertEqual(run_cli('setup', '--workspace', str(workspace), '--source', str(source),
                '--profile', 'knowledge', '--json', '--yes')[0], 0)
            self.assertEqual(run_cli('maintain', '--workspace', str(workspace), '--action', 'lesson',
                '--name', 'archive-check', '--knowledge-area', 'agent-work', '--text', 'Keep the seal intact.',
                '--origin', 'Synthetic', '--conditions', 'Test only', '--verification', 'Fixture',
                '--limitations', 'No production evidence')[0], 0)
            self.assertEqual(run_cli('maintain', '--workspace', str(workspace), '--action', 'review',
                '--name', 'lesson:archive-check', answer='approve\n')[0], 0)
            archive = base / 'backup.zip'
            nested = workspace / ('a' * 100) / ('b' * 100) / ('c' * 80) / 'note.md'
            nested.parent.mkdir(parents=True)
            nested.write_text('Long valid nested path', encoding='utf8')
            self.assertEqual(run_cli('maintain', '--workspace', str(workspace), '--action', 'backup',
                '--archive', str(archive), answer='reject\n')[0], 0)
            self.assertFalse(archive.exists())
            result = run_cli('maintain', '--workspace', str(workspace), '--action', 'backup',
                '--archive', str(archive), answer='apply\n')
            self.assertEqual(result[0], 0, result)
            self.assertEqual(run_cli('maintain', '--workspace', str(workspace), '--action', 'backup',
                '--archive', str(archive), answer='apply\n')[0], 1)
            restored = base / 'restored'
            result = run_cli('maintain', '--workspace', str(restored), '--action', 'restore',
                '--archive', str(archive), answer='apply\n')
            self.assertEqual(result[0], 0, result)
            self.assertEqual((restored / nested.relative_to(workspace)).read_text(), 'Long valid nested path')
            result = run_cli('ask', '--workspace', str(restored), '--name', 'lesson:archive-check')
            self.assertEqual(result[0], 0, result)
            self.assertIn('Keep the seal intact.', result[1])
            self.assertIn('"status": "healthy"', run_cli('doctor', '--workspace', str(restored))[1])


if __name__ == '__main__':
    unittest.main()
