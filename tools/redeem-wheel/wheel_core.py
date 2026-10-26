"""Storage and stream rules for the redeem wheel. No third-party libraries."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


def clean_name(value: str) -> str:
    """Keep a single, human-readable name (no newlines/control characters)."""
    if not isinstance(value, str):
        return ""
    value = value.strip().lstrip('@').strip()
    if not value or len(value) > 45 or any(ord(char) < 32 or ord(char) == 127 for char in value):
        return ""
    return value


def unique_names(names):
    seen = set()
    result = []
    for raw in names:
        name = clean_name(raw)
        if name and name.casefold() not in seen:
            seen.add(name.casefold())
            result.append(name)
    return result


def read_names(path: Path):
    if not path.exists():
        return []
    # utf-8-sig also accepts ordinary utf-8 and files written by Windows Notepad.
    return unique_names(path.read_text(encoding='utf-8-sig').splitlines())


def atomic_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '_', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(content)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


class WheelStore:
    """A simple folder of interoperable .txt files and persistent cooldown data.

    Rule: a name selected in stream N cannot be added again in streams N or N+1.
    It becomes eligible at stream N+2.
    """

    def __init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.roster_path = self.folder / 'names.txt'
        self.entries_path = self.folder / 'wheel_entries.txt'
        self.state_path = self.folder / 'state.json'
        self.roster_path.touch(exist_ok=True)
        self.entries_path.touch(exist_ok=True)
        self.roster = read_names(self.roster_path)
        self.stream = 1
        self.cooldowns = {}
        self.history = []
        self.entries = []
        self._load_state()
        self.sync_entries()

    def _load_state(self):
        if not self.state_path.exists():
            return
        data = json.loads(self.state_path.read_text(encoding='utf-8'))
        self.stream = max(1, int(data.get('stream', 1)))
        self.cooldowns = {str(k).casefold(): int(v) for k, v in data.get('cooldowns', {}).items()}
        self.history = list(data.get('history', []))[-200:]

    def save_state(self):
        atomic_write(self.state_path, json.dumps({
            'stream': self.stream,
            'cooldowns': self.cooldowns,
            'history': self.history[-200:],
        }, ensure_ascii=False, indent=2) + '\n')

    def _save_roster(self):
        atomic_write(self.roster_path, ''.join(n + '\n' for n in self.roster))

    def _save_entries(self):
        atomic_write(self.entries_path, ''.join(n + '\n' for n in self.entries))

    def name_issue(self, name):
        """Machine-readable eligibility reason for translated user interfaces."""
        name = clean_name(name)
        if not name:
            return 'invalid', None
        blocked_until = self.cooldowns.get(name.casefold(), 0)
        if self.stream <= blocked_until:
            return 'cooldown', blocked_until
        if any(n.casefold() == name.casefold() for n in self.entries):
            return 'duplicate', None
        return None, None

    def check_name(self, name):
        name = clean_name(name)
        issue, value = self.name_issue(name)
        if issue == 'invalid':
            return 'Please enter one name (maximum 45 characters).'
        if issue == 'cooldown':
            return f'{name} is on cooldown through stream {value}.'
        if issue == 'duplicate':
            return f'{name} is already in the wheel.'
        return ''

    def add_names(self, raw_names, *, add_to_roster=True):
        """Add a batch with one write per file. Returns (added, rejected).

        rejected contains (name, issue, value) tuples. Repeated names in the
        batch are treated as duplicates. The caller must sync external files
        before applying changes, as it does for single additions.
        """
        added, rejected = [], []
        entry_keys = {n.casefold() for n in self.entries}
        roster_keys = {n.casefold() for n in self.roster}
        roster_changed = False
        for raw in raw_names:
            name = clean_name(raw)
            key = name.casefold()
            if not name:
                rejected.append((str(raw), 'invalid', None))
            elif self.stream <= self.cooldowns.get(key, 0):
                rejected.append((name, 'cooldown', self.cooldowns[key]))
            elif key in entry_keys:
                rejected.append((name, 'duplicate', None))
            else:
                self.entries.append(name)
                entry_keys.add(key)
                added.append(name)
                if add_to_roster and key not in roster_keys:
                    self.roster.append(name)
                    roster_keys.add(key)
                    roster_changed = True
        if roster_changed:
            self._save_roster()
        if added:
            self._save_entries()
        return added, rejected

    def add_name(self, raw, *, add_to_roster=True):
        added, rejected = self.add_names([raw], add_to_roster=add_to_roster)
        if added:
            return True, f'Added {added[0]}.'
        name, issue, value = rejected[0]
        if issue == 'invalid':
            return False, 'Please enter one name (maximum 45 characters).'
        if issue == 'duplicate':
            return False, f'{name} is already in the wheel.'
        return False, f'{name} is on cooldown through stream {value}.'

    def sync_entries(self):
        """Read changes made to wheel_entries.txt outside this program.

        Invalid, duplicate, and cooldown names are excluded and the file is
        normalized, preventing those names from silently entering the wheel.
        """
        incoming = read_names(self.entries_path)
        permitted = [n for n in incoming if self.stream > self.cooldowns.get(n.casefold(), 0)]
        filtered = len(incoming) - len(permitted)
        changed = permitted != self.entries
        self.entries = permitted
        if filtered:
            self._save_entries()
        return changed, filtered

    def reload_roster(self):
        self.roster = read_names(self.roster_path)

    def remove_names(self, raw_names):
        """Remove checked names in a batch, saving once and without cooldowns."""
        keys = {name.casefold() for raw in raw_names if (name := clean_name(raw))}
        removed = [name for name in self.entries if name.casefold() in keys]
        if removed:
            self.entries = [name for name in self.entries if name.casefold() not in keys]
            self._save_entries()
        return removed

    def remove_name(self, raw):
        return bool(self.remove_names([raw]))

    def pick_name(self, winner):
        """Commit a winner at the END of animation, reloading external additions."""
        self.sync_entries()
        winner = clean_name(winner)
        self.remove_name(winner)
        self.cooldowns[winner.casefold()] = self.stream + 1
        self.history.append({'name': winner, 'stream': self.stream})
        self.save_state()
        # Removes any external duplicate of the winner even if it appeared
        # during the animation, and enforces cooldown on further polling.
        self.sync_entries()

    def next_stream(self):
        self.stream += 1
        self.entries = []
        self._save_entries()
        # Keep current/next stream cooldowns, discard expired cooldown data.
        self.cooldowns = {key: stream for key, stream in self.cooldowns.items() if stream >= self.stream}
        self.save_state()

    def clear_entries(self):
        self.entries = []
        self._save_entries()

    def roster_stamp(self):
        try:
            stat = self.roster_path.stat()
            return stat.st_mtime_ns, stat.st_size
        except FileNotFoundError:
            return None

    def stamp(self):
        try:
            stat = self.entries_path.stat()
            return stat.st_mtime_ns, stat.st_size
        except FileNotFoundError:
            return None
