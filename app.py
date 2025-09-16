import random
import pandas as pd
import streamlit as st

# -----------------------------
# لیست قلاب‌های احساسی و CTAها
# -----------------------------
emotional_hooks = [
    lambda: "گاهی آرامش در حذف چیزهای اضافی پیدا می‌شود.",
    lambda: "مثل رودخانه باش، مسیر را ساده بگیر.",
    lambda: "زیبایی زندگی در سادگی آن پنهان است.",
    lambda: "وقتی از ساده‌ترین راه بروی، مقصد زودتر می‌رسد."
]

ctas = [
    lambda: "شما امروز چه چیزی را می‌توانید ساده‌تر کنید؟",
    lambda: "امروز یک کار بیهوده را حذف کنید و تجربۀ خود را با ما به اشتراک بگذارید.",
    lambda: "آخرین باری که بی‌دلیل چیزی را سخت کردید چه زمانی بود؟"
]

# -----------------------------
# تابع تولید کپشن
# -----------------------------
def generate_caption(quote, author=""):
    words = quote.split()
    focus_word = random.choice(words) if words else ""
    
    translation = f"این جمله می‌گوید که {quote.lower()} (ترجمه خلاقانه فارسی)."
    
    word_focus = {
        "word": focus_word,
        "meaning": "معنی فارسی کوتاه برای این کلمه/عبارت",
        "example": f"Example: I use '{focus_word}' in a simple sentence."
    }
    
    caption = f"""{quote} — {author}

{translation}

📝 Word Focus: {word_focus['word']} = {word_focus['meaning']}
{word_focus['example']}

{random.choice(emotional_hooks)()}

💬 {random.choice(ctas)()}"""
    
    return caption

# -----------------------------
# رابط کاربری Streamlit
# -----------------------------
st.set_page_config(page_title="Caption Generator", page_icon="✍️", layout="centered")

st.title("📜 جعبه‌ابزار هوشمند کپشن دو زبانه")
st.write("جمله انگلیسی خود را وارد کنید:")

quote = st.text_input(" جمله انگلیسی")
author = st.text_input(" نویسنده (اختیاری)")

if st.button("تولید کپشن"):
    if quote.strip():
        caption = generate_caption(quote, author)
        st.text_area("کپشن تولید شده:", caption, height=300)
        
        # ذخیره در فایل Excel
        df = pd.DataFrame({"Quote": [quote], "Author": [author], "Caption": [caption]})
        df.to_excel("caption_output.xlsx", index=False)
        
        with open("caption_output.xlsx", "rb") as f:
            st.download_button("دانلود خروجی Excel", f, file_name="caption_output.xlsx")
    else:
        st.warning("لطفاً یک جمله وارد کنید.")
