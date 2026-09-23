from dash import html
from datetime import datetime


def page_metadata():
    """
    Reusable professional metadata section for all pages.
    """
    last_updated = datetime.now().strftime("%d %b %Y, %I:%M %p")

    return html.Div([
        html.Span("🏥 Source: Multicare Hospital ERP System"),
        html.Span(" | "),
        html.Span(f"🕒 Last Updated: {last_updated}"),
    ], style={
        "textAlign": "center",
        "padding": "20px",
        "marginTop": "30px",
        "color": "black",
        "fontSize": "14px",
        "borderTop": "1px solid black"
    })


def page_footer():
    """
    Reusable professional footer for all pages.
    """
    return html.Div(
        "© 2026 CareFlow Analytics | Developed by Anandi Thakare & Shruti Borkar",
        style={
            "textAlign": "center",
            "padding": "5px",
            "color": "black",
            "fontSize": "13px",
        }
    )