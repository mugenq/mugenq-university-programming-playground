"""Run using: python -m unittest -v test_wheel.py"""
import tempfile
import unittest
from pathlib import Path
from wheel_core import WheelStore, read_names, unique_names


class WheelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        self.wheel = WheelStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_normalize_and_deduplicate(self):
        ok, _ = self.wheel.add_name('@Alice')
        self.assertTrue(ok)
        self.assertEqual(self.wheel.entries, ['Alice'])
        ok, reason = self.wheel.add_name('ALICE')
        self.assertFalse(ok)
        self.assertIn('already', reason)
        self.assertEqual(read_names(self.path / 'names.txt'), ['Alice'])

    def test_one_full_next_stream_cooldown(self):
        self.wheel.add_name('Alice')
        self.wheel.add_name('Bob')
        self.wheel.pick_name('Alice')
        self.assertEqual(self.wheel.entries, ['Bob'])
        self.assertEqual(self.wheel.cooldowns['alice'], 2)
        self.assertFalse(self.wheel.add_name('Alice')[0])  # same stream
        self.wheel.next_stream()                          # stream 2
        self.assertFalse(self.wheel.add_name('alice')[0]) # next stream
        self.assertTrue(self.wheel.add_name('Bob')[0])
        self.wheel.next_stream()                          # stream 3
        self.assertTrue(self.wheel.add_name('Alice')[0])
        self.assertNotIn('alice', self.wheel.cooldowns)

    def test_reload_and_block_file_edits(self):
        self.wheel.add_name('Alice')
        self.wheel.pick_name('Alice')
        (self.path / 'wheel_entries.txt').write_text('Alice\nBob\nbob\n', encoding='utf-8')
        changed, blocked = self.wheel.sync_entries()
        self.assertTrue(changed)
        self.assertEqual(blocked, 1)
        self.assertEqual(self.wheel.entries, ['Bob'])
        self.assertEqual(read_names(self.path / 'wheel_entries.txt'), ['Bob'])

    def test_persistent_restart(self):
        self.wheel.add_name('Alice')
        self.wheel.pick_name('Alice')
        next_instance = WheelStore(self.path)
        self.assertEqual(next_instance.stream, 1)
        self.assertEqual(next_instance.cooldowns['alice'], 2)
        self.assertEqual(next_instance.history[-1], {'name': 'Alice', 'stream': 1})
        self.assertFalse(next_instance.add_name('ALICE')[0])

    def test_external_append_no_accidental_loss(self):
        self.wheel.add_name('Alice')
        with (self.path / 'wheel_entries.txt').open('a', encoding='utf-8') as f:
            f.write('Bob\n')
        self.wheel.sync_entries()
        self.wheel.pick_name('Alice')
        self.assertEqual(self.wheel.entries, ['Bob'])

    def test_invalid_names(self):
        self.assertEqual(unique_names(['@a', 'A', 'a', '  ', 'Joe\x00']), ['a'])
        self.assertFalse(self.wheel.add_name('A\nB')[0])
        self.assertFalse(self.wheel.add_name('x' * 46)[0])

    def test_bulk_add_and_rejection_reasons(self):
        self.wheel.add_name('Alice')
        self.wheel.pick_name('Alice')
        added, rejected = self.wheel.add_names(['Bob', 'BOB', 'Alice', '山田太郎', '', 'João'])
        self.assertEqual(added, ['Bob', '山田太郎', 'João'])
        self.assertEqual([r[1] for r in rejected], ['duplicate', 'cooldown', 'invalid'])
        self.assertEqual(read_names(self.path / 'wheel_entries.txt'), added)
        self.assertEqual(read_names(self.path / 'names.txt'), ['Alice', 'Bob', '山田太郎', 'João'])

    def test_name_issue_updates_when_cooldown_expires(self):
        self.wheel.add_name('Alice')
        self.assertEqual(self.wheel.name_issue('Alice')[0], 'duplicate')
        self.wheel.pick_name('Alice')
        self.assertEqual(self.wheel.name_issue('Alice'), ('cooldown', 2))
        self.wheel.next_stream()
        self.assertEqual(self.wheel.name_issue('Alice'), ('cooldown', 2))
        self.wheel.next_stream()
        self.assertEqual(self.wheel.name_issue('Alice'), (None, None))

    def test_remove_names_batch_preserves_other_entries_and_cooldowns(self):
        self.wheel.add_names(['Alice', 'Bob', 'Charlie', 'João'])
        removed = self.wheel.remove_names(['BOB', 'alice', 'not_in_list'])
        self.assertEqual(removed, ['Alice', 'Bob'])
        self.assertEqual(self.wheel.entries, ['Charlie', 'João'])
        self.assertEqual(read_names(self.path / 'wheel_entries.txt'), ['Charlie', 'João'])
        self.assertEqual(self.wheel.cooldowns, {})
        self.assertEqual(self.wheel.remove_names(['nobody']), [])
        self.assertTrue(self.wheel.add_name('Alice')[0])

    def test_utf8_bom_file(self):
        (self.path / 'wheel_entries.txt').write_text('\ufeff山田\nJoão\n', encoding='utf-8')
        self.wheel.sync_entries()
        self.assertEqual(self.wheel.entries, ['山田', 'João'])


if __name__ == '__main__':
    unittest.main()
