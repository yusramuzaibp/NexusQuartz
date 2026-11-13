# =======================================================================
# AI HEALTH ASSISTANT — real LLM (Google Gemini) with keyword-bot fallback
# Paste this whole block into your project file, then add
# 'AI Health Assistant' to your sidebar option_menu list (see note
# at the bottom of this file for that one-line change).
# =======================================================================

import streamlit as st
import streamlit as st
from chatbot_engine import get_best_match
from database.database import get_user_predictions


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
    q = question.lower().strip()
    history = history or []

    # Handle latest prediction
    if any(phrase in q for phrase in [
        'my prediction',
        'my result',
        'my latest',
        'latest result',
        'last result',
        'recent result'
    ]):
        if not history:
            return "I couldn't find any saved predictions in your account."

        # Database returns newest record first
        latest = history[0]

        return (
            f"Your most recent test was for **{latest['condition']}**, "
            f"classified as **{latest['risk']} Risk** — result: "
            f"\"{latest['result']}\".\n\n"
            f"Recorded on: {latest['timestamp']}"
        )

    # Handle prediction history
    if any(word in q for word in ['history', 'previous', 'past result']):
        if not history:
            return "You don't have any saved prediction records yet."

        lines = '\n'.join(
            f"- {h['timestamp']}: {h['condition']} — {h['risk']} Risk"
            for h in history[:5]
        )
        return f"Here are your five most recent predictions:\n{lines}"

    # Handle greetings
    if any(word in q.split() for word in ['hello', 'hi', 'hey']):
        return (
            "Hello! I'm your AI Health Assistant. "
            "Ask me about diabetes, heart disease, "
            "Parkinson's disease or general health."
        )

    if 'thank' in q:
        return "You're welcome! Let me know if you have any other questions."

    answer, score = get_best_match(question)
    return answer

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
    st.caption(
    "🟢 Offline · Powered by TF-IDF and Cosine Similarity "
    "· Ask about diabetes, heart disease, Parkinson's and general health"
)

    history = get_user_predictions(st.session_state.user_id)
    
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

        reply = bot_reply(user_prompt, history)

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
