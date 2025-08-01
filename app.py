print("App started")
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()
from database import init_database, get_temple_count, get_contribution_count, get_recent_contributions
from utils.supabase_client import get_supabase_client

# Configure page
st.set_page_config(
    page_title="Temple Heritage Hub",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_database()

# Custom CSS for card styling
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
}
.nav-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.nav-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.title("🏛️ Temple Heritage Hub")
    st.markdown("### A collaborative platform to document, preserve, and share temple heritage")
    
    # Check Supabase connection
    try:
        supabase = get_supabase_client()
        if supabase:
            st.success("✅ Connected to Supabase database")
        else:
            st.warning("⚠️ Supabase connection not configured")
            st.info("""
            To connect to your Supabase database:
            
            1. **Get your database password:**
               - Go to: https://supabase.com/dashboard/project/rrbrghxzuzzxroqbwfqi
               - Navigate to Settings > Database
               - Copy your database password
            
            2. **Set the environment variable:**
               - Windows: `set SUPABASE_PASSWORD=your_password_here`
               - Linux/Mac: `export SUPABASE_PASSWORD=your_password_here`
            
            3. **Or run the setup script:**
               - `python setup_supabase.py`
            
            The app will work with limited functionality until the database is connected.
            """)
    except Exception as e:
        st.error(f"❌ Database connection error: {str(e)}")
        st.info("Please ensure your Supabase credentials are set correctly.")
    
    # Statistics section
    st.markdown("---")
    st.subheader("📊 Platform Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        temple_count = get_temple_count()
        st.metric("Temples Documented", temple_count, delta=None)
    
    with col2:
        contribution_count = get_contribution_count()
        st.metric("Total Contributions", contribution_count, delta=None)
    
    with col3:
        st.metric("Active Contributors", "Coming Soon", delta=None)
    
    with col4:
        st.metric("Heritage Items", "Coming Soon", delta=None)
    
    # Navigation cards
    st.markdown("---")
    st.subheader("🧭 Navigate Heritage Hub")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload Content", use_container_width=True):
            st.success("Navigate to Upload Content page using the sidebar!")
        st.markdown("Contribute photos, audio, documents, temple data, or events")
        
        if st.button("🗂️ Browse Temples", use_container_width=True):
            st.success("Navigate to Browse Temples page using the sidebar!")
        st.markdown("Explore documented temples with search and filters")
    
    with col2:
        if st.button("🌟 Community Contributions", use_container_width=True):
            st.success("Navigate to Community Contributions page using the sidebar!")
        st.markdown("View all community uploads and contributions")
        
        if st.button("📈 Heritage Statistics", use_container_width=True):
            st.success("Navigate to Heritage Statistics page using the sidebar!")
        st.markdown("Analytics and insights about platform activity")
    
    with col3:
        if st.button("🗺️ Heritage Map", use_container_width=True):
            st.success("Navigate to Heritage Map page using the sidebar!")
        st.markdown("Interactive map of all heritage locations")
        
        st.markdown("") # Spacer
        st.markdown("") # Spacer
    
    # Recent activity
    st.markdown("---")
    st.subheader("🕒 Recent Activity")
    
    recent_contributions = get_recent_contributions(limit=5)
    if not recent_contributions.empty:
        for _, contribution in recent_contributions.iterrows():
            with st.expander(f"{contribution['title']} - {contribution['content_type']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(contribution['description'])
                    if contribution['contributor_name']:
                        st.caption(f"By: {contribution['contributor_name']}")
                    else:
                        st.caption("By: Anonymous")
                with col2:
                    st.caption(f"📍 {contribution['location_address']}")
                    # Handle created_at safely
                    try:
                        if pd.notna(contribution['created_at']):
                            if hasattr(contribution['created_at'], 'strftime'):
                                st.caption(f"📅 {contribution['created_at'].strftime('%Y-%m-%d')}")
                            else:
                                st.caption(f"📅 {contribution['created_at']}")
                        else:
                            st.caption("📅 Date not available")
                    except:
                        st.caption("📅 Date not available")
    else:
        st.info("No recent contributions yet. Be the first to contribute!")
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and Supabase")
    st.markdown("Help us preserve temple heritage — contribute today!")

if __name__ == "__main__":
    main()
