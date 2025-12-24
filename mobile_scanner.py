
import streamlit as st
from core.dl_vision import HandwritingGrader
from core.i18n import get_text
import json

def show_vision_grader():
    """
    Renders the AI Vision Grader UI, optimized for a mobile PWA experience.
    """
    st.header(f"👁️ {get_text('vision_grader_title', 'Vision Grader')}")
    st.caption(get_text('vision_grader_caption', 'Scan student handwriting for AI-powered grading'))

    # --- Rubric Input ---
    rubric = st.text_area(
        label=get_text('rubric_label', "Enter Grading Rubric or Model Answer"),
        placeholder=get_text('rubric_placeholder', "e.g., 'The capital of France is Paris. Full marks for mentioning Paris.'")
    )

    # --- Camera Input ---
    # Styled to look like a native scanner button
    st.markdown("---")
    image_file = st.camera_input(
        label=get_text('camera_label', "Scan Student's Answer"),
        help=get_text('camera_help', "Position the handwriting in the frame and tap to capture.")
    )
    st.markdown("---")

    if image_file is not None and rubric:
        with st.spinner(get_text('grading_in_progress', "AI is grading...")):
            try:
                # Initialize the grader
                grader = HandwritingGrader()
                
                # Get the image bytes
                img_bytes = image_file.getvalue()
                
                # Get the grading result from the DL module
                result_json_str = grader.grade_handwriting(img_bytes, rubric)
                
                # --- Display Results ---
                # The Gemini response might include markdown ```json ... ```, so we clean it
                cleaned_json_str = result_json_str.strip().replace('```json', '').replace('```', '')
                result = json.loads(cleaned_json_str)

                st.subheader(get_text('results_header', "Grading Results"))
                
                # Display the grade prominently
                st.metric(
                    label=get_text('grade_label', "Assigned Grade"),
                    value=result.get("grade", "N/A")
                )

                # Display transcription and corrections in an expander
                with st.expander(get_text('details_expander', "Show Details")):
                    st.text_area(
                        label=get_text('transcription_label', "Transcribed Text"),
                        value=result.get("transcription", "Could not read text."),
                        height=100,
                        disabled=True
                    )
                    st.write(get_text('corrections_label', "**Corrections & Suggestions:**"))
                    for correction in result.get("corrections", []):
                        st.write(f"- {correction}")
                
                # Placeholder for audio feedback
                st.subheader(get_text('audio_feedback_header', "Audio Feedback"))
                st.audio(b"", format="audio/mp3") # Placeholder for TTS output
                st.info(f"🎙️ {result.get('feedback_summary', 'No feedback generated.')}")

            except Exception as e:
                st.error(f"Failed to process and grade the image. Error: {e}")
    elif image_file is not None and not rubric:
        st.warning(get_text('rubric_warning', "Please enter a rubric before scanning."))

# Add new keys to i18n.py for this view
# "ar": {
#     "vision_grader_title": "المصحح البصري",
#     "vision_grader_caption": "امسح خط يد الطالب ضوئيًا لتقييمه بالذكاء الاصطناعي",
#     "rubric_label": "أدخل معيار التقييم أو الإجابة النموذجية",
#     "rubric_placeholder": "مثال: 'عاصمة فرنسا هي باريس. علامة كاملة لذكر باريس.'",
#     "camera_label": "مسح إجابة الطالب",
#     "camera_help": "ضع خط اليد في الإطار وانقر لالتقاط الصورة.",
#     "grading_in_progress": "الذكاء الاصطناعي يقوم بالتقييم...",
#     "results_header": "نتائج التقييم",
#     "grade_label": "الدرجة الممنوحة",
#     "details_expander": "إظهار التفاصيل",
#     "transcription_label": "النص المكتوب",
#     "corrections_label": "**التصحيحات والاقتراحات:**",
#     "audio_feedback_header": "ملاحظات صوتية",
#     "rubric_warning": "الرجاء إدخال معيار تقييم قبل المسح الضوئي."
# },
# "en": { ... }
