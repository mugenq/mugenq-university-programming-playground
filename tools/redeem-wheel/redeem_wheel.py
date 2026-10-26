"""Redeem Wheel: offline streamer wheel with compact roster, instant checklist and EN/日本語.

Run with Python 3.9+ and Tkinter, no third-party libraries.
"""
from __future__ import annotations

import json
import math
import secrets
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from wheel_core import WheelStore, atomic_write, clean_name

BG = '#121521'
PANEL = '#1B2030'
FIELD = '#242B3D'
INK = '#F7F2E7'
MUTED = '#AAB4C7'
ACCENT = '#F6C977'
ROSE = '#E9A8AE'
COLORS = [
    '#647DAD', '#CD776C', '#70A6A1', '#B88CC8', '#C6A068', '#7188B8',
    '#BB8198', '#6D9C90', '#D0A17F', '#9D87A7', '#78A7BC', '#BDA565',
]
FONT = 'Yu Gothic UI' if sys.platform == 'win32' else 'Noto Sans CJK JP'


def asset_path(name: str) -> Path:
    "Packaged read-only artwork; available in source and PyInstaller builds."
    bundle = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    return bundle / 'assets' / name


def data_directory() -> Path:
    "Persistent user-editable files live alongside the portable Windows EXE."
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

TRANSLATIONS = {
    'en': {
        'controller_title': 'Redeem Wheel · Stream controller',
        'display_title': 'Redeem Wheel · OBS display',
        'title': 'REDEEM WHEEL',
        'next_stream': 'NEXT STREAM  →',
        'clear_wheel': 'Clear wheel',
        'stream': 'STREAM {n}',
        'find': 'ROSTER',
        'find_help': 'Browse names.txt or search / paste a username:',
        'search_hint': 'Search or enter a new name…',
        'select_visible': 'Add visible',
        'uncheck_all': 'Remove visible',
        'add_typed': 'Add typed name',
        'selection_tip': 'Check = add now; uncheck = remove (no cooldown).',
        'in_wheel': ' [in wheel]',
        'on_cooldown': ' [cooldown to stream {n}]',
        'eligible_count': '{n} on wheel',
        'reload': 'Reload files',
        'controls': 'STREAM CONTROLS',
        'cooldown_help': 'Winner cannot re-enter this stream or the next.',
        'obs': 'Open OBS display window',
        'footer': 'LOCAL ONLY  ·  No Twitch credentials required',
        'spin': 'SPIN THE WHEEL',
        'last_winner': 'LAST WINNER: {name}',
        'no_spins': 'No spins yet',
        'display_info': 'STREAM {stream}  •  {count} IN THE WHEEL',
        'display_winner': 'LAST WINNER   {name}',
        'wheel_empty': 'WHEEL IS EMPTY',
        'wheel_empty_help': 'Add a redeemed viewer to begin',
        'ready': 'Ready. Tick a viewer to add immediately; untick to remove.',
        'invalid': 'Please enter one name (maximum 45 characters).',
        'duplicate': '{name} is already in the wheel.',
        'cooldown': '{name} is on cooldown through stream {n}.',
        'added': 'Added {name}.',
        'bulk_added': 'Added {added} viewer(s). {skipped} skipped (duplicate / cooldown).',
        'no_checked': 'Check one or more eligible names first.',
        'no_visible': 'No eligible visible names to add.',
        'selected_visible': 'Added {added} visible viewer(s). {skipped} skipped.',
        'no_visible_entries': 'No visible wheel entries to remove.',
        'cleared_checks': 'Removed {n} visible viewer(s) without cooldown.',
        'removed': 'Removed {name} without applying cooldown.',
        'files_reloaded': 'Files reloaded. {n} cooldown name(s) excluded.',
        'reload_error': 'Cannot reload file: {error}',
        'imported': 'Imported text-file changes. {n} name(s) blocked by cooldown.',
        'file_error': 'Problem reading wheel_entries.txt: {error}',
        'spin_read_error': 'Cannot read entries: {error}',
        'no_entries': 'No eligible entries. Add a redeemed name first.',
        'spinning': 'Spinning…',
        'spin_save_error': 'Winner {name} selected, but saving FAILED: {error}',
        'winner_picked': 'Picked {name}. Removed and blocked through stream {n}.',
        'clear_title': 'Clear entries',
        'clear_confirm': 'Remove ALL current wheel entries?\nNo cooldowns will be applied.',
        'entries_cleared': 'Current entries cleared.',
        'next_title': 'Next stream',
        'next_confirm': 'Start stream {n}?\n\nThis clears the current wheel. Winners from the previous stream remain on cooldown for one more stream; older cooldowns expire.',
        'next_started': 'Stream {n} started. Previous-stream winners are still on cooldown.',
    },
    'ja': {
        'controller_title': '抽選ルーレット · 配信者用',
        'display_title': '抽選ルーレット · OBS表示',
        'title': '抽選ルーレット',
        'next_stream': '次の配信へ  →',
        'clear_wheel': '全員削除',
        'stream': '配信 {n} 回目',
        'find': '視聴者リスト',
        'find_help': 'names.txt から選ぶか、名前を検索・入力：',
        'search_hint': '検索、または新しい名前を入力…',
        'select_visible': '表示中を全員追加',
        'uncheck_all': '表示中を全員削除',
        'add_typed': '入力名を追加',
        'selection_tip': 'チェックで即追加・解除で削除（クールダウンなし）。',
        'in_wheel': ' [登録済み]',
        'on_cooldown': ' [配信{n}まで参加不可]',
        'eligible_count': '参加中：{n}人',
        'reload': 'ファイル再読込',
        'controls': '配信操作',
        'cooldown_help': '当選者は今の配信と次の配信に参加できません。',
        'obs': 'OBS表示ウィンドウを開く',
        'footer': 'ローカル動作  ·  Twitch認証不要',
        'spin': 'ルーレットを回す',
        'last_winner': '前回の当選者：{name}',
        'no_spins': 'まだ抽選していません',
        'display_info': '配信 {stream} 回目  ・  参加者 {count}人',
        'display_winner': '前回の当選者：{name}',
        'wheel_empty': '参加者がいません',
        'wheel_empty_help': '参加者を追加してください',
        'ready': '準備完了。チェックを入れると即追加、外すと削除されます。',
        'invalid': '名前を1つ入力してください（45文字以内）。',
        'duplicate': '{name} さんは既に参加しています。',
        'cooldown': '{name} さんは配信{n}回目まで参加できません。',
        'added': '{name} さんを追加しました。',
        'bulk_added': '{added}人追加しました。{skipped}人は重複またはクールダウンのため除外しました。',
        'no_checked': '参加可能な名前にチェックを入れてください。',
        'no_visible': '表示中に追加可能な名前がありません。',
        'selected_visible': '表示中の{added}人を追加しました。除外：{skipped}人。',
        'no_visible_entries': '表示中に削除できる参加者がいません。',
        'cleared_checks': '表示中の{n}人をクールダウンなしで削除しました。',
        'removed': '{name} さんをクールダウンなしで削除しました。',
        'files_reloaded': '再読込完了。クールダウン中の{n}人を除外しました。',
        'reload_error': 'ファイルを読み込めません：{error}',
        'imported': 'ファイルの変更を反映しました。クールダウン中の{n}人を除外しました。',
        'file_error': 'wheel_entries.txt 読込エラー：{error}',
        'spin_read_error': '参加者を読み込めません：{error}',
        'no_entries': '参加者がいません。先に追加してください。',
        'spinning': '抽選中…',
        'spin_save_error': '{name} さんが当選しましたが、保存に失敗しました：{error}',
        'winner_picked': '{name} さんが当選！削除済み、配信{n}回目まで参加不可。',
        'clear_title': '参加者の一括削除',
        'clear_confirm': '現在の参加者を全て削除しますか？\nクールダウンは適用されません。',
        'entries_cleared': '参加者を全て削除しました。',
        'next_title': '次の配信',
        'next_confirm': '配信{n}回目を始めますか？\n\nルーレットは空になります。前の配信の当選者はもう1配信だけ参加不可となり、それ以前のクールダウンは終了します。',
        'next_started': '配信{n}回目を開始しました。前回の当選者は引き続き参加できません。',
    },
}


def label(parent, text='', size=11, color=INK, bold=False, **kwargs):
    return tk.Label(parent, text=text, bg=kwargs.pop('bg', BG), fg=color,
                    font=(FONT, size, 'bold' if bold else 'normal'), **kwargs)


def button(parent, text, command, color=FIELD, fg=INK, **kwargs):
    return tk.Button(parent, text=text, command=command,
                     bg=color, fg=fg, activebackground=ACCENT, activeforeground=BG,
                     relief=tk.FLAT, bd=0, cursor='hand2',
                     font=(FONT, 10, 'bold'), padx=10, pady=7,
                     disabledforeground=MUTED, **kwargs)


class WheelUI:
    def __init__(self, root, directory):
        self.root = root
        self.store = WheelStore(directory)
        self.settings_path = self.store.folder / 'wheel_settings.json'
        self.lang = 'en'
        if self.settings_path.exists():
            try:
                saved = json.loads(self.settings_path.read_text(encoding='utf-8'))
                if saved.get('language') in TRANSLATIONS:
                    self.lang = saved['language']
            except (OSError, ValueError, TypeError):
                pass
        self.root.configure(bg=BG)
        self.icon_image = None
        try:
            self.icon_image = tk.PhotoImage(file=str(asset_path('redeem_wheel.png')))
            self.root.iconphoto(True, self.icon_image)
            if sys.platform == 'win32':
                self.root.iconbitmap(str(asset_path('redeem_wheel.ico')))
        except (OSError, tk.TclError):
            pass  # An unavailable icon must not stop the wheel from starting.
        self.pending_after = set()
        self.destroyed = False
        self.root.bind('<Destroy>', self._on_destroy)
        self.root.geometry('1250x805')
        self.root.minsize(990, 735)
        self.angle = 12.0
        self.spinning = False
        self.snapshot = []
        self.winner = None
        self.started = 0.0
        self.duration = 5.0
        self.start_angle = 0.0
        self.end_angle = 0.0
        self.display_window = None
        self.display_canvas = None
        self.display_info = None
        self.display_winner = None
        self.display_title = None
        self.last_stamp = self.store.stamp()
        self.last_roster_stamp = self.store.roster_stamp()
        self.status_var = tk.StringVar(value=self.t('ready'))
        self.search_var = tk.StringVar()
        self.last_winner = None
        self.visible_names = []
        self.check_vars = {}
        self.static_labels = {}
        self.static_buttons = {}

        outer = tk.Frame(root, bg=BG)
        outer.pack(fill=tk.BOTH, expand=True, padx=18, pady=12)
        header = tk.Frame(outer, bg=BG)
        header.pack(fill=tk.X, pady=(0, 12))
        self.title_label = label(header, '', 22, ACCENT, True)
        self.title_label.pack(side=tk.LEFT)
        self.stream_tag = label(header, '', 11, MUTED, True)
        self.stream_tag.pack(side=tk.RIGHT, padx=(10, 0))
        self.next_btn = button(header, '', self.next_stream, color='#4A536C')
        self.next_btn.pack(side=tk.RIGHT, padx=(8, 8))
        self.clear_btn = button(header, '', self.clear_entries, fg=MUTED)
        self.clear_btn.pack(side=tk.RIGHT, padx=4)
        self.lang_btn = button(header, '', self.toggle_language, color='#3E6C71')
        self.lang_btn.pack(side=tk.RIGHT, padx=(4, 5))

        body = tk.Frame(outer, bg=BG)
        body.pack(fill=tk.BOTH, expand=True)
        left = tk.Frame(body, bg=PANEL, highlightbackground='#353D50', highlightthickness=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 14))
        right = tk.Frame(body, bg=PANEL, width=412, highlightbackground='#353D50', highlightthickness=1)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        self.wheel_canvas = tk.Canvas(left, bg=PANEL, bd=0, highlightthickness=0)
        self.wheel_canvas.pack(fill=tk.BOTH, expand=True, padx=9, pady=9)
        self.wheel_canvas.bind('<Configure>', lambda _: self.render_wheels())
        self.winner_label = label(left, '', 13, ACCENT, True, bg=PANEL)
        self.winner_label.pack(pady=(0, 3))
        self.spin_btn = button(left, '', self.spin, color=ACCENT, fg=BG)
        self.spin_btn.pack(fill=tk.X, padx=24, pady=(10, 16))

        pad = tk.Frame(right, bg=PANEL)
        pad.pack(fill=tk.BOTH, expand=True, padx=16, pady=6)
        roster_header = tk.Frame(pad, bg=PANEL)
        roster_header.pack(fill=tk.X)
        self.find_label = label(roster_header, '', 11, ACCENT, True, bg=PANEL)
        self.find_label.pack(side=tk.LEFT)
        self.summary_label = label(roster_header, '', 9, MUTED, bg=PANEL)
        self.summary_label.pack(side=tk.RIGHT)
        self.find_help = label(pad, '', 9, MUTED, bg=PANEL)
        self.find_help.pack(anchor='w', pady=(3, 5))
        self.search_box = tk.Entry(pad, textvariable=self.search_var, bg=FIELD, fg=INK,
                                   insertbackground=INK, relief=tk.FLAT, font=(FONT, 11), bd=0)
        self.search_box.pack(fill=tk.X, ipady=5)
        self.search_box.bind('<Return>', lambda _: self.add_typed())
        self.search_var.trace_add('write', lambda *_: self.refresh_search(reset_scroll=True))

        # A real scrollable checklist, rather than a single-select Listbox.
        roster_frame = tk.Frame(pad, bg=FIELD)
        roster_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 4))
        self.roster_canvas = tk.Canvas(roster_frame, bg=FIELD, bd=0, highlightthickness=0,
                                        height=100)
        roster_scroll = tk.Scrollbar(roster_frame, orient='vertical', command=self.roster_canvas.yview)
        roster_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.roster_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.roster_canvas.configure(yscrollcommand=roster_scroll.set)
        self.roster_rows = tk.Frame(self.roster_canvas, bg=FIELD)
        self.roster_window_id = self.roster_canvas.create_window((0, 0), window=self.roster_rows, anchor='nw')
        self.roster_rows.bind('<Configure>', self._roster_resize)
        self.roster_canvas.bind('<Configure>', self._roster_width)
        # Only scroll this list while the pointer is over it.
        for widget in (self.roster_canvas, self.roster_rows):
            widget.bind('<MouseWheel>', self._roster_wheel)
            widget.bind('<Button-4>', self._roster_wheel)
            widget.bind('<Button-5>', self._roster_wheel)

        select_row = tk.Frame(pad, bg=PANEL)
        select_row.pack(fill=tk.X, pady=(0, 4))
        self.select_visible_btn = button(select_row, '', self.select_visible, fg=MUTED)
        self.select_visible_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.uncheck_btn = button(select_row, '', self.uncheck_all, fg=MUTED)
        self.uncheck_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))
        add_row = tk.Frame(pad, bg=PANEL)
        add_row.pack(fill=tk.X)
        self.add_btn = button(add_row, '', self.add_typed, color='#3E6C71')
        self.add_btn.pack(fill=tk.X, expand=True)
        self.selection_tip = label(pad, '', 8, MUTED, bg=PANEL)
        self.selection_tip.pack(anchor='w', pady=(4, 0))

        # Single roster is the source of truth: current entries are marked by
        # their checked boxes, no redundant list or extra Remove button.
        reload_row = tk.Frame(pad, bg=PANEL)
        reload_row.pack(fill=tk.X, pady=(6, 0))
        self.reload_btn = button(reload_row, '', self.reload_files, fg=MUTED)
        self.reload_btn.pack(side=tk.RIGHT)
        tk.Frame(pad, bg='#394358', height=1).pack(fill=tk.X, pady=(8, 8))
        self.controls_label = label(pad, '', 11, ACCENT, True, bg=PANEL)
        self.controls_label.pack(anchor='w')
        self.cooldown_help = label(pad, '', 9, MUTED, bg=PANEL, wraplength=345, justify=tk.LEFT)
        self.cooldown_help.pack(anchor='w', pady=(3, 5))
        self.obs_btn = button(pad, '', self.open_display)
        self.obs_btn.pack(fill=tk.X)

        footer = tk.Frame(outer, bg=BG)
        footer.pack(fill=tk.X, pady=(9, 0))
        self.footer_label = label(footer, '', 9, MUTED)
        self.footer_label.pack(side=tk.RIGHT)
        self.status = label(footer, '', 9, MUTED)
        self.status.pack(side=tk.LEFT)
        self.status.configure(textvariable=self.status_var, wraplength=690, justify=tk.LEFT)

        self._apply_language()
        self.refresh_search(reset_scroll=True)
        self.refresh_queue()
        self._schedule(750, self.poll_external)
        self.search_box.focus_set()

    def _schedule(self, delay_ms, callback):
        """Tie scheduled callbacks to this window's lifetime."""
        if self.destroyed:
            return
        def run():
            self.pending_after.discard(handle)
            if not self.destroyed:
                callback()
        handle = self.root.after(delay_ms, run)
        self.pending_after.add(handle)

    def _on_destroy(self, event):
        if event.widget is not self.root:
            return
        self.destroyed = True
        for handle in tuple(self.pending_after):
            try:
                self.root.after_cancel(handle)
            except tk.TclError:
                pass
        self.pending_after.clear()

    def t(self, key, **values):
        return TRANSLATIONS[self.lang][key].format(**values)

    def toggle_language(self):
        self.lang = 'ja' if self.lang == 'en' else 'en'
        try:
            atomic_write(self.settings_path, json.dumps({'language': self.lang}, ensure_ascii=False, indent=2) + '\n')
        except OSError as exc:
            self.set_status(str(exc), error=True)
        self._apply_language()
        self.refresh_search()
        self.refresh_queue()
        self.set_status(self.t('ready'))

    def _apply_language(self):
        self.root.title(self.t('controller_title'))
        for widget, key in (
            (self.title_label, 'title'), (self.next_btn, 'next_stream'),
            (self.clear_btn, 'clear_wheel'), (self.spin_btn, 'spin'),
            (self.find_label, 'find'), (self.find_help, 'find_help'),
            (self.select_visible_btn, 'select_visible'), (self.uncheck_btn, 'uncheck_all'),
            (self.add_btn, 'add_typed'), (self.selection_tip, 'selection_tip'),
            (self.reload_btn, 'reload'), (self.controls_label, 'controls'),
            (self.cooldown_help, 'cooldown_help'), (self.obs_btn, 'obs'),
            (self.footer_label, 'footer'),
        ):
            widget.configure(text=self.t(key))
        self.lang_btn.configure(text='日本語' if self.lang == 'en' else 'English')
        if self.display_window and self.display_window.winfo_exists():
            self.display_window.title(self.t('display_title'))
            self.display_title.config(text=self.t('title'))
        self._update_counts()

    def _roster_resize(self, _=None):
        self.roster_canvas.configure(scrollregion=self.roster_canvas.bbox('all'))

    def _roster_width(self, event):
        self.roster_canvas.itemconfigure(self.roster_window_id, width=event.width)

    def _roster_wheel(self, event):
        if getattr(event, 'num', None) == 4:
            amount = -3
        elif getattr(event, 'num', None) == 5:
            amount = 3
        else:
            amount = -int(event.delta / 120) * 3
        self.roster_canvas.yview_scroll(amount, 'units')
        return 'break'

    def _on_check(self, name, var):
        """A check is a file-backed wheel entry, not a pending selection."""
        if self.spinning:
            self.refresh_search()
            return
        desired = bool(var.get())
        try:
            # Preserve new names appended by Streamer.bot while the UI is open.
            self.store.sync_entries()
            if desired:
                added, rejected = self.store.add_names([name], add_to_roster=False)
                message = (self.t('added', name=added[0]) if added else
                           self._problem(*rejected[0]))
                error = not bool(added)
            else:
                removed = self.store.remove_name(name)
                message = self.t('removed', name=name) if removed else self.t('no_visible_entries')
                error = not removed
            self.last_stamp = self.store.stamp()
        except (OSError, UnicodeError) as exc:
            message = self.t('file_error', error=exc)
            error = True
        # The current entry file is the only source of checkbox state.
        # Redraw the checklist to update labels and enabled states immediately.
        self.refresh_search()
        self.refresh_queue()
        self.set_status(message, error=error)

    def refresh_search(self, reset_scroll=False):
        """Render checkboxes from wheel entries and preserve the scroll offset."""
        if not hasattr(self, 'roster_rows'):
            return
        canvas = self.roster_canvas
        old_offset = 0.0 if reset_scroll else max(0, canvas.canvasy(0))
        query = self.search_var.get().strip().lstrip('@').casefold()
        self.visible_names = [name for name in self.store.roster if query in name.casefold()]
        entry_keys = {name.casefold() for name in self.store.entries}
        for child in self.roster_rows.winfo_children():
            child.destroy()
        self.check_vars.clear()
        for name in self.visible_names:
            issue, value = self.store.name_issue(name)
            suffix = (self.t('in_wheel') if issue == 'duplicate' else
                      self.t('on_cooldown', n=value) if issue == 'cooldown' else '')
            var = tk.BooleanVar(value=name.casefold() in entry_keys)
            widget = tk.Checkbutton(
                self.roster_rows, text=name + suffix, variable=var,
                command=lambda n=name, v=var: self._on_check(n, v),
                bg=FIELD, fg=MUTED if issue == 'cooldown' else INK,
                activebackground=FIELD, activeforeground=INK,
                selectcolor=FIELD, disabledforeground=MUTED,
                highlightthickness=0, bd=0, relief=tk.FLAT, anchor='w',
                font=(FONT, 9), padx=6, pady=1,
                state=tk.DISABLED if issue == 'cooldown' or self.spinning else tk.NORMAL,
            )
            widget.pack(fill=tk.X)
            for ev in ('<MouseWheel>', '<Button-4>', '<Button-5>'):
                widget.bind(ev, self._roster_wheel)
            self.check_vars[name.casefold()] = var
        # Use pixel offset instead of a row index to avoid scroll jumps.
        canvas.update_idletasks()
        self._roster_resize()
        region = canvas.bbox('all')
        if region:
            height = max(1, region[3] - region[1])
            canvas.yview_moveto(min(1, old_offset / height))
        self._update_counts()

    def _update_counts(self):
        if not hasattr(self, 'select_visible_btn'):
            return
        self.stream_tag.configure(text=self.t('stream', n=self.store.stream))
        self.summary_label.configure(text=self.t('eligible_count', n=len(self.store.entries)))
        self.winner_label.configure(text=self.t('last_winner', name=self.last_winner or self.t('no_spins')))
        self.spin_btn.configure(state=tk.DISABLED if self.spinning or not self.store.entries else tk.NORMAL)
        self.add_btn.configure(state=tk.DISABLED if self.spinning else tk.NORMAL)
        self.select_visible_btn.configure(state=tk.DISABLED if self.spinning else tk.NORMAL)
        self.uncheck_btn.configure(state=tk.DISABLED if self.spinning else tk.NORMAL)
        if self.display_info:
            self.display_info.configure(text=self.t('display_info', stream=self.store.stream, count=len(self.store.entries)))
        if self.display_winner:
            self.display_winner.configure(text=self.t('display_winner', name=self.last_winner or self.t('no_spins')))

    def refresh_queue(self):
        "Redraw wheel and counts; checked roster is the only entry list."
        self._update_counts()
        self.render_wheels()

    def set_status(self, text, error=False):
        self.status_var.set(text)
        self.status.configure(fg=ROSE if error else MUTED)

    def select_visible(self):
        """Immediately add all eligible visible names with one disk write."""
        if self.spinning:
            return
        try:
            self.store.sync_entries()
            eligible = [name for name in self.visible_names
                        if self.store.name_issue(name)[0] is None]
            if not eligible:
                self.refresh_search()
                self.refresh_queue()
                self.set_status(self.t('no_visible'), error=True)
                return
            added, rejected = self.store.add_names(eligible, add_to_roster=False)
            self.last_stamp = self.store.stamp()
        except (OSError, UnicodeError) as exc:
            self.set_status(self.t('file_error', error=exc), error=True)
            return
        self.refresh_search()
        self.refresh_queue()
        self.set_status(self.t('selected_visible', added=len(added), skipped=len(rejected)))

    def uncheck_all(self):
        """Immediately remove visible checked names, without a cooldown."""
        if self.spinning:
            return
        try:
            self.store.sync_entries()
            visible = {name.casefold() for name in self.visible_names}
            to_remove = [name for name in self.store.entries if name.casefold() in visible]
            if not to_remove:
                self.refresh_search()
                self.refresh_queue()
                self.set_status(self.t('no_visible_entries'), error=True)
                return
            removed = self.store.remove_names(to_remove)
            self.last_stamp = self.store.stamp()
        except (OSError, UnicodeError) as exc:
            self.set_status(self.t('file_error', error=exc), error=True)
            return
        self.refresh_search()
        self.refresh_queue()
        self.set_status(self.t('cleared_checks', n=len(removed)))

    def _problem(self, name, issue, value):
        if issue == 'invalid':
            return self.t('invalid')
        if issue == 'cooldown':
            return self.t('cooldown', name=name, n=value)
        return self.t('duplicate', name=name)

    def add_typed(self):
        if self.spinning:
            return
        value = self.search_var.get().strip()
        try:
            self.store.sync_entries()
            added, rejected = self.store.add_names([value])
        except (OSError, UnicodeError) as exc:
            self.set_status(self.t('file_error', error=exc), error=True)
            return
        self.last_stamp = self.store.stamp()
        self.last_roster_stamp = self.store.roster_stamp()
        # Do not clear search after adding: that unexpectedly resets the list.
        self.refresh_search()
        self.refresh_queue()
        if added:
            self.set_status(self.t('added', name=added[0]))
            self.search_box.focus_set()
            self.search_box.select_range(0, tk.END)
        else:
            name, issue, value = rejected[0]
            self.set_status(self._problem(name, issue, value), error=True)

    def reload_files(self):
        if self.spinning:
            return
        try:
            self.store.reload_roster()
            _, rejected = self.store.sync_entries()
            self.last_stamp = self.store.stamp()
            self.last_roster_stamp = self.store.roster_stamp()
            self.refresh_search()
            self.refresh_queue()
            self.set_status(self.t('files_reloaded', n=rejected))
        except (OSError, UnicodeError) as exc:
            self.set_status(self.t('reload_error', error=exc), error=True)

    def poll_external(self):
        try:
            if not self.spinning:
                need_search = False
                if self.store.roster_stamp() != self.last_roster_stamp:
                    self.store.reload_roster()
                    self.last_roster_stamp = self.store.roster_stamp()
                    need_search = True
                if self.store.stamp() != self.last_stamp:
                    changed, rejected = self.store.sync_entries()
                    self.last_stamp = self.store.stamp()
                    if changed or rejected:
                        self.refresh_queue()
                        need_search = True
                        self.set_status(self.t('imported', n=rejected))
                if need_search:
                    self.refresh_search()
        except (OSError, UnicodeError) as exc:
            self.set_status(self.t('file_error', error=exc), error=True)
        self._schedule(750, self.poll_external)

    def spin(self):
        if self.spinning:
            return
        try:
            self.store.sync_entries()
        except (OSError, UnicodeError) as exc:
            self.set_status(self.t('spin_read_error', error=exc), error=True)
            return
        if not self.store.entries:
            self.refresh_queue()
            self.set_status(self.t('no_entries'), error=True)
            return
        self.snapshot = list(self.store.entries)
        self.winner = secrets.choice(self.snapshot)
        count = len(self.snapshot)
        win_i = self.snapshot.index(self.winner)
        step = 360.0 / count
        wanted_mod = (90.0 - (win_i + 0.5) * step) % 360.0
        extra = (wanted_mod - self.angle % 360.0) % 360.0
        self.start_angle = self.angle
        self.end_angle = self.angle + 360.0 * secrets.choice([6, 7, 8]) + extra
        self.started = time.monotonic()
        self.spinning = True
        self.last_stamp = self.store.stamp()
        self.set_status(self.t('spinning'))
        self.refresh_search()
        self.refresh_queue()
        self.tick()

    def tick(self):
        if not self.spinning:
            return
        p = min(1.0, (time.monotonic() - self.started) / self.duration)
        eased = 1.0 - (1.0 - p) ** 5
        self.angle = self.start_angle + (self.end_angle - self.start_angle) * eased
        self.render_wheels()
        if p < 1.0:
            self._schedule(25, self.tick)
            return
        self.angle %= 360
        try:
            self.store.pick_name(self.winner)
            self.last_stamp = self.store.stamp()
        except (OSError, UnicodeError) as exc:
            self.set_status(self.t('spin_save_error', name=self.winner, error=exc), error=True)
            self.spinning = False
            self.refresh_search()
            self.refresh_queue()
            return
        self.last_winner = self.winner
        # The wheel still shows the winning slice for 1.8 seconds; the roster
        # cooldown/eligibility and the queue update immediately.
        self.refresh_search()
        self.refresh_queue()
        self.set_status(self.t('winner_picked', name=self.winner, n=self.store.stream + 1))
        self._schedule(1800, self.finish_result)

    def finish_result(self):
        self.spinning = False
        self.snapshot = []
        self.refresh_search()
        self.refresh_queue()

    def clear_entries(self):
        if self.spinning or not self.store.entries:
            return
        if messagebox.askyesno(self.t('clear_title'), self.t('clear_confirm')):
            self.store.clear_entries()
            self.last_stamp = self.store.stamp()
            self.refresh_search()
            self.refresh_queue()
            self.set_status(self.t('entries_cleared'))

    def next_stream(self):
        if self.spinning:
            return
        if not messagebox.askyesno(self.t('next_title'), self.t('next_confirm', n=self.store.stream + 1)):
            return
        self.store.next_stream()
        self.last_stamp = self.store.stamp()
        self.last_winner = None
        self.refresh_search()
        self.refresh_queue()
        self.set_status(self.t('next_started', n=self.store.stream))

    def open_display(self):
        if self.display_window and self.display_window.winfo_exists():
            self.display_window.lift()
            return
        win = tk.Toplevel(self.root)
        win.title(self.t('display_title'))
        win.geometry('750x690')
        win.minsize(450, 460)
        win.configure(bg=BG)
        if self.icon_image is not None:
            try:
                win.iconphoto(False, self.icon_image)
                if sys.platform == 'win32':
                    win.iconbitmap(str(asset_path('redeem_wheel.ico')))
            except tk.TclError:
                pass
        self.display_title = label(win, self.t('title'), 21, ACCENT, True)
        self.display_title.pack(pady=(21, 3))
        self.display_info = label(win, '', 11, MUTED, True)
        self.display_info.pack()
        self.display_canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
        self.display_canvas.pack(fill=tk.BOTH, expand=True, padx=12)
        self.display_canvas.bind('<Configure>', lambda _: self.render_wheels())
        self.display_winner = label(win, '', 15, ACCENT, True)
        self.display_winner.pack(pady=(0, 23))
        self.display_window = win

        def close():
            win.destroy()
            self.display_window = None
            self.display_canvas = None
            self.display_info = None
            self.display_winner = None
            self.display_title = None

        win.protocol('WM_DELETE_WINDOW', close)
        self.refresh_queue()

    def render_wheels(self):
        if hasattr(self, 'wheel_canvas'):
            self.draw_wheel(self.wheel_canvas)
        if self.display_canvas:
            self.draw_wheel(self.display_canvas)

    def draw_wheel(self, canvas):
        if not canvas.winfo_exists():
            return
        canvas.delete('all')
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w < 100 or h < 100:
            return
        x, y = w / 2, h / 2 + 9
        radius = min(w * .45, h * .44, 315)
        box = (x - radius, y - radius, x + radius, y + radius)
        participants = self.snapshot if self.spinning else self.store.entries
        n = len(participants)
        canvas.create_oval(x-radius-7, y-radius-7, x+radius+7, y+radius+7,
                           fill='#111823', outline='#E2BB82', width=3)
        if not n:
            canvas.create_oval(*box, fill='#262D3E', outline='#495267', width=2)
            canvas.create_text(x, y-6, text=self.t('wheel_empty'), fill=INK,
                               font=(FONT, max(11, int(radius/11)), 'bold'))
            canvas.create_text(x, y+31, text=self.t('wheel_empty_help'), fill=MUTED,
                               font=(FONT, max(8, int(radius/23))))
        else:
            size = 360.0 / n
            for i, name in enumerate(participants):
                begin = (self.angle + i * size) % 360
                canvas.create_arc(*box, start=begin, extent=size, style=tk.PIESLICE,
                                  fill=COLORS[i % len(COLORS)], outline='#18202B', width=2 if n <= 40 else 1)
                if n <= 60 or (i % max(1, math.ceil(n/60)) == 0):
                    direction = math.radians(begin + size / 2)
                    text_r = radius * (0.63 if n <= 18 else 0.70)
                    tx = x + text_r * math.cos(direction)
                    ty = y - text_r * math.sin(direction)
                    short = name if len(name) <= 14 else name[:12] + '…'
                    font_size = max(8, min(12, int(radius / (17 if n <= 18 else 25))))
                    canvas.create_text(tx, ty, text=short, fill='#101822',
                                       font=(FONT, font_size, 'bold'),
                                       width=max(25, int(radius*.55)))
            center_radius = max(23, radius * .09)
            canvas.create_oval(x-center_radius, y-center_radius, x+center_radius, y+center_radius,
                               fill='#172131', outline=ACCENT, width=3)
            canvas.create_text(x, y, text=str(n), fill=ACCENT,
                               font=(FONT, max(10, int(center_radius*.65)), 'bold'))
        # A fixed downward-pointing triangular pointer at twelve o'clock.
        tip_y = y - radius + 10
        canvas.create_polygon(x-19, tip_y-28, x+19, tip_y-28, x, tip_y+12,
                              fill=ACCENT, outline='#231F24', width=2)
        canvas.create_oval(x-5, tip_y-26, x+5, tip_y-16, fill=BG, outline='')


def main():
    folder = data_directory()
    if len(sys.argv) >= 2:
        folder = Path(sys.argv[1]).resolve()
    try:
        root = tk.Tk()
        WheelUI(root, folder)
        root.mainloop()
    except (OSError, UnicodeError, ValueError) as error:
        print(f'Cannot start the wheel: {error}', file=sys.stderr)
        raise


if __name__ == '__main__':
    main()
