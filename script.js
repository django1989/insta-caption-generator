const quoteInput = document.getElementById('quote');
const apiKeyInput = document.getElementById('apiKey');
const analyzeBtn = document.getElementById('analyzeBtn');
const btnText = document.querySelector('.btn-text');
const loading = document.querySelector('.loading');
const results = document.getElementById('results');
const notification = document.getElementById('notification');
const notificationText = document.getElementById('notificationText');

let selectedTemplate = 'elegant';
let currentAnalysis = null;

analyzeBtn.addEventListener('click', analyzeQuote);

async function analyzeQuote() {
    const quote = quoteInput.value.trim();
    
    if (!quote) {
        showNotification('لطفاً نقل قولی وارد کنید', 'error');
        return;
    }

    setLoading(true);

    try {
        const apiKey = apiKeyInput.value.trim();
        let analysis;

        if (apiKey) {
            analysis = await callOpenAI(quote, apiKey);
        } else {
            // نمونه آزمایشی
            analysis = getDemoAnalysis(quote);
        }

        currentAnalysis = analysis;
        displayResults(analysis);
        showNotification('تحلیل با موفقیت انجام شد!');
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('خطایی رخ داد. لطفاً دوباره تلاش کنید.', 'error');
    } finally {
        setLoading(false);
    }
}

async function callOpenAI(quote, apiKey) {
    const prompt = `
تو یک متخصص زبان انگلیسی و تولید محتوا هستی. 
این نقل قول انگلیسی رو تحلیل کن و برام این اطلاعات رو بده:

نقل قول: "${quote}"

لطفاً پاسخت رو دقیقاً به این فرمت JSON بده:
{
    "source": "نام نویسنده یا گوینده + سال (اگر معلوم باشه)",
    "translation": "ترجمه دقیق و روان به فارسی",
    "educational": "یک نکته آموزشی دربارۀ گرامر، واژگان، یا استفاده از این جمله به زبان فارسی",
    "instagram": "یک متن جذاب برای اینستاگرام با call to action (شامل درخواست لایک، فالو، کامنت)",
    "hashtags": ["هشتگ1", "هشتگ2", "هشتگ3", "هشتگ4", "هشتگ5"]
}

فقط JSON رو برگردون، هیچ توضیح اضافی نده.
`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            model: 'gpt-4o',
            messages: [
                {
                    role: 'user',
                    content: prompt
                }
            ],
            max_tokens: 1000,
            temperature: 0.7
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    const content = data.choices[0].message.content.trim();
    
    // پاک کردن کاراکترهای اضافی
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
        throw new Error('Invalid response format');
    }

    return JSON.parse(jsonMatch[0]);
}

function getDemoAnalysis(quote) {
    // نمونه آزمایشی
    return {
        source: "نویسنده نامعلوم",
        translation: "این یک ترجمه نمونه است. برای دریافت ترجمه دقیق، لطفاً کلید API خود را وارد کنید.",
        educational: "این یک نکته آموزشی نمونه است. برای دریافت نکات آموزشی دقیق، لطفاً کلید API خود را وارد کنید.",
        instagram: "🌟 این نقل قول الهام‌بخش چطور؟ \n\n💭 نظرتون رو در کامنت بنویسید و اگر مفید بود لایک کنید! \n\n👥 برای نقل قول‌های بیشتر ما رو فالو کنید!",
        hashtags: ["motivation", "quotes", "inspiration", "success", "mindset"]
    };
}

function selectTemplate(template) {
    selectedTemplate = template;
    
    // آپدیت دکمه‌های انتخاب
    document.querySelectorAll('.template-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // اگر نتایج نمایش داده شده، پست رو دوباره بساز
    if (currentAnalysis && !results.classList.contains('hidden')) {
        updateFinalPost(quoteInput.value.trim(), currentAnalysis);
    }
}

function updateFinalPost(quote, analysis) {
    const templates = {
        elegant: `✨ ════════════════════ ✨

💎 "${quote}"

🌟 ${analysis.source}

✨ ════════════════════ ✨

ترجمۀ :
${analysis.translation}

📚 ════════════════════ 📚

🎯 نکتۀ آموزشی:
${analysis.educational}

🚀 ════════════════════ 🚀

${analysis.instagram}

✨ ════════════════════ ✨

${analysis.hashtags.map(tag => `#${tag}`).join(' ')}

#انگلیسی_آموز #نقل_قول_انگلیسی #یادگیری_زبان #انگیزشی #موفقیت`,

        modern: `┌─────────────────────────────┐
│  💫 ENGLISH QUOTE CORNER 💫  │
└─────────────────────────────┘

🎭 "${quote}"

👤 منبع: ${analysis.source}

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

🇮🇷 معنی فارسی:
💭 ${analysis.translation}

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

🧠 TIP زبان‌آموزی:
💡 ${analysis.educational}

▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

${analysis.instagram}

┌─────────────────────────────┐
│ ${analysis.hashtags.map(tag => `#${tag}`).join(' ')} │
└─────────────────────────────┘

#انگلیسی_آموز #نقل_قول_انگلیسی #یادگیری_زبان #انگیزشی #موفقیت`,

        minimal: `⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
✦ · · · · · · · · · · · · · · · · · · · · · · · · · ✦

💎 "${quote}"

✦ ${analysis.source}

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

🇮🇷 ${analysis.translation}

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

📖 ${analysis.educational}

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

${analysis.instagram}

✦ · · · · · · · · · · · · · · · · · · · · · · · · · ✦

${analysis.hashtags.map(tag => `#${tag}`).join(' ')}

#انگلیسی_آموز #نقل_قول_انگلیسی #یادگیری_زبان`,

        simple: `"${quote}"

ترجمه: ${analysis.translation}

نکته آموزشی: ${analysis.educational}

${analysis.instagram}

${analysis.hashtags.map(tag => `#${tag}`).join(' ')}

#انگلیسی_آموز #نقل_قول_انگلیسی #یادگیری_زبان`
    };

    document.getElementById('finalPost').textContent = templates[selectedTemplate];
}

function displayResults(analysis) {
    // نمایش منبع
    document.getElementById('source').innerHTML = `
        <div style="font-size: 1.1rem; font-weight: 600; color: #333;">
            ${analysis.source}
        </div>
    `;

    // نمایش ترجمه
    document.getElementById('translation').innerHTML = `
        <div style="font-size: 1rem; line-height: 1.8;">
            ${analysis.translation}
        </div>
    `;

    // نمایش نکته آموزشی
    document.getElementById('educational').innerHTML = `
        <div style="font-size: 1rem; line-height: 1.8;">
            ${analysis.educational}
        </div>
    `;

    // نمایش متن اینستاگرام
    document.getElementById('instagram').innerHTML = `
        <div style="font-size: 1rem; line-height: 1.8;">
            ${analysis.instagram}
        </div>
    `;

    // نمایش هشتگ‌ها
    const hashtagsHTML = analysis.hashtags.map(tag => 
        `<span class="hashtag">#${tag}</span>`
    ).join('');
    document.getElementById('hashtags').innerHTML = hashtagsHTML;

    // ساخت پست نهایی
    updateFinalPost(quoteInput.value.trim(), analysis);

    // نمایش نتایج
    results.classList.remove('hidden');
    results.scrollIntoView({ behavior: 'smooth' });
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    let textToCopy;

    if (elementId === 'hashtags') {
        const hashtags = Array.from(element.querySelectorAll('.hashtag'))
            .map(span => span.textContent)
            .join(' ');
        textToCopy = hashtags;
    } else {
        textToCopy = element.textContent;
    }

    navigator.clipboard.writeText(textToCopy).then(() => {
        showNotification('متن کپی شد!');
    }).catch(() => {
        // fallback برای مرورگرهای قدیمی
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('متن کپی شد!');
    });
}

function setLoading(isLoading) {
    if (isLoading) {
        btnText.classList.add('hidden');
        loading.classList.remove('hidden');
        analyzeBtn.disabled = true;
    } else {
        btnText.classList.remove('hidden');
        loading.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
}

function showNotification(message, type = 'success') {
    notificationText.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');

    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}
