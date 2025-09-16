import streamlit as st
import pandas as pd
import random
import requests
import io

# -----------------------------------
# داده‌ها و پیکربندی ثابت
# -----------------------------------
emotional_hooks = [
    lambda: "🌟 Keep shining, the world needs your light!",
    lambda: "❤️ Every word here has a heartbeat.",
    lambda: "💪 This is your daily boost!"
]

ctas = [
    lambda: "💬 Share your thoughts below!",
    lambda: "🗣 Which part touched you most?",
    lambda: "📌 Save this post for later!"
]

general_hashtags = "#EnglishQuotes #DailyQuote #الهام #انگیزشی #PositiveVibes"

# -----------------------------------
# تابع گرفتن هشتگ آنلاین با پروکسی OpenRouter
# -----------------------------------
def generate_hashtags_online(quote):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-or-openrouter-testing-key",  # کلید آزمایشی
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an Instagram content assistant."},
            {"role": "user", "content": f'Generate 10 relevant Instagram hashtags in English and Persian for: "{quote}". Just return the hashtags separated by spaces.'}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            result = response.json()
            hashtags = result["choices"][0]["message"]["content"].strip()
            return hashtags if hashtags else general_hashtags
        else:
            return general_hashtags
    except Exception:
        return general_hashtags

# -----------------------------------
# تابع ساخت کپشن
# -----------------------------------
def generate_caption(quote, author=""):
    words = quote.split()
    focus_word = random.choice(words) if words else ""
    
    translation = f"این جمله می‌گوید که {quote.lower()} (ترجمه خلاقانه فارسی)."
    
    word_focus = {
        "word": focus_word,
        "meaning": "معنی فارسی کوتاه",
        "example": f"Example: I use '{focus_word}' in a simple sentence."
    }
    
    hashtags = generate_hashtags_online(quote)
    
    caption = f"""{quote} — {author}

{translation}

📝 Word Focus: {word_focus['word']} = {word_focus['meaning']}
{word_focus['example']}

{random.choice(emotional_hooks)()}

💬 {random.choice(ctas)()}

{hashtags}"""
    
    return caption

# -----------------------------------
# رابط کاربری Streamlit
# -----------------------------------
st.title("📸 Instagram Bilingual Caption Generator (Online Hashtags)")

uploaded_file = st.file_uploader("📂 آپلود فایل Excel جملات", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    if "Quote" not in df.columns:
        st.error("فایل باید ستونی به نام 'Quote' داشته باشد.")
    else:
        captions = []
        for _, row in df.iterrows():
            quote = str(row["Quote"])
            author = str(row.get("Author", ""))
            captions.append(generate_caption(quote, author))
        
        df["Caption"] = captions

        # دانلود Excel
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        # دانلود CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        st.success("✅ کپشن‌ها ساخته شدند!")

        st.download_button("⬇ دانلود Excel", data=excel_buffer, file_name="captions.xlsx")
        st.download_button("⬇ دانلود CSV", data=csv_buffer, file_name="captions.csv")

        st.write(df[["Quote", "Caption"]])
