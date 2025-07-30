import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Optional
import numpy as np
from .topic_modeling import TopicModeler
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

class TopicVisualizer:
    """Class for visualizing topic modeling results"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.topic_modeler = get_topic_modeler()
    
    def create_topic_distribution_chart(
        self,
        records: List[Dict[str, Any]],
        bank_name: str,
        quarter: str
    ) -> go.Figure:
        """Create a bar chart showing topic distribution"""
        df = pd.DataFrame(records)
        
        # Count occurrences of each topic
        topic_counts = df["topic_label"].value_counts().reset_index()
        topic_counts.columns = ["Topic", "Count"]
        
        # Separate seed and emerging topics
        seed_topics = topic_counts[topic_counts["Topic"].str.startswith("Emerging").fillna(False)]
        emerging_topics = topic_counts[~topic_counts["Topic"].str.startswith("Emerging").fillna(False)]
        
        # Create figure
        fig = go.Figure()
        
        # Add seed topics
        fig.add_trace(go.Bar(
            x=seed_topics["Topic"],
            y=seed_topics["Count"],
            name="Seed Topics",
            marker_color="#1f77b4"
        ))
        
        # Add emerging topics
        fig.add_trace(go.Bar(
            x=emerging_topics["Topic"],
            y=emerging_topics["Count"],
            name="Emerging Topics",
            marker_color="#ff7f0e"
        ))
        
        # Update layout
        fig.update_layout(
            title=f"Topic Distribution - {bank_name} {quarter}",
            xaxis_title="Topic",
            yaxis_title="Number of Mentions",
            barmode='group',
            template="plotly_white"
        )
        
        return fig
    
    def create_sentiment_by_topic_chart(
        self,
        records: List[Dict[str, Any]]
    ) -> go.Figure:
        """Create a box plot showing sentiment distribution by topic"""
        df = pd.DataFrame(records)
        
        # Create figure
        fig = px.box(
            df,
            x="topic_label",
            y="sentiment_score",
            color="topic_label",
            title="Sentiment Distribution by Topic",
            template="plotly_white"
        )
        
        fig.update_layout(
            xaxis_title="Topic",
            yaxis_title="Sentiment Score",
            showlegend=False
        )
        
        return fig
    
    def create_topic_trend_chart(
        self,
        records: List[Dict[str, Any]],
        bank_name: str
    ) -> go.Figure:
        """Create a line chart showing topic trends over time"""
        df = pd.DataFrame(records)
        
        # Convert timestamps to datetime
        df["timestamp_iso"] = pd.to_datetime(df["timestamp_iso"])
        
        # Group by topic and time
        grouped = df.groupby([
            pd.Grouper(key="timestamp_iso", freq="M"),
            "topic_label"
        ]).size().reset_index(name="count")
        
        # Create figure
        fig = px.line(
            grouped,
            x="timestamp_iso",
            y="count",
            color="topic_label",
            title=f"Topic Trends Over Time - {bank_name}",
            template="plotly_white"
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Mention Count",
            showlegend=True
        )
        
        return fig
    
    def create_topic_comparison_chart(
        self,
        records: List[Dict[str, Any]],
        bank_names: List[str]
    ) -> go.Figure:
        """Create a comparison chart for different banks"""
        df = pd.DataFrame(records)
        
        # Filter for selected banks
        df = df[df["bank_name"].isin(bank_names)]
        
        # Count occurrences of each topic per bank
        topic_counts = df.groupby(["bank_name", "topic_label"]).size().reset_index(name="count")
        
        # Create figure
        fig = px.bar(
            topic_counts,
            x="bank_name",
            y="count",
            color="topic_label",
            title="Topic Distribution by Bank",
            template="plotly_white"
        )
        
        fig.update_layout(
            xaxis_title="Bank",
            yaxis_title="Number of Mentions",
            showlegend=True
        )
        
        return fig

def get_topic_visualizer() -> TopicVisualizer:
    """Get the singleton topic visualizer instance"""
    if not hasattr(get_topic_visualizer, 'instance'):
        get_topic_visualizer.instance = TopicVisualizer()
    return get_topic_visualizer.instance
