## Install

clone the git python -m pip install -e .

## Usage

Preview the default `\~/Downloads` folder:

```bash
tidy-downloads plan
```

Preview another folder:

```bash
tidy-downloads plan \~/Desktop/inbox
```

Apply the plan after confirming each run:

```bash
tidy-downloads apply \~/Downloads
```

For scripts or cron jobs, explicitly skip the prompt:

```bash
tidy-downloads apply \~/Downloads --yes
```

Reverse a run using the history file printed at the end:

```bash
tidy-downloads undo \~/Downloads/.tidy-downloads/history/20260101T120000Z.json
```

Dotfiles are skipped by default. Include them only when you really mean to:

```bash
tidy-downloads plan --include-hidden
```

## File groups

|Folder|Examples|
|-|-|
|Images|PNG, JPG, GIF, SVG, WEBP|
|Documents|PDF, DOCX, TXT, Markdown|
|Spreadsheets|CSV, XLSX, ODS|
|Archives|ZIP, TAR, GZ, 7Z, RAR|
|Audio|MP3, WAV, FLAC, M4A|
|Video|MP4, MOV, MKV, WEBM|
|Code|Python, JavaScript, TypeScript, HTML, CSS, JSON|
|Installers|DMG, PKG, DEB, RPM, EXE|
|Other|Anything not in the groups above|

If a destination already contains `example.pdf`, the new file becomes `example (1).pdf` instead of replacing the old one.

## 

