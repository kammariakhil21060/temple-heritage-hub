import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import get_all_temples, get_all_contributions
from sqlalchemy import create_engine, text
import os

st.set_page_config(page_title="Heritage Statistics", page_icon="📈", layout="wide")

st.title("📈 Heritage Statistics")
st.markdown("Analytics and insights about temple heritage documentation activity")

# Load data
temples_df = get_all_temples()
contributions_df = get_all_contributions()

# Summary metrics
st.subheader("📊 Platform Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Temples",
        value=len(temples_df),
        delta=None
    )

with col2:
    st.metric(
        label="Total Contributions", 
        value=len(contributions_df),
        delta=None
    )

with col3:
    if not contributions_df.empty:
        unique_contributors = contributions_df['contributor_name'].nunique()
        anonymous_count = contributions_df['contributor_name'].isna().sum()
        if anonymous_count > 0:
            unique_contributors += 1
        st.metric(
            label="Active Contributors",
            value=unique_contributors,
            delta=None
        )
    else:
        st.metric(label="Active Contributors", value=0)

with col4:
    total_with_location = 0
    if not temples_df.empty:
        total_with_location += len(temples_df.dropna(subset=['latitude', 'longitude']))
    if not contributions_df.empty:
        total_with_location += len(contributions_df.dropna(subset=['latitude', 'longitude']))
    
    st.metric(
        label="Items with Location",
        value=total_with_location,
        delta=None
    )

# Content analysis
st.markdown("---")
st.subheader("📋 Content Analysis")

if not contributions_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        # Content type distribution
        st.markdown("#### Content Type Distribution")
        content_type_counts = contributions_df['content_type'].value_counts()
        
        fig_pie = px.pie(
            values=content_type_counts.values,
            names=content_type_counts.index,
            title="Distribution of Content Types"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Contributor analysis
        st.markdown("#### Contributor Activity")
        contributor_counts = contributions_df['contributor_name'].fillna('Anonymous').value_counts().head(10)
        
        fig_bar = px.bar(
            x=contributor_counts.values,
            y=contributor_counts.index,
            orientation='h',
            title="Top 10 Contributors",
            labels={'x': 'Number of Contributions', 'y': 'Contributor'}
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No contribution data available for analysis yet.")

# Temple analysis
st.markdown("---")
st.subheader("🏛️ Temple Analysis")

if not temples_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        # Architectural styles
        st.markdown("#### Architectural Styles")
        style_counts = temples_df['architectural_style'].value_counts()
        
        fig_arch = px.bar(
            x=style_counts.index,
            y=style_counts.values,
            title="Temples by Architectural Style",
            labels={'x': 'Architectural Style', 'y': 'Number of Temples'}
        )
        fig_arch.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_arch, use_container_width=True)
    
    with col2:
        # Built year distribution
        st.markdown("#### Historical Distribution")
        temples_with_year = temples_df.dropna(subset=['built_year'])
        
        if not temples_with_year.empty:
            # Create century bins
            temples_with_year = temples_with_year.copy()
            temples_with_year['century'] = ((temples_with_year['built_year'] - 1) // 100 + 1).astype(int)
            century_counts = temples_with_year['century'].value_counts().sort_index()
            
            fig_hist = px.bar(
                x=[f"{c}th Century" for c in century_counts.index],
                y=century_counts.values,
                title="Temples by Century Built",
                labels={'x': 'Century', 'y': 'Number of Temples'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No temple age data available for historical analysis.")
else:
    st.info("No temple data available for analysis yet.")

# Time-based analysis
st.markdown("---")
st.subheader("📅 Activity Timeline")

if not contributions_df.empty:
    # Prepare time-based data
    contributions_df['created_at'] = pd.to_datetime(contributions_df['created_at'])
    contributions_df['date'] = contributions_df['created_at'].dt.date
    
    # Daily activity
    daily_counts = contributions_df.groupby('date').size().reset_index(name='count')
    
    fig_timeline = px.line(
        daily_counts,
        x='date',
        y='count',
        title="Daily Contribution Activity",
        labels={'date': 'Date', 'count': 'Number of Contributions'}
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Monthly summary
    contributions_df['month_year'] = contributions_df['created_at'].dt.to_period('M')
    monthly_counts = contributions_df.groupby('month_year').size()
    
    if len(monthly_counts) > 1:
        st.markdown("#### Monthly Activity Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_month = monthly_counts.iloc[-1] if len(monthly_counts) > 0 else 0
            st.metric("This Month", current_month)
        
        with col2:
            last_month = monthly_counts.iloc[-2] if len(monthly_counts) > 1 else 0
            change = current_month - last_month if len(monthly_counts) > 1 else 0
            st.metric("Last Month", last_month, delta=change)
        
        with col3:
            avg_monthly = monthly_counts.mean()
            st.metric("Monthly Average", f"{avg_monthly:.1f}")
else:
    st.info("No activity data available for timeline analysis yet.")

# Geographic analysis
st.markdown("---")
st.subheader("🌍 Geographic Distribution")

# Combine location data from temples and contributions
location_data = []

if not temples_df.empty:
    temples_with_coords = temples_df.dropna(subset=['latitude', 'longitude'])
    for _, temple in temples_with_coords.iterrows():
        location_data.append({
            'latitude': temple['latitude'],
            'longitude': temple['longitude'],
            'type': 'Temple',
            'name': temple['name']
        })

if not contributions_df.empty:
    contributions_with_coords = contributions_df.dropna(subset=['latitude', 'longitude'])
    for _, contrib in contributions_with_coords.iterrows():
        location_data.append({
            'latitude': contrib['latitude'],
            'longitude': contrib['longitude'],
            'type': 'Contribution',
            'name': contrib['title']
        })

if location_data:
    location_df = pd.DataFrame(location_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Items with Coordinates", len(location_df))
        
        # Type distribution
        type_counts = location_df['type'].value_counts()
        fig_geo_types = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="Geographic Data by Type"
        )
        st.plotly_chart(fig_geo_types, use_container_width=True)
    
    with col2:
        # Geographic spread
        lat_range = location_df['latitude'].max() - location_df['latitude'].min()
        lon_range = location_df['longitude'].max() - location_df['longitude'].min()
        
        st.metric("Latitude Spread", f"{lat_range:.4f}°")
        st.metric("Longitude Spread", f"{lon_range:.4f}°")
        
        # Center point
        center_lat = location_df['latitude'].mean()
        center_lon = location_df['longitude'].mean()
        st.write(f"**Geographic Center:**")
        st.write(f"Lat: {center_lat:.4f}°, Lon: {center_lon:.4f}°")
else:
    st.info("No geographic data available for analysis yet.")

# Advanced statistics
st.markdown("---")
st.subheader("🔍 Advanced Analytics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Data Quality Metrics")
    
    # Calculate completeness scores
    temple_completeness = {}
    if not temples_df.empty:
        temple_completeness['Name'] = (temples_df['name'].notna().sum() / len(temples_df)) * 100
        temple_completeness['Location'] = (temples_df['location_address'].notna().sum() / len(temples_df)) * 100
        temple_completeness['Coordinates'] = (temples_df[['latitude', 'longitude']].notna().all(axis=1).sum() / len(temples_df)) * 100
        temple_completeness['Deity'] = (temples_df['deity'].notna().sum() / len(temples_df)) * 100
        temple_completeness['History'] = (temples_df['history'].notna().sum() / len(temples_df)) * 100
    
    if temple_completeness:
        completeness_df = pd.DataFrame(list(temple_completeness.items()), columns=['Field', 'Completeness %'])
        fig_completeness = px.bar(
            completeness_df,
            x='Completeness %',
            y='Field',
            orientation='h',
            title="Temple Data Completeness",
            range_x=[0, 100]
        )
        st.plotly_chart(fig_completeness, use_container_width=True)
    else:
        st.info("No temple data available for quality analysis.")

with col2:
    st.markdown("#### Platform Growth")
    
    if not contributions_df.empty:
        # Cumulative growth
        contributions_df_sorted = contributions_df.sort_values('created_at')
        contributions_df_sorted['cumulative'] = range(1, len(contributions_df_sorted) + 1)
        
        fig_growth = px.line(
            contributions_df_sorted,
            x='created_at',
            y='cumulative',
            title="Cumulative Contributions Over Time",
            labels={'created_at': 'Date', 'cumulative': 'Total Contributions'}
        )
        st.plotly_chart(fig_growth, use_container_width=True)
        
        # Growth rate
        if len(contributions_df) > 1:
            days_active = (contributions_df['created_at'].max() - contributions_df['created_at'].min()).days
            if days_active > 0:
                daily_rate = len(contributions_df) / days_active
                st.metric("Daily Growth Rate", f"{daily_rate:.2f} contributions/day")
            else:
                st.metric("Daily Growth Rate", "N/A (single day)")
    else:
        st.info("No contribution data available for growth analysis.")

# Export data option
st.markdown("---")
st.subheader("📥 Data Export")

col1, col2, col3 = st.columns(3)

with col1:
    if not temples_df.empty:
        csv_temples = temples_df.to_csv(index=False)
        st.download_button(
            label="Download Temple Data (CSV)",
            data=csv_temples,
            file_name=f"temple_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if not contributions_df.empty:
        csv_contributions = contributions_df.to_csv(index=False)
        st.download_button(
            label="Download Contributions (CSV)",
            data=csv_contributions,
            file_name=f"contributions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col3:
    if location_data:
        csv_locations = pd.DataFrame(location_data).to_csv(index=False)
        st.download_button(
            label="Download Location Data (CSV)",
            data=csv_locations,
            file_name=f"locations_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")
with col2:
    if st.button("🗂️ Browse Temples"):
        st.switch_page("pages/2_Browse_Temples.py")
with col3:
    if st.button("🗺️ Heritage Map"):
        st.switch_page("pages/5_Heritage_Map.py")
