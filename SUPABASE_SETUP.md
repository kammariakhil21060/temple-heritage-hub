# 🏛️ Temple Heritage Hub - Supabase Setup Guide

## ✅ Your Supabase Project Details

- **Project URL**: https://rrbrghxzuzzxroqbwfqi.supabase.co
- **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJyYnJnaHh6dXp6eHJvcWJ3ZnFpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4MDU0OTMsImV4cCI6MjA2OTM4MTQ5M30.Evcf0lPD7reXvgZNZrAZDoHHLDx72AUmUHMSOXgQNV4`

## 🔧 Setup Instructions

### Step 1: Get Your Database Password

1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/rrbrghxzuzzxroqbwfqi
2. Navigate to **Settings** > **Database**
3. Find your **Database Password**
4. Copy this password (you'll need it for the next step)

### Step 2: Set Environment Variables

#### Option A: Using the Setup Script (Recommended)
```bash
python setup_supabase.py
```
This script will guide you through the setup process and test the connection.

#### Option B: Manual Setup

**Windows (PowerShell):**
```powershell
$env:SUPABASE_PASSWORD="your_database_password_here"
```

**Windows (Command Prompt):**
```cmd
set SUPABASE_PASSWORD=your_database_password_here
```

**Linux/Mac:**
```bash
export SUPABASE_PASSWORD=your_database_password_here
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

## 🧪 Testing the Connection

To test if your Supabase connection is working:

```bash
python setup_supabase.py
```

This will:
- Set up your environment variables
- Test the database connection
- Verify that all components are working

## 🔍 Troubleshooting

### Connection Issues

1. **"Database password incorrect"**
   - Double-check your database password from the Supabase dashboard
   - Make sure you're using the correct password (not the anon key)

2. **"Connection timeout"**
   - Check if your Supabase project is active
   - Verify your internet connection
   - Check if your IP is not blocked by Supabase

3. **"Permission denied"**
   - Ensure you're using the correct database password
   - Check if your Supabase project has the necessary permissions

### Environment Variable Issues

1. **"SUPABASE_PASSWORD not set"**
   - Make sure you've set the environment variable correctly
   - Try using the setup script: `python setup_supabase.py`

2. **"Invalid connection string"**
   - The app automatically constructs the connection string
   - Make sure your password doesn't contain special characters that need escaping

## 📊 Database Tables

The application will automatically create these tables in your Supabase database:

- `temples` - Temple information
- `temple_media` - Media files associated with temples
- `historical_events` - Historical events related to temples
- `content_contributions` - User contributions

## 🔐 Security Notes

- Keep your database password secure
- Never commit your password to version control
- The anon key is safe to share (it's designed for client-side use)
- Consider using environment variables or a secure configuration management system

## 🚀 Next Steps

Once your connection is working:

1. **Explore the app**: Navigate through different pages using the sidebar
2. **Add content**: Upload temple information, photos, and documents
3. **Customize**: Modify the app to suit your specific needs
4. **Deploy**: Consider deploying to Streamlit Cloud or other platforms

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify your Supabase project settings
3. Ensure all dependencies are installed correctly
4. Check the Streamlit logs for detailed error messages

---

**Happy coding! 🎉** 