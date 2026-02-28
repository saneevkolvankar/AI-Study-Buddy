import streamlit as st
import os
from dotenv import load_dotenv
from google import genai

# ---------- LOAD ENV ----------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE_API_KEY not found in .env file")
    st.stop()

# ---------- CREATE GEMINI CLIENT ----------
client = genai.Client(api_key=api_key)

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Study Buddy", layout="wide")

# ---------- SIDEBAR ----------
st.sidebar.title("📘 Input Material")

input_method = st.sidebar.radio(
    "Choose input method:",
    ["Paste Text", "Upload Text File"]
)

study_text = ""

if input_method == "Paste Text":
    study_text = st.sidebar.text_area(
        "Paste your study material here:",
        height=250
    )
else:
    uploaded_file = st.sidebar.file_uploader("Upload a .txt file")
    if uploaded_file:
        study_text = uploaded_file.read().decode("utf-8")

# ---------- MAIN TITLE ----------
st.title("📚 AI Study Buddy")
st.write("Upload your study material and let AI help you learn!")

# ---------- GEMINI FUNCTION ----------
def ask_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ---------- STUDY TOOLS ----------
if study_text:

    st.subheader("📄 Your Study Material")
    st.text_area("Preview", study_text, height=200)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Summary", "Flashcards", "Quiz", "Ask Questions"]
    )

    # ---------- SUMMARY ----------
    with tab1:
        st.subheader("Summary")
        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                summary = ask_gemini(
                    "Summarize in simple language:\n" + study_text[:1500]
                )
                st.success(summary)

    # ---------- FLASHCARDS ----------
    with tab2:
        st.subheader("Flashcards")

        if st.button("Generate Flashcards"):
            with st.spinner("Creating flashcards..."):
                flashcards_text = ask_gemini(
                    """Create 5 flashcards from the text.

Return format EXACTLY like:

Flashcard 1
Question: ...
Answer: ...

Text:
""" + study_text[:1500]
                )
                st.session_state.flashcards = flashcards_text

        if "flashcards" in st.session_state:
            cards = st.session_state.flashcards.split("Flashcard")

            for card in cards:
                if card.strip() == "":
                    continue

                lines = card.strip().split("\n")

                title = lines[0]
                question = ""
                answer = ""

                for line in lines:
                    if line.startswith("Question"):
                        question = line.replace("Question:", "").strip()
                    if line.startswith("Answer"):
                        answer = line.replace("Answer:", "").strip()

                st.success(f"Flashcard {title}")
                st.write(f"**Question:** {question}")
                st.write(f"**Answer:** {answer}")
                st.write("---")

    # ---------- QUIZ ----------
    with tab3:
        st.subheader("Quiz")

        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz..."):
                quiz_text = ask_gemini(
                    """Create 5 multiple choice questions.

Return format:

Q1: question
A) option
B) option
C) option
D) option
Answer: A

Text:
""" + study_text[:1500]
                )
                st.session_state.quiz = quiz_text

        if "quiz" in st.session_state:
            questions = st.session_state.quiz.split("Q")

            for q in questions:
                if q.strip() == "":
                    continue

                lines = q.strip().split("\n")
                question = lines[0]
                options = lines[1:5]
                answer_line = lines[-1]
                correct = answer_line.split(":")[-1].strip()

                st.write(f"### {question}")

                choice = st.radio("Choose answer:", options, key=question)

                if st.button(f"Check {question}", key="btn"+question):
                    if choice.startswith(correct):
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Correct answer: {correct}")

                st.write("---")

    # ---------- ASK QUESTIONS ----------
    with tab4:
        st.subheader("Ask a Question about the Material")
        user_question = st.text_input("Enter your question:")

        if st.button("Get Answer"):
            if user_question:
                with st.spinner("Finding answer..."):
                    answer = ask_gemini(
                        f"Answer from this material:\n{study_text[:1500]}\nQuestion: {user_question}"
                    )
                    st.success(answer)
            else:
                st.warning("Please enter a question.")

else:
    st.info("Please provide study material using the sidebar.")

st.write("---")
st.caption("Built with Streamlit + Google Gemini AI")