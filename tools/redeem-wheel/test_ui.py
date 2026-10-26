"""GUI regression tests. Use 'xvfb-run -a python -m unittest -v test_ui.py' on Linux."""
import os
import tempfile
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from redeem_wheel import WheelUI


@unittest.skipUnless(os.name == 'nt' or os.environ.get('DISPLAY'), 'Tk requires a display; use xvfb-run')
class WheelGUITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        self.names = [f'viewer_{i:03}' for i in range(100)] + ['山田太郎', 'João']
        (self.path / 'names.txt').write_text('\n'.join(self.names) + '\n', encoding='utf-8')
        self.root = tk.Tk()
        self.app = WheelUI(self.root, self.path)
        self.root.update()

    def tearDown(self):
        self.root.destroy()
        self.temp.cleanup()

    def roster_checkbox(self, prefix):
        return next(w for w in self.app.roster_rows.winfo_children()
                    if w.cget('text').startswith(prefix))

    def test_click_check_adds_immediately_and_uncheck_removes_without_cooldown(self):
        app = self.app
        self.assertEqual(len(app.visible_names), len(self.names))
        app.roster_canvas.yview_moveto(.55)
        self.root.update_idletasks()
        offset = app.roster_canvas.canvasy(0)
        self.roster_checkbox('viewer_063').invoke()
        self.assertEqual(app.store.entries, ['viewer_063'])
        self.assertEqual((self.path / 'wheel_entries.txt').read_text(), 'viewer_063\n')
        self.assertTrue(app.check_vars['viewer_063'].get())
        self.assertEqual(self.roster_checkbox('viewer_063').cget('state'), 'normal')
        self.assertAlmostEqual(offset, app.roster_canvas.canvasy(0), delta=10)
        self.roster_checkbox('viewer_064').invoke()
        self.assertEqual(app.store.entries, ['viewer_063', 'viewer_064'])
        self.assertAlmostEqual(offset, app.roster_canvas.canvasy(0), delta=10)
        self.roster_checkbox('viewer_063').invoke()
        self.assertEqual(app.store.entries, ['viewer_064'])
        self.assertFalse(app.check_vars['viewer_063'].get())
        self.assertEqual(app.store.cooldowns, {})
        self.assertAlmostEqual(offset, app.roster_canvas.canvasy(0), delta=10)
        self.roster_checkbox('viewer_063').invoke()
        self.assertEqual(app.store.entries, ['viewer_064', 'viewer_063'])

    def test_add_and_remove_visible_bulk_act_immediately(self):
        app = self.app
        app.search_var.set('viewer_00')
        self.root.update_idletasks()
        app.select_visible()
        self.assertEqual(app.store.entries, self.names[:10])
        self.assertTrue(all(app.check_vars[name].get() for name in self.names[:10]))
        app.search_var.set('viewer_001')
        app.uncheck_all()
        self.assertEqual(app.store.entries, [n for n in self.names[:10] if n != 'viewer_001'])
        self.assertEqual(app.store.cooldowns, {})
        app.search_var.set('')
        self.assertTrue(app.check_vars['viewer_002'].get())
        self.assertFalse(app.check_vars['viewer_001'].get())

    def test_external_file_sync_changes_checkbox_immediately(self):
        app = self.app
        (self.path / 'wheel_entries.txt').write_text('viewer_015\n', encoding='utf-8')
        app.poll_external()
        self.assertTrue(app.check_vars['viewer_015'].get())
        self.roster_checkbox('viewer_015').invoke()
        self.assertEqual(app.store.entries, [])

    def test_cooldown_refreshes_after_spin_and_next_stream_without_search(self):
        app = self.app
        app.store.add_name('viewer_001')
        app.last_stamp = app.store.stamp()
        app.refresh_search()
        app.refresh_queue()
        app.spin()
        app.started = time.monotonic() - 12
        app.tick()
        w = next(w for w in app.roster_rows.winfo_children() if w.cget('text').startswith('viewer_001'))
        self.assertIn('cooldown', w.cget('text'))
        self.assertEqual(w.cget('state'), 'disabled')
        app.finish_result()
        with patch('redeem_wheel.messagebox.askyesno', return_value=True):
            app.next_stream()
        w = next(w for w in app.roster_rows.winfo_children() if w.cget('text').startswith('viewer_001'))
        self.assertIn('cooldown', w.cget('text'))
        with patch('redeem_wheel.messagebox.askyesno', return_value=True):
            app.next_stream()
        w = next(w for w in app.roster_rows.winfo_children() if w.cget('text').startswith('viewer_001'))
        self.assertNotIn('cooldown', w.cget('text'))
        self.assertEqual(w.cget('state'), 'normal')

    def test_language_toggle_updates_obs_and_persists(self):
        app = self.app
        app.open_display()
        app.toggle_language()
        self.root.update_idletasks()
        self.assertEqual(app.lang, 'ja')
        self.assertIn('抽選', self.root.title())
        self.assertIn('OBS表示', app.display_window.title())
        self.assertIn('配信', app.stream_tag.cget('text'))
        self.assertIn('準備', app.status_var.get())
        app.roster_canvas.yview_moveto(.45)
        self.roster_checkbox('viewer_050').invoke()
        self.assertIn('viewer_050', app.store.entries)
        self.assertTrue(app.check_vars['viewer_050'].get())
        self.assertTrue((self.path / 'wheel_settings.json').exists())
        other = tk.Toplevel(self.root)
        second = WheelUI(other, self.path)
        self.assertEqual(second.lang, 'ja')
        other.destroy()
        app.toggle_language()
        self.assertEqual(app.lang, 'en')
        self.assertEqual(app.title_label.cget('text'), 'REDEEM WHEEL')

    def test_simple_roster_has_no_second_entries_list(self):
        app = self.app
        self.assertEqual(app.find_label.cget('text'), 'ROSTER')
        self.assertEqual(app.controls_label.cget('text'), 'STREAM CONTROLS')
        self.assertFalse(hasattr(app, 'queue_list'))
        self.assertFalse(hasattr(app, 'entries_label'))
        self.assertFalse(hasattr(app, 'remove_btn'))
        self.assertEqual(app.summary_label.cget('text'), '0 on wheel')
        self.roster_checkbox('viewer_001').invoke()
        self.assertEqual(app.summary_label.cget('text'), '1 on wheel')
        app.toggle_language()
        self.assertEqual(app.find_label.cget('text'), '視聴者リスト')
        self.assertEqual(app.controls_label.cget('text'), '配信操作')

    def test_icon_artwork_is_loaded(self):
        app = self.app
        self.assertIsNotNone(app.icon_image)
        # GitHub copy includes an optimized small icon; original local ZIP has 256px.
        self.assertGreaterEqual(app.icon_image.width(), 32)
        self.assertGreaterEqual(app.icon_image.height(), 32)

    def test_controls_visible_at_minimum_window_size(self):
        self.root.geometry('990x735')
        self.root.update()
        obs = self.app.obs_btn
        bottom = obs.winfo_rooty() + obs.winfo_height() - self.root.winfo_rooty()
        self.assertLessEqual(bottom, self.root.winfo_height())


if __name__ == '__main__':
    unittest.main()
