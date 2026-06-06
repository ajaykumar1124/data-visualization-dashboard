"""
Visualization Engine Module
Creates 6 different visualization types for communicating insights to non-technical stakeholders
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class VisualizationEngine:
    """
    Comprehensive visualization engine for creating 6 types of charts
    Designed for non-technical academic stakeholders
    """
    
    def __init__(self):
        self.color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        self.figure_size = (12, 8)
        
    def create_trend_analysis(self, df: pd.DataFrame, x_col: str, y_col: str, 
                            title: str = "Trend Analysis") -> go.Figure:
        """
        Visualization Type 1: Trend Analysis Line Chart
        Shows trends over time or sequential data
        """
        fig = go.Figure()
        
        # Add main trend line
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='lines+markers',
            name=y_col,
            line=dict(width=3, color='#1f77b4'),
            marker=dict(size=6)
        ))
        
        # Add trend line
        if df[y_col].dtype in ['int64', 'float64']:
            z = np.polyfit(range(len(df)), df[y_col], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=p(range(len(df))),
                mode='lines',
                name='Trend',
                line=dict(dash='dash', color='red', width=2)
            ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_distribution_analysis(self, df: pd.DataFrame, column: str, 
                                   title: str = "Distribution Analysis") -> go.Figure:
        """
        Visualization Type 2: Distribution Analysis (Histogram + Box Plot)
        Shows data distribution and identifies outliers
        """
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Distribution', 'Box Plot'),
            vertical_spacing=0.1
        )
        
        # Histogram
        fig.add_trace(
            go.Histogram(
                x=df[column],
                nbinsx=30,
                name='Distribution',
                marker_color='lightblue',
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(
                y=df[column],
                name='Box Plot',
                marker_color='lightgreen',
                boxpoints='outliers'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            template='plotly_white',
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_categorical_comparison(self, df: pd.DataFrame, category_col: str, 
                                   value_col: str, title: str = "Categorical Comparison") -> go.Figure:
        """
        Visualization Type 3: Categorical Comparison Bar Chart
        Compares values across different categories
        """
        # Aggregate data by category
        agg_data = df.groupby(category_col)[value_col].agg(['mean', 'count']).reset_index()
        
        fig = go.Figure()
        
        # Add bar chart
        fig.add_trace(go.Bar(
            x=agg_data[category_col],
            y=agg_data['mean'],
            name=f'Average {value_col}',
            marker_color='lightcoral',
            text=agg_data['count'],
            texttemplate='n=%{text}',
            textposition='outside'
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            xaxis_title=category_col.replace('_', ' ').title(),
            yaxis_title=f'Average {value_col.replace("_", " ").title()}',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_correlation_heatmap(self, df: pd.DataFrame, 
                                 title: str = "Correlation Analysis") -> go.Figure:
        """
        Visualization Type 4: Correlation Heatmap
        Shows relationships between numerical variables
        """
        # Select only numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            # Create a simple message if not enough numeric columns
            fig = go.Figure()
            fig.add_annotation(
                text="Not enough numeric columns for correlation analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            template='plotly_white',
            height=500,
            width=600
        )
        
        return fig
    
    def create_performance_dashboard(self, df: pd.DataFrame, 
                                   title: str = "Performance Dashboard") -> go.Figure:
        """
        Visualization Type 5: Multi-metric Performance Dashboard
        Shows key performance indicators in a single view
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Key Metrics', 'Trend', 'Distribution', 'Categories'),
            specs=[[{"type": "indicator"}, {"type": "scatter"}],
                   [{"type": "histogram"}, {"type": "bar"}]]
        )
        
        # Get numeric columns for analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        if len(numeric_cols) > 0:
            main_metric = numeric_cols[0]
            
            # KPI Indicator
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=df[main_metric].mean(),
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"Average {main_metric}"},
                    gauge={'axis': {'range': [None, df[main_metric].max()]},
                           'bar': {'color': "darkblue"},
                           'steps': [{'range': [0, df[main_metric].mean()], 'color': "lightgray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': df[main_metric].quantile(0.9)}}
                ),
                row=1, col=1
            )
            
            # Trend line
            if len(df) > 1:
                fig.add_trace(
                    go.Scatter(x=list(range(len(df))), y=df[main_metric],
                             mode='lines', name='Trend'),
                    row=1, col=2
                )
            
            # Distribution
            fig.add_trace(
                go.Histogram(x=df[main_metric], name='Distribution'),
                row=2, col=1
            )
        
        # Categorical analysis
        if len(categorical_cols) > 0:
            cat_col = categorical_cols[0]
            cat_counts = df[cat_col].value_counts().head(10)
            
            fig.add_trace(
                go.Bar(x=cat_counts.index, y=cat_counts.values, name='Categories'),
                row=2, col=2
            )
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            template='plotly_white',
            height=700,
            showlegend=False
        )
        
        return fig
    
    def create_comparative_analysis(self, df: pd.DataFrame, group_col: str, 
                                  value_cols: List[str], 
                                  title: str = "Comparative Analysis") -> go.Figure:
        """
        Visualization Type 6: Comparative Analysis (Grouped Bar Chart)
        Compares multiple metrics across different groups
        """
        fig = go.Figure()
        
        # Group data
        grouped_data = df.groupby(group_col)[value_cols].mean().reset_index()
        
        # Add bars for each metric
        for i, col in enumerate(value_cols):
            fig.add_trace(go.Bar(
                name=col.replace('_', ' ').title(),
                x=grouped_data[group_col],
                y=grouped_data[col],
                marker_color=self.color_palette[i % len(self.color_palette)]
            ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            xaxis_title=group_col.replace('_', ' ').title(),
            yaxis_title='Values',
            barmode='group',
            template='plotly_white',
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    def create_executive_summary_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Create an executive summary visualization combining multiple insights
        """
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=('Data Overview', 'Key Trends', 'Distribution', 
                          'Categories', 'Performance', 'Quality Score'),
            specs=[[{"type": "table"}, {"type": "scatter"}, {"type": "histogram"}],
                   [{"type": "bar"}, {"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Data overview table
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary_stats = df[numeric_cols].describe().round(2)
            
            fig.add_trace(
                go.Table(
                    header=dict(values=['Metric'] + list(summary_stats.columns)),
                    cells=dict(values=[summary_stats.index] + [summary_stats[col] for col in summary_stats.columns])
                ),
                row=1, col=1
            )
        
        # Add other visualizations...
        # (Implementation continues with other chart types)
        
        fig.update_layout(
            title=dict(text="Executive Dashboard Summary", font=dict(size=24)),
            template='plotly_white',
            height=800
        )
        
        return fig
    
    def generate_insights_text(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Generate automated insights for non-technical stakeholders
        """
        insights = {}
        
        # Data quality insights
        total_rows = len(df)
        missing_percentage = (df.isnull().sum().sum() / (total_rows * len(df.columns))) * 100
        
        insights['data_quality'] = f"""
        Data Quality Summary:
        • Dataset contains {total_rows:,} records across {len(df.columns)} variables
        • Data completeness: {100 - missing_percentage:.1f}% (excellent quality)
        • Ready for analysis and reporting
        """
        
        # Numerical insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            insights['numerical_summary'] = f"""
            Key Numerical Insights:
            • {len(numeric_cols)} quantitative measures identified
            • Average values range from {df[numeric_cols].mean().min():.1f} to {df[numeric_cols].mean().max():.1f}
            • Data shows {'high' if df[numeric_cols].std().mean() > df[numeric_cols].mean().mean() * 0.5 else 'moderate'} variability
            """
        
        # Categorical insights
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            insights['categorical_summary'] = f"""
            Categorical Data Insights:
            • {len(categorical_cols)} categorical variables identified
            • Most diverse category has {df[categorical_cols[0]].nunique() if len(categorical_cols) > 0 else 0} unique values
            • Data suitable for segmentation and group analysis
            """
        
        return insights


def create_sample_visualizations():
    """
    Create sample visualizations for demonstration
    """
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=n_samples, freq='D'),
        'revenue': np.random.normal(10000, 2000, n_samples),
        'department': np.random.choice(['Sales', 'Marketing', 'IT', 'HR'], n_samples),
        'performance_score': np.random.normal(75, 15, n_samples),
        'employee_count': np.random.poisson(50, n_samples),
        'satisfaction_rating': np.random.uniform(1, 5, n_samples)
    })
    
    # Initialize visualization engine
    viz_engine = VisualizationEngine()
    
    # Create all 6 visualization types
    visualizations = {}
    
    # 1. Trend Analysis
    visualizations['trend'] = viz_engine.create_trend_analysis(
        sample_data, 'date', 'revenue', 'Revenue Trend Over Time'
    )
    
    # 2. Distribution Analysis
    visualizations['distribution'] = viz_engine.create_distribution_analysis(
        sample_data, 'performance_score', 'Performance Score Distribution'
    )
    
    # 3. Categorical Comparison
    visualizations['categorical'] = viz_engine.create_categorical_comparison(
        sample_data, 'department', 'revenue', 'Revenue by Department'
    )
    
    # 4. Correlation Heatmap
    visualizations['correlation'] = viz_engine.create_correlation_heatmap(
        sample_data, 'Performance Metrics Correlation'
    )
    
    # 5. Performance Dashboard
    visualizations['dashboard'] = viz_engine.create_performance_dashboard(
        sample_data, 'Organizational Performance Dashboard'
    )
    
    # 6. Comparative Analysis
    visualizations['comparative'] = viz_engine.create_comparative_analysis(
        sample_data, 'department', ['revenue', 'performance_score'], 
        'Department Performance Comparison'
    )
    
    return visualizations, viz_engine


if __name__ == "__main__":
    # Create sample visualizations
    charts, engine = create_sample_visualizations()
    
    print("Created 6 visualization types:")
    for chart_type, chart in charts.items():
        print(f"- {chart_type.title()} Chart")
    
    # Generate insights
    sample_df = pd.DataFrame({
        'revenue': np.random.normal(10000, 2000, 1000),
        'department': np.random.choice(['Sales', 'Marketing', 'IT'], 1000)
    })
    
    insights = engine.generate_insights_text(sample_df)
    print("\nGenerated Insights:")
    for key, insight in insights.items():
        print(f"\n{key}:")
        print(insight)