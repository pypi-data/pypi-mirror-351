"""
GPT2 Tokenizer Creation

Create a custom tokenizer for a gpt2 model from a .txt file.

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tokenizers import Tokenizer, trainers, models, pre_tokenizers, decoders
from tokenizers.processors import TemplateProcessing

VOCAB_SIZE = 32000

def clean_raw_text(raw_path, output_path):
    print("[*] Cleaning raw corpus...")
    with open(raw_path, "r", encoding="utf-8") as f:
        raw = f.read()

    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(clean_text)

    print(f"[✓] Cleaned corpus saved with {len(lines)} lines.")

def train_tokenizer(corpus_path, tokenizer_save_path, vocab_size=VOCAB_SIZE):
    print("[*] Training tokenizer...")

    tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()

    special_tokens = ["<pad>", "<unk>", "<bos>", "<eos>", "<sep>"]
    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        special_tokens=special_tokens
    )

    tokenizer.train([corpus_path], trainer)

    tokenizer.post_processor = TemplateProcessing(
        single="<bos> $A <eos>",
        pair="<bos> $A <sep> $B:1 <eos>:1",
        special_tokens=[
            ("<bos>", tokenizer.token_to_id("<bos>")),
            ("<eos>", tokenizer.token_to_id("<eos>")),
            ("<sep>", tokenizer.token_to_id("<sep>"))
        ]
    )

    tokenizer.enable_truncation(max_length=512)
    tokenizer.enable_padding(
        pad_id=tokenizer.token_to_id("<pad>"),
        pad_type_id=0,
        pad_token="<pad>",
        length=512
    )

    os.makedirs(os.path.dirname(tokenizer_save_path), exist_ok=True)
    tokenizer.save(tokenizer_save_path)
    print(f"[✓] Tokenizer fully saved in one file: {tokenizer_save_path}")

def browse_file(entry):
    filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if filepath:
        entry.delete(0, tk.END)
        entry.insert(0, filepath)

def process_file(input_file):
    if not input_file:
        messagebox.showerror("Error", "Please select a text file.")
        return

    base_dir = os.getcwd()  # location where the script is launched
    filename = os.path.basename(input_file)
    name_without_ext = os.path.splitext(filename)[0]
    cleaned_file = os.path.join(base_dir, f"{name_without_ext}_cleaned.txt")
    tokenizer_dir = os.path.join(base_dir, f"tokenizer[{name_without_ext}]")
    tokenizer_save_path = os.path.join(tokenizer_dir, "tokenizer.json")

    clean_raw_text(input_file, cleaned_file)
    train_tokenizer(cleaned_file, tokenizer_save_path)

    messagebox.showinfo("Done", f"Tokenizer saved at:\n{tokenizer_save_path}")

def main():
    root = tk.Tk()
    root.title("Tokenizer Trainer")

    tk.Label(root, text="Select Corpus Text File:").pack(pady=10)
    file_entry = tk.Entry(root, width=60)
    file_entry.pack(padx=10)

    browse_button = tk.Button(root, text="Browse", command=lambda: browse_file(file_entry))
    browse_button.pack(pady=5)

    process_button = tk.Button(root, text="Start Processing", command=lambda: process_file(file_entry.get()))
    process_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
