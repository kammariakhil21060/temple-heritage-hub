# Temple Heritage Hub

## Overview

Temple Heritage Hub is a collaborative, location-aware platform built with Streamlit that enables users to document, preserve, and share temple heritage through multimedia content and geolocation features. The application serves as a digital repository for temple information, community contributions, and historical documentation.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application with multi-page architecture
- **UI Components**: Card-based navigation system with custom CSS styling
- **Interactive Elements**: Forms, file uploads, maps, charts, and data tables
- **Visualization**: Plotly for charts and Folium for interactive maps
- **Layout**: Wide layout with responsive column-based design

### Backend Architecture
- **Database Layer**: PostgreSQL database accessed through SQLAlchemy ORM
- **Cloud Storage**: Supabase for database hosting and file storage
- **Data Access**: Direct SQL queries with SQLAlchemy engine connections
- **File Management**: Supabase storage integration for multimedia files

### Data Storage Solutions
- **Primary Database**: PostgreSQL hosted on Supabase
- **File Storage**: Supabase storage buckets for images, audio, and documents
- **Schema Design**: Relational database with tables for temples, media, events, and contributions
- **Connection Management**: SQLAlchemy engine with connection pooling

## Key Components

### Core Application Files
- **app.py**: Main dashboard with navigation cards and metrics display
- **database.py**: Database initialization, connection management, and data access functions
- **Pages Directory**: Multi-page Streamlit application structure
  - Upload Content: Multimedia file uploads with geolocation
  - Browse Temples: Search, filter, and view temple information
  - Community Contributions: Display and filter user contributions
  - Heritage Statistics: Analytics dashboard with charts and metrics
  - Heritage Map: Interactive map with clustered markers

### Utility Modules
- **supabase_client.py**: Database connection management and error handling
- **geolocation.py**: Location services including IP-based and address geocoding
- **file_handler.py**: File validation, type detection, and upload management

### Database Schema
- **temples**: Core temple information with location and metadata
- **temple_media**: Multimedia content linked to temples
- **historical_events**: Time-based events associated with temples
- **content_contributions**: General community contributions with geolocation

## Data Flow

### Content Upload Process
1. User selects content type (photo/audio/document/temple/event)
2. Location is determined through GPS, manual entry, or IP detection
3. Files are validated for type and size constraints
4. Content is uploaded to Supabase storage
5. Metadata is stored in PostgreSQL database
6. Confirmation and success feedback provided

### Data Retrieval Process
1. Database queries through SQLAlchemy engine
2. Data filtering and sorting based on user preferences
3. Geospatial data processing for map visualizations
4. Real-time statistics calculation and display

## External Dependencies

### Cloud Services
- **Supabase**: Primary database and file storage provider
- **OpenStreetMap Nominatim**: Address geocoding service
- **IP-API**: IP-based location detection service

### Python Libraries
- **Streamlit**: Web application framework
- **SQLAlchemy**: Database ORM and connection management
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charting and visualization
- **Folium**: Interactive map generation
- **Requests**: HTTP client for external API calls

### Frontend Libraries
- **Streamlit-Folium**: Folium integration for Streamlit
- **Custom CSS**: Styling for cards and UI components

## Deployment Strategy

### Environment Configuration
- **DATABASE_URL**: Supabase PostgreSQL connection string
- **Environment Variables**: Managed through platform-specific configuration
- **Connection Pooling**: SQLAlchemy engine with transaction pooler

### Database Initialization
- **Automatic Setup**: Database tables created on first run
- **Schema Migration**: Tables created with CREATE IF NOT EXISTS statements
- **Connection Testing**: Built-in connection validation and error reporting

### File Storage Strategy
- **Supabase Storage**: Centralized file management with URL-based access
- **File Validation**: Size limits (50MB) and type checking
- **Unique Naming**: UUID-based file naming to prevent conflicts

### Error Handling
- **Database Connections**: Graceful degradation with user-friendly error messages
- **File Uploads**: Comprehensive validation with detailed error feedback
- **External APIs**: Timeout handling and fallback mechanisms