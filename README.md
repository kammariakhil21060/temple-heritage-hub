# Temple Heritage Hub

A collaborative, location-aware platform built with Streamlit that enables users to document, preserve, and share temple heritage through multimedia content and geolocation features.

## Features

- **Multi-page Dashboard**: Card-based navigation to all primary sections
- **Content Upload**: Photos, audio, documents, temple data, and historical events with geolocation
- **Interactive Maps**: Color-coded, filterable view of all temples and contributions
- **Search & Filter**: By name, location, architectural style, content type, and contributor
- **Rich Temple Metadata**: Name, deity, architectural style, built year, history, and more
- **Community Attribution**: Choose to contribute with your name or anonymously
- **Statistics & Analytics**: Real-time dashboards and charts of activity and content

## Technology Stack

- **Frontend**: Streamlit with multi-page architecture
- **Backend**: PostgreSQL database via Supabase
- **Maps**: Folium for interactive mapping
- **Charts**: Plotly for data visualization
- **Storage**: Supabase for file storage (configurable)

## Prerequisites

- Python 3.11+
- Supabase account and project
- Required Python packages (see pyproject.toml)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/temple-heritage-hub.git
cd temple-heritage-hub
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create a .env file with your Supabase database URL
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:6543/postgres
```

4. Run the application:
```bash
streamlit run app.py --server.port 5000
```

## Database Setup

The application automatically creates the following tables in your Supabase database:

- `temples`: Core temple information with location and metadata
- `temple_media`: Multimedia content linked to temples
- `historical_events`: Time-based events associated with temples
- `content_contributions`: General community contributions with geolocation

## Usage

1. **Home Dashboard**: View platform statistics and navigate to different sections
2. **Upload Content**: Add photos, audio, documents, temple information, or historical events
3. **Browse Temples**: Search and filter temples with various viewing modes
4. **Community Contributions**: View all user contributions with filtering options
5. **Heritage Statistics**: Analytics dashboard with charts and metrics
6. **Heritage Map**: Interactive map showing all heritage locations

## Configuration

### Streamlit Configuration
The app includes proper configuration in `.streamlit/config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

### Database Configuration
Ensure your DATABASE_URL follows the correct format for Supabase connection pooling.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## File Structure

```
temple-heritage-hub/
├── app.py                      # Main dashboard
├── database.py                 # Database operations
├── pages/                      # Streamlit pages
│   ├── 1_Upload_Content.py
│   ├── 2_Browse_Temples.py
│   ├── 3_Community_Contributions.py
│   ├── 4_Heritage_Statistics.py
│   └── 5_Heritage_Map.py
├── utils/                      # Utility modules
│   ├── supabase_client.py
│   ├── geolocation.py
│   └── file_handler.py
├── .streamlit/
│   └── config.toml
└── requirements.txt
```

## License

This project is open source and available under the MIT License.

## Support

For support and questions, please open an issue in the GitHub repository.