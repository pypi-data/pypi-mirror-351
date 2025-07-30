import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from .data_versioning import get_data_version_manager
from .version_tagging import get_version_tag_manager
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

class VersionVisualizer:
    """Visualizer for version history and comparisons"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.version_manager = get_data_version_manager()
        self.tag_manager = get_version_tag_manager()
    
    def create_version_timeline(
        self,
        bank_name: str,
        quarter: str,
        show_tags: bool = True
    ) -> go.Figure:
        """
        Create a timeline visualization of version history
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
            show_tags: Whether to show tags in the visualization
        Returns:
            Plotly figure
        """
        # Get version history
        versions = self.version_manager.list_versions(bank_name, quarter)
        
        # Convert to DataFrame
        df = pd.DataFrame(versions)
        df["created_at"] = pd.to_datetime(df["created_at"])
        
        # Get tags if needed
        if show_tags:
            tags = self.tag_manager.list_tags(bank_name, quarter)
            for tag_name, versions in tags.items():
                for version_id in versions:
                    df.loc[df["version_id"] == version_id, "tag"] = tag_name
        
        # Create figure
        fig = go.Figure()
        
        # Add timeline markers
        for _, row in df.iterrows():
            fig.add_trace(go.Scatter(
                x=[row["created_at"]],
                y=[row["version_id"]],
                mode='markers+text',
                name=row["version_id"],
                text=row["version_id"],
                textposition="top center",
                marker=dict(
                    size=15,
                    color='blue' if pd.isna(row["tag"]) else 'green'
                )
            ))
        
        # Add tag indicators
        if show_tags:
            for tag_name, versions in tags.items():
                for version_id in versions:
                    tag_version = df[df["version_id"] == version_id]
                    if not tag_version.empty:
                        fig.add_annotation(
                            x=tag_version["created_at"].iloc[0],
                            y=tag_version["version_id"].iloc[0],
                            text=tag_name,
                            showarrow=False,
                            bgcolor='rgba(255, 255, 255, 0.8)',
                            bordercolor='black',
                            borderwidth=1
                        )
        
        # Update layout
        fig.update_layout(
            title=f"Version History - {bank_name} {quarter}",
            xaxis_title="Date",
            yaxis_title="Version ID",
            showlegend=False,
            template="plotly_white",
            height=600
        )
        
        return fig
    
    def create_version_comparison_chart(
        self,
        bank_name: str,
        quarter: str,
        version_ids: List[str],
        metric: str
    ) -> go.Figure:
        """
        Create a comparison chart for specific versions
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
            version_ids: List of version IDs to compare
            metric: Metric to compare (e.g., "num_topics", "accuracy")
        Returns:
            Plotly figure
        """
        data = []
        for version_id in version_ids:
            metadata = self.version_manager.get_version_metadata(bank_name, quarter, version_id)
            if metadata:
                version_info = metadata.get("version_info", {})
                metric_value = version_info.get(metric)
                if metric_value is not None:
                    data.append({
                        "version_id": version_id,
                        "metric": metric_value,
                        "created_at": metadata["created_at"]
                    })
        
        if not data:
            raise ValueError("No data available for comparison")
            
        df = pd.DataFrame(data)
        df["created_at"] = pd.to_datetime(df["created_at"])
        
        # Create figure
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=df["version_id"],
            y=df["metric"],
            text=df["metric"],
            textposition="outside",
            marker_color=df["metric"],
            name=metric
        ))
        
        # Add trend line
        fig.add_trace(go.Scatter(
            x=df["version_id"],
            y=df["metric"],
            mode='lines+markers',
            name="Trend",
            line=dict(color='red')
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{metric} Comparison - {bank_name} {quarter}",
            xaxis_title="Version ID",
            yaxis_title=metric,
            template="plotly_white",
            height=600,
            showlegend=True
        )
        
        return fig
    
    def create_tag_distribution_chart(
        self,
        bank_name: str,
        quarter: str
    ) -> go.Figure:
        """
        Create a chart showing tag distribution
        Args:
            bank_name: Name of the bank
            quarter: Quarter identifier
        Returns:
            Plotly figure
        """
        tags = self.tag_manager.list_tags(bank_name, quarter)
        
        # Prepare data
        tag_counts = []
        for tag_name, versions in tags.items():
            tag_counts.append({
                "tag": tag_name,
                "count": len(versions)
            })
        
        if not tag_counts:
            raise ValueError("No tags found")
            
        df = pd.DataFrame(tag_counts)
        
        # Create figure
        fig = go.Figure(
            go.Pie(
                labels=df["tag"],
                values=df["count"],
                textinfo='label+percent',
                insidetextorientation='radial'
            )
        )
        
        # Update layout
        fig.update_layout(
            title=f"Tag Distribution - {bank_name} {quarter}",
            template="plotly_white"
        )
        
        return fig

def get_version_visualizer() -> VersionVisualizer:
    """Get the singleton version visualizer instance"""
    if not hasattr(get_version_visualizer, 'instance'):
        get_version_visualizer.instance = VersionVisualizer()
    return get_version_visualizer.instance
