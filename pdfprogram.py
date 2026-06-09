import os 
import shutil 
import logging 
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext,messagebox
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

def classify(width_mm,height_mm, tolerance=5):
    w,h = sorted([width_mm,height_mm])
    for name, (sw,sh) in ROZMIARY.items():
        if  abs(w-sw) <= tolerance and abs (h-sh) <= tolerance:
            return name
    return "NIEZNANY"

def unique_path(dest_folder,filename):
    dest = os.path.join(dest_folder, filename)
    if not os.path.exists(dest):
        return dest
    base, ext = os.path.splitext(filename)
    i=1
    while True: 
        new = os.path.join(dest_folder, f"{base}_{i}{ext}")
        if not os.path.exists(new):
            return new
        i += 1

def process_folder(input_folder,log_func):
    logging.basicConfig(
        filename=os.path.join(input_folder, "pdf_sorter.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )
    pdf_files= [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        return 0,0

    sukces, bledy= 0,0

    for filename in pdf_files:
        filepath = os.path.join(input_folder,filename)
        try:
            reader = PdfReader(filepath)
            page = reader.pages[0]
            w_mm= float(page.mediabox.width) * PT_TO_MM
            h_mm= float(page.mediabox.height) * PT_TO_MM
            format_name= classify(w_mm,h_mm)
            folder_name= FOLDER_MAPPING[format_name]
            orientation= "A4" if w_mm > h_mm else "A3"

            dest_folder= os.path.join(input_folder,folder_name)
            os.makedirs(dest_folder,exist_ok=True)
            dest_path=unique_path(dest_folder,filename)
            
            shutil.move(filepath,dest_path)

            dest_filename=os.path.basename(dest_path)
            extra= f"[Wykryto: {format_name}]" if format_name != folder_name else ""
            info = f"{filename} -> {folder_name}{extra} | {orientation} | {w_mm:.1f} x {h_mm:.1f} mm"
            if dest_filename != filename:
                info += f"(zapisano jako: {dest_filename})"
            log_func(info)
            logging.info(info)
            sukces+=1
        except Exception as e:
            msg = f"BLAD {filename}: {e}"
            log_func(msg)
            logging.error(f"{filename}: {e}")
            bledy+=1
    return sukces,bledy


#gui 
def select_folder():
    folder = filedialog.askdirectory(title="Wybierz folder z plikami PDF")
    if folder:
        folder_var.set(folder)

def log(msg):
    output.configure(state="normal")
    output.insert(tk.END,msg + "\n")
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
    
    pdf_files= [f for f in os.listdir(folder)if f.lower().endswith(".pdf")]
    if not pdf_files:
        messagebox.showwarning("brak plików pdf")
        btn_run.configure(state="normal")
        return
    log(f"Znaleziono {len(pdf_files)} plików PDF.\n")

    def task():
        sukces, bledy= process_folder(folder,log)
        btn_run.configure(state="normal")
        if bledy == 0 :
            messagebox.showinfo("Sukces", f"gotowe!\n\nPrzeniesiono: {sukces} plików\nBłędy: {bledy}")
        else:
            messagebox.showwarning("Zakończono z błędami", f"Przeniesiono: {sukces} plików\nBłędy: {bledy}")
    threading.Thread(target=task, daemon=True).start()

root = tk.Tk()
root.title("PDF Sorter")
root.resizable(False,False)
root.configure(padx=16, pady=16)

folder_var= tk.StringVar()
tk.Label(root, text="Folder z plikami PDF:").grid(row=0, column=0, sticky="w",pady=(0,4))

frame=tk.Frame(root)
frame.grid(row=1,column=0,columnspan=2,sticky="ew")
tk.Entry(frame,textvariable=folder_var,width=50).pack(side="left",padx=(0,8))
tk.Button(frame,text="Przeglądaj...", command=select_folder).pack(side="left")

btn_run=tk.Button(root,text="-> Start", command=run, width=20, bg="#0078D4", fg="white", font=("Segoe UI", 10, "bold"))
btn_run.grid(row=2,column=0,columnspan=2,pady=(14,10))

tk.Label(root,text="Log").grid(row=3,column=0,sticky="w")
output= scrolledtext.ScrolledText(root,width=66,height=16,state="disabled",font=("Consolas",9))
output.grid(row=4,column=0,columnspan=2)
root.mainloop()