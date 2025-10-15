from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, NameObject, FloatObject

def modify_linewidths(input_pdf, output_pdf, min_width=5, logger=print):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page_num, page in enumerate(reader.pages, start=1):
        contents = page.get_contents()
        if contents is None:
            writer.add_page(page)
            continue

        # Parse content stream into operator sequence
        content = ContentStream(contents, reader)

        modified = False
        for operands, operator in content.operations:
            if operator == b"w":  # 'set line width' operator
                try:
                    if float(operands[0]) < min_width:
                        # logger(f"Page {page_num}: {operands[0]} -> {min_width}")
                        operands[0] = FloatObject(min_width)  # <-- use PDF number object
                        modified = True
                except Exception as e:
                    logger(f"Page {page_num}: error reading line width ({e})")

        if modified:
            # Replace the page’s content with updated one
            page[NameObject("/Contents")] = writer._add_object(content)

        # Add page to writer first
        writer.add_page(page)

        # Re-compress content streams after the page is part of the writer
        try:
            writer.pages[-1].compress_content_streams()
        except Exception as e:
            logger(f"Compression warning page {page_num}: {e}")

    with open(output_pdf, "wb") as f:
        writer.write(f)

    logger(f"Saved modified PDF: {output_pdf}")

# GUI Front End
import os
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Attempt drag & drop support
_dnd_available = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _dnd_available = True
except Exception:
    pass

log_queue = queue.Queue()

def safe_log(msg):
    log_queue.put(msg)

def process_log_async(text_widget):
    try:
        while True:
            msg = log_queue.get_nowait()
            text_widget.configure(state="normal")
            text_widget.insert("end", msg + "\n")
            text_widget.see("end")
            text_widget.configure(state="disabled")
    except queue.Empty:
        pass
    text_widget.after(150, lambda: process_log_async(text_widget))

def unique_old_name(path):
    base, ext = os.path.splitext(path)
    candidate = f"{base}_old{ext}"
    counter = 1
    while os.path.exists(candidate):
        candidate = f"{base}_old({counter}){ext}"
        counter += 1
    return candidate

def process_files(file_paths, min_width, ui_elements):
    progress_bar, run_button = ui_elements
    total = len(file_paths)
    errors = 0
    for idx, original in enumerate(file_paths, start=1):
        safe_log(f"\nProcessing: {original}")
        if not os.path.isfile(original):
            safe_log("  Skipped (not a file).")
            continue
        try:
            old_path = unique_old_name(original)
            # Rename original first
            os.rename(original, old_path)
            safe_log(f"  Renamed original -> {old_path}")
            try:
                modify_linewidths(old_path, original, min_width=min_width, logger=safe_log)
            except Exception as inner:
                safe_log(f"  Error modifying: {inner}")
                # Attempt rollback
                if os.path.exists(old_path) and not os.path.exists(original):
                    os.rename(old_path, original)
                    safe_log("  Rolled back original file.")
                errors += 1
            else:
                safe_log("  Replacement complete.")
        except Exception as e:
            safe_log(f"  Fatal error: {e}")
            errors += 1
        progress_bar["value"] = (idx / total) * 100
    safe_log("\nDone.")
    if errors:
        safe_log(f"Completed with {errors} error(s).")
    run_button.configure(state="normal")

def start_processing(selected_files_var, width_var, progress_bar, run_button):
    files = selected_files_var.get().split("|")
    files = [f for f in files if f.strip()]
    if not files:
        messagebox.showwarning("No files", "Select or drop at least one PDF.")
        return
    try:
        mw = float(width_var.get())
        if mw <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid value", "Minimum line weight must be a positive number.")
        return
    run_button.configure(state="disabled")
    progress_bar["value"] = 0
    threading.Thread(target=process_files, args=(files, mw, (progress_bar, run_button)), daemon=True).start()

def add_files(selected_files_var):
    paths = filedialog.askopenfilenames(title="Select PDF files", filetypes=[("PDF files","*.pdf")])
    if not paths:
        return
    current = selected_files_var.get().split("|") if selected_files_var.get() else []
    current_set = {c for c in current if c}
    for p in paths:
        current_set.add(p)
    selected_files_var.set("|".join(sorted(current_set)))

def clear_files(selected_files_var):
    selected_files_var.set("")

def build_gui():
    root_cls = TkinterDnD.Tk if _dnd_available else tk.Tk
    root = root_cls()
    root.title("PDF Hairline Fix")
    root.geometry("760x520")

    main = ttk.Frame(root, padding=10)
    main.pack(fill="both", expand=True)

    top_row = ttk.Frame(main)
    top_row.pack(fill="x")

    ttk.Label(top_row, text="Minimum line width:").pack(side="left")
    width_var = tk.StringVar(value="3")
    width_entry = ttk.Entry(top_row, width=8, textvariable=width_var)
    width_entry.pack(side="left", padx=(4,12))

    selected_files_var = tk.StringVar()

    def refresh_file_listbox():
        listbox.delete(0, "end")
        files = selected_files_var.get().split("|")
        for f in files:
            if f.strip():
                listbox.insert("end", f)

    files_frame = ttk.LabelFrame(main, text="Selected PDF Files (drag & drop or Add)")
    files_frame.pack(fill="both", expand=True, pady=8)

    listbox = tk.Listbox(files_frame, height=10, selectmode="extended")
    listbox.pack(fill="both", expand=True, padx=5, pady=5)

    if _dnd_available:
        def drop(event):
            raw = event.data
            # Windows style: {path1} {path2}
            parts = []
            current = ""
            in_brace = False
            for ch in raw:
                if ch == "{":
                    in_brace = True
                    current = ""
                elif ch == "}":
                    in_brace = False
                    parts.append(current)
                    current = ""
                elif ch == " " and not in_brace:
                    if current:
                        parts.append(current)
                        current = ""
                else:
                    current += ch
            if current:
                parts.append(current)
            pdfs = [p for p in parts if p.lower().endswith(".pdf")]
            if not pdfs:
                safe_log("No PDF files detected in drop.")
                return
            existing = selected_files_var.get().split("|") if selected_files_var.get() else []
            new_set = {e for e in existing if e}
            for p in pdfs:
                new_set.add(p)
            selected_files_var.set("|".join(sorted(new_set)))
            refresh_file_listbox()
        listbox.drop_target_register(DND_FILES)
        listbox.dnd_bind("<<Drop>>", drop)
    else:
        placeholder = ttk.Label(files_frame, text="(Install tkinterdnd2 for drag & drop support)")
        placeholder.pack(pady=3)

    buttons_row = ttk.Frame(main)
    buttons_row.pack(fill="x", pady=(0,8))
    ttk.Button(buttons_row, text="Add PDFs...", command=lambda: [add_files(selected_files_var), refresh_file_listbox()]).pack(side="left")
    ttk.Button(buttons_row, text="Remove Selected", command=lambda: remove_selected(listbox, selected_files_var, refresh_file_listbox)).pack(side="left", padx=4)
    ttk.Button(buttons_row, text="Clear All", command=lambda: [clear_files(selected_files_var), refresh_file_listbox()]).pack(side="left")

    progress_bar = ttk.Progressbar(main, mode="determinate")
    progress_bar.pack(fill="x", pady=(4,4))

    run_button = ttk.Button(main, text="Run Conversion", command=lambda: start_processing(selected_files_var, width_var, progress_bar, run_button))
    run_button.pack(fill="x")

    log_frame = ttk.LabelFrame(main, text="Log")
    log_frame.pack(fill="both", expand=True, pady=(8,0))
    log_text = tk.Text(log_frame, wrap="word", height=10, state="disabled")
    log_text.pack(fill="both", expand=True)
    process_log_async(log_text)

    def sync_selection(event):
        # Keep variable aligned if user deletes entries manually (not typical)
        pass

    listbox.bind("<<ListboxSelect>>", sync_selection)

    def on_close():
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)

    return root

def remove_selected(listbox, selected_files_var, refresh_cb):
    selections = list(listbox.curselection())
    if not selections:
        return
    files = [f for f in selected_files_var.get().split("|") if f]
    remaining = [f for idx, f in enumerate(files) if idx not in selections]
    selected_files_var.set("|".join(remaining))
    refresh_cb()

if __name__ == "__main__":
    try:
        app = build_gui()
        app.mainloop()
    except Exception as e:
        print(f"Failed to start GUI: {e}")
