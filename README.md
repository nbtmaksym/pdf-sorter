# PDF Sorter – Automatic PDF Page-Size Classifier

A desktop tool that automatically scans a folder of PDF files, detects their page size (A0–A6), and sorts them into named subfolders. Built with Python and tkinter, packaged as a standalone `.exe` for use at Elmo S.A.

## Features

- Detects PDF page sizes: A0, A1, A2, A3, A4, A5, A6
- Automatically creates subfolders and moves files accordingly
- Business rule: A0 and A1 files are sorted into the A2 folder (with log annotation)
- Handles landscape orientation and mixed-page documents
- Real-time scrollable log output in the GUI
- Success/error popups on completion
- Packaged as a standalone `.exe` — no Python required

## Tech Stack

- **Python 3** · **tkinter** · **pypdf**
- **PyInstaller** (`.exe` packaging)

## Getting Started

### Option 1 — Run as .exe

Download the latest release from the [Releases](../../releases) page and run `pdf_sorter.exe` directly.

### Option 2 — Run from source

```bash
git clone https://github.com/nbtmaksym/pdf_sorter.git
cd pdf_sorter

pip install pypdf
python pdf_sorter.py
```

### Option 3 — Build .exe yourself

```bash
pip install pyinstaller pypdf
pyinstaller --onefile --noconsole pdf_sorter.py
```

## How It Works

1. Select a folder using the "Przeglądaj..." button
2. Click "Start"
3. The tool scans all `.pdf` files in the folder
4. Each file is classified by page size and moved to the matching subfolder:

```
input_folder/
├── A2/          ← A2, A1, and A0 files go here
├── A3/
├── A4/
└── A5/
```

5. The log shows each file's detected size and destination

## Business Rules

| Detected Size | Target Folder | Note |
|---------------|--------------|-------|
| A0 | A2 | Logged as "A0 → A2" |
| A1 | A2 | Logged as "A1 → A2" |
| A2 | A2 | |
| A3 | A3 | |
| A4 | A4 | |
| A5 | A5 | |

## Screenshots

<img width="638" height="513" alt="image" src="https://github.com/user-attachments/assets/2ca57f6e-8590-488f-9a63-2884be4f4a0e" />


## Author

**Maksym Jagodzinski** — [github.com/nbtmaksym](https://github.com/nbtmaksym)
