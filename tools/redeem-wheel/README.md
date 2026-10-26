# Redeem Wheel (source review)

Offline English / Japanese streamer roulette with a persistent viewer roster, checkbox entry control, an OBS display, and one-stream winner cooldown.

## Current distribution status

**Do not redistribute the previously built RedeemWheel.exe yet.** On 26 October 2026, the submitted Windows executable was flagged by **8 of 70 VirusTotal scanners**, including Microsoft Defender (Trojan:Win32/Wacatac.C!ml) and CrowdStrike. Those alerts could be false positives caused by packaging, but this has not been verified.

The original flagged EXE is intentionally **not hosted here**. A detection ratio is not a safety certificate, and a clean scan of a different build does not validate that old EXE.

## For reviewers and streamers

- The app runs locally and does not require Twitch credentials.
- One viewer per line in `names.txt`. Check a name to add it to the wheel immediately; uncheck to remove without cooldown.
- Winners are removed and cannot participate again this stream or next stream, but can return in the following stream.
- Current wheel entries are stored in `wheel_entries.txt`. `state.json` and `wheel_settings.json` are generated locally.
- Choose **日本語** or **English** in the app to switch languages.
- A separate window can be captured by OBS.

## Before any Windows release

Audit the Python source, run tests, build on a clean Windows machine, scan the **new** EXE, and investigate any alerts. For lower false-positive risk, consider PyInstaller `--onedir` rather than `--onefile`; it is not a guarantee. Code signing can help establish publisher identity, but is not proof that software is harmless.

This subdirectory is a source-review staging area in an existing repository. It is not a security endorsement or an EXE release.