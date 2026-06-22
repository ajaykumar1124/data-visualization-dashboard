"""
Dashboard Enhancements Integration Example
Demonstrates how to integrate all enhancement features into a Streamlit dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from dashboard_enhancements import (
    DashboardEnhancementsManager,
    MobileConfig,
    NotificationConfig,
    RefreshConfig,
    FilterConfig,
    NotificationChannel
)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'enhancements' not in st.session_state:
        st.session_state.enhancements = DashboardEnhancementsManager(
            mobile_config=MobileConfig(enabled=True),
            theme_config='light',
            notification_config=NotificationConfig(
                channel=NotificationChannel.WEBHOOK,
                enabled=False
            ),
            refresh_config=RefreshConfig(
                enabled=True,
                interval_seconds=300
            ),
            filter_config=FilterConfig(
                enable_regex_search=True,
                enable_date_range_filter=True
            )
        )
    
    if 'sample_data' not in st.session_state:
        st.session_state.sample_data = generate_sample_data()


def generate_sample_data() -> pd.DataFrame:
    """Generate sample data for demonstration"""
    np.random.seed(42)
    
    dates = pd.date_range(start='2024-01-01', end='2024-06-30', freq='D')
    
    data = {
        'Date': np.random.choice(dates, 100),
        'Department': np.random.choice(['Sales', 'IT', 'HR', 'Finance', 'Marketing'], 100),
        'Employee': [f'Employee_{i}' for i in range(1, 101)],
        'Sales': np.random.randint(1000, 10000, 100),
        'Performance_Score': np.random.uniform(50, 100, 100),
        'Status': np.random.choice(['Active', 'Inactive', 'On Leave'], 100),
        'Email': [f'employee{i}@company.com' for i in range(1, 101)]
    }
    
    return pd.DataFrame(data)


def render_mobile_section(enhancements):
    """Render mobile optimization section"""
    st.subheader("📱 Mobile Optimization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(
            "✓ Responsive CSS applied\n"
            f"✓ Touch target size: {enhancements.mobile.config.touch_target_size}px\n"
            f"✓ Breakpoints: Mobile, Tablet, Desktop, Wide"
        )
    
    with col2:
        if st.checkbox("Show Mobile Configuration"):
            config = enhancements.mobile.apply_mobile_optimizations()
            st.json({
                'responsive': config['responsive_css'][:100] + '...',
                'touch_friendly': config['touch_friendly_buttons'],
                'swipe_navigation': config['swipe_navigation'],
                'breakpoints': config['breakpoints']
            })


def render_theme_section(enhancements):
    """Render theme management section"""
    st.subheader("🎨 Theme Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Available Themes:**")
        themes = enhancements.theme.get_available_themes()
        
        selected_theme = st.selectbox(
            "Select Theme",
            themes,
            index=0
        )
        
        if st.button("Apply Theme"):
            enhancements.theme.apply_theme(selected_theme)
            st.success(f"✓ Theme '{selected_theme}' applied!")
            st.rerun()
    
    with col2:
        if enhancements.theme.current_theme:
            st.markdown("**Current Theme Colors:**")
            theme = enhancements.theme.current_theme
            
            color_data = {
                'Color': ['Primary', 'Secondary', 'Accent', 'Background', 'Text'],
                'Value': [
                    theme.primary_color,
                    theme.secondary_color,
                    theme.accent_color,
                    theme.background_color,
                    theme.text_color
                ]
            }
            
            st.dataframe(color_data, use_container_width=True)
    
    # Color palette
    if st.checkbox("Show Color Palette"):
        palette = enhancements.theme.generate_color_palette(num_colors=12)
        
        cols = st.columns(6)
        for i, color in enumerate(palette):
            with cols[i % 6]:
                st.color_picker(f"Color {i+1}", color, disabled=True)


def render_notifications_section(enhancements):
    """Render notifications configuration section"""
    st.subheader("🔔 Slack/Teams Notifications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Configure Notifications:**")
        
        channel_type = st.selectbox(
            "Notification Channel",
            [ch.value for ch in NotificationChannel]
        )
        
        webhook_url = st.text_input(
            "Webhook URL",
            type="password",
            placeholder="Paste your webhook URL here"
        )
        
        if webhook_url:
            enhancements.notifications.config.webhook_url = webhook_url
            st.success("✓ Webhook URL configured")
    
    with col2:
        st.markdown("**Send Test Notification:**")
        
        test_type = st.selectbox(
            "Notification Type",
            ["Success", "Warning", "Error", "Info"]
        )
        
        if st.button("Send Test Notification"):
            if enhancements.notifications.config.webhook_url:
                success = enhancements.notifications.send_notification(
                    title="🧪 Test Notification",
                    message="This is a test notification from Dashboard Enhancements",
                    message_type=test_type.lower(),
                    fields={
                        'Timestamp': datetime.now().isoformat(),
                        'Type': test_type,
                        'Status': 'Test'
                    }
                )
                if success:
                    st.success("✓ Notification sent!")
                else:
                    st.warning("⚠ Notification sending failed (check webhook URL)")
            else:
                st.error("❌ Please configure webhook URL first")


def render_refresh_section(enhancements):
    """Render data refresh section"""
    st.subheader("🔄 Real-Time Data Refresh")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data Now"):
            enhancements.refresh.refresh()
            st.success("✓ Data refreshed!")
            st.rerun()
    
    with col2:
        interval = st.selectbox(
            "Refresh Interval (seconds)",
            [30, 60, 300, 600, 1800, 3600],
            index=2
        )
        enhancements.refresh.set_refresh_interval(interval)
    
    with col3:
        auto_refresh = st.checkbox(
            "Enable Auto-Refresh",
            value=enhancements.refresh.config.enabled
        )
        enhancements.refresh.config.enabled = auto_refresh
    
    # Refresh statistics
    stats = enhancements.refresh.get_refresh_statistics()
    
    if st.checkbox("Show Refresh Statistics"):
        stats_df = pd.DataFrame([
            ['Enabled', stats['enabled']],
            ['Interval (seconds)', stats['interval_seconds']],
            ['Is Refreshing', stats['is_refreshing']],
            ['Callback Count', stats['callback_count']],
            ['Time to Next Refresh (s)', round(stats['time_until_next_refresh'], 1)]
        ], columns=['Metric', 'Value'])
        
        st.dataframe(stats_df, use_container_width=True)


def render_filters_section(enhancements):
    """Render advanced filtering section"""
    st.subheader("🔍 Advanced Filtering & Search")
    
    # Get sample data
    df = st.session_state.sample_data.copy()
    
    # Render filter UI
    df = enhancements.filters.render_filter_ui(df, key_suffix="main")
    
    # Display filtered results
    st.markdown("### Filtered Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Rows", len(df))
    
    with col2:
        st.metric("Filtered Rows", len(df))
    
    st.dataframe(df, use_container_width=True)
    
    return df


def render_dashboard_metrics(df):
    """Render dashboard metrics"""
    st.subheader("📊 Dashboard Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Records",
            len(df),
            delta=f"{len(df)} records"
        )
    
    with col2:
        avg_performance = df['Performance_Score'].mean()
        st.metric(
            "Avg Performance",
            f"{avg_performance:.1f}%",
            delta=f"{avg_performance:.1f}% avg"
        )
    
    with col3:
        total_sales = df['Sales'].sum()
        st.metric(
            "Total Sales",
            f"${total_sales:,}",
            delta=f"${total_sales:,} total"
        )
    
    with col4:
        active_count = len(df[df['Status'] == 'Active'])
        st.metric(
            "Active Employees",
            active_count,
            delta=f"{active_count} active"
        )


def render_visualizations(df):
    """Render data visualizations"""
    st.subheader("📈 Data Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Sales by Department**")
        dept_sales = df.groupby('Department')['Sales'].sum().reset_index()
        st.bar_chart(dept_sales.set_index('Department'))
    
    with col2:
        st.markdown("**Performance Distribution**")
        st.histogram_chart(df['Performance_Score'])


def main():
    """Main application"""
    # Page configuration
    st.set_page_config(
        page_title="Enhanced Dashboard Demo",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize
    initialize_session_state()
    enhancements = st.session_state.enhancements
    
    # Apply all enhancements
    enhancements.initialize_all()
    
    # Header
    st.title("📊 Dashboard Enhancements Demo")
    st.markdown(
        "Comprehensive dashboard with mobile optimization, themes, "
        "notifications, real-time refresh, and advanced filtering"
    )
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard",
        "📱 Mobile",
        "🎨 Themes",
        "🔔 Notifications",
        "🔄 Refresh",
        "🔍 Filters"
    ])
    
    with tab1:
        st.markdown(
            "### Main Dashboard View\n"
            "This tab demonstrates the core dashboard with metrics and visualizations."
        )
        
        df = st.session_state.sample_data.copy()
        render_dashboard_metrics(df)
        st.divider()
        render_visualizations(df)
    
    with tab2:
        render_mobile_section(enhancements)
    
    with tab3:
        render_theme_section(enhancements)
    
    with tab4:
        render_notifications_section(enhancements)
    
    with tab5:
        render_refresh_section(enhancements)
    
    with tab6:
        st.markdown(
            "### Advanced Filtering & Search\n"
            "Apply multiple filters to find specific data."
        )
        filtered_df = render_filters_section(enhancements)
    
    # Sidebar settings
    st.sidebar.title("⚙️ Settings")
    
    with st.sidebar.expander("📋 Enhancement Status"):
        status = enhancements.get_status_report()
        st.json(status)
    
    with st.sidebar.expander("📥 Import/Export"):
        if st.button("Export Configuration"):
            try:
                enhancements.export_configuration("dashboard_config.json")
                st.success("✓ Configuration exported to dashboard_config.json")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #888; padding: 1rem;'>
        <small>Dashboard Enhancements v1.0.0 | 
        Mobile-Optimized • Themeable • Integrated • Real-Time • Advanced Filtering</small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
