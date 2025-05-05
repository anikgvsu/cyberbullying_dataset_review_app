import streamlit as st
import json
import pandas as pd
import os

# File paths
DATA_FILE = "cyberbullying_conversations_generated.json"
REVIEW_FILE = "conversation_reviews.csv"

if "index" not in st.session_state:
    st.session_state.index = 0


# Load JSON data
@st.cache_data
def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["cyberbullying_scenarios"]

# Save review
def save_review(entry, cyberbullying_presence, content_authenticity, comments):
    new_entry = {
        "id": entry["id"],
        "bullying_type": entry["bullying_type"],
        "age_group": entry["age_group"],
        "scenario": entry["scenario"],
        "cyberbullying_presence": cyberbullying_presence,
        "content_authenticity": content_authenticity,
        "comments": comments
    }

    # Load existing reviews or create new DataFrame
    if os.path.exists(REVIEW_FILE):
        df = pd.read_csv(REVIEW_FILE)
        df = df[df["id"] != entry["id"]]  # Remove existing entry if re-reviewed
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    else:
        df = pd.DataFrame([new_entry])

    df.to_csv(REVIEW_FILE, index=False)
    st.success("Review saved!")

# Sidebar instructions and metric descriptions
with st.sidebar:
    st.title("📋 Review Guide")
    st.markdown("""
Welcome to the **Cyberbullying Conversation Review Tool**.

Please read the conversation carefully and evaluate it using the following two metrics:

---

### 🚨 Cyberbullying Presence  
**Definition**: How clearly does the conversation show signs of cyberbullying?  
**Consider**:  
- Intentional harm  
- Power imbalance  
- Repetition or escalation  
- Use of bullying tactics (mocking, threats, exclusion, etc.)  
**Scale**:  
1 = None → 5 = Strong evidence of cyberbullying

---

### 🧠 Content Authenticity  
**Definition**: How realistic and natural is the conversation for the stated age group and context?  
**Consider**:  
- Language style and tone  
- Flow and coherence  
- Age-appropriate expressions  
**Scale**:  
1 = Fake/stilted → 5 = Highly realistic

---

✅ After rating, add any optional comments and click **Save Review**.
    """)


# Main app
data = load_data()
index = st.session_state.index
entry = data[index]

st.subheader(f"Scenario: {entry['scenario']}")
st.markdown(f"**Bullying Type**: {entry['bullying_type']} | **Age Group**: {entry['age_group']}")

max_index = len(load_data()) - 1
selected_index = st.number_input(
    "Go to Conversation Index",
    min_value=0,
    max_value=max_index,
    value=st.session_state.index,
    step=1
)

# Update state if changed manually
if selected_index != st.session_state.index:
    st.session_state.index = selected_index
    st.experimental_rerun()


# Show conversation
st.markdown("### Conversation")
for turn in entry["conversation"]:
    role = turn["role"]
    text = turn["text"]
    st.markdown(f"**{role}**: {text}")

st.markdown("---")
st.markdown("### Evaluation")

cyberbullying_presence = st.slider(
    "Cyberbullying Presence (1 = None, 5 = Strong)",
    min_value=1, max_value=5, value=3
)

content_authenticity = st.slider(
    "Content Authenticity (1 = Fake, 5 = Very Realistic)",
    min_value=1, max_value=5, value=3
)

comments = st.text_area("Optional Comments")

if st.button("Save Review"):
    save_review(entry, cyberbullying_presence, content_authenticity, comments)
    st.success("Review saved!")

    # Move to next entry if not last
    if st.session_state.index < len(load_data()) - 1:
        st.session_state.index += 1
        st.experimental_rerun()

