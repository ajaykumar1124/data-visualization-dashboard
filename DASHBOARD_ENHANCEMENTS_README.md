# Dashboard Enhancements Module

A comprehensive enhancement module for the data visualization dashboard providing mobile optimization, custom themes, notifications, real-time refresh, and advanced filtering capabilities.

## Features Overview

### 1. 📱 Mobile Optimization
- **Responsive CSS Generation**: Automatically generates responsive CSS for all screen sizes
- **Touch-Friendly UI**: Optimized button sizes (48px) and touch targets
- **Adaptive Layouts**: Mobile-first responsive design with breakpoints for mobile, tablet, desktop, and wide screens
- **Viewport Configuration**: Proper viewport meta tags for mobile devices
- **Flexible Typography**: Responsive text sizing using CSS clamp()
- **Gesture Support**: Support for touch gestures and swipe navigation

**Key Features:**
- Mobile breakpoints: 480px (mobile), 768px (tablet), 1024px (desktop), 1440px (wide)
- Default touch target size: 48 pixels
- Responsive columns and flexbox layouts
- Hide/show elements based on screen size
- Responsive tables and cards

### 2. 🎨 Theme Management
- **Multiple Built-in Themes**: Light, Dark, and Professional themes
- **Custom Themes**: Create and manage custom color schemes
- **Dynamic CSS Generation**: Generate CSS from theme configurations
- **Color Palettes**: Generate complementary color palettes
- **Theme Import/Export**: Save and load themes as JSON
- **Real-time Application**: Apply themes instantly in Streamlit

**Available Themes:**
- `light`: Professional light theme with blue primary color
- `dark`: Dark theme for low-light environments
- `professional`: Custom business theme with sophisticated colors
- Create custom themes using `ThemeConfig`

### 3. 🔔 Slack/Teams Integration
- **Webhook Support**: Send notifications to Slack and Microsoft Teams
- **Message Formatting**: Rich message formatting with fields/facts
- **Retry Logic**: Automatic retry with configurable attempts
- **Multiple Channels**: Support for Slack channels and Teams webhooks
- **Dashboard Updates**: Send update notifications for data events
- **Error Handling**: Comprehensive error handling and logging

**Supported Notifications:**
- Data loaded
- Processing complete
- Processing errors
- Report generated
- Custom alerts

### 4. 🔄 Real-Time Data Refresh
- **Auto-Refresh**: Configurable automatic refresh intervals
- **Refresh Controls**: UI controls for manual refresh and interval selection
- **Callbacks**: Register functions to execute on refresh
- **Time Tracking**: Monitor time until next refresh
- **Browser Integration**: JavaScript-based auto-refresh support
- **Status Monitoring**: Track refresh statistics

**Configuration:**
- Minimum interval: 30 seconds
- Maximum interval: 3600 seconds (1 hour)
- Default interval: 300 seconds (5 minutes)
- Auto-refresh on load option

### 5. 🔍 Advanced Filtering & Search
- **Multi-Column Filtering**: Filter across multiple columns simultaneously
- **Regex Search**: Pattern matching using regular expressions
- **Date Range Filters**: Filter by date ranges
- **Operators**: Support for eq, ne, gt, lt, gte, lte, contains, in, notin
- **Text Search**: Full-text search across columns
- **Filter Management**: Add, remove, and clear filters dynamically
- **Interactive UI**: Streamlit-based filter controls

**Operators:**
- `eq` - Equals
- `ne` - Not equals
- `gt` - Greater than
- `lt` - Less than
- `gte` - Greater than or equal
- `lte` - Less than or equal
- `contains` - String contains
- `startswith` - String starts with
- `endswith` - String ends with
- `in` - Value in list
- `notin` - Value not in list
- `date_range` - Date range filter

## Installation & Setup

### Prerequisites
```bash
pip install streamlit pandas numpy plotly requests
```

### Import the Module
```python
from dashboard_enhancements import (
    DashboardEnhancementsManager,
    MobileOptimizer,
    ThemeManager,
    NotificationManager,
    DataRefreshManager,
    AdvancedFilterManager,
    MobileConfig,
    ThemeConfig,
    NotificationConfig,
    RefreshConfig,
    FilterConfig,
    ThemeType,
    NotificationChannel
)
```

## Usage Examples

### Quick Start - Initialize All Enhancements
```python
import streamlit as st
from dashboard_enhancements import DashboardEnhancementsManager

# Create enhancement manager with defaults
enhancements = DashboardEnhancementsManager(theme_config='light')

# Initialize all enhancements
enhancements.initialize_all()

# Render settings panel in sidebar
enhancements.render_settings_panel()

# Your dashboard content here
st.title("Enhanced Dashboard")
```

### 1. Mobile Optimization

```python
from dashboard_enhancements import MobileOptimizer, MobileConfig

# Create mobile optimizer with custom config
mobile_config = MobileConfig(
    enabled=True,
    touch_target_size=50,
    enable_swipe_navigation=True
)
mobile = MobileOptimizer(mobile_config)

# Generate and apply responsive CSS
import streamlit as st
mobile.render_mobile_css()

# Your mobile-friendly content here
```

**Configuration Options:**
```python
MobileConfig(
    enabled=True,
    viewport_width="device-width",
    viewport_scale=1.0,
    touch_target_size=48,
    enable_swipe_navigation=True,
    enable_responsive_text=True
)
```

### 2. Theme Management

```python
from dashboard_enhancements import ThemeManager, ThemeConfig, ThemeType

theme_manager = ThemeManager()

# Apply built-in theme
theme_manager.apply_theme('dark')

# Create custom theme
custom_theme = ThemeConfig(
    name='Ocean Wave',
    theme_type=ThemeType.CUSTOM,
    primary_color='#0066cc',
    secondary_color='#00ccff',
    background_color='#001a33',
    text_color='#e6f2ff',
    accent_color='#00ff99'
)
theme_manager.add_theme(custom_theme)
theme_manager.apply_theme('ocean wave')

# Generate color palette
palette = theme_manager.generate_color_palette()

# Export/Import themes
theme_manager.export_theme('dark', 'my_theme.json')
theme_manager.import_theme('my_theme.json')
```

### 3. Slack/Teams Notifications

```python
from dashboard_enhancements import NotificationManager, NotificationChannel

# Configure Slack
notifier = NotificationManager()
notifier.configure_slack('https://hooks.slack.com/services/YOUR/WEBHOOK/URL')

# Send notification
notifier.send_notification(
    title='📊 Data Processing Complete',
    message='Your dataset has been processed successfully',
    message_type='success',
    fields={
        'Rows Processed': '15,000',
        'Accuracy': '98%',
        'Duration': '2m 45s'
    }
)

# Configure Teams
notifier.configure_teams('https://outlook.webhook.office.com/...')

# Send dashboard update notification
notifier.send_dashboard_update(
    update_type='data_loaded',
    details={
        'message': 'New dataset loaded',
        'rows': 15000,
        'columns': 12
    }
)

# Check notification status
status = notifier.get_status()
```

### 4. Real-Time Data Refresh

```python
from dashboard_enhancements import DataRefreshManager, RefreshConfig

refresh_config = RefreshConfig(
    enabled=True,
    interval_seconds=300,  # 5 minutes
    auto_refresh_on_load=True
)
refresh_manager = DataRefreshManager(refresh_config)

# Register refresh callback
def on_data_refresh():
    print("Data refreshed!")
    # Your refresh logic here

refresh_manager.register_refresh_callback(on_data_refresh)

# Render refresh controls in Streamlit
refresh_manager.render_refresh_controls()

# Manual refresh
if st.button('Refresh Now'):
    refresh_manager.refresh()
    st.rerun()

# Check if should refresh
if refresh_manager.should_refresh():
    refresh_manager.refresh()

# Get statistics
stats = refresh_manager.get_refresh_statistics()
```

### 5. Advanced Filtering & Search

```python
from dashboard_enhancements import AdvancedFilterManager, FilterConfig
import pandas as pd

filter_config = FilterConfig(
    enable_regex_search=True,
    enable_date_range_filter=True,
    case_sensitive=False
)
filter_manager = AdvancedFilterManager(filter_config)

# Create sample dataframe
df = pd.read_csv('data.csv')

# Add column filter
filter_manager.add_column_filter('Department', 'eq', 'Sales')

# Add date range filter
from datetime import datetime
filter_manager.add_date_range_filter(
    'Date',
    datetime(2024, 1, 1),
    datetime(2024, 12, 31)
)

# Apply filters
filtered_df = filter_manager.apply_filters(df)

# Text search
search_results = filter_manager.search_text(df, 'product')

# Regex filter
regex_results = filter_manager.apply_regex_filter(
    df, 'Email', r'^[a-z]+@example\.com$'
)

# Render filter UI
filtered_df = filter_manager.render_filter_ui(df)

# Get filter summary
summary = filter_manager.get_filter_summary()
```

## Class Reference

### MobileOptimizer
Handles responsive design and mobile UX optimization.

**Methods:**
- `generate_viewport_meta()` - Generate viewport meta tag
- `generate_responsive_css()` - Generate responsive CSS
- `get_mobile_layout_columns(desktop_count)` - Get layout columns
- `apply_mobile_optimizations()` - Apply all optimizations
- `render_mobile_css()` - Render CSS in Streamlit

### ThemeManager
Manages custom themes and branding.

**Methods:**
- `add_theme(theme_config)` - Add custom theme
- `get_theme(theme_name)` - Retrieve theme
- `set_current_theme(theme_name)` - Set active theme
- `get_available_themes()` - List available themes
- `generate_theme_css(theme)` - Generate CSS from theme
- `generate_color_palette(theme, num_colors)` - Generate palette
- `apply_theme(theme_name)` - Apply theme in Streamlit
- `export_theme(theme_name, filepath)` - Export to JSON
- `import_theme(filepath)` - Import from JSON

### NotificationManager
Manages Slack/Teams webhook integration.

**Methods:**
- `configure_slack(webhook_url, channel)` - Configure Slack
- `configure_teams(webhook_url)` - Configure Teams
- `send_notification(title, message, message_type, fields)` - Send notification
- `send_dashboard_update(update_type, details)` - Send update
- `build_slack_message(title, message, color, fields)` - Build Slack payload
- `build_teams_message(title, message, color, facts)` - Build Teams payload
- `get_status()` - Get status information
- `validate_webhook_url(url)` - Validate webhook URL

### DataRefreshManager
Manages real-time data refresh capabilities.

**Methods:**
- `set_refresh_interval(seconds)` - Set refresh interval
- `register_refresh_callback(callback)` - Register callback
- `should_refresh()` - Check if should refresh
- `refresh(data)` - Trigger refresh
- `get_time_until_refresh()` - Get seconds to next refresh
- `render_refresh_controls(key_suffix)` - Render UI controls
- `render_auto_refresh_script()` - Generate JS auto-refresh
- `get_refresh_statistics()` - Get statistics

### AdvancedFilterManager
Handles advanced filtering and search.

**Methods:**
- `add_column_filter(column, operator, value)` - Add column filter
- `add_date_range_filter(column, start, end)` - Add date filter
- `apply_filters(df)` - Apply all filters
- `apply_regex_filter(df, column, pattern, invert)` - Apply regex
- `clear_filters()` - Clear all filters
- `remove_filter(column)` - Remove specific filter
- `search_text(df, search_term, columns)` - Text search
- `render_filter_ui(df, key_suffix)` - Render filter UI
- `get_filter_summary()` - Get filter summary

### DashboardEnhancementsManager
Central manager for all enhancements.

**Methods:**
- `initialize_all()` - Initialize all enhancements
- `render_settings_panel(key_suffix)` - Render settings UI
- `get_status_report()` - Get comprehensive status
- `export_configuration(filepath)` - Export to JSON

## Configuration Data Classes

### MobileConfig
```python
MobileConfig(
    enabled=True,
    viewport_width="device-width",
    viewport_scale=1.0,
    touch_target_size=48,
    responsive_breakpoints={
        'mobile': 480,
        'tablet': 768,
        'desktop': 1024,
        'wide': 1440
    },
    enable_swipe_navigation=True,
    enable_responsive_text=True
)
```

### ThemeConfig
```python
ThemeConfig(
    name="Custom Theme",
    theme_type=ThemeType.CUSTOM,
    primary_color="#1f77b4",
    secondary_color="#ff7f0e",
    background_color="#ffffff",
    text_color="#000000",
    accent_color="#2ca02c",
    font_family="Arial, sans-serif",
    custom_css=""
)
```

### NotificationConfig
```python
NotificationConfig(
    channel=NotificationChannel.SLACK,
    webhook_url="https://hooks.slack.com/...",
    channel_name="#alerts",
    username="Dashboard Bot",
    icon_emoji=":chart_with_upwards_trend:",
    enabled=True,
    retry_attempts=3,
    retry_delay_seconds=5
)
```

### RefreshConfig
```python
RefreshConfig(
    enabled=True,
    interval_seconds=300,
    min_interval_seconds=30,
    max_interval_seconds=3600,
    auto_refresh_on_load=True,
    show_refresh_button=True,
    show_last_updated=True
)
```

### FilterConfig
```python
FilterConfig(
    enable_regex_search=True,
    enable_date_range_filter=True,
    enable_multi_column_filter=True,
    case_sensitive=False,
    partial_match=True,
    max_filter_values=1000
)
```

## Error Handling

All classes include comprehensive error handling and logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Errors are logged automatically
# Check logs for troubleshooting
```

## Performance Considerations

1. **Mobile Optimization**: CSS is cached and minimal - no performance impact
2. **Themes**: CSS generation is fast, cached in Streamlit
3. **Notifications**: Async-friendly, won't block UI
4. **Refresh**: Callbacks execute independently, minimal overhead
5. **Filters**: Optimized for up to 100,000 rows

## Best Practices

1. **Initialize Once**: Create enhancement manager once per session
2. **Use Callbacks**: Register refresh callbacks instead of polling
3. **Cache Themes**: Store custom themes as JSON, import at startup
4. **Test Webhooks**: Validate webhook URLs before storing
5. **Monitor Logs**: Check logs for debugging issues
6. **Responsive Design**: Always test on multiple screen sizes
7. **Performance**: Limit refresh callbacks to essential operations

## Troubleshooting

### Issue: Mobile CSS not applied
- Ensure `render_mobile_css()` is called before content
- Check browser cache (Ctrl+Shift+Del)
- Verify Streamlit is in wide layout mode

### Issue: Theme colors not working
- Check CSS is rendered with `st.markdown(..., unsafe_allow_html=True)`
- Verify theme has valid hex colors
- Clear browser cache

### Issue: Notifications not sending
- Validate webhook URL format (must start with https://)
- Check network connectivity
- Verify webhook URL is correct in Slack/Teams
- Check logs for error messages

### Issue: Refresh not triggering
- Check `enabled=True` in RefreshConfig
- Verify interval_seconds is between min and max
- Ensure callback functions are registered
- Check browser console for JavaScript errors

### Issue: Filters not applying
- Verify column names match exactly (case-sensitive)
- Check data types match filter expectations
- Test regex patterns separately
- Ensure dataframe is not empty

## Contributing & Support

For issues, enhancements, or questions:
1. Check existing documentation
2. Review example code
3. Enable debug logging for troubleshooting
4. Check GitHub issues/discussions

## License

Same as main project

## Changelog

### Version 1.0.0 (2024-06-16)
- Initial release
- Mobile optimization with responsive CSS
- Theme management with multiple built-in themes
- Slack/Teams webhook integration
- Real-time data refresh with auto-refresh
- Advanced filtering with regex and date range support
- Comprehensive documentation and examples
