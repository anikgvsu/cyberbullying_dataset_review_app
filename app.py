import streamlit as st
import json
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ---- Page Config ----
st.set_page_config(
    page_title="AI vs Human Conversation Review",
    page_icon="🤖",
    layout="wide"
)

# ---- Connect to Google Sheets ----
@st.cache_resource
def connect_to_gsheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
        client = gspread.authorize(credentials)
        return client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

# ---- Load Data ----
@st.cache_data
def load_conversations():
    try:
        with open("conversations_id_only.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("conversations_id_only.json file not found!")
        return []
    
# ---- Save Review Function ----
def save_review(conversation_id, assessment, reviewer_name):
    """Save review to Google Sheets and update session state"""
    sheet = connect_to_gsheet()
    
    if sheet:
        try:
            # Prepare row data
            row = [
                conversation_id,
                reviewer_name,
                assessment,
                datetime.now().isoformat()
            ]
            
            # Add to Google Sheets
            sheet.append_row(row)
            
            # Update session state
            st.session_state.completed_reviews.add(st.session_state.current_index)
            
            # Show success message
            st.success(f"✅ Review saved: {assessment}")
            
            # Auto-advance to next conversation
            if st.session_state.current_index < total_conversations - 1:
                # Find next unreviewed conversation
                next_index = st.session_state.current_index + 1
                while next_index < total_conversations and next_index in st.session_state.completed_reviews:
                    next_index += 1
                
                if next_index < total_conversations:
                    st.session_state.current_index = next_index
                else:
                    st.balloons()
                    st.success("🎉 You have completed all conversations! Thank you for your contribution!")
                
                st.rerun()
            else:
                st.balloons()
                st.success("🎉 You have completed all conversations! Thank you for your contribution!")
                
        except Exception as e:
            st.error(f"Error saving review: {e}")
    else:
        st.error("Could not connect to database. Please try again.")

# ---- Initialize Session State ----
if "reviewer_name" not in st.session_state:
    st.session_state.reviewer_name = ""
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "show_instructions" not in st.session_state:
    st.session_state.show_instructions = True
if "completed_reviews" not in st.session_state:
    st.session_state.completed_reviews = set()

# Load conversations
conversations = load_conversations()
total_conversations = len(conversations)

# ---- Header ----
st.title("🤖 AI vs Human Conversation Review")
st.markdown("Help us determine whether conversations appear to be AI-generated or human-written!")

# ---- Sidebar: Reviewer Info & Progress ----
with st.sidebar:
    st.header("👤 Reviewer Information")
    
    # Get reviewer name
    reviewer_name = st.text_input(
        "Your Name/ID *", 
        value=st.session_state.reviewer_name,
        placeholder="e.g., John Doe or JD001",
        help="Required to track your reviews"
    )
    
    if reviewer_name != st.session_state.reviewer_name:
        st.session_state.reviewer_name = reviewer_name
    
    st.markdown("---")
    
    # Progress tracking
    st.header("📊 Progress")
    progress = len(st.session_state.completed_reviews)
    st.metric("Completed Reviews", f"{progress}/{total_conversations}")
    st.progress(progress / total_conversations if total_conversations > 0 else 0)
    
    st.markdown("---")
    
    # Navigation
    st.header("🧭 Navigation")
    
    # Jump to conversation
    jump_to = st.number_input(
        "Jump to Conversation ID",
        min_value=0,
        max_value=total_conversations - 1 if total_conversations > 0 else 0,
        value=st.session_state.current_index
    )
    
    if st.button("Go to Conversation"):
        st.session_state.current_index = jump_to
        st.rerun()
    
    # Skip reviewed option
    skip_reviewed = st.checkbox("Skip already reviewed", value=True)
    
    if st.button("Next Unreviewed") and skip_reviewed:
        # Find next unreviewed conversation
        for i in range(st.session_state.current_index + 1, total_conversations):
            if i not in st.session_state.completed_reviews:
                st.session_state.current_index = i
                st.rerun()
                break

# ---- Instructions Modal ----
if st.session_state.show_instructions:
    with st.container():
        st.markdown("""
        ### 📋 Instructions
        
        You will be shown conversations one at a time. Your task is to determine whether each conversation appears to be:
        
        - **AI-Generated**: The conversation seems artificial, repetitive, or unnatural
        - **Human-Written**: The conversation feels authentic and natural
        """)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Reviewing", type="primary", use_container_width=True):
                st.session_state.show_instructions = False
                st.rerun()

# ---- Main Review Interface ----
if not st.session_state.show_instructions and conversations:
    current_conv = conversations[st.session_state.current_index]
    
    # Conversation header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"### 💬 Conversation {current_conv['id']} of {total_conversations - 1}")
    
    # Check if already reviewed
    is_reviewed = st.session_state.current_index in st.session_state.completed_reviews
    if is_reviewed:
        st.info("✅ You have already reviewed this conversation")
    
    # Display conversation
    st.markdown("#### Conversation:")
    
    with st.container():
        # Create a nice conversation display
        for i, message in enumerate(current_conv['conversation']):
            sender = message['sender']
            text = message['message']
            
            # Alternate sides for different senders
            if i % 2 == 0:
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 5px 0; margin-right: 20%;">
                    <strong>{sender}:</strong> {text}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #e8f4f8; padding: 10px; border-radius: 10px; margin: 5px 0; margin-left: 20%;">
                    <strong>{sender}:</strong> {text}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Review buttons
    st.markdown("#### Your Assessment:")
    
    if not st.session_state.reviewer_name.strip():
        st.warning("⚠️ Please enter your name in the sidebar before submitting a review.")
    else:
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🤖 AI-Generated", type="secondary", use_container_width=True):
                save_review(current_conv['id'], "AI-Generated", st.session_state.reviewer_name)
        
        with col3:
            if st.button("👤 Human-Written", type="secondary", use_container_width=True):
                save_review(current_conv['id'], "Human-Written", st.session_state.reviewer_name)
    
    # Navigation buttons
    st.markdown("---")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
    
    with nav_col1:
        if st.button("⬅️ Previous") and st.session_state.current_index > 0:
            st.session_state.current_index -= 1
            st.rerun()
    
    with nav_col3:
        if st.button("➡️ Next") and st.session_state.current_index < total_conversations - 1:
            st.session_state.current_index += 1
            st.rerun()



# ---- Footer ----
if not st.session_state.show_instructions:
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 14px;">
        Thank you for participating in this research study! 
        Your reviews help improve our understanding of AI-generated content.
    </div>
    """, unsafe_allow_html=True)
