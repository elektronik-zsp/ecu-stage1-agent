# ECU Stage 1 Agent

Windows desktop GUI prototype for inspecting ECU binary files and managing a constrained Stage 1 workflow. Python 3.11+.

> **Safety and scope:** This is a software prototype, not a validated calibration product. It does not contain real ECU map definitions or tuning prescriptions. Do not write modified files to a vehicle. Any future calibration work requires qualified validation on a suitable test setup. Emissions-system defeat requests are rejected. Checksum correction is intentionally not implemented.

## Run (Windows)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

The app is GUI-only. There is no command-line interface for operating on ECU files.

## Codespaces / Linux development

The GUI can be tested headlessly with Qt's offscreen platform. In Codespaces, run:

```bash
python -m pip install -r requirements.txt
QT_QPA_PLATFORM=offscreen pytest
```

A Codespace is suitable for core tests and GUI smoke tests, not for validating a native Windows desktop or producing a Windows executable. Build the Windows package on Windows.

## Tests and build

```bash
pytest
mypy core
```

On Windows, `build.bat` creates a windowed PyInstaller build under `dist/`. Check the packaged app on a Windows machine before distribution.

## Design

- `core/` contains deterministic, GUI-independent byte and validation logic.
- Original input is opened read-only; edits are applied to a separate in-memory working copy.
- Input CRC32/SHA-256 are retained in the project identity.
- Writes are limited to explicitly declared map regions; diffs flag undeclared modifications.
- No checksum correction is attempted. Saved files use `_stage1_NOCHK.bin` and show a warning.
- The initial SW database is intentionally empty. No map addresses or tuning values for real ECUs are supplied.
- The agent panel currently provides a safe local planning stub; it cannot edit bytes or autonomously invoke untrusted tools.
