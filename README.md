# 🏛️ Temple Heritage Hub

A collaborative location-aware platform to document and preserve sacred temple knowledge using Streamlit and Supabase.

## 🚀 Features

- **📤 Content Upload**: Upload temple information, photos, audio recordings, documents, and historical events
- **🗂️ Browse Temples**: View and search through uploaded temple information
- **🗺️ Interactive Map**: Explore temples and heritage sites on an interactive map
- **📊 Heritage Statistics**: View analytics and statistics about contributions
- **👥 Community Contributions**: See contributions from the community

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Supabase (PostgreSQL + Storage)
- **Database**: PostgreSQL with custom schemas
- **File Storage**: Supabase Storage
- **Maps**: Folium/Streamlit-Folium

## 📋 Prerequisites

- Python 3.8+
- Supabase account and project
- Required Python packages (see requirements.txt)

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd temple-heritage-hub
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Supabase Setup**
   - Create a Supabase project at [supabase.com](https://supabase.com)
   - Set up the following tables in your Supabase database:
     - `temples`
     - `content_contributions`
     - `historical_events`
     - `media_uploads`
     - `users`

4. **Environment Configuration**
   The application is configured to use your Supabase credentials directly in the code:
   - Supabase URL: `https://rrbrghxzuzzxroqbwfqi.supabase.co`
   - Database URL: `postgresql://postgres:Akhil%40112233@db.rrbrghxzuzzxroqbwfqi.supabase.co:5432/postgres`
   - Anon Key: Configured in the code

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📊 Database Schema

### Temples Table
```sql
CREATE TABLE public.temples (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text,
  location text,
  image_url text,
  audio_url text,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT temples_pkey PRIMARY KEY (id)
);
```

### Content Contributions Table
```sql
CREATE TABLE public.content_contributions (
  id serial NOT NULL,
  title character varying(255) NOT NULL,
  content_type character varying(50),
  description text,
  file_url text,
  latitude numeric(10, 8),
  longitude numeric(11, 8),
  location_address text,
  contributor_name character varying(255),
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT content_contributions_pkey PRIMARY KEY (id)
);
```

### Historical Events Table
```sql
CREATE TABLE public.historical_events (
  id serial NOT NULL,
  temple_id integer,
  event_date date,
  event_title character varying(255),
  event_description text,
  latitude numeric(10, 8),
  longitude numeric(11, 8),
  contributor_name character varying(255),
  created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT historical_events_pkey PRIMARY KEY (id)
);
```

### Media Uploads Table
```sql
CREATE TABLE public.media_uploads (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  temple_id uuid,
  uploaded_by uuid,
  file_type text,
  file_url text NOT NULL,
  uploaded_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT media_uploads_pkey PRIMARY KEY (id),
  CONSTRAINT media_uploads_temple_id_fkey FOREIGN KEY (temple_id) REFERENCES temples (id) ON DELETE CASCADE,
  CONSTRAINT media_uploads_file_type_check CHECK (file_type = ANY (ARRAY['image'::text, 'audio'::text, 'document'::text]))
);
```

## 🎯 Usage

1. **Upload Content**: Use the "Upload Content" page to add temple information, photos, audio, or historical events
2. **Browse Temples**: View all uploaded temples and their details
3. **View Map**: Explore temples on an interactive map
4. **Community Contributions**: See what others have contributed
5. **Statistics**: View analytics about the heritage data

## 🔧 Configuration

The application is pre-configured with your Supabase credentials. If you need to change them:

1. Update the environment variables in `app.py` and `pages/1_Upload_Content.py`
2. Update the database connection string with your credentials
3. Ensure your Supabase project has the required tables and storage buckets

## 📁 Project Structure

```
temple-heritage-hub/
├── app.py                          # Main Streamlit application
├── database.py                     # Database operations
├── requirements.txt                # Python dependencies
├── pages/                          # Streamlit pages
│   ├── 1_Upload_Content.py        # Content upload page
│   ├── 2_Browse_Temples.py        # Temple browsing page
│   ├── 3_Community_Contributions.py # Community page
│   ├── 4_Heritage_Statistics.py   # Statistics page
│   └── 5_Heritage_Map.py          # Interactive map page
└── utils/                          # Utility modules
    ├── supabase_client.py         # Supabase connection
    ├── file_handler.py            # File upload utilities
    └── geolocation.py             # Location utilities
```

## 🧪 Testing

Run the connection test to verify your Supabase setup:
```bash
python test_connection.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Streamlit for the web interface
- Powered by Supabase for backend services
- Community contributions for temple heritage preservation

---

**Note**: This application is configured to work with your specific Supabase project. Make sure to update the credentials if you're using a different Supabase project.