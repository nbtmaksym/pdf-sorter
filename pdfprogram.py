import os
import re
import shutil
import logging
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pypdf import PdfReader

PT_TO_MM = 0.3528

ROZMIARY = {
    "A0": (841, 1189),
    "A1": (594, 841),
    "A2": (420, 594),
    "A3": (297, 420),
    "A4": (210, 297),
    "A5": (148, 210),
    "A6": (105, 148),
}

FOLDER_MAPPING = {
    "A0": "A2",
    "A1": "A2",
    "A2": "A2",
    "A3": "A3",
    "A4": "A4",
    "A5": "A5",
    "A6": "A6",
    "NIEZNANY": "NIEZNANY",
}

NAZWA_PREFIKSY = [
    ("HEAA", "belki_dwuteowe"), ("HEM", "belki_dwuteowe"), ("HEB", "belki_dwuteowe"),
    ("HEA", "belki_dwuteowe"), ("IPE", "belki_dwuteowe"), ("IPN", "belki_dwuteowe"),
    ("HD ", "belki_dwuteowe"), ("HP ", "belki_dwuteowe"), ("UB", "belki_dwuteowe"),
    ("UC", "belki_dwuteowe"), ("UBP", "belki_dwuteowe"), ("W ", "belki_dwuteowe"),
    ("W1", "belki_dwuteowe"), ("W2", "belki_dwuteowe"), ("W3", "belki_dwuteowe"),
    ("W4", "belki_dwuteowe"), ("W5", "belki_dwuteowe"), ("W6", "belki_dwuteowe"),
    ("W8", "belki_dwuteowe"), ("S ", "belki_dwuteowe"),
    ("UPN", "ceowniki"), ("UPE", "ceowniki"),("U", "ceowniki"), ("UPA", "ceowniki"), ("UNP", "ceowniki"),
    ("PFC", "ceowniki"), ("MC", "ceowniki"), ("CH", "ceowniki"), ("BLU", "ceowniki"),
    ("L ", "katowniki"), ("L1", "katowniki"), ("L2", "katowniki"), ("L3", "katowniki"),
    ("L4", "katowniki"), ("L5", "katowniki"), ("L6", "katowniki"), ("L7", "katowniki"),
    ("L8", "katowniki"), ("L9", "katowniki"), ("EA", "katowniki"), ("UA", "katowniki"),
    ("BLL", "katowniki"),
    ("WT", "teowniki"), ("MT", "teowniki"), ("T ", "teowniki"), ("T1", "teowniki"),
    ("T2", "teowniki"), ("T3", "teowniki"),
    ("CFRHS", "rury_prostokat"), ("CFSHS", "rury_prostokat"), ("RHS", "rury_prostokat"),
    ("SHS", "rury_prostokat"), ("HSS", "rury_prostokat"), ("TR", "rury_prostokat"),
    ("CHS", "rury_okragle"), ("RO", "rury_okragle"), ("OB", "rury_okragle"),
    ("SO", "rury_okragle"), ("SH", "rury_okragle"), ("E ", "rury_okragle"),
    ("RU", "prety_okragle"), ("RND", "prety_okragle"), ("ROD", "prety_okragle"),
    ("PLT", "blachy"), ("PL", "blachy"), ("BL", "blachy"), ("FB", "blachy"), ("FL", "blachy"),("WI","blachownica"),
    ("ZED", "profile_specjalne"), ("ZETA", "profile_specjalne"), ("SIGMA", "profile_specjalne"),
    ("OMEGA", "profile_specjalne"), ("HAT", "profile_specjalne"), ("SF", "profile_specjalne"),
    ("Z ", "profile_specjalne"),
]


def _build_profile_patterns(prefixes):
    patterns = []
    for prefix, category in prefixes:
        requires_space = prefix.endswith(" ")
        p = prefix.rstrip()
        sep = r"\s" if requires_space else r"\s?"
        patterns.append(re.compile(r"\b" + re.escape(p) + sep + r"\d[\dxX.,]*\b", re.IGNORECASE))
    return patterns


PROFILE_PATTERNS = _build_profile_patterns(NAZWA_PREFIKSY)


def classify(width_mm, height_mm, tolerance=5):
    w, h = sorted([width_mm, height_mm])
    for name, (sw, sh) in ROZMIARY.items():
        if abs(w - sw) <= tolerance and abs(h - sh) <= tolerance:
            return name
    return "NIEZNANY"


def find_profile(text):
    text_up = text.upper()
    for pattern in PROFILE_PATTERNS:
        m = pattern.search(text_up)
        if m:
            return re.sub(r"\s+", "", m.group())
    return "NIEZNANY_PROFIL"


def unique_path(dest_folder, filename):
    dest = os.path.join(dest_folder, filename)
    if not os.path.exists(dest):
        return dest
    base, ext = os.path.splitext(filename)
    i = 1
    while True:
        new = os.path.join(dest_folder, f"{base}_{i}{ext}")
        if not os.path.exists(new):
            return new
        i += 1


def process_folder_by_format(input_folder, log_func):
    logging.basicConfig(
        filename=os.path.join(input_folder, "pdf_sorter.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        return 0, 0

    sukces, bledy = 0, 0

    for filename in pdf_files:
        filepath = os.path.join(input_folder, filename)
        try:
            reader = PdfReader(filepath)
            page = reader.pages[0]
            w_mm = float(page.mediabox.width) * PT_TO_MM
            h_mm = float(page.mediabox.height) * PT_TO_MM
            format_name = classify(w_mm, h_mm)
            folder_name = FOLDER_MAPPING[format_name]

            dest_folder = os.path.join(input_folder, folder_name)
            os.makedirs(dest_folder, exist_ok=True)
            dest_path = unique_path(dest_folder, filename)
            shutil.move(filepath, dest_path)

            dest_filename = os.path.basename(dest_path)
            extra = f" [wykryto: {format_name}]" if format_name != folder_name else ""
            info = f"OK  {filename} -> {folder_name}{extra} | {w_mm:.1f} x {h_mm:.1f} mm"
            if dest_filename != filename:
                info += f" (zapisano jako: {dest_filename})"
            log_func(info)
            logging.info(info)
            sukces += 1

        except Exception as e:
            msg = f"BLAD  {filename}: {e}"
            log_func(msg)
            logging.error(msg)
            bledy += 1

    return sukces, bledy
def process_folder_by_profile(input_folder, log_func):
    logging.basicConfig(
        filename=os.path.join(input_folder, "pdf_sorter_profil.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        return 0, 0

    sukces, bledy = 0, 0

    for filename in pdf_files:
        filepath = os.path.join(input_folder, filename)
        try:
            reader = PdfReader(filepath)
            page = reader.pages[0]
            w_mm = float(page.mediabox.width) * PT_TO_MM
            h_mm = float(page.mediabox.height) * PT_TO_MM
            format_name = classify(w_mm, h_mm)
            folder_name = FOLDER_MAPPING[format_name]

            text = page.extract_text() or ""
            profile_name = find_profile(text)

            dest_folder = os.path.join(input_folder, folder_name, profile_name)
            os.makedirs(dest_folder, exist_ok=True)
            dest_path = unique_path(dest_folder, filename)
            shutil.move(filepath, dest_path)

            dest_filename = os.path.basename(dest_path)
            info = f"OK  {filename} -> {folder_name}/{profile_name} | {w_mm:.1f} x {h_mm:.1f} mm"
            if dest_filename != filename:
                info += f" (zapisano jako: {dest_filename})"
            log_func(info)
            logging.info(info)
            sukces += 1

        except Exception as e:
            msg = f"BLAD  {filename}: {e}"
            log_func(msg)
            logging.error(msg)
            bledy += 1

    return sukces, bledy


def build_tab(parent, process_func, tytul_przycisku):
    frame_top = tk.Frame(parent)
    frame_top.pack(fill="x", pady=(10, 4), padx=10)

    tk.Label(frame_top, text="Folder z plikami PDF:").pack(anchor="w")

    folder_var = tk.StringVar()

    row = tk.Frame(frame_top)
    row.pack(fill="x", pady=(4, 0))
    tk.Entry(row, textvariable=folder_var, width=50).pack(side="left", padx=(0, 8))

    def select_folder():
        folder = filedialog.askdirectory(title="Wybierz folder z plikami PDF")
        if folder:
            folder_var.set(folder)

    tk.Button(row, text="Przeglądaj...", command=select_folder).pack(side="left")

    output = scrolledtext.ScrolledText(parent, width=70, height=16, state="disabled", font=("Consolas", 9))

    def log(msg):
        output.configure(state="normal")
        output.insert(tk.END, msg + "\n")
        output.see(tk.END)
        output.configure(state="disabled")

    def run():
        folder = folder_var.get().strip()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Błąd", "Wybierz poprawny folder!")
            return

        btn_run.configure(state="disabled")
        output.configure(state="normal")
        output.delete("1.0", tk.END)
        output.configure(state="disabled")

        pdf_files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
        if not pdf_files:
            messagebox.showwarning("Brak plików", "W wybranym folderze nie ma żadnych plików PDF.")
            btn_run.configure(state="normal")
            return

        log(f"Znaleziono {len(pdf_files)} plików PDF.\n")

        def task():
            sukces, bledy = process_func(folder, log)
            btn_run.configure(state="normal")
            if bledy == 0:
                messagebox.showinfo("Sukces", f"Gotowe!\n\nPrzeniesiono: {sukces} plików\nBłędy: {bledy}")
            else:
                messagebox.showwarning("Zakończono z błędami", f"Przeniesiono: {sukces} plików\nBłędy: {bledy}\n\nSzczegóły w logu poniżej.")

        threading.Thread(target=task, daemon=True).start()

    btn_run = tk.Button(parent, text=tytul_przycisku, command=run, width=24,
                         bg="#0078D4", fg="white", font=("Segoe UI", 10, "bold"))
    btn_run.pack(pady=(10, 8))

    tk.Label(parent, text="Log:").pack(anchor="w", padx=10)
    output.pack(padx=10, pady=(0, 10))


root = tk.Tk()
root.title("PDF Sorter")
root.resizable(False, False)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab_format = tk.Frame(notebook)
tab_profil = tk.Frame(notebook)

notebook.add(tab_format, text="Sortuj wg formatu")
notebook.add(tab_profil, text="Sortuj wg profilu")

build_tab(tab_format, process_folder_by_format, "▶  Start")
build_tab(tab_profil, process_folder_by_profile, "▶  Start profili")

root.mainloop()