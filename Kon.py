import streamlit as st
import os
from PIL import Image
from gtts import gTTS

# استيراد متوافق مع جميع إصدارات MoviePy
try:
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# 1. إعدادات الصفحة
st.set_page_config(page_title="Local Images Cosmos Video Generator", layout="wide")
st.title("🌌 مولد الفيديو من الصور المحلية في مجلد 'صور'")

IMAGES_DIR = "صور"
TEMP_DIR = "temp_assets"
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# دالة لتنسيق الصورة ووضعها على خلفية سينمائية HD (1280x720)
def prepare_hd_image(image_path, output_path):
    img = Image.open(image_path).convert("RGB")
    background = Image.new("RGB", (1280, 720), color="#020208")
    img.thumbnail((1100, 680), Image.Resampling.LANCZOS)
    offset = ((1280 - img.width) // 2, (720 - img.height) // 2)
    background.paste(img, offset)
    background.save(output_path)

# قاموس اختياري لوضع تعليق عربي مخصص لكل اسم صورة بالفرنسية
# إذا كانت الصورة باسم غير موجود هنا، سينطق الكود اسمها تلقائياً
FRENCH_TO_ARABIC_TEXT = {
    "soleil": "الشمس، النجم المركزي الذي يمنح الضوء والحياة لمجموعتنا الشمسية.",
    "mercure": "كوكب عطارد، أصغر كواكب المجموعة الشمسية والأقرب إلى الشمس.",
    "venus": "كوكب الزهرة، أشد الكواكب حرارة في النظام الشمسي.",
    "terre": "كوكب الأرض، موطن الحياة والماء السائل في هذا الكون الشاسع.",
    "lune": "القمر، التابع الطبيعي الأقرب لكوكب الأرض.",
    "mars": "كوكب المريخ الأحمر، الكوكب الجاف الغني بأكسيد الحديد.",
    "jupiter": "كوكب المشتري، العملاق الغازي وأضخم كواكب المجموعة الشمسية.",
    "saturne": "كوكب زحل، صاحب الحلقات البراقة والمذهلة من الجليد والصخور.",
    "uranus": "كوكب أورانوس، العملاق الثلجي البارد.",
    "neptune": "كوكب نبتون، أبعد كواكب المجموعة الشمسية وتسوده الرياح العاتية.",
    "pluton": "بلوتو، الكوكب القزم المتواجد على أطراف النظام الشمسي.",
    "voie_lactee": "مجرة درب التبانة، المجرة الحلزونية التي تحتضن كوكبنا.",
    "galaxie": "المجرة الكونية، تجمع هائل من ملايين النجوم والغبار الكوني.",
    "nebuleuse": "السديم الكوني، سحابة ضخمة من الغاز تولد فيها النجوم الجديدة.",
    "trou_noir": "الثقب الأسود، جرم فلكي ذو جاذبية خارقة لا يهرب منها الضوء.",
    "supernova": "المستعر الأعظم، الانفجار الهائل الذي ينهي حياة النجوم الضخمة.",
    "etoile": "النجوم الكونية، كرات غازية متوهجة تضيء أرجاء الفضاء.",
    "comete": "المذنب الفضائي، كتل من الجليد والغبار تدور حول الشمس."
}

st.subheader("تحويل الصور الموجودة في مجلد 'صور' إلى فيديو")

# جلب كافة الصور الموجودة داخل مجلد صور
valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
image_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(valid_extensions)]

if not image_files:
    st.info(f"📁 مجلد '{IMAGES_DIR}' فارغ حالياً. ضع فيه الصور بأسماء مثل: `Soleil.jpg`, `Terre.png`, `Mars.jpg` ... إلخ، ثم اضغط زر التوليد.")
else:
    st.success(f"تم العثور على {len(image_files)} صورة داخل مجلد '{IMAGES_DIR}'.")

if st.button("🚀 إنشاء الفيديو الآن"):
    if not image_files:
        st.error("يرجى إضافة الصور أولاً داخل المجلد!")
    else:
        clips = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_items = len(image_files)
        
        for idx, file_name in enumerate(image_files):
            status_text.text(f"جاري معالجة الصورة ({idx+1}/{total_items}): {file_name}...")
            
            local_img_path = os.path.join(IMAGES_DIR, file_name)
            hd_img_path = os.path.join(TEMP_DIR, f"{idx}_{file_name}_hd.png")
            
            # أ. تجهيز الصورة بدقة HD
            prepare_hd_image(local_img_path, hd_img_path)
            
            # ب. تحديد النص العربي المناسب للتعليق الصوتي
            base_name = os.path.splitext(file_name)[0].lower()
            
            # البحث عن كلمة مفتاحية في اسم الملف
            text_to_speak = f"صورة لـ {base_name} في الكون"
            for key in FRENCH_TO_ARABIC_TEXT:
                if key in base_name:
                    text_to_speak = FRENCH_TO_ARABIC_TEXT[key]
                    break
            
            # ج. توليد الصوت العربي
            audio_path = os.path.join(TEMP_DIR, f"{idx}_{base_name}.mp3")
            if not os.path.exists(audio_path):
                tts = gTTS(text=text_to_speak, lang='ar')
                tts.save(audio_path)
            
            # د. دمج الصورة مع الصوت
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 0.8
            
            img_clip = ImageClip(hd_img_path)
            if hasattr(img_clip, 'with_duration'):
                img_clip = img_clip.with_duration(duration).with_audio(audio_clip)
            else:
                img_clip = img_clip.set_duration(duration).set_audio(audio_clip)
                
            clips.append(img_clip)
            progress_bar.progress((idx + 1) / total_items)
            
        status_text.text("جاري مونتاج وتجميع الفيديو النهائي...")
        
        final_video = concatenate_videoclips(clips)
        output_video_path = "cosmos_local_video.mp4"
        
        final_video.write_videofile(
            output_video_path, 
            fps=24
        )
        
        status_text.success("✨ تم إنشاء الفيديو بنجاح من صورك الخاصة!")
        st.video(output_video_path)

elif os.path.exists("cosmos_local_video.mp4"):
    st.write("الفيديو المُنشأ سابقاً:")
    st.video("cosmos_local_video.mp4")
