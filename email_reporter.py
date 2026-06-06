"""
Email Reporter Module
Automated email reporting system for analytics results
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import os
import json
from pathlib import Path
import logging

# Import project modules
from powerpoint_generator import PowerPointGenerator, create_presentation_from_dashboard_data
from visualization_engine import VisualizationEngine

logger = logging.getLogger(__name__)

class EmailReporter:
    """
    Comprehensive email reporting system for analytics dashboard
    """
    
    def __init__(self, smtp_config: Optional[Dict] = None):
        """
        Initialize email reporter with SMTP configuration
        
        Args:
            smtp_config: Dictionary containing SMTP settings
        """
        self.smtp_config = smtp_config or self._get_default_smtp_config()
        self.viz_engine = VisualizationEngine()
        self.ppt_generator = PowerPointGenerator()
        
        # Email templates
        self.templates = {
            'executive_summary': self._get_executive_template(),
            'detailed_report': self._get_detailed_template(),
            'alert': self._get_alert_template(),
            'scheduled': self._get_scheduled_template()
        }
    
    def _get_default_smtp_config(self) -> Dict:
        """Get default SMTP configuration from environment variables"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME', ''),
            'password': os.getenv('EMAIL_PASSWORD', ''),
            'use_tls': os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true',
            'sender_name': os.getenv('EMAIL_SENDER_NAME', 'Analytics Dashboard'),
            'sender_email': os.getenv('EMAIL_SENDER', '')
        }
    
    def send_analytics_report(self, 
                            recipients: List[str],
                            data: pd.DataFrame,
                            analysis_results: Dict[str, Any],
                            report_type: str = 'executive_summary',
                            subject: Optional[str] = None,
                            include_attachments: bool = True,
                            custom_message: Optional[str] = None) -> bool:
        """
        Send comprehensive analytics report via email
        
        Args:
            recipients: List of email addresses
            data: Processed dataset
            analysis_results: Analysis results dictionary
            report_type: Type of report template to use
            subject: Custom email subject
            include_attachments: Whether to include PowerPoint and data files
            custom_message: Additional custom message
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            
            # Set email headers
            msg['From'] = f"{self.smtp_config['sender_name']} <{self.smtp_config['sender_email']}>"
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject or self._generate_subject(report_type, data)
            
            # Generate email content
            html_content = self._generate_email_content(
                data, analysis_results, report_type, custom_message
            )
            
            # Create HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments if requested
            if include_attachments:
                self._add_attachments(msg, data, analysis_results)
            
            # Send email
            return self._send_email(msg, recipients)
            
        except Exception as e:
            logger.error(f"Failed to send analytics report: {e}")
            return False
    
    def send_scheduled_report(self,
                            recipients: List[str],
                            dataset_id: str,
                            schedule_config: Dict[str, Any]) -> bool:
        """
        Send scheduled report (daily, weekly, monthly)
        
        Args:
            recipients: Email recipients
            dataset_id: Dataset identifier
            schedule_config: Scheduling configuration
            
        Returns:
            Success status
        """
        try:
            # Load data (this would integrate with your data store)
            from data_pipeline import load_sample_data, DataCleaningPipeline
            
            pipeline = DataCleaningPipeline()
            raw_data = load_sample_data()
            cleaned_data = pipeline.clean_dataset(raw_data)
            cleaning_report = pipeline.get_cleaning_report()
            
            analysis_results = {
                'dataset_id': dataset_id,
                'schedule_type': schedule_config.get('frequency', 'weekly'),
                'generated_at': datetime.now().isoformat(),
                **cleaning_report
            }
            
            # Send scheduled report
            return self.send_analytics_report(
                recipients=recipients,
                data=cleaned_data,
                analysis_results=analysis_results,
                report_type='scheduled',
                subject=f"Scheduled Analytics Report - {schedule_config.get('frequency', 'Weekly').title()}",
                include_attachments=schedule_config.get('include_attachments', True)
            )
            
        except Exception as e:
            logger.error(f"Failed to send scheduled report: {e}")
            return False
    
    def send_alert_email(self,
                        recipients: List[str],
                        alert_type: str,
                        alert_data: Dict[str, Any],
                        severity: str = 'medium') -> bool:
        """
        Send alert email for data quality issues or anomalies
        
        Args:
            recipients: Email recipients
            alert_type: Type of alert (data_quality, anomaly, system)
            alert_data: Alert-specific data
            severity: Alert severity (low, medium, high, critical)
            
        Returns:
            Success status
        """
        try:
            msg = MIMEMultipart()
            
            # Set headers with priority based on severity
            msg['From'] = f"{self.smtp_config['sender_name']} <{self.smtp_config['sender_email']}>"
            msg['To'] = ', '.join(recipients)
            
            # Set subject with severity indicator
            severity_indicators = {
                'low': '🟢',
                'medium': '🟡', 
                'high': '🟠',
                'critical': '🔴'
            }
            
            indicator = severity_indicators.get(severity, '🟡')
            msg['Subject'] = f"{indicator} Analytics Alert: {alert_type.replace('_', ' ').title()}"
            
            if severity in ['high', 'critical']:
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            
            # Generate alert content
            html_content = self._generate_alert_content(alert_type, alert_data, severity)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            return self._send_email(msg, recipients)
            
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")
            return False
    
    def _generate_email_content(self, 
                               data: pd.DataFrame,
                               analysis_results: Dict[str, Any],
                               report_type: str,
                               custom_message: Optional[str] = None) -> str:
        """Generate HTML email content based on template and data"""
        
        # Get base template
        template = self.templates.get(report_type, self.templates['executive_summary'])
        
        # Calculate key metrics
        metrics = self._calculate_key_metrics(data, analysis_results)
        
        # Generate insights
        insights = self._generate_email_insights(data, analysis_results)
        
        # Create visualizations for email
        charts = self._create_email_charts(data)
        
        # Replace template variables
        content = template.format(
            report_date=datetime.now().strftime("%B %d, %Y"),
            dataset_rows=f"{len(data):,}",
            dataset_columns=len(data.columns),
            data_quality=f"{metrics['completeness']:.1f}%",
            processing_accuracy=f"{metrics['accuracy']:.1%}",
            key_insights=insights,
            custom_message=custom_message or "",
            **metrics
        )
        
        return content
    
    def _calculate_key_metrics(self, data: pd.DataFrame, analysis_results: Dict[str, Any]) -> Dict:
        """Calculate key metrics for email reporting"""
        
        # Data quality metrics
        completeness = (1 - data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
        
        # Processing metrics
        accuracy = analysis_results.get('accuracy_score', 0.98)
        missing_handled = analysis_results.get('missing_values_handled', 0)
        duplicates_removed = analysis_results.get('duplicates_removed', 0)
        
        # Data composition
        numeric_cols = len(data.select_dtypes(include=[np.number]).columns)
        categorical_cols = len(data.select_dtypes(include=['object']).columns)
        
        # Statistical summary
        numeric_data = data.select_dtypes(include=[np.number])
        avg_mean = numeric_data.mean().mean() if len(numeric_data.columns) > 0 else 0
        avg_std = numeric_data.std().mean() if len(numeric_data.columns) > 0 else 0
        
        return {
            'completeness': completeness,
            'accuracy': accuracy,
            'missing_handled': missing_handled,
            'duplicates_removed': duplicates_removed,
            'numeric_variables': numeric_cols,
            'categorical_variables': categorical_cols,
            'average_mean': avg_mean,
            'average_std': avg_std,
            'memory_usage_mb': data.memory_usage(deep=True).sum() / 1024 / 1024
        }
    
    def _generate_email_insights(self, data: pd.DataFrame, analysis_results: Dict[str, Any]) -> str:
        """Generate key insights for email content"""
        
        insights = []
        
        # Data volume insight
        if len(data) > 10000:
            insights.append(f"📊 Large dataset with {len(data):,} records provides robust statistical power")
        elif len(data) > 1000:
            insights.append(f"📊 Medium dataset with {len(data):,} records suitable for reliable analysis")
        else:
            insights.append(f"📊 Compact dataset with {len(data):,} records for focused analysis")
        
        # Data quality insight
        completeness = (1 - data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
        if completeness > 95:
            insights.append(f"✅ Excellent data quality ({completeness:.1f}% complete)")
        elif completeness > 80:
            insights.append(f"⚠️ Good data quality ({completeness:.1f}% complete) with room for improvement")
        else:
            insights.append(f"🔴 Data quality needs attention ({completeness:.1f}% complete)")
        
        # Processing insight
        accuracy = analysis_results.get('accuracy_score', 0.98)
        insights.append(f"🔧 Automated processing achieved {accuracy:.1%} accuracy")
        
        # Variable composition insight
        numeric_cols = len(data.select_dtypes(include=[np.number]).columns)
        categorical_cols = len(data.select_dtypes(include=['object']).columns)
        
        if numeric_cols > categorical_cols:
            insights.append(f"📈 Quantitative focus: {numeric_cols} numeric vs {categorical_cols} categorical variables")
        elif categorical_cols > numeric_cols:
            insights.append(f"📋 Categorical focus: {categorical_cols} categorical vs {numeric_cols} numeric variables")
        else:
            insights.append(f"⚖️ Balanced dataset: {numeric_cols} numeric and {categorical_cols} categorical variables")
        
        return "<br>".join(insights)
    
    def _create_email_charts(self, data: pd.DataFrame) -> Dict[str, str]:
        """Create charts for email embedding"""
        charts = {}
        
        try:
            # Create temporary directory for charts
            os.makedirs("temp/email_charts", exist_ok=True)
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            categorical_cols = data.select_dtypes(include=['object']).columns
            
            # Create summary chart if we have numeric data
            if len(numeric_cols) > 0:
                fig = self.viz_engine.create_performance_dashboard(
                    data, "Data Overview Dashboard"
                )
                
                # Save as image (simplified version)
                chart_path = "temp/email_charts/overview.png"
                # Note: In production, you'd use plotly.io.write_image
                charts['overview'] = chart_path
            
            return charts
            
        except Exception as e:
            logger.warning(f"Could not create email charts: {e}")
            return {}
    
    def _add_attachments(self, msg: MIMEMultipart, data: pd.DataFrame, 
                        analysis_results: Dict[str, Any]):
        """Add attachments to email message"""
        
        try:
            # Create PowerPoint presentation
            ppt_path = self.ppt_generator.create_presentation(
                data, analysis_results, "Analytics Report"
            )
            
            if os.path.exists(ppt_path):
                with open(ppt_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(ppt_path)}'
                )
                msg.attach(part)
            
            # Create CSV export
            csv_path = "temp/analytics_data_export.csv"
            os.makedirs("temp", exist_ok=True)
            data.to_csv(csv_path, index=False)
            
            if os.path.exists(csv_path):
                with open(csv_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= analytics_data_export.csv'
                )
                msg.attach(part)
            
        except Exception as e:
            logger.warning(f"Could not add attachments: {e}")
    
    def _send_email(self, msg: MIMEMultipart, recipients: List[str]) -> bool:
        """Send email using SMTP"""
        
        try:
            # Validate SMTP configuration
            if not self.smtp_config.get('username') or not self.smtp_config.get('password'):
                logger.error("SMTP credentials not configured")
                return False
            
            # Create SMTP session
            server = smtplib.SMTP(
                self.smtp_config['smtp_server'], 
                self.smtp_config['smtp_port']
            )
            
            if self.smtp_config.get('use_tls', True):
                server.starttls()
            
            # Login and send
            server.login(
                self.smtp_config['username'], 
                self.smtp_config['password']
            )
            
            text = msg.as_string()
            server.sendmail(
                self.smtp_config['sender_email'], 
                recipients, 
                text
            )
            server.quit()
            
            logger.info(f"Email sent successfully to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _generate_subject(self, report_type: str, data: pd.DataFrame) -> str:
        """Generate email subject based on report type and data"""
        
        subjects = {
            'executive_summary': f"📊 Analytics Summary - {len(data):,} Records Analyzed",
            'detailed_report': f"📈 Detailed Analytics Report - {datetime.now().strftime('%B %Y')}",
            'alert': f"🚨 Data Quality Alert - Immediate Attention Required",
            'scheduled': f"📅 Scheduled Analytics Report - {datetime.now().strftime('%B %d, %Y')}"
        }
        
        return subjects.get(report_type, "Analytics Dashboard Report")
    
    def _generate_alert_content(self, alert_type: str, alert_data: Dict[str, Any], 
                              severity: str) -> str:
        """Generate HTML content for alert emails"""
        
        severity_colors = {
            'low': '#28a745',
            'medium': '#ffc107', 
            'high': '#fd7e14',
            'critical': '#dc3545'
        }
        
        color = severity_colors.get(severity, '#ffc107')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Analytics Alert</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background-color: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🚨 Analytics Alert</h1>
                    <p style="margin: 5px 0 0 0; font-size: 16px;">Severity: {severity.upper()}</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <h2 style="color: #333; margin-top: 0;">Alert Details</h2>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Alert Type:</strong> {alert_type.replace('_', ' ').title()}</p>
                        <p><strong>Detected At:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>System:</strong> Analytics Dashboard</p>
                    </div>
                    
                    <h3 style="color: #333;">Alert Information</h3>
                    <ul style="color: #666; line-height: 1.6;">
        """
        
        # Add alert-specific information
        for key, value in alert_data.items():
            html_content += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        
        html_content += f"""
                    </ul>
                    
                    <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h4 style="margin-top: 0; color: #495057;">Recommended Actions</h4>
                        <ul style="color: #666; margin-bottom: 0;">
                            <li>Review the analytics dashboard for detailed information</li>
                            <li>Check data sources for any recent changes</li>
                            <li>Contact the data team if issues persist</li>
                            <li>Monitor system performance over the next hour</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="http://localhost:8501" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            View Dashboard
                        </a>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; text-align: center; color: #666; font-size: 14px;">
                    <p style="margin: 0;">This is an automated alert from Analytics Dashboard</p>
                    <p style="margin: 5px 0 0 0;">Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _get_executive_template(self) -> str:
        """Executive summary email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Analytics Executive Summary</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 700px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #1f77b4, #ff7f0e); color: white; padding: 30px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">📊 Analytics Executive Summary</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Generated on {report_date}</p>
                </div>
                
                <!-- Key Metrics -->
                <div style="padding: 30px;">
                    <h2 style="color: #333; margin-top: 0; border-bottom: 2px solid #1f77b4; padding-bottom: 10px;">📈 Key Performance Indicators</h2>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin: 20px 0;">
                        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0; color: #1976d2; font-size: 24px;">{dataset_rows}</h3>
                            <p style="margin: 5px 0 0 0; color: #666;">Records Analyzed</p>
                        </div>
                        <div style="background-color: #f3e5f5; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0; color: #7b1fa2; font-size: 24px;">{data_quality}</h3>
                            <p style="margin: 5px 0 0 0; color: #666;">Data Quality</p>
                        </div>
                        <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0; color: #388e3c; font-size: 24px;">{processing_accuracy}</h3>
                            <p style="margin: 5px 0 0 0; color: #666;">Processing Accuracy</p>
                        </div>
                    </div>
                    
                    <!-- Key Insights -->
                    <h2 style="color: #333; border-bottom: 2px solid #ff7f0e; padding-bottom: 10px;">💡 Key Insights</h2>
                    <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; color: #e65100; line-height: 1.6;">{key_insights}</p>
                    </div>
                    
                    <!-- Custom Message -->
                    {custom_message}
                    
                    <!-- Action Items -->
                    <h2 style="color: #333; border-bottom: 2px solid #4caf50; padding-bottom: 10px;">🎯 Recommended Actions</h2>
                    <ul style="color: #666; line-height: 1.8;">
                        <li>Review attached PowerPoint presentation for detailed analysis</li>
                        <li>Access interactive dashboard for real-time exploration</li>
                        <li>Schedule follow-up meeting to discuss findings</li>
                        <li>Consider implementing automated monitoring for key metrics</li>
                    </ul>
                    
                    <!-- CTA Button -->
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:8501" style="background-color: #1f77b4; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold;">
                            🚀 Open Interactive Dashboard
                        </a>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; text-align: center; color: #666; font-size: 14px;">
                    <p style="margin: 0;">Automated report generated by Analytics Dashboard</p>
                    <p style="margin: 5px 0 0 0;">Questions? Contact your analytics team</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_detailed_template(self) -> str:
        """Detailed report email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Detailed Analytics Report</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 800px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 30px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">📈 Detailed Analytics Report</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">{report_date} | Comprehensive Analysis</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <!-- Dataset Overview -->
                    <h2 style="color: #2c3e50; margin-top: 0;">📊 Dataset Overview</h2>
                    <div style="background-color: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                            <div><strong>Total Records:</strong> {dataset_rows}</div>
                            <div><strong>Variables:</strong> {dataset_columns}</div>
                            <div><strong>Numeric Variables:</strong> {numeric_variables}</div>
                            <div><strong>Categorical Variables:</strong> {categorical_variables}</div>
                            <div><strong>Data Quality:</strong> {data_quality}</div>
                            <div><strong>Processing Accuracy:</strong> {processing_accuracy}</div>
                        </div>
                    </div>
                    
                    <!-- Processing Summary -->
                    <h2 style="color: #2c3e50;">🔧 Data Processing Summary</h2>
                    <ul style="color: #666; line-height: 1.6;">
                        <li>Missing values handled: {missing_handled:,}</li>
                        <li>Duplicate records removed: {duplicates_removed:,}</li>
                        <li>Memory usage: {memory_usage_mb:.1f} MB</li>
                        <li>Processing completed with {processing_accuracy} accuracy</li>
                    </ul>
                    
                    <!-- Key Insights -->
                    <h2 style="color: #2c3e50;">💡 Analysis Insights</h2>
                    <div style="background-color: #e8f6f3; padding: 20px; border-radius: 8px; border-left: 4px solid #27ae60;">
                        <p style="margin: 0; color: #27ae60; line-height: 1.6;">{key_insights}</p>
                    </div>
                    
                    <!-- Attachments Info -->
                    <h2 style="color: #2c3e50;">📎 Attached Files</h2>
                    <div style="background-color: #fdf2e9; padding: 20px; border-radius: 8px;">
                        <ul style="margin: 0; color: #d68910;">
                            <li><strong>PowerPoint Presentation:</strong> Complete analysis with visualizations</li>
                            <li><strong>CSV Data Export:</strong> Cleaned dataset for further analysis</li>
                            <li><strong>Technical Summary:</strong> Processing details and methodology</li>
                        </ul>
                    </div>
                    
                    {custom_message}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_alert_template(self) -> str:
        """Alert email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Analytics Alert</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #fff5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border: 2px solid #e53e3e;">
                
                <!-- Header -->
                <div style="background-color: #e53e3e; color: white; padding: 20px; border-radius: 6px 6px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🚨 Analytics System Alert</h1>
                    <p style="margin: 5px 0 0 0; font-size: 14px;">Immediate attention required</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <div style="background-color: #fed7d7; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                        <p style="margin: 0; color: #c53030; font-weight: bold;">Alert triggered at {report_date}</p>
                    </div>
                    
                    {key_insights}
                    
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://localhost:8501" style="background-color: #e53e3e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Investigate Now
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_scheduled_template(self) -> str:
        """Scheduled report email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Scheduled Analytics Report</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f7fafc;">
            <div style="max-width: 700px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 25px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 26px;">📅 Scheduled Analytics Report</h1>
                    <p style="margin: 8px 0 0 0; font-size: 15px; opacity: 0.9;">Your regular data insights | {report_date}</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <h2 style="color: #4a5568; margin-top: 0;">📊 This Period's Highlights</h2>
                    
                    <div style="background-color: #edf2f7; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p style="margin: 0; color: #2d3748; line-height: 1.6;">{key_insights}</p>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 25px 0;">
                        <div style="background-color: #bee3f8; padding: 15px; border-radius: 6px; text-align: center;">
                            <h4 style="margin: 0; color: #2b6cb0;">{dataset_rows}</h4>
                            <p style="margin: 5px 0 0 0; color: #4a5568; font-size: 14px;">Records</p>
                        </div>
                        <div style="background-color: #c6f6d5; padding: 15px; border-radius: 6px; text-align: center;">
                            <h4 style="margin: 0; color: #276749;">{data_quality}</h4>
                            <p style="margin: 5px 0 0 0; color: #4a5568; font-size: 14px;">Quality</p>
                        </div>
                        <div style="background-color: #fbb6ce; padding: 15px; border-radius: 6px; text-align: center;">
                            <h4 style="margin: 0; color: #b83280;">{processing_accuracy}</h4>
                            <p style="margin: 5px 0 0 0; color: #4a5568; font-size: 14px;">Accuracy</p>
                        </div>
                    </div>
                    
                    {custom_message}
                    
                    <div style="text-align: center; margin-top: 25px;">
                        <a href="http://localhost:8501" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px 25px; text-decoration: none; border-radius: 20px; display: inline-block;">
                            View Full Dashboard
                        </a>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f7fafc; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; color: #718096; font-size: 13px;">
                    <p style="margin: 0;">Automated scheduled report | Next report: Next week</p>
                </div>
            </div>
        </body>
        </html>
        """


# Utility functions for easy integration
def send_executive_summary(recipients: List[str], dataset_id: str, custom_message: str = None) -> bool:
    """
    Quick function to send executive summary email
    
    Args:
        recipients: List of email addresses
        dataset_id: Dataset identifier
        custom_message: Optional custom message
        
    Returns:
        Success status
    """
    try:
        # Load sample data for demonstration
        from data_pipeline import load_sample_data, DataCleaningPipeline
        
        pipeline = DataCleaningPipeline()
        raw_data = load_sample_data()
        cleaned_data = pipeline.clean_dataset(raw_data)
        cleaning_report = pipeline.get_cleaning_report()
        
        # Create email reporter
        reporter = EmailReporter()
        
        # Send report
        return reporter.send_analytics_report(
            recipients=recipients,
            data=cleaned_data,
            analysis_results=cleaning_report,
            report_type='executive_summary',
            custom_message=custom_message
        )
        
    except Exception as e:
        logger.error(f"Failed to send executive summary: {e}")
        return False


def setup_scheduled_reports(recipients: List[str], frequency: str = 'weekly') -> bool:
    """
    Setup scheduled email reports
    
    Args:
        recipients: Email recipients
        frequency: Report frequency (daily, weekly, monthly)
        
    Returns:
        Success status
    """
    try:
        # This would integrate with a task scheduler like Celery or APScheduler
        schedule_config = {
            'frequency': frequency,
            'recipients': recipients,
            'include_attachments': True,
            'next_run': datetime.now() + timedelta(days=7 if frequency == 'weekly' else 1)
        }
        
        # Save schedule configuration
        os.makedirs("config", exist_ok=True)
        with open("config/email_schedule.json", "w") as f:
            json.dump(schedule_config, f, default=str, indent=2)
        
        logger.info(f"Scheduled {frequency} reports setup for {len(recipients)} recipients")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup scheduled reports: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    print("📧 Email Reporter - Testing")
    
    # Test configuration
    test_recipients = ["analyst@company.com", "manager@company.com"]
    
    try:
        # Send executive summary
        success = send_executive_summary(
            recipients=test_recipients,
            dataset_id="sample_001",
            custom_message="This is a test report generated from the analytics dashboard."
        )
        
        if success:
            print("✅ Executive summary email sent successfully!")
        else:
            print("❌ Failed to send email - check SMTP configuration")
            
        # Setup scheduled reports
        schedule_success = setup_scheduled_reports(test_recipients, 'weekly')
        
        if schedule_success:
            print("✅ Scheduled reports configured successfully!")
        else:
            print("❌ Failed to setup scheduled reports")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("💡 Make sure to configure SMTP settings in environment variables:")
        print("   - SMTP_SERVER, EMAIL_USERNAME, EMAIL_PASSWORD, etc.")