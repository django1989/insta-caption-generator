import streamlit as st
import pandas as pd
import requests
import io
import json

# کپشنFallback آفلاین
def offline_caption(quote, author=""):
    return f"""{quote} — {author}

📖 معنی کلمه: simple = ساده

💡 نکته آموزشی: در این جمله از ساختار متضاد بین 'simple' و 'complicated' استفاده شده.

🤔 به نظر شما چطور میشه زندگی رو ساده‌تر دید؟

#LifeQuotes #EnglishLearning #زندگی #سادگی #انگیزشی
"""

# کپشن‌ساز ترکیبی آنلاین+آفلاین
def generate_caption(quote, author=""):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-or-openrouter-testing-key",  # کلید تستی
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are an Instagram content creator assistant for a bilingual page that teaches English using inspirational quotes.
    Analyze this quote: "{quote}" by {author if author else "Unknown"}.
    Return ONLY a JSON object with these keys:
    word_meaning: Pick 1 key English word from the quote and give its meaning in Persian.
    educational_tip: Give a short grammar/vocabulary tip based on the sentence.
    cta: Create an engaging call-to-action (in Persian or English) to boost user interaction.
    hashtags: Generate 8-12 relevant hashtags in both English and Persian, separated by spaces.
    """

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Respond ONLY with valid JSON and nothing else."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)

        if response.status_code == 200:
            raw_content = response.json()["choices"][0]["message"]["content"].strip()
            try:
                parsed = json.loads(raw_content)
                return f"""{quote} — {author}

📖 معنی کلمه: {parsed['word_meaning']}

💡 نکته آموزشی: {parsed['educational_tip']}

{parsed['cta']}

{parsed['hashtags']}"""
            except json.JSONDecodeError:
                # اگر JSON خراب باشه، برگرده به آفلاین
                return offline_caption(quote, author)
        else:
            # اگر status_code غیر 200 باشه، فوری بره آفلاین
            return offline_caption(quote, author)

    except Exception:
        # هر نوع خطای اتصال → آفلاین
        return offline_caption(quote, author)

# -----------------------------------
# رابط کاربری استریم‌لیت
# -----------------------------------
st.title("📸 Instagram Bilingual Caption Generator (Always Works)")

# حالت ۱: ورود دستی
st.subheader("✏ حالت ۱: ورود مستقیم متن")
user_text = st.text_area("یک جمله یا نقل قول انگلیسی وارد کنید:")
author_name = st.text_input("نام گوینده (اختیاری)")

if st.button("تولید کپشن از متن"):
    if user_text.strip():
        st.success("✅ کپشن ساخته شد")
        st.write(generate_caption(user_text, author_name))
    else:
        st.warning("⚠ لطفاً یک جمله وارد کنید.")

st.markdown("---")

# حالت ۲: آپلود Excel
st.subheader("📂 حالت ۲: آپلود Excel")
st.info("فایل باید ستونی به نام 'Quote' و در صورت نیاز 'Author' داشته باشد.")

uploaded_file = st.file_uploader("فایل اکسل را آپلود کنید", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    if "Quote" not in df.columns:
        st.error("فایل باید ستونی به نام 'Quote' داشته باشد.")
    else:
        captions = [generate_caption(str(row["Quote"]), str(row.get("Author", ""))) for _, row in df.iterrows()]
        df["Caption"] = captions

        # ذخیره Excel
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        # ذخیره CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        st.success("✅ کپشن‌ها ساخته شدند!")
        st.download_button("⬇ دانلود Excel", data=excel_buffer, file_name="captions.xlsx")
        st.download_button("⬇ دانلود CSV", data=csv_buffer, file_name="captions.csv")
        st.dataframe(df[["Quote", "Caption"]])
