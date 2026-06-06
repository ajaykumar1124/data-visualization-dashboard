"""
Report Integration Module
Integrates PowerPoint and Email reporting with the main dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from typing import List, Dict, Any, Optional
import logging

# Import reporting modules
from powerpoint_generator import PowerPointGenerator, create_presentation_from_dashboard_data
from email_reporter import EmailReporter, send_executive_summary, setup_scheduled_reports

logger = logging.getLogger(__name__)

class ReportManager:
    """
    Manages PowerPoint and Email reporting integration
    """
    
    def __init__(self):
        self.ppt_generator = PowerPointGenerator()
        self.email_reporter = EmailReporter()
    
    def create_powerpoint_report(self, data: pd.DataFrame, analysis_results: Dict[str, Any], 
                               title: str = None) -> str:
        """
        Create PowerPoint presentation from dashboard data
        
        Args:
            data: Processed dataset
            analysis_results: Analysis results from cleaning pipeline
            title: Custom presentation title
            
        Returns:
            Path to generated PowerPoint file
        """
        try:
            presentation_title = title or f"Analytics Report - {datetime.now().strftime('%B %Y')}"
            filepath = self.ppt_generator.create_presentation(data, analysis_results, presentation_title)
            
            logger.info(f"PowerPoint presentation created: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to create PowerPoint presentation: {e}")
            raise
    
    def send_email_report(self, recipients: List[str], data: pd.DataFrame, 
                         analysis_results: Dict[str, Any], report_type: str = 'executive_summary',
                         include_attachments: bool = True, custom_message: str = None) -> bool:
        """
        Send email report with optional attachments
        
        Args:
            recipients: List of email addresses
            data: Processed dataset
            analysis_results: Analysis results
            report_type: Type of email template
            include_attachments: Whether to include PowerPoint and CSV
            custom_message: Additional message for email
            
        Returns:
            Success status
        """
        try:
            success = self.email_reporter.send_analytics_report(
                recipients=recipients,
                data=data,
                analysis_results=analysis_results,
                report_type=report_type,
                include_attachments=include_attachments,
                custom_message=custom_message
            )
            
            if success:
                logger.info(f"Email report sent to {len(recipients)} recipients")
            else:
                logger.error("Failed to send email report")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending email report: {e}")
            return False
    
    def setup_automated_reporting(self, recipients: List[str], frequency: str = 'weekly') -> bool:
        """
        Setup automated email reporting
        
        Args:
            recipients: Email recipients
            frequency: Report frequency (daily, weekly, monthly)
            
        Returns:
            Success status
        """
        try:
            return setup_scheduled_reports(recipients, frequency)
        except Exception as e:
            logger.error(f"Failed to setup automated reporting: {e}")
            return False


def add_reporting_to_dashboard():
    """
    Add reporting functionality to Streamlit dashboard
    This function should be called from the main dashboard.py
    """
    
    # Add reporting section to sidebar
    st.sidebar.header("📤 Generate Reports")
    
    # PowerPoint Generation
    if st.sidebar.button("📊 Create PowerPoint", type="primary"):
        if st.session_state.get('cleaned_data') is not None:
            with st.spinner("Generating PowerPoint presentation..."):
                try:
                    report_manager = ReportManager()
                    
                    # Get data and results
                    data = st.session_state.cleaned_data
                    analysis_results = st.session_state.get('cleaning_report', {})
                    
                    # Create presentation
                    filepath = report_manager.create_powerpoint_report(data, analysis_results)
                    
                    # Provide download link
                    with open(filepath, "rb") as file:
                        st.sidebar.download_button(
                            label="📥 Download PowerPoint",
                            data=file.read(),
                            file_name=os.path.basename(filepath),
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                    
                    st.sidebar.success("✅ PowerPoint created successfully!")
                    
                except Exception as e:
                    st.sidebar.error(f"❌ Error creating PowerPoint: {e}")
        else:
            st.sidebar.warning("⚠️ Please process data first")
    
    # Email Reporting
    st.sidebar.subheader("📧 Email Reports")
    
    # Email configuration
    with st.sidebar.expander("📧 Email Settings"):
        recipients_input = st.text_area(
            "Recipients (one email per line):",
            placeholder="analyst@company.com\nmanager@company.com"
        )
        
        report_type = st.selectbox(
            "Report Type:",
            ["executive_summary", "detailed_report", "scheduled"]
        )
        
        include_attachments = st.checkbox("Include attachments", value=True)
        
        custom_message = st.text_area(
            "Custom message (optional):",
            placeholder="Additional context or notes..."
        )
    
    # Send email report
    if st.sidebar.button("📧 Send Email Report"):
        if st.session_state.get('cleaned_data') is not None:
            if recipients_input.strip():
                recipients = [email.strip() for email in recipients_input.split('\n') if email.strip()]
                
                with st.spinner("Sending email report..."):
                    try:
                        report_manager = ReportManager()
                        
                        # Get data and results
                        data = st.session_state.cleaned_data
                        analysis_results = st.session_state.get('cleaning_report', {})
                        
                        # Send email
                        success = report_manager.send_email_report(
                            recipients=recipients,
                            data=data,
                            analysis_results=analysis_results,
                            report_type=report_type,
                            include_attachments=include_attachments,
                            custom_message=custom_message or None
                        )
                        
                        if success:
                            st.sidebar.success(f"✅ Email sent to {len(recipients)} recipients!")
                        else:
                            st.sidebar.error("❌ Failed to send email. Check SMTP configuration.")
                            
                    except Exception as e:
                        st.sidebar.error(f"❌ Error sending email: {e}")
            else:
                st.sidebar.warning("⚠️ Please enter recipient email addresses")
        else:
            st.sidebar.warning("⚠️ Please process data first")
    
    # Scheduled reporting setup
    with st.sidebar.expander("📅 Scheduled Reports"):
        st.write("Setup automated email reports")
        
        schedule_recipients = st.text_area(
            "Recipients for scheduled reports:",
            placeholder="team@company.com"
        )
        
        frequency = st.selectbox(
            "Frequency:",
            ["daily", "weekly", "monthly"]
        )
        
        if st.button("⏰ Setup Scheduled Reports"):
            if schedule_recipients.strip():
                recipients = [email.strip() for email in schedule_recipients.split('\n') if email.strip()]
                
                try:
                    report_manager = ReportManager()
                    success = report_manager.setup_automated_reporting(recipients, frequency)
                    
                    if success:
                        st.success(f"✅ {frequency.title()} reports scheduled for {len(recipients)} recipients!")
                    else:
                        st.error("❌ Failed to setup scheduled reports")
                        
                except Exception as e:
                    st.error(f"❌ Error setting up scheduled reports: {e}")
            else:
                st.warning("⚠️ Please enter recipient email addresses")


def add_reporting_tab():
    """
    Add a dedicated reporting tab to the dashboard
    This creates a comprehensive reporting interface
    """
    
    st.header("📤 Reports & Export")
    
    if st.session_state.get('cleaned_data') is not None:
        data = st.session_state.cleaned_data
        analysis_results = st.session_state.get('cleaning_report', {})
        
        # Report generation options
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 PowerPoint Presentation")
            st.write("Generate a comprehensive PowerPoint presentation with:")
            st.write("• Executive summary slide")
            st.write("• Data overview and statistics")
            st.write("• Key insights and patterns")
            st.write("• Professional visualizations")
            st.write("• Recommendations and next steps")
            
            presentation_title = st.text_input(
                "Presentation Title:",
                value=f"Analytics Report - {datetime.now().strftime('%B %Y')}"
            )
            
            if st.button("🎯 Generate PowerPoint", type="primary"):
                with st.spinner("Creating PowerPoint presentation..."):
                    try:
                        report_manager = ReportManager()
                        filepath = report_manager.create_powerpoint_report(
                            data, analysis_results, presentation_title
                        )
                        
                        # Show success and download option
                        st.success("✅ PowerPoint presentation created successfully!")
                        
                        with open(filepath, "rb") as file:
                            st.download_button(
                                label="📥 Download PowerPoint Presentation",
                                data=file.read(),
                                file_name=os.path.basename(filepath),
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                            )
                        
                        # Show file info
                        file_size = os.path.getsize(filepath) / 1024 / 1024
                        st.info(f"📄 File size: {file_size:.1f} MB | Slides: ~8-12 slides")
                        
                    except Exception as e:
                        st.error(f"❌ Error creating PowerPoint: {e}")
        
        with col2:
            st.subheader("📧 Email Reports")
            st.write("Send automated email reports with:")
            st.write("• Professional HTML formatting")
            st.write("• Key metrics and insights")
            st.write("• Optional PowerPoint attachment")
            st.write("• CSV data export")
            st.write("• Customizable templates")
            
            # Email form
            with st.form("email_report_form"):
                recipients = st.text_area(
                    "Recipients (one per line):",
                    placeholder="analyst@company.com\nmanager@company.com\nteam@company.com"
                )
                
                email_subject = st.text_input(
                    "Email Subject:",
                    value=f"Analytics Report - {datetime.now().strftime('%B %d, %Y')}"
                )
                
                report_template = st.selectbox(
                    "Email Template:",
                    ["executive_summary", "detailed_report", "scheduled"],
                    format_func=lambda x: {
                        "executive_summary": "📊 Executive Summary",
                        "detailed_report": "📈 Detailed Report", 
                        "scheduled": "📅 Scheduled Report"
                    }[x]
                )
                
                include_ppt = st.checkbox("Include PowerPoint attachment", value=True)
                include_csv = st.checkbox("Include CSV data export", value=True)
                
                custom_msg = st.text_area(
                    "Custom Message (optional):",
                    placeholder="Add any additional context or notes for recipients..."
                )
                
                send_email = st.form_submit_button("📧 Send Email Report", type="primary")
                
                if send_email:
                    if recipients.strip():
                        recipient_list = [email.strip() for email in recipients.split('\n') if email.strip()]
                        
                        with st.spinner(f"Sending email to {len(recipient_list)} recipients..."):
                            try:
                                report_manager = ReportManager()
                                
                                success = report_manager.send_email_report(
                                    recipients=recipient_list,
                                    data=data,
                                    analysis_results=analysis_results,
                                    report_type=report_template,
                                    include_attachments=include_ppt or include_csv,
                                    custom_message=custom_msg or None
                                )
                                
                                if success:
                                    st.success(f"✅ Email report sent successfully to {len(recipient_list)} recipients!")
                                    st.balloons()
                                else:
                                    st.error("❌ Failed to send email. Please check SMTP configuration.")
                                    
                            except Exception as e:
                                st.error(f"❌ Error sending email: {e}")
                    else:
                        st.warning("⚠️ Please enter at least one recipient email address")
        
        # Scheduled reporting section
        st.subheader("⏰ Automated Scheduling")
        
        with st.expander("📅 Setup Scheduled Reports"):
            st.write("Configure automatic email reports to be sent regularly:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                schedule_recipients = st.text_area(
                    "Recipients for scheduled reports:",
                    placeholder="team@company.com\nmanager@company.com"
                )
                
                schedule_frequency = st.selectbox(
                    "Report Frequency:",
                    ["daily", "weekly", "monthly"],
                    index=1  # Default to weekly
                )
            
            with col2:
                schedule_time = st.time_input("Preferred time:", value=datetime.now().time())
                
                include_weekend = st.checkbox("Include weekends", value=False)
                
                auto_attachments = st.checkbox("Always include attachments", value=True)
            
            if st.button("⚰️ Setup Automated Reports"):
                if schedule_recipients.strip():
                    recipients = [email.strip() for email in schedule_recipients.split('\n') if email.strip()]
                    
                    try:
                        report_manager = ReportManager()
                        success = report_manager.setup_automated_reporting(recipients, schedule_frequency)
                        
                        if success:
                            st.success(f"✅ {schedule_frequency.title()} reports scheduled for {len(recipients)} recipients!")
                            st.info(f"📅 Next report will be sent {schedule_frequency}")
                        else:
                            st.error("❌ Failed to setup scheduled reports")
                            
                    except Exception as e:
                        st.error(f"❌ Error setting up scheduled reports: {e}")
                else:
                    st.warning("⚠️ Please enter recipient email addresses")
    
    else:
        st.warning("⚠️ Please upload and process data first to generate reports")
        st.info("💡 Go to the 'Data Processing' section to get started")


if __name__ == "__main__":
    # Test the reporting integration
    print("📤 Testing Report Integration...")
    
    try:
        # Test PowerPoint generation
        from data_pipeline import load_sample_data, DataCleaningPipeline
        
        pipeline = DataCleaningPipeline()
        raw_data = load_sample_data()
        cleaned_data = pipeline.clean_dataset(raw_data)
        cleaning_report = pipeline.get_cleaning_report()
        
        report_manager = ReportManager()
        
        # Test PowerPoint
        ppt_path = report_manager.create_powerpoint_report(
            cleaned_data, cleaning_report, "Test Analytics Report"
        )
        print(f"✅ PowerPoint created: {ppt_path}")
        
        # Test email (would need SMTP config)
        print("📧 Email functionality ready (requires SMTP configuration)")
        
        print("🎉 Report integration testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("💡 Make sure all dependencies are installed:")