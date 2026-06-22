"""
Dashboard Enhancements Module
Comprehensive enhancements for the data visualization dashboard including:
- Mobile-friendly responsive design
- Custom themes and branding (dark/light modes)
- Slack/Teams integration for notifications
- Real-time data refresh capabilities
- Advanced filtering and search functionality
"""

import logging
import json
import re
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
import requests
from enum import Enum
from abc import ABC, abstractmethod
import pandas as pd
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS & ENUMS
# ============================================================================

class ThemeType(Enum):
    """Available theme types"""
    LIGHT = "light"
    DARK = "dark"
    CUSTOM = "custom"


class NotificationChannel(Enum):
    """Supported notification channels"""
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"


@dataclass
class ThemeConfig:
    """Theme configuration data class"""
    name: str
    theme_type: ThemeType
    primary_color: str
    secondary_color: str
    background_color: str
    text_color: str
    accent_color: str
    font_family: str = "Arial"
    custom_css: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'theme_type': self.theme_type.value,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'background_color': self.background_color,
            'text_color': self.text_color,
            'accent_color': self.accent_color,
            'font_family': self.font_family,
            'custom_css': self.custom_css
        }


@dataclass
class MobileConfig:
    """Mobile optimization configuration"""
    enabled: bool = True
    viewport_width: str = "device-width"
    viewport_scale: float = 1.0
    touch_target_size: int = 48  # pixels
    responsive_breakpoints: Dict[str, int] = field(default_factory=lambda: {
        'mobile': 480,
        'tablet': 768,
        'desktop': 1024,
        'wide': 1440
    })
    enable_swipe_navigation: bool = True
    enable_responsive_text: bool = True


@dataclass
class NotificationConfig:
    """Notification configuration"""
    channel: NotificationChannel
    webhook_url: str = ""
    channel_name: str = ""
    username: str = "Dashboard Bot"
    icon_emoji: str = ":chart_with_upwards_trend:"
    enabled: bool = True
    retry_attempts: int = 3
    retry_delay_seconds: int = 5


@dataclass
class RefreshConfig:
    """Data refresh configuration"""
    enabled: bool = True
    interval_seconds: int = 300  # 5 minutes default
    min_interval_seconds: int = 30
    max_interval_seconds: int = 3600
    auto_refresh_on_load: bool = True
    show_refresh_button: bool = True
    show_last_updated: bool = True


@dataclass
class FilterConfig:
    """Advanced filtering configuration"""
    enable_regex_search: bool = True
    enable_date_range_filter: bool = True
    enable_multi_column_filter: bool = True
    case_sensitive: bool = False
    partial_match: bool = True
    max_filter_values: int = 1000


# ============================================================================
# MOBILE OPTIMIZER CLASS
# ============================================================================

class MobileOptimizer:
    """
    Handles responsive design and mobile UX optimization.
    Provides mobile-friendly layout adjustments, touch-friendly buttons,
    and responsive CSS generation.
    """
    
    def __init__(self, config: Optional[MobileConfig] = None):
        """
        Initialize the MobileOptimizer.
        
        Args:
            config: MobileConfig instance with mobile settings
        """
        self.config = config or MobileConfig()
        self.logger = logging.getLogger(f"{__name__}.MobileOptimizer")
        self.logger.info("MobileOptimizer initialized")
    
    def generate_viewport_meta(self) -> str:
        """
        Generate viewport meta tag for mobile responsiveness.
        
        Returns:
            HTML meta tag string
        """
        try:
            meta_tag = (
                f'<meta name="viewport" content='
                f'"width={self.config.viewport_width}, '
                f'initial-scale={self.config.viewport_scale}, '
                f'user-scalable=yes">'
            )
            self.logger.debug("Viewport meta tag generated")
            return meta_tag
        except Exception as e:
            self.logger.error(f"Error generating viewport meta: {e}")
            return ''
    
    def generate_responsive_css(self) -> str:
        """
        Generate responsive CSS for mobile optimization.
        
        Returns:
            CSS string for responsive design
        """
        try:
            touch_size = self.config.touch_target_size
            
            css = f"""
<style>
/* Mobile Responsive Design */
:root {{
    --touch-target-size: {touch_size}px;
    --mobile-padding: 1rem;
    --tablet-padding: 1.5rem;
    --desktop-padding: 2rem;
}}

/* Base responsive styles */
* {{
    box-sizing: border-box;
}}

body {{
    font-size: 16px;
    margin: 0;
    padding: 0;
}}

/* Container responsive padding */
.container {{
    padding: var(--mobile-padding);
    width: 100%;
}}

/* Mobile-first approach */
@media (min-width: {self.config.responsive_breakpoints['mobile']}px) {{
    .container {{
        padding: var(--mobile-padding);
    }}
}}

@media (min-width: {self.config.responsive_breakpoints['tablet']}px) {{
    .container {{
        padding: var(--tablet-padding);
    }}
    
    .two-column {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }}
}}

@media (min-width: {self.config.responsive_breakpoints['desktop']}px) {{
    .container {{
        padding: var(--desktop-padding);
    }}
    
    .three-column {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1.5rem;
    }}
}}

@media (min-width: {self.config.responsive_breakpoints['wide']}px) {{
    .container {{
        max-width: 1400px;
        margin: 0 auto;
    }}
}}

/* Touch-friendly buttons */
button, .btn, a.button {{
    min-height: var(--touch-target-size);
    min-width: var(--touch-target-size);
    padding: 12px 16px;
    font-size: 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    -webkit-tap-highlight-color: transparent;
}}

button:active, .btn:active {{
    transform: scale(0.98);
    opacity: 0.8;
}}

/* Responsive text */
h1 {{
    font-size: clamp(1.5rem, 5vw, 2.5rem);
}}

h2 {{
    font-size: clamp(1.25rem, 4vw, 2rem);
}}

h3 {{
    font-size: clamp(1rem, 3vw, 1.5rem);
}}

p {{
    font-size: clamp(0.875rem, 2vw, 1rem);
    line-height: 1.6;
}}

/* Responsive images */
img {{
    max-width: 100%;
    height: auto;
    display: block;
}}

/* Responsive tables */
table {{
    width: 100%;
    border-collapse: collapse;
    font-size: clamp(0.75rem, 1.5vw, 0.875rem);
}}

@media (max-width: {self.config.responsive_breakpoints['mobile']}px) {{
    table {{
        display: block;
        overflow-x: auto;
    }}
    
    th, td {{
        padding: 8px;
    }}
}}

/* Responsive cards */
.card {{
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}}

@media (max-width: {self.config.responsive_breakpoints['tablet']}px) {{
    .card {{
        padding: 0.75rem;
        margin-bottom: 0.75rem;
    }}
}}

/* Hide on mobile */
@media (max-width: {self.config.responsive_breakpoints['tablet']}px) {{
    .hide-mobile {{
        display: none !important;
    }}
}}

/* Show only on mobile */
@media (min-width: {self.config.responsive_breakpoints['tablet']}px) {{
    .show-mobile {{
        display: none !important;
    }}
}}

/* Flex responsive layouts */
.flex-responsive {{
    display: flex;
    flex-direction: column;
    gap: 1rem;
}}

@media (min-width: {self.config.responsive_breakpoints['tablet']}px) {{
    .flex-responsive {{
        flex-direction: row;
        flex-wrap: wrap;
    }}
    
    .flex-responsive > * {{
        flex: 1 1 calc(50% - 0.5rem);
        min-width: 300px;
    }}
}}

@media (min-width: {self.config.responsive_breakpoints['desktop']}px) {{
    .flex-responsive > * {{
        flex: 1 1 calc(33.333% - 0.667rem);
        min-width: 300px;
    }}
}}

/* Touch gestures support */
@supports (touch-action: manipulation) {{
    button, .btn, a.button {{
        touch-action: manipulation;
    }}
}}
</style>
"""
            self.logger.debug("Responsive CSS generated")
            return css
        except Exception as e:
            self.logger.error(f"Error generating responsive CSS: {e}")
            return ""
    
    def get_mobile_layout_columns(self, desktop_count: int = 3) -> int:
        """
        Get appropriate number of columns based on screen size.
        
        Args:
            desktop_count: Number of columns on desktop
            
        Returns:
            Number of columns to use
        """
        try:
            # This is a helper for streamlit column layout
            # In practice, would check window size via streamlit
            return 1  # Default to 1 column (full width) for mobile-first
        except Exception as e:
            self.logger.error(f"Error getting mobile layout columns: {e}")
            return 1
    
    def apply_mobile_optimizations(self) -> Dict[str, Any]:
        """
        Apply all mobile optimizations and return configuration.
        
        Returns:
            Dictionary containing all mobile optimization settings
        """
        try:
            optimizations = {
                'responsive_css': self.generate_responsive_css(),
                'viewport_meta': self.generate_viewport_meta(),
                'touch_friendly_buttons': True,
                'swipe_navigation': self.config.enable_swipe_navigation,
                'responsive_text': self.config.enable_responsive_text,
                'touch_target_size': self.config.touch_target_size,
                'breakpoints': self.config.responsive_breakpoints
            }
            
            self.logger.info("Mobile optimizations applied successfully")
            return optimizations
        except Exception as e:
            self.logger.error(f"Error applying mobile optimizations: {e}")
            return {}
    
    def render_mobile_css(self):
        """Render mobile CSS using Streamlit markdown."""
        try:
            st.markdown(self.generate_responsive_css(), unsafe_allow_html=True)
            self.logger.debug("Mobile CSS rendered in Streamlit")
        except Exception as e:
            self.logger.error(f"Error rendering mobile CSS: {e}")


# ============================================================================
# THEME MANAGER CLASS
# ============================================================================

class ThemeManager:
    """
    Manages custom themes and branding for the dashboard.
    Supports dark/light themes, color schemes, and custom CSS.
    """
    
    def __init__(self):
        """Initialize the ThemeManager"""
        self.logger = logging.getLogger(f"{__name__}.ThemeManager")
        self.themes: Dict[str, ThemeConfig] = {}
        self.current_theme: Optional[ThemeConfig] = None
        self._initialize_default_themes()
        self.logger.info("ThemeManager initialized")
    
    def _initialize_default_themes(self):
        """Initialize default light and dark themes"""
        try:
            # Light theme
            self.themes['light'] = ThemeConfig(
                name='Light Theme',
                theme_type=ThemeType.LIGHT,
                primary_color='#1f77b4',
                secondary_color='#ff7f0e',
                background_color='#ffffff',
                text_color='#000000',
                accent_color='#2ca02c',
                font_family='Arial, sans-serif'
            )
            
            # Dark theme
            self.themes['dark'] = ThemeConfig(
                name='Dark Theme',
                theme_type=ThemeType.DARK,
                primary_color='#1f77b4',
                secondary_color='#ff7f0e',
                background_color='#1e1e1e',
                text_color='#e0e0e0',
                accent_color='#4ade80',
                font_family='Arial, sans-serif'
            )
            
            # Professional theme
            self.themes['professional'] = ThemeConfig(
                name='Professional Theme',
                theme_type=ThemeType.CUSTOM,
                primary_color='#2E86AB',
                secondary_color='#A23B72',
                background_color='#f5f5f5',
                text_color='#333333',
                accent_color='#F18F01',
                font_family='Segoe UI, sans-serif'
            )
            
            self.current_theme = self.themes['light']
            self.logger.info("Default themes initialized")
        except Exception as e:
            self.logger.error(f"Error initializing default themes: {e}")
    
    def add_theme(self, theme_config: ThemeConfig):
        """
        Add a custom theme.
        
        Args:
            theme_config: ThemeConfig instance
            
        Raises:
            ValueError: If theme name is empty
        """
        try:
            if not theme_config.name:
                raise ValueError("Theme name cannot be empty")
            
            self.themes[theme_config.name.lower()] = theme_config
            self.logger.info(f"Theme '{theme_config.name}' added successfully")
        except Exception as e:
            self.logger.error(f"Error adding theme: {e}")
            raise
    
    def get_theme(self, theme_name: str) -> Optional[ThemeConfig]:
        """
        Get a theme by name.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            ThemeConfig instance or None if not found
        """
        try:
            return self.themes.get(theme_name.lower())
        except Exception as e:
            self.logger.error(f"Error getting theme: {e}")
            return None
    
    def set_current_theme(self, theme_name: str) -> bool:
        """
        Set the current active theme.
        
        Args:
            theme_name: Name of the theme to activate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            theme = self.get_theme(theme_name)
            if theme is None:
                self.logger.warning(f"Theme '{theme_name}' not found")
                return False
            
            self.current_theme = theme
            self.logger.info(f"Current theme set to '{theme_name}'")
            return True
        except Exception as e:
            self.logger.error(f"Error setting current theme: {e}")
            return False
    
    def get_available_themes(self) -> List[str]:
        """
        Get list of available theme names.
        
        Returns:
            List of theme names
        """
        return list(self.themes.keys())
    
    def generate_theme_css(self, theme: Optional[ThemeConfig] = None) -> str:
        """
        Generate CSS from theme configuration.
        
        Args:
            theme: ThemeConfig instance (uses current if not provided)
            
        Returns:
            CSS string
        """
        try:
            if theme is None:
                if self.current_theme is None:
                    return ""
                theme = self.current_theme
            
            css = f"""
<style>
:root {{
    --primary-color: {theme.primary_color};
    --secondary-color: {theme.secondary_color};
    --background-color: {theme.background_color};
    --text-color: {theme.text_color};
    --accent-color: {theme.accent_color};
}}

body {{
    background-color: var(--background-color);
    color: var(--text-color);
    font-family: {theme.font_family};
    transition: background-color 0.3s ease, color 0.3s ease;
}}

/* Primary elements */
.stButton > button {{
    background-color: var(--primary-color) !important;
    color: white !important;
    border: none !important;
}}

.stButton > button:hover {{
    background-color: var(--secondary-color) !important;
}}

/* Headers */
h1, h2, h3, h4, h5, h6 {{
    color: var(--primary-color);
}}

/* Links */
a {{
    color: var(--accent-color);
}}

a:hover {{
    color: var(--secondary-color);
}}

/* Cards and containers */
.stSelectbox, .stMultiSelect, .stTextInput, .stTextArea {{
    background-color: var(--background-color);
    color: var(--text-color);
}}

/* Metrics */
.stMetric {{
    background-color: var(--background-color);
    border: 1px solid var(--primary-color);
    border-radius: 8px;
    padding: 1rem;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: var(--background-color);
    color: var(--text-color);
}}

/* Data frames */
.dataframe {{
    background-color: var(--background-color);
    color: var(--text-color);
}}

/* Expanders */
.streamlit-expanderHeader {{
    color: var(--primary-color);
    background-color: transparent;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] button {{
    color: var(--text-color);
}}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
    border-bottom-color: var(--primary-color);
}}

{theme.custom_css}
</style>
"""
            self.logger.debug(f"Theme CSS generated for '{theme.name}'")
            return css
        except Exception as e:
            self.logger.error(f"Error generating theme CSS: {e}")
            return ""
    
    def generate_color_palette(self, theme: Optional[ThemeConfig] = None, 
                              num_colors: int = 8) -> List[str]:
        """
        Generate a color palette from theme colors.
        
        Args:
            theme: ThemeConfig instance (uses current if not provided)
            num_colors: Number of colors to generate
            
        Returns:
            List of color hex strings
        """
        try:
            if theme is None:
                theme = self.current_theme or self.themes['light']
            
            base_colors = [
                theme.primary_color,
                theme.secondary_color,
                theme.accent_color,
                theme.background_color,
                theme.text_color
            ]
            
            # Add complementary colors and variations
            palette = base_colors.copy()
            
            if len(palette) < num_colors:
                # Generate additional colors with variations
                for i in range(num_colors - len(palette)):
                    variation = f"#{hash(str(i)) % 0xFFFFFF:06x}"
                    palette.append(variation)
            
            self.logger.debug(f"Color palette generated with {len(palette)} colors")
            return palette[:num_colors]
        except Exception as e:
            self.logger.error(f"Error generating color palette: {e}")
            return []
    
    def apply_theme(self, theme_name: str) -> bool:
        """
        Apply a theme by rendering its CSS.
        
        Args:
            theme_name: Name of theme to apply
            
        Returns:
            True if successful
        """
        try:
            if not self.set_current_theme(theme_name):
                return False
            
            st.markdown(self.generate_theme_css(), unsafe_allow_html=True)
            self.logger.info(f"Theme '{theme_name}' applied successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error applying theme: {e}")
            return False
    
    def export_theme(self, theme_name: str, filepath: str):
        """
        Export theme configuration to JSON file.
        
        Args:
            theme_name: Name of theme to export
            filepath: Path to save JSON file
            
        Raises:
            ValueError: If theme not found
        """
        try:
            theme = self.get_theme(theme_name)
            if theme is None:
                raise ValueError(f"Theme '{theme_name}' not found")
            
            with open(filepath, 'w') as f:
                json.dump(theme.to_dict(), f, indent=2)
            
            self.logger.info(f"Theme '{theme_name}' exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Error exporting theme: {e}")
            raise
    
    def import_theme(self, filepath: str) -> bool:
        """
        Import theme configuration from JSON file.
        
        Args:
            filepath: Path to JSON theme file
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'r') as f:
                theme_dict = json.load(f)
            
            # Convert theme_type string back to enum
            if 'theme_type' in theme_dict:
                theme_dict['theme_type'] = ThemeType(theme_dict['theme_type'])
            
            theme = ThemeConfig(**theme_dict)
            self.add_theme(theme)
            self.logger.info(f"Theme imported from {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error importing theme: {e}")
            return False


# ============================================================================
# NOTIFICATION MANAGER CLASS
# ============================================================================

class NotificationManager:
    """
    Manages Slack/Teams webhook integration for notifications.
    Handles notification sending, retry logic, and error handling.
    """
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        """
        Initialize the NotificationManager.
        
        Args:
            config: NotificationConfig instance
        """
        self.config = config or NotificationConfig(
            channel=NotificationChannel.WEBHOOK
        )
        self.logger = logging.getLogger(f"{__name__}.NotificationManager")
        self.logger.info("NotificationManager initialized")
    
    def validate_webhook_url(self, url: str) -> bool:
        """
        Validate webhook URL format.
        
        Args:
            url: Webhook URL to validate
            
        Returns:
            True if valid URL format
        """
        try:
            # Check if URL starts with http/https
            if not (url.startswith('http://') or url.startswith('https://')):
                self.logger.warning(f"Invalid webhook URL format: {url}")
                return False
            
            # Basic URL validation
            if len(url) < 10:
                return False
            
            self.logger.debug("Webhook URL validated")
            return True
        except Exception as e:
            self.logger.error(f"Error validating webhook URL: {e}")
            return False
    
    def configure_slack(self, webhook_url: str, channel: str = "#alerts"):
        """
        Configure Slack integration.
        
        Args:
            webhook_url: Slack webhook URL
            channel: Slack channel (optional)
            
        Raises:
            ValueError: If webhook URL is invalid
        """
        try:
            if not self.validate_webhook_url(webhook_url):
                raise ValueError("Invalid webhook URL")
            
            self.config.channel = NotificationChannel.SLACK
            self.config.webhook_url = webhook_url
            self.config.channel_name = channel
            self.logger.info(f"Slack configured for channel {channel}")
        except Exception as e:
            self.logger.error(f"Error configuring Slack: {e}")
            raise
    
    def configure_teams(self, webhook_url: str):
        """
        Configure Microsoft Teams integration.
        
        Args:
            webhook_url: Teams webhook URL
            
        Raises:
            ValueError: If webhook URL is invalid
        """
        try:
            if not self.validate_webhook_url(webhook_url):
                raise ValueError("Invalid webhook URL")
            
            self.config.channel = NotificationChannel.TEAMS
            self.config.webhook_url = webhook_url
            self.logger.info("Teams configured")
        except Exception as e:
            self.logger.error(f"Error configuring Teams: {e}")
            raise
    
    def build_slack_message(self, title: str, message: str, 
                           color: str = "#36a64f", 
                           fields: Optional[Dict[str, str]] = None) -> Dict:
        """
        Build Slack message payload.
        
        Args:
            title: Message title
            message: Message text
            color: Message color (hex)
            fields: Additional fields as dict
            
        Returns:
            Message payload dictionary
        """
        try:
            payload = {
                "attachments": [
                    {
                        "fallback": title,
                        "color": color,
                        "title": title,
                        "text": message,
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            if fields:
                attachment_fields = [
                    {
                        "title": k,
                        "value": v,
                        "short": True
                    }
                    for k, v in fields.items()
                ]
                payload["attachments"][0]["fields"] = attachment_fields
            
            self.logger.debug("Slack message payload built")
            return payload
        except Exception as e:
            self.logger.error(f"Error building Slack message: {e}")
            return {}
    
    def build_teams_message(self, title: str, message: str,
                           color: str = "28a745",
                           facts: Optional[Dict[str, str]] = None) -> Dict:
        """
        Build Microsoft Teams message payload.
        
        Args:
            title: Message title
            message: Message text
            color: Message color (hex without #)
            facts: Additional facts as dict
            
        Returns:
            Message payload dictionary
        """
        try:
            payload = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": title,
                "themeColor": color,
                "sections": [
                    {
                        "activityTitle": title,
                        "activitySubtitle": datetime.now().isoformat(),
                        "text": message
                    }
                ]
            }
            
            if facts:
                facts_list = [
                    {
                        "name": k,
                        "value": v
                    }
                    for k, v in facts.items()
                ]
                payload["sections"][0]["facts"] = facts_list
            
            self.logger.debug("Teams message payload built")
            return payload
        except Exception as e:
            self.logger.error(f"Error building Teams message: {e}")
            return {}
    
    def send_notification(self, title: str, message: str,
                         message_type: str = "info",
                         fields: Optional[Dict[str, str]] = None) -> bool:
        """
        Send notification to configured channel.
        
        Args:
            title: Notification title
            message: Notification message
            message_type: Type of message (info, success, warning, error)
            fields: Additional fields/facts
            
        Returns:
            True if successful
        """
        try:
            if not self.config.enabled:
                self.logger.warning("Notifications are disabled")
                return False
            
            if not self.config.webhook_url:
                self.logger.error("Webhook URL not configured")
                return False
            
            # Map message type to color
            color_map = {
                'info': '#0099ff',
                'success': '#28a745',
                'warning': '#ffc107',
                'error': '#dc3545'
            }
            color = color_map.get(message_type, '#0099ff')
            
            # Build appropriate message based on channel
            if self.config.channel == NotificationChannel.SLACK:
                payload = self.build_slack_message(title, message, color, fields)
            elif self.config.channel == NotificationChannel.TEAMS:
                color_hex = color.lstrip('#')
                payload = self.build_teams_message(title, message, color_hex, fields)
            else:
                payload = {"title": title, "message": message, "fields": fields}
            
            # Send with retry logic
            return self._send_with_retry(payload)
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False
    
    def _send_with_retry(self, payload: Dict) -> bool:
        """
        Send notification with retry logic.
        
        Args:
            payload: Message payload
            
        Returns:
            True if successful
        """
        try:
            for attempt in range(self.config.retry_attempts):
                try:
                    response = requests.post(
                        self.config.webhook_url,
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        self.logger.info(
                            f"Notification sent successfully "
                            f"(attempt {attempt + 1})"
                        )
                        return True
                    
                    self.logger.warning(
                        f"Notification send failed with status "
                        f"{response.status_code} "
                        f"(attempt {attempt + 1})"
                    )
                    
                except requests.exceptions.RequestException as e:
                    self.logger.warning(
                        f"Request failed on attempt {attempt + 1}: {e}"
                    )
                
                # Wait before retry (except on last attempt)
                if attempt < self.config.retry_attempts - 1:
                    import time
                    time.sleep(self.config.retry_delay_seconds)
            
            return False
        except Exception as e:
            self.logger.error(f"Error in retry logic: {e}")
            return False
    
    def send_dashboard_update(self, update_type: str, details: Dict) -> bool:
        """
        Send dashboard update notification.
        
        Args:
            update_type: Type of update (data_loaded, processing_complete, etc.)
            details: Update details
            
        Returns:
            True if successful
        """
        try:
            title_map = {
                'data_loaded': '📊 Data Loaded',
                'processing_complete': '✅ Processing Complete',
                'processing_error': '❌ Processing Error',
                'report_generated': '📄 Report Generated',
                'alert': '🚨 Dashboard Alert'
            }
            
            title = title_map.get(update_type, 'Dashboard Update')
            message = f"Update: {update_type}"
            
            if 'message' in details:
                message = details['message']
            
            return self.send_notification(
                title=title,
                message=message,
                message_type=self._infer_message_type(update_type),
                fields={k: str(v) for k, v in details.items() 
                       if k != 'message'}
            )
        except Exception as e:
            self.logger.error(f"Error sending dashboard update: {e}")
            return False
    
    @staticmethod
    def _infer_message_type(update_type: str) -> str:
        """Infer message type from update type."""
        if 'error' in update_type.lower():
            return 'error'
        elif 'complete' in update_type.lower():
            return 'success'
        elif 'alert' in update_type.lower():
            return 'warning'
        else:
            return 'info'
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get notification manager status.
        
        Returns:
            Status dictionary
        """
        return {
            'enabled': self.config.enabled,
            'channel': self.config.channel.value,
            'webhook_configured': bool(self.config.webhook_url),
            'channel_name': self.config.channel_name,
            'retry_attempts': self.config.retry_attempts
        }


# ============================================================================
# DATA REFRESH MANAGER CLASS
# ============================================================================

class DataRefreshManager:
    """
    Manages real-time data refresh capabilities.
    Handles auto-refresh intervals, refresh triggers, and update callbacks.
    """
    
    def __init__(self, config: Optional[RefreshConfig] = None):
        """
        Initialize the DataRefreshManager.
        
        Args:
            config: RefreshConfig instance
        """
        self.config = config or RefreshConfig()
        self.logger = logging.getLogger(f"{__name__}.DataRefreshManager")
        self.last_refresh_time: Optional[datetime] = None
        self.refresh_callbacks: List[Callable] = []
        self.is_refreshing = False
        self.logger.info("DataRefreshManager initialized")
    
    def set_refresh_interval(self, seconds: int) -> bool:
        """
        Set the data refresh interval.
        
        Args:
            seconds: Interval in seconds
            
        Returns:
            True if successful
        """
        try:
            if (seconds < self.config.min_interval_seconds or
                seconds > self.config.max_interval_seconds):
                self.logger.warning(
                    f"Interval {seconds}s is outside allowed range "
                    f"({self.config.min_interval_seconds}s - "
                    f"{self.config.max_interval_seconds}s)"
                )
                # Clamp to valid range
                seconds = max(
                    self.config.min_interval_seconds,
                    min(seconds, self.config.max_interval_seconds)
                )
            
            self.config.interval_seconds = seconds
            self.logger.info(f"Refresh interval set to {seconds} seconds")
            return True
        except Exception as e:
            self.logger.error(f"Error setting refresh interval: {e}")
            return False
    
    def register_refresh_callback(self, callback: Callable):
        """
        Register a callback function to be called on refresh.
        
        Args:
            callback: Callable function with no parameters
        """
        try:
            if not callable(callback):
                raise TypeError("Callback must be callable")
            
            self.refresh_callbacks.append(callback)
            self.logger.debug(
                f"Refresh callback registered "
                f"(total callbacks: {len(self.refresh_callbacks)})"
            )
        except Exception as e:
            self.logger.error(f"Error registering refresh callback: {e}")
            raise
    
    def should_refresh(self) -> bool:
        """
        Check if refresh interval has elapsed.
        
        Returns:
            True if refresh interval has elapsed
        """
        try:
            if not self.config.enabled:
                return False
            
            if self.last_refresh_time is None:
                return True
            
            elapsed = (datetime.now() - self.last_refresh_time).total_seconds()
            should_refresh = elapsed >= self.config.interval_seconds
            
            self.logger.debug(
                f"Refresh check: elapsed={elapsed:.1f}s, "
                f"interval={self.config.interval_seconds}s, "
                f"should_refresh={should_refresh}"
            )
            
            return should_refresh
        except Exception as e:
            self.logger.error(f"Error checking refresh status: {e}")
            return False
    
    def refresh(self, data: Optional[Any] = None) -> bool:
        """
        Trigger data refresh.
        
        Args:
            data: Optional data to refresh with
            
        Returns:
            True if successful
        """
        try:
            if self.is_refreshing:
                self.logger.warning("Refresh already in progress")
                return False
            
            self.is_refreshing = True
            
            try:
                self.logger.info("Data refresh triggered")
                self.last_refresh_time = datetime.now()
                
                # Execute all registered callbacks
                for callback in self.refresh_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        self.logger.error(f"Error in refresh callback: {e}")
                
                self.logger.info("Data refresh completed successfully")
                return True
            finally:
                self.is_refreshing = False
        except Exception as e:
            self.logger.error(f"Error during refresh: {e}")
            self.is_refreshing = False
            return False
    
    def get_time_until_refresh(self) -> float:
        """
        Get seconds until next refresh.
        
        Returns:
            Seconds until next refresh (0 if should refresh now)
        """
        try:
            if not self.config.enabled or self.last_refresh_time is None:
                return 0
            
            elapsed = (datetime.now() - self.last_refresh_time).total_seconds()
            time_until_refresh = max(
                0,
                self.config.interval_seconds - elapsed
            )
            
            return time_until_refresh
        except Exception as e:
            self.logger.error(f"Error calculating time until refresh: {e}")
            return 0
    
    def render_refresh_controls(self, key_suffix: str = ""):
        """
        Render refresh controls in Streamlit UI.
        
        Args:
            key_suffix: Suffix for Streamlit keys
        """
        try:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Refresh button
                if st.button(
                    f"🔄 Refresh Now",
                    key=f"refresh_btn_{key_suffix}"
                ):
                    self.refresh()
                    st.rerun()
            
            with col2:
                # Refresh interval selector
                intervals = [30, 60, 300, 600, 1800, 3600]
                selected_interval = st.selectbox(
                    "Refresh Interval",
                    intervals,
                    index=2,  # Default to 5 minutes
                    key=f"refresh_interval_{key_suffix}"
                )
                self.set_refresh_interval(selected_interval)
            
            with col3:
                # Auto-refresh toggle
                auto_refresh = st.checkbox(
                    "Auto-refresh",
                    value=self.config.enabled,
                    key=f"auto_refresh_{key_suffix}"
                )
                self.config.enabled = auto_refresh
            
            # Display last refresh time
            if self.config.show_last_updated and self.last_refresh_time:
                time_until = self.get_time_until_refresh()
                st.caption(
                    f"Last updated: {self.last_refresh_time.strftime('%H:%M:%S')} "
                    f"• Next in: {int(time_until)}s"
                )
            
            self.logger.debug("Refresh controls rendered")
        except Exception as e:
            self.logger.error(f"Error rendering refresh controls: {e}")
    
    def render_auto_refresh_script(self) -> str:
        """
        Generate JavaScript for browser-based auto-refresh.
        
        Returns:
            JavaScript code
        """
        try:
            interval_ms = self.config.interval_seconds * 1000
            
            script = f"""
<script>
(function() {{
    let lastRefresh = Date.now();
    const refreshInterval = {interval_ms};
    
    function performRefresh() {{
        const now = Date.now();
        if (now - lastRefresh >= refreshInterval) {{
            console.log('Auto-refreshing data...');
            lastRefresh = now;
            // Trigger Streamlit rerun
            window.parent.document.querySelector('[data-testid="stApp"]').style.opacity = '0.8';
            setTimeout(() => {{
                location.reload();
            }}, 500);
        }}
    }}
    
    // Check refresh interval periodically
    setInterval(performRefresh, {interval_ms});
}})();
</script>
"""
            self.logger.debug("Auto-refresh script generated")
            return script
        except Exception as e:
            self.logger.error(f"Error generating auto-refresh script: {e}")
            return ""
    
    def get_refresh_statistics(self) -> Dict[str, Any]:
        """
        Get refresh statistics.
        
        Returns:
            Dictionary with refresh stats
        """
        try:
            return {
                'enabled': self.config.enabled,
                'interval_seconds': self.config.interval_seconds,
                'last_refresh_time': (
                    self.last_refresh_time.isoformat()
                    if self.last_refresh_time else None
                ),
                'time_until_next_refresh': self.get_time_until_refresh(),
                'is_refreshing': self.is_refreshing,
                'callback_count': len(self.refresh_callbacks),
                'min_interval': self.config.min_interval_seconds,
                'max_interval': self.config.max_interval_seconds
            }
        except Exception as e:
            self.logger.error(f"Error getting refresh statistics: {e}")
            return {}


# ============================================================================
# ADVANCED FILTER MANAGER CLASS
# ============================================================================

class AdvancedFilterManager:
    """
    Handles advanced filtering and search functionality.
    Supports multi-column filtering, regex search, and date range filters.
    """
    
    def __init__(self, config: Optional[FilterConfig] = None):
        """
        Initialize the AdvancedFilterManager.
        
        Args:
            config: FilterConfig instance
        """
        self.config = config or FilterConfig()
        self.logger = logging.getLogger(f"{__name__}.AdvancedFilterManager")
        self.active_filters: Dict[str, Any] = {}
        self.logger.info("AdvancedFilterManager initialized")
    
    def add_column_filter(self, column_name: str, operator: str, 
                         value: Any) -> bool:
        """
        Add a column filter condition.
        
        Args:
            column_name: Column to filter
            operator: Filter operator (eq, ne, gt, lt, gte, lte, contains, in)
            value: Filter value(s)
            
        Returns:
            True if successful
        """
        try:
            valid_operators = [
                'eq', 'ne', 'gt', 'lt', 'gte', 'lte',
                'contains', 'startswith', 'endswith', 'in', 'notin'
            ]
            
            if operator not in valid_operators:
                raise ValueError(f"Invalid operator: {operator}")
            
            self.active_filters[column_name] = {
                'operator': operator,
                'value': value
            }
            
            self.logger.debug(
                f"Filter added: {column_name} {operator} {value}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Error adding column filter: {e}")
            return False
    
    def add_date_range_filter(self, column_name: str, 
                             start_date: datetime, 
                             end_date: datetime) -> bool:
        """
        Add a date range filter.
        
        Args:
            column_name: Date column to filter
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            True if successful
        """
        try:
            if start_date > end_date:
                raise ValueError("Start date must be before end date")
            
            self.active_filters[column_name] = {
                'operator': 'date_range',
                'start_date': start_date,
                'end_date': end_date
            }
            
            self.logger.debug(
                f"Date range filter added: {column_name} "
                f"from {start_date} to {end_date}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Error adding date range filter: {e}")
            return False
    
    def apply_regex_filter(self, df: pd.DataFrame, column_name: str,
                          pattern: str, invert: bool = False) -> pd.DataFrame:
        """
        Apply regex filter to dataframe column.
        
        Args:
            df: Input dataframe
            column_name: Column to filter
            pattern: Regex pattern
            invert: Invert filter (keep non-matching rows)
            
        Returns:
            Filtered dataframe
        """
        try:
            if column_name not in df.columns:
                raise ValueError(f"Column '{column_name}' not found")
            
            # Validate regex pattern
            try:
                regex = re.compile(pattern, 
                    re.IGNORECASE if not self.config.case_sensitive else 0)
            except re.error as e:
                self.logger.error(f"Invalid regex pattern: {e}")
                raise ValueError(f"Invalid regex pattern: {e}")
            
            # Apply regex filter
            mask = df[column_name].astype(str).str.contains(
                pattern,
                case=self.config.case_sensitive,
                regex=True,
                na=False
            )
            
            if invert:
                mask = ~mask
            
            filtered_df = df[mask].copy()
            
            self.logger.info(
                f"Regex filter applied: {len(filtered_df)} rows matched"
            )
            return filtered_df
        except Exception as e:
            self.logger.error(f"Error applying regex filter: {e}")
            return df.copy()
    
    def apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all active filters to dataframe.
        
        Args:
            df: Input dataframe
            
        Returns:
            Filtered dataframe
        """
        try:
            result_df = df.copy()
            
            for column_name, filter_spec in self.active_filters.items():
                if column_name not in result_df.columns:
                    self.logger.warning(
                        f"Column '{column_name}' not found in dataframe"
                    )
                    continue
                
                operator = filter_spec.get('operator')
                value = filter_spec.get('value')
                
                # Apply appropriate filter based on operator
                if operator == 'eq':
                    result_df = result_df[result_df[column_name] == value]
                
                elif operator == 'ne':
                    result_df = result_df[result_df[column_name] != value]
                
                elif operator == 'gt':
                    result_df = result_df[result_df[column_name] > value]
                
                elif operator == 'lt':
                    result_df = result_df[result_df[column_name] < value]
                
                elif operator == 'gte':
                    result_df = result_df[result_df[column_name] >= value]
                
                elif operator == 'lte':
                    result_df = result_df[result_df[column_name] <= value]
                
                elif operator == 'contains':
                    result_df = result_df[
                        result_df[column_name].astype(str).str.contains(
                            str(value),
                            case=self.config.case_sensitive,
                            na=False
                        )
                    ]
                
                elif operator == 'startswith':
                    result_df = result_df[
                        result_df[column_name].astype(str).str.startswith(
                            str(value),
                            na=False
                        )
                    ]
                
                elif operator == 'endswith':
                    result_df = result_df[
                        result_df[column_name].astype(str).str.endswith(
                            str(value),
                            na=False
                        )
                    ]
                
                elif operator == 'in':
                    if isinstance(value, (list, tuple)):
                        result_df = result_df[result_df[column_name].isin(value)]
                
                elif operator == 'notin':
                    if isinstance(value, (list, tuple)):
                        result_df = result_df[~result_df[column_name].isin(value)]
                
                elif operator == 'date_range':
                    start = filter_spec.get('start_date')
                    end = filter_spec.get('end_date')
                    result_df = result_df[
                        (pd.to_datetime(result_df[column_name]) >= start) &
                        (pd.to_datetime(result_df[column_name]) <= end)
                    ]
            
            self.logger.info(
                f"Filters applied: {len(result_df)} rows remaining "
                f"from {len(df)} total"
            )
            return result_df
        except Exception as e:
            self.logger.error(f"Error applying filters: {e}")
            return df.copy()
    
    def clear_filters(self):
        """Clear all active filters"""
        try:
            self.active_filters.clear()
            self.logger.info("All filters cleared")
        except Exception as e:
            self.logger.error(f"Error clearing filters: {e}")
    
    def remove_filter(self, column_name: str) -> bool:
        """
        Remove a specific filter.
        
        Args:
            column_name: Column to remove filter from
            
        Returns:
            True if successful
        """
        try:
            if column_name in self.active_filters:
                del self.active_filters[column_name]
                self.logger.debug(f"Filter removed for column '{column_name}'")
                return True
            
            self.logger.warning(f"No filter found for column '{column_name}'")
            return False
        except Exception as e:
            self.logger.error(f"Error removing filter: {e}")
            return False
    
    def search_text(self, df: pd.DataFrame, search_term: str,
                   columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Search for text across columns.
        
        Args:
            df: Input dataframe
            search_term: Search term
            columns: Specific columns to search (None = all columns)
            
        Returns:
            Filtered dataframe with matching rows
        """
        try:
            if search_term.strip() == '':
                return df.copy()
            
            # Get columns to search
            if columns is None:
                columns = df.select_dtypes(include=['object']).columns.tolist()
            else:
                # Validate columns exist
                columns = [c for c in columns if c in df.columns]
            
            if not columns:
                self.logger.warning("No valid columns for text search")
                return df.copy()
            
            # Build search mask
            mask = pd.Series([False] * len(df), index=df.index)
            
            for column in columns:
                column_mask = df[column].astype(str).str.contains(
                    search_term,
                    case=self.config.case_sensitive,
                    na=False,
                    regex=self.config.enable_regex_search
                )
                mask = mask | column_mask
            
            result_df = df[mask].copy()
            
            self.logger.info(
                f"Text search '{search_term}' found {len(result_df)} matches"
            )
            return result_df
        except Exception as e:
            self.logger.error(f"Error in text search: {e}")
            return df.copy()
    
    def render_filter_ui(self, df: pd.DataFrame, key_suffix: str = ""):
        """
        Render filter UI controls in Streamlit.
        
        Args:
            df: Dataframe to filter
            key_suffix: Suffix for Streamlit keys
            
        Returns:
            Filtered dataframe
        """
        try:
            st.subheader("🔍 Advanced Filters")
            
            filter_type = st.selectbox(
                "Filter Type",
                ["Simple Search", "Column Filter", "Date Range", "Regex"],
                key=f"filter_type_{key_suffix}"
            )
            
            if filter_type == "Simple Search":
                search_term = st.text_input(
                    "Search term",
                    key=f"search_term_{key_suffix}",
                    placeholder="Search across all columns..."
                )
                
                if search_term:
                    df = self.search_text(df, search_term)
            
            elif filter_type == "Column Filter":
                column = st.selectbox(
                    "Select column",
                    df.columns,
                    key=f"filter_col_{key_suffix}"
                )
                
                operator = st.selectbox(
                    "Operator",
                    ["equals", "contains", "greater than", "less than"],
                    key=f"filter_op_{key_suffix}"
                )
                
                value = st.text_input(
                    "Value",
                    key=f"filter_val_{key_suffix}"
                )
                
                if value:
                    operator_map = {
                        'equals': 'eq',
                        'contains': 'contains',
                        'greater than': 'gt',
                        'less than': 'lt'
                    }
                    self.add_column_filter(
                        column,
                        operator_map.get(operator, 'eq'),
                        value
                    )
                    df = self.apply_filters(df)
            
            elif filter_type == "Date Range":
                date_columns = df.select_dtypes(include=['datetime64']).columns
                
                if len(date_columns) > 0:
                    column = st.selectbox(
                        "Select date column",
                        date_columns,
                        key=f"date_col_{key_suffix}"
                    )
                    
                    start_date = st.date_input(
                        "Start date",
                        key=f"start_date_{key_suffix}"
                    )
                    
                    end_date = st.date_input(
                        "End date",
                        key=f"end_date_{key_suffix}"
                    )
                    
                    if start_date and end_date:
                        self.add_date_range_filter(
                            column,
                            pd.Timestamp(start_date),
                            pd.Timestamp(end_date)
                        )
                        df = self.apply_filters(df)
                else:
                    st.warning("No date columns found in dataframe")
            
            elif filter_type == "Regex":
                column = st.selectbox(
                    "Select column",
                    df.columns,
                    key=f"regex_col_{key_suffix}"
                )
                
                pattern = st.text_input(
                    "Regex pattern",
                    key=f"regex_pattern_{key_suffix}",
                    placeholder="e.g., ^[A-Z].*"
                )
                
                if pattern:
                    try:
                        df = self.apply_regex_filter(df, column, pattern)
                    except ValueError as e:
                        st.error(f"Invalid regex: {e}")
            
            # Display active filters
            if self.active_filters:
                st.info(
                    f"Active filters: {len(self.active_filters)} • "
                    f"Results: {len(df)} rows"
                )
                
                if st.button("Clear all filters", key=f"clear_filters_{key_suffix}"):
                    self.clear_filters()
                    st.rerun()
            
            self.logger.debug("Filter UI rendered")
            return df
        except Exception as e:
            self.logger.error(f"Error rendering filter UI: {e}")
            return df
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """
        Get summary of active filters.
        
        Returns:
            Dictionary with filter summary
        """
        return {
            'filter_count': len(self.active_filters),
            'filters': self.active_filters,
            'regex_enabled': self.config.enable_regex_search,
            'case_sensitive': self.config.case_sensitive
        }


# ============================================================================
# DASHBOARD ENHANCEMENTS INTEGRATION CLASS
# ============================================================================

class DashboardEnhancementsManager:
    """
    Central manager for all dashboard enhancements.
    Integrates all enhancement modules for easy access and configuration.
    """
    
    def __init__(self,
                 mobile_config: Optional[MobileConfig] = None,
                 theme_config: Optional[str] = None,
                 notification_config: Optional[NotificationConfig] = None,
                 refresh_config: Optional[RefreshConfig] = None,
                 filter_config: Optional[FilterConfig] = None):
        """
        Initialize the DashboardEnhancementsManager.
        
        Args:
            mobile_config: MobileConfig instance
            theme_config: Theme name to apply
            notification_config: NotificationConfig instance
            refresh_config: RefreshConfig instance
            filter_config: FilterConfig instance
        """
        self.logger = logging.getLogger(f"{__name__}.DashboardEnhancementsManager")
        
        # Initialize all managers
        self.mobile = MobileOptimizer(mobile_config)
        self.theme = ThemeManager()
        self.notifications = NotificationManager(notification_config)
        self.refresh = DataRefreshManager(refresh_config)
        self.filters = AdvancedFilterManager(filter_config)
        
        # Apply theme if specified
        if theme_config:
            self.theme.apply_theme(theme_config)
        
        self.logger.info("DashboardEnhancementsManager initialized")
    
    def initialize_all(self):
        """Initialize all enhancements"""
        try:
            # Apply mobile optimizations
            self.mobile.render_mobile_css()
            
            # Apply theme
            if self.theme.current_theme:
                st.markdown(
                    self.theme.generate_theme_css(),
                    unsafe_allow_html=True
                )
            
            self.logger.info("All enhancements initialized")
        except Exception as e:
            self.logger.error(f"Error initializing enhancements: {e}")
    
    def render_settings_panel(self, key_suffix: str = ""):
        """
        Render settings panel for all enhancements.
        
        Args:
            key_suffix: Suffix for Streamlit keys
        """
        try:
            st.sidebar.header("⚙️ Enhancement Settings")
            
            # Theme selector
            with st.sidebar.expander("🎨 Theme Settings"):
                themes = self.theme.get_available_themes()
                selected_theme = st.selectbox(
                    "Select Theme",
                    themes,
                    key=f"theme_select_{key_suffix}"
                )
                
                if st.button("Apply Theme", key=f"apply_theme_{key_suffix}"):
                    self.theme.apply_theme(selected_theme)
                    st.success(f"Theme '{selected_theme}' applied!")
            
            # Notification settings
            with st.sidebar.expander("🔔 Notification Settings"):
                st.selectbox(
                    "Notification Channel",
                    [nc.value for nc in NotificationChannel],
                    key=f"notif_channel_{key_suffix}"
                )
                
                webhook_url = st.text_input(
                    "Webhook URL",
                    value=self.notifications.config.webhook_url or "",
                    type="password",
                    key=f"webhook_url_{key_suffix}"
                )
                
                if webhook_url and webhook_url != self.notifications.config.webhook_url:
                    self.notifications.config.webhook_url = webhook_url
                    st.success("Webhook URL updated!")
                
                st.toggle(
                    "Enable Notifications",
                    value=self.notifications.config.enabled,
                    key=f"notif_enabled_{key_suffix}",
                    on_change=lambda: setattr(
                        self.notifications.config,
                        'enabled',
                        st.session_state.get(f"notif_enabled_{key_suffix}", True)
                    )
                )
            
            # Refresh settings
            with st.sidebar.expander("🔄 Refresh Settings"):
                self.refresh.render_refresh_controls(key_suffix)
            
            # Mobile settings
            with st.sidebar.expander("📱 Mobile Settings"):
                st.toggle(
                    "Enable Mobile Optimizations",
                    value=self.mobile.config.enabled,
                    key=f"mobile_enabled_{key_suffix}"
                )
                
                st.number_input(
                    "Touch Target Size (px)",
                    min_value=32,
                    max_value=64,
                    value=self.mobile.config.touch_target_size,
                    step=4,
                    key=f"touch_size_{key_suffix}"
                )
        except Exception as e:
            self.logger.error(f"Error rendering settings panel: {e}")
    
    def get_status_report(self) -> Dict[str, Any]:
        """
        Get comprehensive status report of all enhancements.
        
        Returns:
            Status dictionary
        """
        try:
            return {
                'mobile': {
                    'enabled': self.mobile.config.enabled,
                    'responsive': True,
                    'touch_friendly': True
                },
                'theme': {
                    'current': (
                        self.theme.current_theme.name
                        if self.theme.current_theme else None
                    ),
                    'available': self.theme.get_available_themes(),
                    'theme_type': (
                        self.theme.current_theme.theme_type.value
                        if self.theme.current_theme else None
                    )
                },
                'notifications': self.notifications.get_status(),
                'refresh': self.refresh.get_refresh_statistics(),
                'filters': self.filters.get_filter_summary()
            }
        except Exception as e:
            self.logger.error(f"Error generating status report: {e}")
            return {}
    
    def export_configuration(self, filepath: str):
        """
        Export all configuration to JSON file.
        
        Args:
            filepath: Path to save configuration
        """
        try:
            config = {
                'mobile': self.mobile.config.__dict__,
                'theme': (
                    self.theme.current_theme.to_dict()
                    if self.theme.current_theme else None
                ),
                'notifications': {
                    'channel': self.notifications.config.channel.value,
                    'enabled': self.notifications.config.enabled,
                    'retry_attempts': self.notifications.config.retry_attempts
                },
                'refresh': {
                    'enabled': self.refresh.config.enabled,
                    'interval_seconds': self.refresh.config.interval_seconds
                },
                'filters': {
                    'enable_regex': self.filters.config.enable_regex_search,
                    'case_sensitive': self.filters.config.case_sensitive
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            
            self.logger.info(f"Configuration exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            raise


# ============================================================================
# UTILITY FUNCTIONS & EXAMPLES
# ============================================================================

def create_default_enhancements() -> DashboardEnhancementsManager:
    """
    Create a DashboardEnhancementsManager with default configurations.
    
    Returns:
        Configured DashboardEnhancementsManager instance
    """
    try:
        manager = DashboardEnhancementsManager(
            mobile_config=MobileConfig(enabled=True),
            theme_config='light',
            notification_config=NotificationConfig(
                channel=NotificationChannel.WEBHOOK,
                enabled=True
            ),
            refresh_config=RefreshConfig(
                enabled=True,
                interval_seconds=300
            ),
            filter_config=FilterConfig(
                enable_regex_search=True,
                enable_date_range_filter=True,
                enable_multi_column_filter=True
            )
        )
        return manager
    except Exception as e:
        logger.error(f"Error creating default enhancements: {e}")
        raise


# ============================================================================
# EXAMPLE USAGE FUNCTIONS
# ============================================================================

def example_mobile_optimization():
    """Example: Mobile optimization usage"""
    print("=" * 60)
    print("EXAMPLE: Mobile Optimization")
    print("=" * 60)
    
    mobile = MobileOptimizer()
    
    # Get responsive CSS
    css = mobile.generate_responsive_css()
    print("✓ Generated responsive CSS")
    print(f"  CSS length: {len(css)} characters")
    
    # Get viewport meta tag
    meta = mobile.generate_viewport_meta()
    print("✓ Generated viewport meta tag")
    
    # Apply optimizations
    optimizations = mobile.apply_mobile_optimizations()
    print("✓ Applied mobile optimizations:")
    for key, value in optimizations.items():
        if key != 'responsive_css':
            print(f"  - {key}: {value}")


def example_theme_management():
    """Example: Theme management usage"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Theme Management")
    print("=" * 60)
    
    theme_manager = ThemeManager()
    
    # Get available themes
    themes = theme_manager.get_available_themes()
    print(f"✓ Available themes: {themes}")
    
    # Set and apply theme
    theme_manager.set_current_theme('dark')
    print("✓ Dark theme applied")
    
    # Generate color palette
    palette = theme_manager.generate_color_palette()
    print(f"✓ Generated color palette: {len(palette)} colors")
    for i, color in enumerate(palette, 1):
        print(f"  {i}. {color}")
    
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
    print("✓ Custom 'Ocean Wave' theme added")


def example_notifications():
    """Example: Notification usage"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Slack/Teams Notifications")
    print("=" * 60)
    
    # Slack configuration
    slack_notifier = NotificationManager()
    
    print("✓ Slack integration example:")
    print("  slack_notifier.configure_slack('https://hooks.slack.com/...')")
    
    # Build notification payload
    payload = slack_notifier.build_slack_message(
        title="📊 Report Ready",
        message="Your data analysis report is ready for review",
        fields={
            'Dataset': 'Academic Q4 2024',
            'Rows Processed': '15,000',
            'Accuracy': '98%'
        }
    )
    print("✓ Slack message payload built")
    print(f"  Payload keys: {list(payload.keys())}")
    
    # Teams configuration
    print("\n✓ Teams integration example:")
    print("  teams_notifier.configure_teams('https://outlook.webhook.office.com/...')")
    
    # Build Teams notification
    teams_payload = slack_notifier.build_teams_message(
        title="✅ Processing Complete",
        message="Data processing completed successfully",
        facts={'Status': 'Success', 'Duration': '2m 45s'}
    )
    print("✓ Teams message payload built")
    print(f"  Payload type: {teams_payload.get('@type')}")


def example_data_refresh():
    """Example: Data refresh usage"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Data Refresh Management")
    print("=" * 60)
    
    refresh_manager = DataRefreshManager()
    
    # Set refresh interval
    refresh_manager.set_refresh_interval(300)
    print("✓ Refresh interval set to 5 minutes")
    
    # Register callback
    def on_refresh():
        print("  → Data refreshed!")
    
    refresh_manager.register_refresh_callback(on_refresh)
    print("✓ Refresh callback registered")
    
    # Check refresh status
    stats = refresh_manager.get_refresh_statistics()
    print("✓ Refresh statistics:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")


def example_advanced_filters():
    """Example: Advanced filtering usage"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Advanced Filtering")
    print("=" * 60)
    
    filter_manager = AdvancedFilterManager()
    
    # Create sample data
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'Age': [25, 30, 35, 28, 32],
        'Department': ['Sales', 'IT', 'HR', 'Sales', 'IT'],
        'Date': pd.date_range('2024-01-01', periods=5)
    }
    df = pd.DataFrame(data)
    
    print("✓ Sample dataframe created with 5 rows")
    
    # Add filters
    filter_manager.add_column_filter('Department', 'eq', 'IT')
    print("✓ Added filter: Department = IT")
    
    # Apply filters
    filtered_df = filter_manager.apply_filters(df)
    print(f"✓ Filter applied: {len(filtered_df)} rows match criteria")
    
    # Text search
    search_results = filter_manager.search_text(df, 'Sale')
    print(f"✓ Text search for 'Sale': {len(search_results)} results")
    
    # Regex filter
    regex_results = filter_manager.apply_regex_filter(
        df, 'Name', '^[A-C]'
    )
    print(f"✓ Regex filter '^[A-C]': {len(regex_results)} results")


def run_all_examples():
    """Run all example functions"""
    print("\n" + "=" * 60)
    print("DASHBOARD ENHANCEMENTS - COMPREHENSIVE EXAMPLES")
    print("=" * 60)
    
    try:
        example_mobile_optimization()
        example_theme_management()
        example_notifications()
        example_data_refresh()
        example_advanced_filters()
        
        print("\n" + "=" * 60)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """Run examples when module is executed directly"""
    run_all_examples()
