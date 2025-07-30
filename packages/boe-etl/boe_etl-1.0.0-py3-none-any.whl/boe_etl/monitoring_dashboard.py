import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from typing import Dict, List
from .error_handling import get_exception_handler
from .progress_tracker import get_progress_tracker
from .version_visualization import get_version_visualizer
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

class MonitoringDashboard:
    """Interactive dashboard for monitoring ETL pipeline"""
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or ConfigManager().get_config()
        self.progress_tracker = get_progress_tracker()
        self.exception_handler = get_exception_handler()
        self.version_visualizer = get_version_visualizer()
        
        # Initialize Dash app
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        """Setup the dashboard layout"""
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("ETL Pipeline Monitoring Dashboard", className="text-center mb-4")
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    # Bank Selection
                    dbc.Card([
                        dbc.CardHeader("Select Bank and Quarter"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id="bank-dropdown",
                                options=[
                                    {"label": bank["name"], "value": bank["name"]}
                                    for bank in self.config["banks"]
                                ],
                                value=None,
                                placeholder="Select a bank..."
                            ),
                            dcc.Dropdown(
                                id="quarter-dropdown",
                                options=[],
                                value=None,
                                placeholder="Select a quarter..."
                            )
                        ])
                    ], className="mb-3")
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    # Progress Overview
                    dbc.Card([
                        dbc.CardHeader("Pipeline Progress"),
                        dbc.CardBody([
                            html.Div(id="progress-summary"),
                            dcc.Graph(id="progress-chart")
                        ])
                    ], className="mb-3")
                ]),
                dbc.Col([
                    # Error Summary
                    dbc.Card([
                        dbc.CardHeader("Error Summary"),
                        dbc.CardBody([
                            html.Div(id="error-summary"),
                            dcc.Graph(id="error-chart")
                        ])
                    ], className="mb-3")
                ])
            ]),
            
            dbc.Row([
                dbc.Col([
                    # Version History
                    dbc.Card([
                        dbc.CardHeader("Version History"),
                        dbc.CardBody([
                            dcc.Graph(id="version-timeline")
                        ])
                    ])
                ])
            ])
        ], fluid=True)
    
    def _setup_callbacks(self):
        """Setup callback functions"""
        @self.app.callback(
            [Output("quarter-dropdown", "options"),
             Output("quarter-dropdown", "value")],
            [Input("bank-dropdown", "value")]
        )
        def update_quarters(selected_bank):
            if not selected_bank:
                return [], None
                
            bank_config = next(
                (b for b in self.config["banks"] if b["name"] == selected_bank),
                None
            )
            
            if bank_config:
                return ([
                    {"label": q, "value": q} for q in bank_config["quarters"]
                ], None)
            return [], None
        
        @self.app.callback(
            [Output("progress-summary", "children"),
             Output("progress-chart", "figure")],
            [Input("bank-dropdown", "value"),
             Input("quarter-dropdown", "value")]
        )
        def update_progress(bank, quarter):
            if not bank or not quarter:
                return "Select a bank and quarter to view progress.", go.Figure()
                
            progress = self.progress_tracker.get_progress(bank, quarter)
            
            summary = html.Div([
                html.H4(f"Progress for {bank} {quarter}"),
                html.P(f"Status: {progress['status']}")
            ])
            
            # Create progress chart
            stages = list(progress["stages"].keys())
            counts = [progress["stages"][s]["count"] for s in stages]
            
            fig = go.Figure(
                go.Bar(
                    x=stages,
                    y=counts,
                    marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
                )
            )
            
            fig.update_layout(
                title="Stage Progress",
                xaxis_title="Pipeline Stage",
                yaxis_title="Records Processed",
                template="plotly_white"
            )
            
            return summary, fig
        
        @self.app.callback(
            [Output("error-summary", "children"),
             Output("error-chart", "figure")],
            [Input("bank-dropdown", "value"),
             Input("quarter-dropdown", "value")]
        )
        def update_errors(bank, quarter):
            if not bank or not quarter:
                return "Select a bank and quarter to view errors.", go.Figure()
                
            error_summary = self.exception_handler.get_error_summary(bank, quarter)
            
            summary = html.Div([
                html.H4(f"Error Summary for {bank} {quarter}"),
                html.P(f"Total Errors: {error_summary['total_errors']}")
            ])
            
            # Create error type chart
            error_types = list(error_summary["error_types"].keys())
            counts = list(error_summary["error_types"].values())
            
            fig = go.Figure(
                go.Pie(
                    labels=error_types,
                    values=counts
                )
            )
            
            fig.update_layout(
                title="Error Type Distribution",
                template="plotly_white"
            )
            
            return summary, fig
        
        @self.app.callback(
            Output("version-timeline", "figure"),
            [Input("bank-dropdown", "value"),
             Input("quarter-dropdown", "value")]
        )
        def update_versions(bank, quarter):
            if not bank or not quarter:
                return go.Figure()
                
            try:
                fig = self.version_visualizer.create_version_timeline(
                    bank_name=bank,
                    quarter=quarter,
                    show_tags=True
                )
                return fig
            except Exception as e:
                logging.error(f"Failed to create version timeline: {e}")
                return go.Figure()
    
    def run(self, port: int = 8050):
        """Run the dashboard server"""
        self.app.run_server(
            port=port,
            debug=True,
            use_reloader=False
        )

def run_monitoring_dashboard(port: int = 8050) -> None:
    """Run the monitoring dashboard"""
    dashboard = MonitoringDashboard()
    dashboard.run(port)

if __name__ == "__main__":
    run_monitoring_dashboard()
