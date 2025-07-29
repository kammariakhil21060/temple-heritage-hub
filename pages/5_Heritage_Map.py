import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from database import get_all_temples, get_all_contributions
from folium.plugins import MarkerCluster, HeatMap
import branca.colormap as cm

st.set_page_config(page_title="Heritage Map", page_icon="🗺️", layout="wide")

st.title("🗺️ Heritage Map")
st.markdown("Interactive map displaying all temples and heritage contributions with location data")

# Load data
temples_df = get_all_temples()
contributions_df = get_all_contributions()

# Filter data with coordinates
temples_with_coords = temples_df.dropna(subset=['latitude', 'longitude']) if not temples_df.empty else pd.DataFrame()
contributions_with_coords = contributions_df.dropna(subset=['latitude', 'longitude']) if not contributions_df.empty else pd.DataFrame()

# Map controls
st.subheader("🎛️ Map Controls")
col1, col2, col3, col4 = st.columns(4)

with col1:
    map_style = st.selectbox(
        "Map Style",
        ["OpenStreetMap", "CartoDB Positron", "CartoDB Dark_Matter", "Stamen Terrain"]
    )

with col2:
    show_temples = st.checkbox("Show Temples", value=True)

with col3:
    show_contributions = st.checkbox("Show Contributions", value=True)

with col4:
    cluster_markers = st.checkbox("Cluster Markers", value=True)

# Advanced filters
with st.expander("🔍 Advanced Filters"):
    col1, col2 = st.columns(2)
    
    with col1:
        if not temples_with_coords.empty:
            architectural_styles = ["All Styles"] + list(temples_with_coords['architectural_style'].dropna().unique())
            selected_style = st.selectbox("Filter Temples by Style", architectural_styles)
        else:
            selected_style = "All Styles"
    
    with col2:
        if not contributions_with_coords.empty:
            content_types = ["All Types"] + list(contributions_with_coords['content_type'].unique())
            selected_content_type = st.selectbox("Filter Contributions by Type", content_types)
        else:
            selected_content_type = "All Types"

# Apply filters
filtered_temples = temples_with_coords.copy() if not temples_with_coords.empty else pd.DataFrame()
filtered_contributions = contributions_with_coords.copy() if not contributions_with_coords.empty else pd.DataFrame()

if not filtered_temples.empty and selected_style != "All Styles":
    filtered_temples = filtered_temples[filtered_temples['architectural_style'] == selected_style]

if not filtered_contributions.empty and selected_content_type != "All Types":
    filtered_contributions = filtered_contributions[filtered_contributions['content_type'] == selected_content_type]

# Check if we have any data to display
total_items = len(filtered_temples) + len(filtered_contributions)

if total_items == 0:
    st.warning("No items with location data found. Upload content with location information to see them on the map.")
    
    # Show upload button
    if st.button("📤 Upload Content with Location"):
        st.switch_page("pages/1_Upload_Content.py")
else:
    # Calculate map center
    all_lats = []
    all_lons = []
    
    if show_temples and not filtered_temples.empty:
        all_lats.extend(filtered_temples['latitude'].tolist())
        all_lons.extend(filtered_temples['longitude'].tolist())
    
    if show_contributions and not filtered_contributions.empty:
        all_lats.extend(filtered_contributions['latitude'].tolist())
        all_lons.extend(filtered_contributions['longitude'].tolist())
    
    if all_lats and all_lons:
        center_lat = sum(all_lats) / len(all_lats)
        center_lon = sum(all_lons) / len(all_lons)
        
        # Determine appropriate zoom level based on data spread
        lat_range = max(all_lats) - min(all_lats)
        lon_range = max(all_lons) - min(all_lons)
        max_range = max(lat_range, lon_range)
        
        if max_range < 0.01:
            zoom_start = 15
        elif max_range < 0.1:
            zoom_start = 12
        elif max_range < 1:
            zoom_start = 10
        elif max_range < 5:
            zoom_start = 8
        else:
            zoom_start = 6
    else:
        # Default to India center if no data
        center_lat, center_lon = 20.5937, 78.9629
        zoom_start = 5
    
    # Create base map
    tile_map = {
        "OpenStreetMap": "OpenStreetMap",
        "CartoDB Positron": "CartoDB positron",
        "CartoDB Dark_Matter": "CartoDB dark_matter",
        "Stamen Terrain": "Stamen Terrain"
    }
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles=tile_map[map_style]
    )
    
    # Add marker cluster if enabled
    if cluster_markers:
        marker_cluster = MarkerCluster().add_to(m)
        marker_container = marker_cluster
    else:
        marker_container = m
    
    # Add temple markers
    if show_temples and not filtered_temples.empty:
        for _, temple in filtered_temples.iterrows():
            popup_content = f"""
            <div style="width: 250px;">
                <h4>🏛️ {temple['name']}</h4>
                <p><strong>Deity:</strong> {temple['deity'] or 'Not specified'}</p>
                <p><strong>Style:</strong> {temple['architectural_style'] or 'Not specified'}</p>
                <p><strong>Built:</strong> {temple['built_year'] or 'Unknown'}</p>
                <p><strong>Location:</strong> {temple['location_address'] or 'Not specified'}</p>
                <p><strong>Contributor:</strong> {temple['contributor_name'] or 'Anonymous'}</p>
                {'<p><strong>History:</strong> ' + temple['history'][:100] + '...</p>' if temple['history'] else ''}
            </div>
            """
            
            folium.Marker(
                location=[temple['latitude'], temple['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"🏛️ {temple['name']}",
                icon=folium.Icon(color='red', icon='home', prefix='fa')
            ).add_to(marker_container)
    
    # Add contribution markers
    if show_contributions and not filtered_contributions.empty:
        # Color code by content type
        content_type_colors = {
            'Photo/Image': 'blue',
            'Audio Recording': 'green',
            'Document': 'orange',
            'Historical Event': 'purple',
            'Temple Information': 'red'
        }
        
        for _, contribution in filtered_contributions.iterrows():
            color = content_type_colors.get(contribution['content_type'], 'gray')
            
            popup_content = f"""
            <div style="width: 250px;">
                <h4>📄 {contribution['title']}</h4>
                <p><strong>Type:</strong> {contribution['content_type']}</p>
                <p><strong>Description:</strong> {(contribution['description'] or '')[:100]}{'...' if len(contribution['description'] or '') > 100 else ''}</p>
                <p><strong>Location:</strong> {contribution['location_address'] or 'Not specified'}</p>
                <p><strong>Contributor:</strong> {contribution['contributor_name'] or 'Anonymous'}</p>
                <p><strong>Added:</strong> {pd.to_datetime(contribution['created_at']).strftime('%Y-%m-%d')}</p>
                {'<p><a href="' + contribution['file_url'] + '" target="_blank">📎 View File</a></p>' if contribution['file_url'] else ''}
            </div>
            """
            
            # Choose icon based on content type
            icon_map = {
                'Photo/Image': 'camera',
                'Audio Recording': 'music',
                'Document': 'file-text',
                'Historical Event': 'calendar',
                'Temple Information': 'info-circle'
            }
            
            icon = icon_map.get(contribution['content_type'], 'circle')
            
            folium.Marker(
                location=[contribution['latitude'], contribution['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"📄 {contribution['title']}",
                icon=folium.Icon(color=color, icon=icon, prefix='fa')
            ).add_to(marker_container)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px;">
    <h4>Legend</h4>
    '''
    
    if show_temples:
        legend_html += '<p><i class="fa fa-home" style="color:red"></i> Temples</p>'
    
    if show_contributions:
        legend_html += '<p><i class="fa fa-camera" style="color:blue"></i> Photos</p>'
        legend_html += '<p><i class="fa fa-music" style="color:green"></i> Audio</p>'
        legend_html += '<p><i class="fa fa-file-text" style="color:orange"></i> Documents</p>'
        legend_html += '<p><i class="fa fa-calendar" style="color:purple"></i> Events</p>'
    
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Display map
    st.subheader(f"🌍 Heritage Map ({total_items} items)")
    map_data = st_folium(m, width=700, height=500, returned_objects=["last_object_clicked"])
    
    # Display clicked item details
    if map_data["last_object_clicked"]:
        clicked_lat = map_data["last_object_clicked"]["lat"]
        clicked_lng = map_data["last_object_clicked"]["lng"]
        
        # Find the closest item to the clicked location
        min_distance = float('inf')
        closest_item = None
        item_type = None
        
        # Check temples
        if show_temples and not filtered_temples.empty:
            for _, temple in filtered_temples.iterrows():
                distance = ((temple['latitude'] - clicked_lat) ** 2 + (temple['longitude'] - clicked_lng) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_item = temple
                    item_type = "temple"
        
        # Check contributions
        if show_contributions and not filtered_contributions.empty:
            for _, contribution in filtered_contributions.iterrows():
                distance = ((contribution['latitude'] - clicked_lat) ** 2 + (contribution['longitude'] - clicked_lng) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_item = contribution
                    item_type = "contribution"
        
        # Display details of closest item
        if closest_item is not None and min_distance < 0.001:  # Very close to a marker
            st.subheader("📍 Selected Item Details")
            
            if item_type == "temple":
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {closest_item['name']}")
                    st.write(f"**Deity:** {closest_item['deity'] or 'Not specified'}")
                    st.write(f"**Style:** {closest_item['architectural_style'] or 'Not specified'}")
                    st.write(f"**Built Year:** {closest_item['built_year'] or 'Unknown'}")
                
                with col2:
                    st.write(f"**Location:** {closest_item['location_address'] or 'Not specified'}")
                    st.write(f"**Coordinates:** {closest_item['latitude']:.6f}, {closest_item['longitude']:.6f}")
                    st.write(f"**Contributor:** {closest_item['contributor_name'] or 'Anonymous'}")
                    st.write(f"**Added:** {pd.to_datetime(closest_item['created_at']).strftime('%Y-%m-%d')}")
                
                if closest_item['history']:
                    st.write("**History:**")
                    st.write(closest_item['history'])
            
            elif item_type == "contribution":
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Title:** {closest_item['title']}")
                    st.write(f"**Type:** {closest_item['content_type']}")
                    st.write(f"**Contributor:** {closest_item['contributor_name'] or 'Anonymous'}")
                    st.write(f"**Added:** {pd.to_datetime(closest_item['created_at']).strftime('%Y-%m-%d')}")
                
                with col2:
                    st.write(f"**Location:** {closest_item['location_address'] or 'Not specified'}")
                    st.write(f"**Coordinates:** {closest_item['latitude']:.6f}, {closest_item['longitude']:.6f}")
                    if closest_item['file_url']:
                        st.markdown(f"**File:** [View/Download]({closest_item['file_url']})")
                
                if closest_item['description']:
                    st.write("**Description:**")
                    st.write(closest_item['description'])

# Map statistics
if total_items > 0:
    st.markdown("---")
    st.subheader("📊 Map Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        temples_shown = len(filtered_temples) if show_temples else 0
        st.metric("Temples on Map", temples_shown)
    
    with col2:
        contributions_shown = len(filtered_contributions) if show_contributions else 0
        st.metric("Contributions on Map", contributions_shown)
    
    with col3:
        if all_lats and all_lons:
            coverage_area = (max(all_lats) - min(all_lats)) * (max(all_lons) - min(all_lons))
            st.metric("Coverage Area", f"{coverage_area:.4f}°²")
        else:
            st.metric("Coverage Area", "0°²")
    
    with col4:
        if all_lats and all_lons:
            avg_density = total_items / max(coverage_area, 0.0001)
            st.metric("Item Density", f"{avg_density:.1f}/°²")
        else:
            st.metric("Item Density", "0/°²")

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")
with col2:
    if st.button("📤 Upload Content"):
        st.switch_page("pages/1_Upload_Content.py")
with col3:
    if st.button("🗂️ Browse Temples"):
        st.switch_page("pages/2_Browse_Temples.py")
