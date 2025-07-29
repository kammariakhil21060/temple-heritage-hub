import streamlit as st
import pandas as pd
from database import get_all_contributions
from datetime import datetime, timedelta

st.set_page_config(page_title="Community Contributions", page_icon="🌟", layout="wide")

st.title("🌟 Community Contributions")
st.markdown("Explore all community uploads and contributions to the temple heritage platform.")

# Get contributions data
contributions_df = get_all_contributions()

if contributions_df.empty:
    st.info("No contributions yet. Be the first to contribute!")
    if st.button("📤 Upload Content"):
        st.switch_page("pages/1_Upload_Content.py")
else:
    # Filters section
    st.subheader("🔍 Filter Contributions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Content type filter
        content_types = ["All Types"] + list(contributions_df['content_type'].unique())
        selected_content_type = st.selectbox("Content Type", content_types)
    
    with col2:
        # Contributor filter
        contributors = ["All Contributors"] + [c for c in contributions_df['contributor_name'].unique() if c is not None] + ["Anonymous"]
        selected_contributor = st.selectbox("Contributor", contributors)
    
    with col3:
        # Date range filter
        date_options = ["All Time", "Last 7 days", "Last 30 days", "Last 90 days"]
        selected_date_range = st.selectbox("Date Range", date_options)
    
    with col4:
        # Sort options
        sort_options = ["Newest First", "Oldest First", "Alphabetical"]
        selected_sort = st.selectbox("Sort By", sort_options)
    
    # Apply filters
    filtered_df = contributions_df.copy()
    
    # Content type filter
    if selected_content_type != "All Types":
        filtered_df = filtered_df[filtered_df['content_type'] == selected_content_type]
    
    # Contributor filter
    if selected_contributor != "All Contributors":
        if selected_contributor == "Anonymous":
            filtered_df = filtered_df[filtered_df['contributor_name'].isna()]
        else:
            filtered_df = filtered_df[filtered_df['contributor_name'] == selected_contributor]
    
    # Date range filter
    if selected_date_range != "All Time":
        now = datetime.now()
        if selected_date_range == "Last 7 days":
            cutoff_date = now - timedelta(days=7)
        elif selected_date_range == "Last 30 days":
            cutoff_date = now - timedelta(days=30)
        elif selected_date_range == "Last 90 days":
            cutoff_date = now - timedelta(days=90)
        
        filtered_df = filtered_df[pd.to_datetime(filtered_df['created_at']) >= cutoff_date]
    
    # Apply sorting
    if selected_sort == "Newest First":
        filtered_df = filtered_df.sort_values('created_at', ascending=False)
    elif selected_sort == "Oldest First":
        filtered_df = filtered_df.sort_values('created_at', ascending=True)
    elif selected_sort == "Alphabetical":
        filtered_df = filtered_df.sort_values('title')
    
    # Display results
    st.subheader(f"📋 Contributions ({len(filtered_df)} found)")
    
    if filtered_df.empty:
        st.info("No contributions match your filter criteria.")
    else:
        # Display mode selection
        display_mode = st.radio("Display Mode", ["Detailed Cards", "Compact List", "Data Table"], horizontal=True)
        
        if display_mode == "Detailed Cards":
            # Card layout with detailed information
            for _, contribution in filtered_df.iterrows():
                with st.container():
                    # Header row
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"### {contribution['title']}")
                        st.markdown(f"**Type:** {contribution['content_type']}")
                    
                    with col2:
                        contributor = contribution['contributor_name'] if contribution['contributor_name'] else "Anonymous"
                        st.markdown(f"**Contributor:**  \n{contributor}")
                    
                    with col3:
                        created_date = pd.to_datetime(contribution['created_at']).strftime('%Y-%m-%d %H:%M')
                        st.markdown(f"**Date:**  \n{created_date}")
                    
                    # Content row
                    if contribution['description']:
                        st.markdown(f"**Description:** {contribution['description']}")
                    
                    # Location and file information
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if contribution['location_address']:
                            st.markdown(f"📍 **Location:** {contribution['location_address']}")
                        if contribution['latitude'] and contribution['longitude']:
                            st.markdown(f"🌐 **Coordinates:** {contribution['latitude']:.4f}, {contribution['longitude']:.4f}")
                    
                    with col2:
                        if contribution['file_url']:
                            st.markdown(f"📎 **File:** [View/Download]({contribution['file_url']})")
                            
                            # Try to display file preview based on content type
                            if contribution['content_type'] in ["Photo/Image"]:
                                try:
                                    st.image(contribution['file_url'], width=200)
                                except:
                                    st.write("📷 Image file (preview not available)")
                            elif contribution['content_type'] in ["Audio Recording"]:
                                try:
                                    st.audio(contribution['file_url'])
                                except:
                                    st.write("🎵 Audio file (preview not available)")
                    
                    st.markdown("---")
        
        elif display_mode == "Compact List":
            # Compact list format
            for _, contribution in filtered_df.iterrows():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{contribution['title']}**")
                    if contribution['description']:
                        description_preview = contribution['description'][:100] + "..." if len(contribution['description']) > 100 else contribution['description']
                        st.caption(description_preview)
                
                with col2:
                    st.write(contribution['content_type'])
                
                with col3:
                    contributor = contribution['contributor_name'] if contribution['contributor_name'] else "Anonymous"
                    st.write(contributor)
                
                with col4:
                    created_date = pd.to_datetime(contribution['created_at']).strftime('%Y-%m-%d')
                    st.write(created_date)
                
                st.markdown("---")
        
        elif display_mode == "Data Table":
            # Table format
            display_columns = ['title', 'content_type', 'contributor_name', 'location_address', 'created_at']
            table_df = filtered_df[display_columns].copy()
            
            # Format the data for better display
            table_df['contributor_name'] = table_df['contributor_name'].fillna('Anonymous')
            table_df['created_at'] = pd.to_datetime(table_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            table_df.columns = ['Title', 'Content Type', 'Contributor', 'Location', 'Created Date']
            
            st.dataframe(
                table_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Detailed view for selected item
            if not table_df.empty:
                st.subheader("📄 Detailed View")
                selected_title = st.selectbox("Select contribution for details", filtered_df['title'].tolist())
                selected_contribution = filtered_df[filtered_df['title'] == selected_title].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Title:** {selected_contribution['title']}")
                    st.write(f"**Type:** {selected_contribution['content_type']}")
                    st.write(f"**Contributor:** {selected_contribution['contributor_name'] or 'Anonymous'}")
                    st.write(f"**Created:** {pd.to_datetime(selected_contribution['created_at']).strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    if selected_contribution['location_address']:
                        st.write(f"**Location:** {selected_contribution['location_address']}")
                    if selected_contribution['latitude'] and selected_contribution['longitude']:
                        st.write(f"**Coordinates:** {selected_contribution['latitude']:.6f}, {selected_contribution['longitude']:.6f}")
                    if selected_contribution['file_url']:
                        st.write(f"**File:** [View/Download]({selected_contribution['file_url']})")
                
                if selected_contribution['description']:
                    st.write("**Description:**")
                    st.write(selected_contribution['description'])

# Statistics section
if not contributions_df.empty:
    st.markdown("---")
    st.subheader("📊 Contribution Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Contributions", len(contributions_df))
    
    with col2:
        unique_contributors = contributions_df['contributor_name'].nunique()
        # Add anonymous contributions
        anonymous_count = contributions_df['contributor_name'].isna().sum()
        if anonymous_count > 0:
            unique_contributors += 1  # Count anonymous as one contributor type
        st.metric("Contributors", unique_contributors)
    
    with col3:
        content_type_counts = contributions_df['content_type'].value_counts()
        most_common_type = content_type_counts.index[0] if not content_type_counts.empty else "N/A"
        st.metric("Most Common Type", most_common_type)
    
    with col4:
        contributions_with_coords = contributions_df.dropna(subset=['latitude', 'longitude'])
        st.metric("With Location", len(contributions_with_coords))
    
    # Content type breakdown
    if not content_type_counts.empty:
        st.subheader("📈 Content Type Breakdown")
        st.bar_chart(content_type_counts)
    
    # Recent activity timeline
    st.subheader("📅 Recent Activity")
    recent_contributions = contributions_df.head(10)
    
    for _, contribution in recent_contributions.iterrows():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{contribution['title']}** ({contribution['content_type']})")
        
        with col2:
            contributor = contribution['contributor_name'] if contribution['contributor_name'] else "Anonymous"
            st.write(contributor)
        
        with col3:
            time_ago = pd.to_datetime(contribution['created_at']).strftime('%Y-%m-%d')
            st.write(time_ago)

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")
with col2:
    if st.button("📤 Upload Content", key="upload_content_nav"):
        st.switch_page("pages/1_Upload_Content.py")
with col3:
    if st.button("🗺️ Heritage Map"):
        st.switch_page("pages/5_Heritage_Map.py")
