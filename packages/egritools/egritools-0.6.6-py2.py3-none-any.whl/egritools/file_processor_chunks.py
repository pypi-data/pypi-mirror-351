"""
Chunking File Processor GUI

Processes a single large .txt file.

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.1"


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import re
import requests
import time
from threading import Thread
from lmstudio import get_models
from datetime import datetime

# ========== Chunking Functions ==========
def read_and_chunk(file_path, max_chars_per_chunk=6000, overlap_chars=500):
    chunks = []
    buffer = ""

    with open(file_path, 'rb') as uploaded_file:
        while True:
            chunk = uploaded_file.read(1024 * 64)
            if not chunk:
                break
            buffer += chunk.decode('utf-8')

            while len(buffer) >= max_chars_per_chunk:
                piece = buffer[:max_chars_per_chunk]
                chunks.append(piece)
                buffer = buffer[max_chars_per_chunk - overlap_chars:]

    if buffer:
        chunks.append(buffer)

    return chunks

def call_llm_with_retry(server_url, model_name, system_prompt, user_content, retries=3, delay=5):
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    }
    for attempt in range(retries):
        try:
            response = requests.post(f"{server_url}/v1/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e

def process_chunks_original(file_path, server_url, model_name, max_chars, overlap_chars, summarize_first, output_dir, progress_var, status_text):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        chunks = read_and_chunk(file_path, max_chars, overlap_chars)
    except Exception as e:
        messagebox.showerror("Error reading file", str(e))
        return

    mega_dataset = []
    total_chunks = len(chunks)

    for idx, chunk in enumerate(chunks):
        try:
            status_text.set(f"Processing chunk {idx+1}/{total_chunks}...")

            if summarize_first:
                summary_prompt = "Summarize the following text into facts, return each new fact on a new line. Ensure no fact is left out. Ensure each fact references its topic or item by name. If there are crafting recipes ensure they are described in one neat sentence. Do not use any tables or extra text formatting. do not include any instructions in your output:"
                summary = call_llm_with_retry(server_url, model_name, summary_prompt, chunk)
                input_for_qa = summary
            else:
                input_for_qa = chunk

            qa_prompt = "Create a list of question and answer pairs solely using the following text as the source ensuring you only output the question and answer pairs. Do not output any instructions. Use only Q: and A: to mark the start of them.:"
            qa_output = call_llm_with_retry(server_url, model_name, qa_prompt, input_for_qa)

            chunk_filename = os.path.join(output_dir, f"chunk_{idx+1:03d}.json")
            with open(chunk_filename, "w", encoding="utf-8") as f:
                json.dump({"chunk_id": idx+1, "qa_pairs": qa_output}, f, indent=4)

            mega_dataset.append({"chunk_id": idx+1, "qa_pairs": qa_output})

        except Exception as e:
            with open(os.path.join(output_dir, "failed_chunks.log"), "a", encoding="utf-8") as log_file:
                log_file.write(f"Chunk {idx+1} failed: {e}\n")

        progress_var.set((idx + 1) / total_chunks * 100)

    mega_filename = os.path.join(output_dir, "all_data_merged.json")
    with open(mega_filename, "w", encoding="utf-8") as f:
        json.dump(mega_dataset, f, indent=4)

    status_text.set(f"All chunks processed! Output saved to {output_dir}.")
    messagebox.showinfo("Success", "All chunks processed successfully!")

def process_chunks(file_path, server_url, model_name, max_chars, overlap_chars, summarize_first, output_dir, progress_var, status_text):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create a subfolder for summaries with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_dir = os.path.join(output_dir, f"summaries_{timestamp}")
    if summarize_first:
        os.makedirs(summary_dir, exist_ok=True)

    try:
        chunks = read_and_chunk(file_path, max_chars, overlap_chars)
    except Exception as e:
        messagebox.showerror("Error reading file", str(e))
        return

    mega_dataset = []
    total_chunks = len(chunks)

    for idx, chunk in enumerate(chunks):
        try:
            status_text.set(f"Processing chunk {idx+1}/{total_chunks}...")

            if summarize_first:
                summary_prompt = "Summarize the following text:"
                summary = call_llm_with_retry(server_url, model_name, summary_prompt, chunk)
                input_for_qa = summary

                # Save summary
                summary_filename = os.path.join(summary_dir, f"summary_chunk_{idx+1:03d}.txt")
                with open(summary_filename, "w", encoding="utf-8") as sf:
                    sf.write(summary)
            else:
                input_for_qa = chunk

            qa_prompt = "Create a list of question and answer pairs based on the following text ensuring you only output the question and answer pairs. If a question does not have an answer do not include it. Use only Q: and A: to mark the start of them.:"
            qa_output = call_llm_with_retry(server_url, model_name, qa_prompt, input_for_qa)

            chunk_filename = os.path.join(output_dir, f"chunk_{idx+1:03d}.json")
            with open(chunk_filename, "w", encoding="utf-8") as f:
                json.dump({"chunk_id": idx+1, "qa_pairs": qa_output}, f, indent=4)

            mega_dataset.append({"chunk_id": idx+1, "qa_pairs": qa_output})

        except Exception as e:
            with open(os.path.join(output_dir, "failed_chunks.log"), "a", encoding="utf-8") as log_file:
                log_file.write(f"Chunk {idx+1} failed: {e}\n")

        progress_var.set((idx + 1) / total_chunks * 100)

    mega_filename = os.path.join(output_dir, "all_data_merged.json")
    with open(mega_filename, "w", encoding="utf-8") as f:
        json.dump(mega_dataset, f, indent=4)

    status_text.set(f"All chunks processed! Output saved to {output_dir}.")
    messagebox.showinfo("Success", "All chunks processed successfully!")

# ========== Cleaning Functions ==========
def clean_text(text):
    text = re.sub(r'\*\*Q&A Pair \d+\*\*', '', text)
    text = re.sub(r'\n\s*\*+\s*', '\n', text)
    text = re.sub(r'\n\s*\d+\.\s*', '\n', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()

def post_process_chunks(chunks_folder="./outputs", output_file="./final_dataset.json"):
    final_dataset = []
    skipped_chunks = []

    for idx, filename in enumerate(sorted(os.listdir(chunks_folder))):
        if filename.startswith("chunk_") and filename.endswith(".json"):
            filepath = os.path.join(chunks_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                qa_text = data.get("qa_pairs", "")

                qa_matches = re.findall(
                    r"(?:\*\*)?Q:(?:\*\*)?\s*(.*?)\s*(?:\*\*)?A:(?:\*\*)?\s*(.*?)(?=(?:\n?(?:\*\*)?Q:|\Z))",
                    qa_text,
                    flags=re.DOTALL
                )

                if not qa_matches:
                    skipped_chunks.append(filename)
                    continue

                for question, answer in qa_matches:
                    final_dataset.append({
                        "question": clean_text(question),
                        "answer": clean_text(answer)
                    })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, indent=4)

    return len(final_dataset), skipped_chunks, output_file

# ========== Full GUI ==========
def main():
    root = tk.Tk()
    root.title("Safe Dataset Creator Toolkit")
    root.geometry("800x650")

    tab_control = ttk.Notebook(root)

    # ===== First Tab - Chunking =====
    creator_tab = ttk.Frame(tab_control)
    tab_control.add(creator_tab, text='Chunk & Process Text')

    ttk.Label(creator_tab, text="LLM Server URL:").pack(pady=(10, 0))
    server_url_var = tk.StringVar(value="http://localhost:1234")
    server_entry = ttk.Entry(creator_tab, textvariable=server_url_var, width=70)
    server_entry.pack()

    ttk.Label(creator_tab, text="Select or Enter Model Name:").pack(pady=(10, 0))
    model_var = tk.StringVar()
    try:
        available_models = get_models()
        model_combo = ttk.Combobox(creator_tab, textvariable=model_var, values=available_models, width=67)
    except Exception as e:
        model_combo = ttk.Combobox(creator_tab, textvariable=model_var, values=[], width=67)
        messagebox.showerror("Model Fetch Error", str(e))
    model_combo.pack()

    ttk.Label(creator_tab, text="Max characters per chunk:").pack(pady=(10, 0))
    max_chars_var = tk.IntVar(value=6000)
    max_chars_spin = ttk.Spinbox(creator_tab, from_=500, to=20000, increment=500, textvariable=max_chars_var)
    max_chars_spin.pack()

    ttk.Label(creator_tab, text="Overlap characters:").pack(pady=(10, 0))
    overlap_chars_var = tk.IntVar(value=500)
    overlap_chars_spin = ttk.Spinbox(creator_tab, from_=0, to=5000, increment=100, textvariable=overlap_chars_var)
    overlap_chars_spin.pack()

    summarize_first_var = tk.BooleanVar(value=True)
    summarize_checkbox = ttk.Checkbutton(creator_tab, text="Summarize before QA generation", variable=summarize_first_var)
    summarize_checkbox.pack(pady=(10, 0))

    file_path_var = tk.StringVar()

    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            file_path_var.set(file_path)

    ttk.Button(creator_tab, text="Upload Large Text File", command=browse_file).pack(pady=(10, 0))
    ttk.Label(creator_tab, textvariable=file_path_var, wraplength=750).pack()

    ttk.Label(creator_tab, text="Output Folder for Chunks:").pack(pady=(10, 5))
    output_folder_var = tk.StringVar(value="./outputs")
    ttk.Entry(creator_tab, textvariable=output_folder_var, width=70).pack()

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(creator_tab, variable=progress_var, maximum=100)
    progress_bar.pack(fill='x', padx=10, pady=10)

    status_text = tk.StringVar()
    ttk.Label(creator_tab, textvariable=status_text).pack()

    def start_processing():
        if not file_path_var.get():
            messagebox.showerror("Error", "Please upload a file first.")
            return

        thread = Thread(target=process_chunks, args=(
            file_path_var.get(),
            server_url_var.get(),
            model_var.get(),
            max_chars_var.get(),
            overlap_chars_var.get(),
            summarize_first_var.get(),
            output_folder_var.get(),
            progress_var,
            status_text
        ))
        thread.start()

    ttk.Button(creator_tab, text="Start Chunking and Processing", command=start_processing).pack(pady=(10, 10))

    # ===== Second Tab - Cleaning =====
    clean_tab = ttk.Frame(tab_control)
    tab_control.add(clean_tab, text='Clean Chunk Outputs')

    ttk.Label(clean_tab, text="Folder with Chunk JSONs:").pack(pady=(10, 0))
    chunks_folder_var = tk.StringVar(value="./outputs")
    ttk.Entry(clean_tab, textvariable=chunks_folder_var, width=70).pack()

    ttk.Label(clean_tab, text="Output JSON file name:").pack(pady=(10, 0))
    output_file_var = tk.StringVar(value="./final_dataset.json")
    ttk.Entry(clean_tab, textvariable=output_file_var, width=70).pack()

    def run_cleaning():
        try:
            total_pairs, skipped, output_file = post_process_chunks(
                chunks_folder=chunks_folder_var.get(),
                output_file=output_file_var.get()
            )
            messagebox.showinfo("Success", f"Dataset cleaned!\nTotal Q&A pairs: {total_pairs}\nOutput: {output_file}")
            if skipped:
                messagebox.showwarning("Skipped Files", f"Some files had no valid Q&A format.\nFirst few skipped:\n{skipped[:5]}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(clean_tab, text="Run Cleaning", command=run_cleaning).pack(pady=(20, 10))

    # Finalize Tabs
    tab_control.pack(expand=1, fill="both")
    root.mainloop()

if __name__ == "__main__":
    main()
