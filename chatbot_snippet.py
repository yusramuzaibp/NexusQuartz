# =======================================================================
# AI HEALTH ASSISTANT — real LLM (Google Gemini) with keyword-bot fallback
# Paste this whole block into your project file, then add
# 'AI Health Assistant' to your sidebar option_menu list (see note
# at the bottom of this file for that one-line change).
# =======================================================================

import streamlit as st

try:
    from google import genai
except ImportError:
    genai = None


SYSTEM_PROMPT = (
    "You are a helpful AI Health Assistant embedded in a Multiple Disease "
    "Prediction app that covers diabetes, heart disease, and Parkinson's "
    "disease. Answer clearly, in plain language, in under 150 words unless "
    "the user asks for more detail. You are NOT a doctor and this is NOT a "
    "diagnostic tool — always remind the user to consult a licensed "
    "healthcare professional for anything specific to their own symptoms, "
    "test results, or medical decisions. If the user asks about their own "
    "prediction history, use the CONTEXT block provided, if any."
)


def _get_client():
    """Returns a Gemini client if a key is configured, else None."""
    if genai is None:
        return None
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


# -----------------------------------------------------------------------
# 1. THE CHATBOT LOGIC
#    Scans the question for keywords and returns a matching canned answer.
#    Add as many `if` blocks as you like — order matters, the first
#    matching keyword wins.
# -----------------------------------------------------------------------
def bot_reply(question, history=None):
    q = question.lower()
    history = history or []

    # ---- questions about the user's own results (uses your app's
    #      st.session_state.history, if you're tracking predictions) ----
    if history and ('my prediction' in q or 'my result' in q or 'my latest' in q):
        latest = history[-1]
        return (f"Your most recent test was for **{latest['condition']}**, "
                f"classified as **{latest['risk']} Risk** — result: "
                f"\"{latest['result']}\".")

    if history and ('history' in q or 'previous' in q or 'past result' in q):
        lines = '\n'.join(
            f"- {h['timestamp']}: {h['condition']} — {h['risk']} Risk"
            for h in history[-5:]
        )
        return f"Here's your recent history:\n{lines}"

    # ---- symptoms (checked BEFORE general disease info, so a symptom
    #      question gets a symptom answer, not the general blurb) ----
    if 'symptom' in q or 'sign' in q or 'warning sign' in q:
        if 'diabetes' in q or 'blood sugar' in q or 'glucose' in q:
            return ("Common symptoms of diabetes include: frequent urination, "
                    "excessive thirst, unexplained weight loss, extreme "
                    "hunger, fatigue, blurred vision, slow-healing sores, and "
                    "tingling/numbness in hands or feet. If you notice "
                    "several of these, it's worth getting tested.")
        if 'heart' in q or 'cardiac' in q or 'cardiovascular' in q:
            return ("Common symptoms of heart disease include: chest pain or "
                    "discomfort, shortness of breath, pain/numbness in the "
                    "arms or shoulder, irregular heartbeat, fatigue, "
                    "dizziness, and swelling in the legs or feet. Chest pain "
                    "with shortness of breath needs urgent medical attention.")
        if 'parkinson' in q:
            return ("Common early symptoms of Parkinson's disease include: "
                    "tremor (often starting in one hand), muscle stiffness, "
                    "slowed movement, changes in handwriting, reduced "
                    "facial expression, and a softer or slurred voice. "
                    "Symptoms usually develop gradually over time.")
        # symptom question but no disease named
        return ("Which condition are you asking about — diabetes, heart "
                "disease, or Parkinson's? I can list the common symptoms "
                "for any of the three.")

    # ---- general health knowledge keywords ----
    if 'blood pressure' in q or 'hypertension' in q:
        return ("High blood pressure (hypertension) means the force of blood "
                "against artery walls is consistently too high. Normal is "
                "below 120/80 mmHg. High BP increases risk of heart disease, "
                "stroke, and kidney problems. Regular monitoring, reduced "
                "sodium intake, exercise, and medication (if prescribed) can "
                "help manage it.")

    if 'diabetes' in q or 'blood sugar' in q or 'glucose' in q:
        return ("Diabetes is a condition where blood sugar levels are too "
                "high, either because the body doesn't produce enough insulin "
                "or can't use it effectively. Managing diet, exercise, and "
                "monitoring glucose levels are key to control.")

    if 'bmi' in q or 'body mass index' in q:
        return ("BMI (Body Mass Index) estimates body fat based on height "
                "and weight. 18.5–24.9 is considered a healthy range, but it "
                "doesn't account for muscle mass, so it's best used alongside "
                "other health indicators.")

    if 'cholesterol' in q:
        return ("Cholesterol is a fatty substance in your blood. LDL ('bad') "
                "cholesterol can build up in arteries, while HDL ('good') "
                "cholesterol helps remove it. Diet, exercise, and sometimes "
                "medication help keep levels balanced.")

    if 'heart rate' in q or 'pulse' in q:
        return ("A normal resting heart rate for adults is typically 60–100 "
                "beats per minute. Lower resting rates are often seen in "
                "people who are more physically fit.")

    if 'parkinson' in q:
        return ("Parkinson's disease is a progressive neurological condition "
                "that affects movement, often causing tremors, stiffness, and "
                "slowed movement. Early detection through voice/motor pattern "
                "analysis (like this app's prediction tool) can help prompt "
                "earlier specialist evaluation.")

    if 'heart disease' in q or 'cardiac' in q or 'cardiovascular' in q:
        return ("Heart disease covers a range of conditions affecting the "
                "heart, often linked to high blood pressure, high cholesterol, "
                "smoking, and lack of exercise. Regular checkups and "
                "cardiovascular screening help catch risk early.")

    if 'doctor' in q or 'specialist' in q or 'consult' in q:
        return ("It's always a good idea to confirm any health concern with "
                "a licensed doctor. If you've run a prediction in this app, "
                "check the result's risk level — a 'High Risk' result "
                "generally warrants a specialist visit sooner rather than later.")

    if 'hello' in q or 'hi' in q or 'hey' in q:
        return ("Hello! I'm your AI Health Assistant. Ask me about your "
                "results, or general topics like blood pressure, diabetes, "
                "BMI, or cholesterol.")

    if 'thank' in q:
        return "You're welcome! Let me know if you have any other questions."

    # ---- fallback for anything that doesn't match a keyword ----
    return ("Thanks for your question! I can share general health "
            "information, but for anything specific to your symptoms or "
            "results, please consult a qualified healthcare professional.")


# -----------------------------------------------------------------------
# 1b. REAL AI REPLY (Claude API), with automatic fallback to the
#     keyword bot above if no API key is set or the request fails.
# -----------------------------------------------------------------------
def bot_reply_ai(question, history=None, chat_messages=None):
    client = _get_client()
    if client is None:
        # No key configured yet -- use the keyword bot so the app
        # still works while you're setting up your API key.
        return bot_reply(question, history)

    # Give the model a little context about the user's own predictions,
    # if any exist, so it can answer things like "what was my latest result?"
    context_note = ""
    if history:
        recent = history[-3:]
        lines = "\n".join(
            f"- {h['timestamp']}: {h['condition']} — {h['risk']} Risk ({h['result']})"
            for h in recent
        )
        context_note = f"\n\nCONTEXT (user's recent predictions in this app):\n{lines}"

    # Include a little recent chat history so follow-up questions make sense
    transcript = ""
    if chat_messages:
        for m in chat_messages[-6:]:
            if m["role"] in ("user", "assistant"):
                speaker = "User" if m["role"] == "user" else "Assistant"
                transcript += f"{speaker}: {m['content']}\n"

    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{transcript}"
        f"{context_note}\n\n"
        f"User: {question}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # fast + free-tier friendly
            contents=full_prompt,
        )
        return response.text
    except Exception:
        # API hiccup (rate limit, network, bad key, etc.) -- degrade
        # gracefully instead of crashing the app.
        fallback = bot_reply(question, history)
        return f"{fallback}\n\n_(AI service temporarily unavailable — showing basic info instead.)_"


# -----------------------------------------------------------------------
# 2. THE CHAT PAGE UI
#    Paste this under: if selected == 'AI Health Assistant':
# -----------------------------------------------------------------------
def render_ai_assistant_page():
    st.title('AI Health Assistant')
    if _get_client() is not None:
        st.caption('🟢 Online · Powered by Gemini · Ask me anything about your results or general health topics')
    else:
        st.caption('🟡 Basic mode (no API key set) · Ask about your results or general health topics')

    history = st.session_state.get('history', [])

    # keep chat messages across reruns
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {'role': 'assistant',
             'content': "Hello! I'm your AI Health Assistant. How can I help "
                        "you today?"}
        ]

    # show past messages
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])

    # quick-reply buttons
    st.write('')
    chip_cols = st.columns(4)
    quick_replies = [
        "What's my latest result?",
        "What does high blood pressure mean?",
        "Tell me about BMI",
        "When should I see a specialist?",
    ]
    chip_clicked = None
    for col, label in zip(chip_cols, quick_replies):
        with col:
            if st.button(label, key=f"chip_{label}", use_container_width=True):
                chip_clicked = label

    # chat input box
    user_prompt = st.chat_input("Type your health question…") or chip_clicked

    if user_prompt:
        st.session_state.chat_messages.append({'role': 'user', 'content': user_prompt})
        with st.chat_message('user'):
            st.markdown(user_prompt)

        reply = bot_reply_ai(user_prompt, history, st.session_state.chat_messages)

        with st.chat_message('assistant'):
            st.markdown(reply)
        st.session_state.chat_messages.append({'role': 'assistant', 'content': reply})

    st.caption('This is a prototype for demonstration only — not a real '
               'diagnostic tool. Always confirm clinical decisions with a '
               'licensed physician.')


# =======================================================================
# HOW TO ATTACH THIS TO YOUR PROJECT FILE:
#
# 1. Add 'AI Health Assistant' to your sidebar option_menu list, e.g.:
#
#       selected = option_menu('Multiple Disease Prediction System',
#                               ['Dashboard',
#                                'Disease Prediction',
#                                'AI Health Assistant'],
#                               icons=['speedometer2', 'clipboard2-pulse',
#                                      'chat-dots'],
#                               default_index=0)
#
# 2. Add this routing block near your other `if selected == ...:` blocks:
#
#       if selected == 'AI Health Assistant':
#           render_ai_assistant_page()
#
# That's it — no API key, no extra installs, works immediately.
# =======================================================================
