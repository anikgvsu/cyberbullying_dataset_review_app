import streamlit as st
import json
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---- Connect to Google Sheets ----
@st.cache_resource
def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
    client = gspread.authorize(credentials)
    return client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1

# ---- State Initialization ----
if "index" not in st.session_state:
    st.session_state.index = 0

# ---- Config ----
DATA_FILE = "cyberbullying_conversations_generated.json"
REVIEW_FILE = "conversation_reviews.csv"

# ---- Load Data ----
@st.cache_data
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()
max_index = len(data) - 1

# ---- Load Reviews ----
review_columns = [
    "id", "reviewer", "group", "type", "subtype", "platform",
    "cyberbullying_presence", "content_authenticity", "comments", "timestamp"
]

if os.path.exists(REVIEW_FILE) and os.path.getsize(REVIEW_FILE) > 0:
    try:
        review_df = pd.read_csv(REVIEW_FILE)
    except Exception:
        st.warning("⚠️ Could not read review file. Using empty fallback.")
        review_df = pd.DataFrame(columns=review_columns)
else:
    review_df = pd.DataFrame(columns=review_columns)

# ---- Track Reviewed ----
reviewed_pairs = set(zip(review_df["id"], review_df["reviewer"]))
completed = len(review_df["id"].unique())
total = len(data)
progress = int((completed / total) * 100)

# ---- Sidebar ----
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
Welcome to the **Cyberbullying Conversation Review Tool**.

Please read the story and conversation carefully and evaluate it using the following two metrics:

---

### 🚨 Cyberbullying Presence  
**Definition**: How clearly does the conversation show signs of cyberbullying?  
**Scale**:  
1 = None → 5 = Strong evidence

---

### 🧠 Content Authenticity  
**Definition**: How realistic and natural is the conversation for the platform and context?  
**Scale**:  
1 = Fake/stilted → 5 = Highly realistic

✅ After rating, add optional comments and click **Save Review**.
    """)

# ---- Skip Reviewed ----
if skip_reviewed and reviewer_id:
    while (data[st.session_state.index]["id"], reviewer_id) in reviewed_pairs:
        if st.session_state.index < max_index:
            st.session_state.index += 1
        else:
            break

# ---- Show Current Entry ----
index = st.session_state.index
entry = data[index]

st.subheader(f"Conversation {entry['id']}")
st.markdown(f"**Group**: {entry['group']}  \n**Type**: {entry['type']}  \n**Subtype**: {entry['subtype']}  \n**Platform**: {entry.get('platform', 'Unknown')}")

st.markdown("### 📝 Story")
st.info(entry["story"])

st.markdown("### 💬 Conversation")
for turn in entry["conversation"]:
    st.markdown(f"**{turn['sender']}**: {turn['message']}")

# ---- Evaluation Sliders ----
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

# ---- Save Review ----
def save_review(entry, cyberbullying_presence, content_authenticity, comments, reviewer_id):
    sheet = connect_to_gsheet()
    row = [
        entry["id"],
        reviewer_id,
        entry["group"],
        entry["type"],
        entry["subtype"],
        entry["platform"],
        cyberbullying_presence,
        content_authenticity,
        comments,
        pd.Timestamp.now().isoformat()
    ]
    sheet.append_row(row)
    st.success("✅ Review saved to Google Sheets!")

    # Auto-advance
    if st.session_state.index < max_index:
        st.session_state.index += 1
        st.rerun()

# ---- Save Button ----
if reviewer_id.strip() == "":
    st.warning("Please enter your name or ID in the sidebar to save your review.")
else:
    if st.button("💾 Save Review"):
        save_review(entry, cyberbullying_presence, content_authenticity, comments, reviewer_id)
