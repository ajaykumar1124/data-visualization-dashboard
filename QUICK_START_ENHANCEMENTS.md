# Dashboard Enhancements - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Import the Module
```python
from dashboard_enhancements import DashboardEnhancementsManager
```

### Step 2: Initialize
```python
enhancements = DashboardEnhancementsManager(theme_config='light')
enhancements.initialize_all()
```

### Step 3: Use Features
```python
# Render settings panel
enhancements.render_settings_panel()

# Apply a theme
enhancements.theme.apply_theme('dark')

# Render filters
filtered_df = enhancements.filters.render_filter_ui(your_dataframe)

# Setup notifications
enhancements.notifications.configure_slack('https://hooks.slack.com/...')

# Render refresh controls
enhancements.refresh.render_refresh_controls()
```

## 📚 Feature Cheat Sheet

### Mobile Optimization
```python
# Applied automatically with initialize_all()
enhancements.mobile.render_mobile_css()
```

### Themes
```python
# List themes
themes = enhancements.theme.get_available_themes()
# ['light', 'dark', 'professional']

# Apply theme
enhancements.theme.apply_theme('dark')

# Create custom theme
from dashboard_enhancements import ThemeConfig, ThemeType
custom = ThemeConfig(
    name='Ocean',
    theme_type=ThemeType.CUSTOM,
    primary_color='#0066cc',
    secondary_color='#00ccff',
    background_color='#001a33',
    text_color='#e6f2ff',
    accent_color='#00ff99'
)
enhancements.theme.add_theme(custom)
enhancements.theme.apply_theme('ocean')
```

### Notifications
```python
# Configure Slack
enhancements.notifications.configure_slack(
    'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    channel='#alerts'
)

# Send notification
enhancements.notifications.send_notification(
    title='📊 Report Ready',
    message='Your report is ready',
    message_type='success',
    fields={'Status': 'Complete'}
)

# Or Teams
enhancements.notifications.configure_teams(
    'https://outlook.webhook.office.com/...'
)
```

### Real-Time Refresh
```python
# Set interval
enhancements.refresh.set_refresh_interval(300)  # 5 minutes

# Register callback
def refresh_data():
    print("Refreshing...")

enhancements.refresh.register_refresh_callback(refresh_data)

# Show controls
enhancements.refresh.render_refresh_controls()

# Manual refresh
enhancements.refresh.refresh()
```

### Advanced Filtering
```python
import pandas as pd

df = pd.read_csv('data.csv')

# Simple filter
enhancements.filters.add_column_filter('Department', 'eq', 'Sales')
df_filtered = enhancements.filters.apply_filters(df)

# Text search
results = enhancements.filters.search_text(df, 'sales')

# Regex filter
regex_results = enhancements.filters.apply_regex_filter(
    df, 'Email', r'^[a-z]+@example\.com$'
)

# Date range
from datetime import datetime
enhancements.filters.add_date_range_filter(
    'Date',
    datetime(2024, 1, 1),
    datetime(2024, 12, 31)
)

# Render UI
df = enhancements.filters.render_filter_ui(df)
```

## 🎯 Common Tasks

### Task: Create Custom Theme
```python
from dashboard_enhancements import ThemeConfig, ThemeType

theme = ThemeConfig(
    name='Company Brand',
    theme_type=ThemeType.CUSTOM,
    primary_color='#003d7a',
    secondary_color='#ff9900',
    background_color='#f8f9fa',
    text_color='#333333',
    accent_color='#00cc44'
)

enhancements.theme.add_theme(theme)
enhancements.theme.apply_theme('company brand')
```

### Task: Setup Slack Alerts
```python
# Configure
enhancements.notifications.configure_slack(
    'https://hooks.slack.com/services/T00/B00/XXXXX',
    channel='#dashboard-alerts'
)

# Send on data loaded
enhancements.notifications.send_dashboard_update(
    'data_loaded',
    {'message': 'Dataset loaded', 'rows': 15000}
)
```

### Task: Filter Data by Department
```python
# Add filter
enhancements.filters.add_column_filter(
    'Department',
    'eq',
    'Sales'
)

# Apply and get filtered data
filtered_df = enhancements.filters.apply_filters(df)
```

### Task: Auto-Refresh Every 5 Minutes
```python
# Configure
enhancements.refresh.config.enabled = True
enhancements.refresh.set_refresh_interval(300)

# Register what to refresh
def load_latest_data():
    # Your data loading logic
    pass

enhancements.refresh.register_refresh_callback(load_latest_data)

# Render controls
enhancements.refresh.render_refresh_controls()
```

## 🔧 Configuration Reference

### MobileConfig
```python
MobileConfig(
    enabled=True,
    touch_target_size=48,  # pixels
    enable_swipe_navigation=True,
    enable_responsive_text=True
)
```

### ThemeConfig
```python
ThemeConfig(
    name='Theme Name',
    theme_type=ThemeType.CUSTOM,
    primary_color='#1f77b4',
    secondary_color='#ff7f0e',
    background_color='#ffffff',
    text_color='#000000',
    accent_color='#2ca02c',
    font_family='Arial, sans-serif'
)
```

### NotificationConfig
```python
NotificationConfig(
    channel=NotificationChannel.SLACK,
    webhook_url='https://...',
    channel_name='#alerts',
    enabled=True,
    retry_attempts=3
)
```

### RefreshConfig
```python
RefreshConfig(
    enabled=True,
    interval_seconds=300,
    min_interval_seconds=30,
    max_interval_seconds=3600
)
```

### FilterConfig
```python
FilterConfig(
    enable_regex_search=True,
    enable_date_range_filter=True,
    case_sensitive=False,
    partial_match=True
)
```

## 📊 Status & Monitoring

```python
# Get comprehensive status
status = enhancements.get_status_report()

# Check individual components
mobile_status = enhancements.mobile.config.enabled
theme_status = enhancements.theme.current_theme.name
notif_status = enhancements.notifications.get_status()
refresh_stats = enhancements.refresh.get_refresh_statistics()
filter_summary = enhancements.filters.get_filter_summary()
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Mobile CSS not applied | Call `render_mobile_css()` before content |
| Theme colors not showing | Use `unsafe_allow_html=True` in `st.markdown()` |
| Notifications not sending | Check webhook URL format (must be https://) |
| Refresh not working | Ensure `enabled=True` and interval is set |
| Filters not applying | Check column names match exactly |

## 📖 Documentation

- **Full Guide**: `DASHBOARD_ENHANCEMENTS_README.md`
- **Examples**: `dashboard_enhancements_example.py`
- **Summary**: `ENHANCEMENTS_SUMMARY.md`

## 🎮 Try the Demo

```bash
streamlit run dashboard_enhancements_example.py
```

## ⚡ Common Patterns

### Pattern 1: Full-Featured Dashboard
```python
import streamlit as st
from dashboard_enhancements import DashboardEnhancementsManager
import pandas as pd

# Initialize
enhancements = DashboardEnhancementsManager(theme_config='light')
enhancements.initialize_all()

# Sidebar
with st.sidebar:
    enhancements.render_settings_panel()
    enhancements.refresh.render_refresh_controls()

# Main content
st.title("Enhanced Dashboard")

# Load and filter data
df = pd.read_csv('data.csv')
df = enhancements.filters.render_filter_ui(df)

# Display
st.dataframe(df)
```

### Pattern 2: Notify on Updates
```python
# Setup notification
enhancements.notifications.configure_slack('webhook_url')

try:
    # Your processing
    process_data()
    
    # Success notification
    enhancements.notifications.send_notification(
        'Processing Complete',
        'Data processed successfully',
        message_type='success'
    )
except Exception as e:
    # Error notification
    enhancements.notifications.send_notification(
        'Processing Error',
        str(e),
        message_type='error'
    )
```

### Pattern 3: Auto-Refresh with Callback
```python
def refresh_callback():
    with st.spinner('Refreshing data...'):
        # Load fresh data
        global df
        df = pd.read_csv('data.csv')
        st.success('Data refreshed!')

enhancements.refresh.register_refresh_callback(refresh_callback)
enhancements.refresh.render_refresh_controls()

if enhancements.refresh.should_refresh():
    enhancements.refresh.refresh()
```

## 💡 Tips & Tricks

1. **Store Theme in Session State**: Themes persist across reruns
2. **Combine Filters**: Stack multiple filters for complex queries
3. **Use Callbacks**: More efficient than polling for refresh
4. **Test Webhooks**: Always test notification URLs
5. **Mobile First**: Design for mobile, enhance for desktop
6. **Cache Data**: Use Streamlit cache for performance
7. **Monitor Logs**: Enable debug logging for troubleshooting

## 🚀 Next Steps

1. ✅ Read the full documentation: `DASHBOARD_ENHANCEMENTS_README.md`
2. ✅ Run the example: `streamlit run dashboard_enhancements_example.py`
3. ✅ Integrate into your dashboard
4. ✅ Customize themes and features
5. ✅ Deploy to production

---

**Questions?** Check the full documentation or review the example code!
