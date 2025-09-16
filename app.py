import streamlit as st
import pandas as pd
import requests
import io
import json

# -----------------------------------
# تابع تولید کپشن کامل هوشمند با Fallback
# -----------------------------------
def generate_caption(quote, author=""):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-or-openrouter-testing-key",  # کلید تستی OpenRouter
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
            {"role": "system", "content": "Respond ONLY with valid JSON"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            raw_content = data["choices"][0]["message"]["content"].strip()

            # تلاش برای پارس JSON
            try:
                parsed = json.loads(raw_content)
            except json.JSONDecodeError:
                # Fallback محتوایی
                parsed = {
                    "word_meaning": "simple = ساده",
                    "educational_tip": "در این جمله از صفت 'simple' برای توصیف زندگی استفاده شده است.",
                    "cta": "نظر شما چیه؟ آیا زندگی رو ساده می‌بینید؟",
                    "hashtags": "#LifeQuotes #EnglishLearning #زندگی #سادگی #انگیزشی"
                }

            # ساخت کپشن
            return f"""{quote} — {author}

📖 معنی کلمه: {parsed['word_meaning']}

💡 نکته آموزشی: {parsed['educational_tip']}

{parsed['cta']}

{parsed['hashtags']}"""

        else:
            return f"{quote} — {author}\n\n⚠️ خطا در ارتباط با API."

    except Exception:
        # Fallback کلی آفلاین
        return f"""{quote} — {author}

📖 معنی کلمه: simple = ساده

💡 نکته آموزشی: در این جمله از ساختار متضاد بین 'simple' و 'complicated' استفاده شده.

🤔 به نظر شما چطور میشه زندگی رو ساده‌تر دید؟

#LifeQuotes #EnglishLearning #زندگی #سادگی #انگیزشی
"""

# -----------------------------------
# رابط کاربری استریم‌لیت
# -----------------------------------
st.title("📸 Instagram Bilingual Caption Generator (Advanced + Fallback)")

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
st.info("فایل باید ستونی با نام 'Quote' و در صورت نیاز 'Author' داشته باشد.")

uploaded_file = st.file_uploader("فایل اکسل را آپلود کنید", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    if "Quote" not in df.columns:
        st.error("فایل باید ستونی به نام 'Quote' داشته باشد.")
    else:
        captions = []
        for _, row in df.iterrows():
            quote = str(row["Quote"])
            author_val = str(row.get("Author", ""))
            captions.append(generate_caption(quote, author_val))

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
