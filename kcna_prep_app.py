import streamlit as st
import pandas as pd

# ✅ Set page config FIRST
st.set_page_config(page_title="KCNA Exam Prep", layout="centered")

# === CONFIG ===
EXCEL_FILE = "KCNA Exam Prep Questions.xlsx"
SHEET_NAMES = None  # Load all sheets
OPTION_LETTERS = ["A", "B", "C", "D", "E"]

# === Load and combine all sheets ===
@st.cache_data
def load_data():
    all_sheets = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAMES)
    frames = []
    for sheet_df in all_sheets.values():
        if not sheet_df.empty and "Question" in sheet_df.columns:
            frames.append(sheet_df)
    full_df = pd.concat(frames, ignore_index=True)
    full_df["Correct Answer"] = full_df["Correct Answer"].astype(str).str.strip().str.upper()
    return full_df

df = load_data()

# === Session state initialization ===
# === Session state initialization ===
if "question_order" not in st.session_state:
    st.session_state.question_order = df.sample(frac=1).index.tolist()
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.answered_this_session = set()

if "answered_all_time" not in st.session_state:
    st.session_state.answered_all_time = set()

if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False

# === Main App UI ===
st.title("📘 KCNA Exam Prep App")

# Get current question
current_idx = st.session_state.question_order[st.session_state.q_index]
row = df.loc[current_idx]

# Display question
st.markdown(f"### Question {st.session_state.q_index + 1} of {len(df)}")
st.markdown(f"**{row['Question']}**")

# Display options
options = []
for letter in OPTION_LETTERS:
    col_name = f"Option {letter}"
    if pd.notna(row.get(col_name)):
        options.append(f"{letter}) {row[col_name]}")

user_choice = st.radio("Select your answer:", options, key=f"choice_{st.session_state.q_index}")

# Submit button
if st.button("Submit") and current_idx not in st.session_state.answered_this_session:
    selected_letter = user_choice.split(")")[0]
    correct_letter = row["Correct Answer"]
    correct_text = row.get(f"Option {correct_letter}", "Unknown")

    # Record answer
    st.session_state.answered_this_session.add(current_idx)
    st.session_state.answered_all_time.add(current_idx)
    st.session_state.feedback_shown = True

    if selected_letter == correct_letter:
        st.success("✅ Correct!")
        st.session_state.score += 1
    else:
        st.error(f"❌ Incorrect. Correct answer: {correct_letter}) {correct_text}")
        st.info(f"📘 Explanation: {row.get('Explanation', 'No explanation provided.')}")

# Next button
if st.session_state.feedback_shown and st.button("Next Question"):
    st.session_state.q_index += 1
    st.session_state.feedback_shown = False
    if st.session_state.q_index >= len(df):
        st.session_state.q_index = 0  # restart from beginning
        st.success("🎉 You've completed all questions in this session!")
    st.rerun()

# Score + Progress
st.markdown(f"#### ✅ Session Score: {st.session_state.score} / {len(st.session_state.answered_this_session)}")
st.markdown(f"#### 🧠 Total Unique Questions Answered: {len(st.session_state.answered_all_time)} / {len(df)}")
st.progress(len(st.session_state.answered_all_time) / len(df))
