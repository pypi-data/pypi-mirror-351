"""
Paraphrase Text files using LMstudio

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.0"

import streamlit as st
import json
import os
from egritools.lmstudio import get_models, chat_with_model
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CONFIG_PATH = "paraphrasing_config.json"
DATA_PATH = "paraphrased_dataset.jsonl"
LOG_PATH = "paraphrasing_log.jsonl"

def save_progress(entry, generated):
    with open(DATA_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(generated) + "\n")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps({"original": entry, "generated": generated}) + "\n")

def save_config(filename, current_index, total):
    config = {"source_file": filename, "current_index": current_index, "total": total}
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def filter_paraphrases(generated, max_versions):
    if not generated:
        return []

    texts = [g["answer"] for g in generated]
    vectorizer = TfidfVectorizer().fit_transform(texts)
    sim_matrix = cosine_similarity(vectorizer)

    selected, seen = [], set()
    for i in range(len(texts)):
        if i in seen:
            continue
        seen.add(i)
        for j in range(i + 1, len(texts)):
            if sim_matrix[i][j] > 0.85:
                seen.add(j)
        selected.append(generated[i])
        if len(selected) >= max_versions:
            break
    return selected

# Streamlit App
st.title("💡 Paraphrasing Tool with Pause/Resume")

models = get_models()
selected_model = st.selectbox("Choose LMStudio model:", models)

instruction = st.text_input("Instruction (must return JSON):",
                            value="Paraphrase this Q&A pair and return as JSON: {'question': ..., 'answer': ...}")
num_versions = st.slider("Number of paraphrases per pair:", 1, 5, 2)

uploaded_file = st.file_uploader("Upload Q&A JSON file", type="json")

pause = st.checkbox("Pause after this entry")

if uploaded_file:
    filename = uploaded_file.name
    dataset = json.load(uploaded_file)

    config = load_config()
    #start_index = config["current_index"] + 1 if config and config["source_file"] == filename else 0
    start_index = config["current_index"] + 1 if config else 0
    total = len(dataset)

    st.info(f"Starting at entry {start_index}/{total}")

    if st.button("▶️ Begin / Resume Paraphrasing"):
        for i in range(start_index, total):
            entry = dataset[i]
            question, answer = entry.get("question"), entry.get("answer")
            if not (question and answer): continue

            prompt = f"{instruction}\n\nQuestion: {question}\nAnswer: {answer}"
            all_generations = []

            for _ in range(num_versions * 2):
                try:
                    output = chat_with_model(selected_model, prompt).strip()
                    start = output.find("{")
                    end = output.rfind("}") + 1
                    if start != -1 and end != -1:
                        try:
                            parsed = json.loads(output[start:end])
                            if parsed.get("question") and parsed.get("answer"):
                                all_generations.append(parsed)
                        except Exception as e:
                            print("Parse error:", e, "Trimmed Output:", output[start:end])

                    if parsed.get("question") and parsed.get("answer"):
                        all_generations.append(parsed)
                except:
                    continue

            filtered = filter_paraphrases(all_generations, num_versions)

            for gen in filtered:
                save_progress(entry, gen)

            save_config(filename, i, total)
            st.write(f"✅ Processed {i + 1}/{total}")

            if pause:
                st.warning("⏸️ Paused after current entry.")
                break

        st.success("🎉 Paraphrasing complete or paused. You can safely close or resume later.")

    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            preview = [json.loads(line) for line in f.readlines()[:2]]
            st.write("📄 Current Paraphrased Preview:", preview)

else:
    st.info("Please upload a dataset to begin.")
