requirements = """streamlit==1.49.1
pandas==2.3.2
openpyxl==3.1.5
requests==2.32.2
deep-translator==1.11.4
"""

app_py = r'''import streamlit as st
import pandas as pd
import requests
import os
import json
from deep_translator import GoogleTranslator

MEMORY_FILE = "/mnt/data/memory.json"

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="Instagram Bilingual Caption Generator (Online Hashtags)", layout="wide")
st.title("Instagram Bilingual Caption Generator (Online Hashtags)")

st.markdown("این ابزار کپشن‌های دو‌زبانه تولید می‌کند — ترجمه حرفه‌ای، معنی کلیدواژه، نکته آموزشی، CTA و هشتگ‌ها.\nاگر API آنلاین در دسترس نبود، یک fallback آفلاین استفاده می‌شود.")

uploaded_file = st.file_uploader("Upload Excel (optional)", type=["xlsx"])
text_input = st.text_area("Or paste the English quote here:")
author = st.text_input("Author / Speaker (optional)")

col1, col2 = st.columns(2)
with col1:
    use_online = st.checkbox("Use OpenRouter test key for online generation (may be blocked)", value=True)
with col2:
    st.write("\n")

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        if 'quote' in df.columns:
            quotes = df['quote'].astype(str).tolist()
        else:
            quotes = df.iloc[:,0].astype(str).tolist()
    except Exception as e:
        st.error("Error reading Excel file: " + str(e))
        quotes = []
else:
    quotes = [q for q in [text_input] if q.strip()]

st.write(f"Quotes to process: {len(quotes)}")

# Utility: memory load/save

def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_memory(mem):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(mem, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def offline_translation(text: str) -> str:
    try:
        return GoogleTranslator(source='en', target='fa').translate(text)
    except Exception:
        return "(ترجمه در دسترس نیست)"


def fallback_caption(quote: str, author: str):
    tr = offline_translation(quote)
    word_meaning = "simple = ساده"  # simple fallback example
    tip = "در این جمله، contrast بین 'simple' و 'complicated' نشان‌دهنده انتخاب‌های زندگی است."
    cta = "اگر این جمله را دوست داشتی، کامنت بذار و دوستت رو منشن کن!"
    hashtags = "#LifeQuotes #EnglishLearning #زندگی #ساده"
    return {
        'full_translation': tr,
        'word_meaning': word_meaning,
        'educational_tip': tip,
        'cta': cta,
        'hashtags': hashtags
    }


def generate_caption(quote: str, author: str = "") -> dict:
    memory = load_memory()
    context = "\n".join([f"Example {i+1}: meaning={entry.get('word_meaning','')}; tip={entry.get('educational_tip','')}; hashtags={entry.get('hashtags','')}" for i, entry in enumerate(memory[-5:])])

    prompt = f"""
You are an expert Instagram content creator and translator.
Given this quote by {author if author else 'Unknown'}: "{quote}"
Context examples (for style):\n{context}

Tasks:\n1) Translate the entire quote into natural Persian (do not include the original English sentence in the output).\n2) Choose one key English word and give its Persian meaning.\n3) Provide a short educational tip (grammar/vocab) related to the sentence.\n4) Write an engaging CTA.\n5) Suggest 8-12 hashtags in Persian and English (space-separated).

Return ONLY a valid JSON object with keys: full_translation, word_meaning, educational_tip, cta, hashtags
"""

    if use_online:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": "Bearer sk-or-openrouter-testing-key", "Content-Type": "application/json"}
            payload = {
                "model": "openai/gpt-4o-mini",
                "messages": [{"role":"system","content":"Respond only with a valid JSON object, no other text."}, {"role":"user","content":prompt}],
                "temperature":0.7
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                content = resp.json().get('choices',[{}])[0].get('message',{}).get('content','')
                try:
                    data = json.loads(content)
                    # save to memory
                    memory.append(data)
                    memory = memory[-50:]
                    save_memory(memory)
                    return data
                except Exception:
                    return fallback_caption(quote, author)
            else:
                return fallback_caption(quote, author)
        except Exception:
            return fallback_caption(quote, author)
    else:
        return fallback_caption(quote, author)


# Process quotes
results = []
for q in quotes:
    res = generate_caption(q, author)
    results.append(res)

# Display
for i, r in enumerate(results):
    st.markdown("---")
    st.markdown(f"### Caption #{i+1}")
    st.markdown(f"**ترجمه:** {r.get('full_translation','')}")
    st.markdown(f"**معنی کلیدواژه:** {r.get('word_meaning','')}")
    st.markdown(f"**نکته آموزشی:** {r.get('educational_tip','')}")
    st.markdown(f"**CTA:** {r.get('cta','')}")
    st.markdown(f"**هشتگ‌ها:** {r.get('hashtags','')}")

st.info("حافظه محلی در /mnt/data/memory.json ذخیره می‌شود. برای ریست کردن حافظه، فایل را حذف یا خالی کنید.")
'''

with open('/mnt/data/requirements.txt','w',encoding='utf-8') as f:
    f.write(requirements)
with open('/mnt/data/app.py','w',encoding='utf-8') as f:
    f.write(app_py)

{"status":"done","files":["/mnt/data/requirements.txt","/mnt/data/app.py"]}