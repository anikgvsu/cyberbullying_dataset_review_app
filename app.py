import streamlit as st
import json
import pandas as pd
import os

# ---- INIT STATE ----
if "index" not in st.session_state:
    st.session_state.index = 0

# ---- FILES ----
DATA_FILE = "cyberbullying_conversations_generated.json"
REVIEW_FILE = "conversation_reviews.csv"

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["cyberbullying_scenarios"]

data = load_data()
max_index = len(data) - 1

# ---- LOAD REVIEWS ----
if os.path.exists(REVIEW_FILE) and os.path.getsize(REVIEW_FILE) > 0:
    review_df = pd.read_csv(REVIEW_FILE)
else:
    review_df = pd.DataFrame(columns=["id", "reviewer"])


# ---- TRACK REVIEWED ----
reviewed_pairs = set(zip(review_df["id"], review_df["reviewer"]))
reviewed_ids = set(review_df["id"])
completed = len(review_df["id"].unique())
total = len(data)
progress = int((completed / total) * 100)

# ---- SIDEBAR ----
with st.sidebar:
    st.title("📋 Review Guide")

    reviewer_id = st.text_input("🧑‍💻 Your Name or ID", value="", help="Required to save your review")

    st.markdown("### ⏩ Navigation")
    skip_reviewed = st.checkbox("Skip reviewed conversations", value=True)

    selected_index = st.number_input(
        "Go to Conversation Index",
        min_value=0,
        max_value=max_index,
        value=st.session_state.index,
        step=1
    )
    if selected_index != st.session_state.index:
        st.session_state.index = selected_index
        st.rerun()

    st.markdown("---")
    st.markdown(f"✅ Reviewed: **{completed} / {total}** ({progress}%)")
    st.progress(progress / 100)

    st.markdown("---")
    st.markdown("""
### 🚨 Cyberbullying Presence  
Rate how clearly the conversation shows signs of cyberbullying  
(1 = none, 5 = very strong)

### 🧠 Content Authenticity  
Rate how natural and realistic the conversation feels  
(1 = fake/stilted, 5 = highly realistic)
""")

# ---- SKIP LOGIC ----
if skip_reviewed and reviewer_id:
    while (data[st.session_state.index]["id"], reviewer_id) in reviewed_pairs:
        if st.session_state.index < max_index:
            st.session_state.index += 1
        else:
            break

# ---- DISPLAY ----
index = st.session_state.index
entry = data[index]

st.subheader(f"Scenario {index}: {entry['scenario']}")
st.markdown(f"**Bullying Type**: {entry['bullying_type']} | **Age Group**: {entry['age_group']}")

if "mini_story" in entry:
    st.markdown("### 📝 Mini Story")
    st.info(entry["mini_story"])


st.markdown("### Conversation")
for turn in entry["conversation"]:
    st.markdown(f"**{turn['role']}**: {turn['text']}")

st.markdown("---")
st.markdown("### Evaluation")

cyberbullying_presence = st.slider(
    "🚨 Cyberbullying Presence (1 = None, 5 = Strong)",
    min_value=1, max_value=5, value=3
)

content_authenticity = st.slider(
    "🧠 Content Authenticity (1 = Fake, 5 = Very Realistic)",
    min_value=1, max_value=5, value=3
)

comments = st.text_area("💬 Optional Comments")

# ---- SAVE FUNCTION ----
def save_review(entry, cyberbullying_presence, content_authenticity, comments, reviewer_id):
    review = {
        "id": entry["id"],
        "reviewer": reviewer_id,
        "bullying_type": entry["bullying_type"],
        "age_group": entry["age_group"],
        "scenario": entry["scenario"],
        "cyberbullying_presence": cyberbullying_presence,
        "content_authenticity": content_authenticity,
        "comments": comments
    }

    if os.path.exists(REVIEW_FILE) and os.path.getsize(REVIEW_FILE) > 0:
        df = pd.read_csv(REVIEW_FILE)
        df = df[~((df["id"] == entry["id"]) & (df["reviewer"] == reviewer_id))]
        df = pd.concat([df, pd.DataFrame([review])], ignore_index=True)
    else:
        df = pd.DataFrame([review])


    df.to_csv(REVIEW_FILE, index=False)
    st.success("✅ Review saved!")

    # Auto advance
    if st.session_state.index < max_index:
        st.session_state.index += 1
        st.rerun()

# ---- SAVE BUTTON ----
if reviewer_id.strip() == "":
    st.warning("Please enter your name or ID in the sidebar to save your review.")
else:
    if st.button("💾 Save Review"):
        save_review(entry, cyberbullying_presence, content_authenticity, comments, reviewer_id)
