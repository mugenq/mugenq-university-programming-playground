# Redeem Wheel v4 / 抽選ルーレット

Offline streamer spinning wheel with **instant checkbox entry**, a bilingual **English / 日本語** interface, a separate OBS display, and winner cooldowns. The application does not require Twitch credentials or a network connection.

## Security and distribution notice (26 October 2026)

**Do not redistribute the previously built `RedeemWheel.exe` yet.** That Windows executable was flagged by **8/70 VirusTotal vendors**, including Microsoft Defender (Trojan:Win32/Wacatac.C!ml) and CrowdStrike. These may be false positives, especially with a PyInstaller one-file executable, **but that is not established**.

The flagged binary is **not included** in this repository. This code was posted for auditability, not as a declaration that any existing executable is safe. Independently review the source, create a fresh Windows build, submit the **new** executable to scanners, and investigate any remaining detections before distributing it to streamers.

## Running from source (Windows)

1. Install [Python 3](https://www.python.org/downloads/windows/), including Tkinter (standard installer).
2. Download this folder using Git or GitHub's **Code → Download ZIP** for the parent repository.
3. From `tools/redeem-wheel`, double-click `start_wheel.bat`, or use `py -3 redeem_wheel.py`.
4. Put one username per line in `names.txt` (automatically created when missing).

Python source requires no third-party packages to run.

## Building an EXE (unverified output)

On Windows double-click `build_windows_exe.bat`. It installs PyInstaller and builds `dist/RedeemWheel.exe`. Alternatively, GitHub **Actions → Redeem Wheel Windows build (manual review only) → Run workflow** builds an artifact on Windows.

**The executable produced by these methods is not certified safe.** It is provided for independent building and investigation, not for automatic public release. Consider experimenting with PyInstaller `--onedir` to compare detections; it does not guarantee a clean scan. Do not ignore antivirus warnings or tell viewers to disable security software.

The included skyline icon is a reduced-size version of the original provided PNG. The full-resolution icon remains in the local v4 ZIP.

## Controls

- **ROSTER / 視聴者リスト:** all names are visible when the search box is empty. Check a viewer to add them immediately; uncheck to remove without cooldown. Scrolling is preserved as entries change. **Add visible / Remove visible** support bulk changes.
- **Spin:** chooses one eligible winner, removes them from the wheel, and saves the result.
- **Cooldown:** winner in stream N cannot enter again in stream N or N+1. They become eligible in stream N+2.
- **NEXT STREAM / 次の配信へ:** clears current entries and advances cooldowns.
- **STREAM CONTROLS / 配信操作:** opens a separate display window suitable for OBS capture.
- **Language button:** switches the entire UI between English and Japanese, saved between sessions.

## Local files

| File | Purpose |
|---|---|
| `names.txt` | Viewer roster (one username per line) |
| `wheel_entries.txt` | Current wheel entries (optional text-file integration point) |
| `state.json` | Saved stream number, winners and cooldowns |
| `wheel_settings.json` | Language preference |
| `assets/redeem_wheel.png` and `assets/redeem_wheel.ico` | Custom application artwork |

These local data files are not tracked in Git. Do not commit real viewer lists to a public repository without permission.

## Tests

Run `python -m unittest discover -v`. The source has been tested in a virtual Linux desktop (18 regression tests). The Windows executable and Twitch integration have **not** been independently verified. Linux GUI tests require an X display, e.g. `xvfb-run -a python -m unittest discover -v`.
