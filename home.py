from dash import html, dcc, Input, Output
from dashboard import df


# ================= KPI =================
def get_kpis():

    total_app = len(df)
    total_pat = df['patient_Id'].nunique()

    no_show_rate = round((df['No_Show_Flag'].sum() / total_app) * 100, 2)

    df['appointment_status'] = df['appointment_status'].astype(str).str.lower()

    attended_df = df[df['appointment_status'].isin(["completed", "attended"])]
    lost_df = df[df['appointment_status'].isin(["no show", "cancelled", "canceled"])]

    revenue = attended_df['payment_amount'].sum()
    loss = lost_df['payment_amount'].sum()

    return total_app, total_pat, revenue, loss, no_show_rate


# ================= HOME =================
def home_layout():

    total_app, total_pat, revenue, loss, no_show = get_kpis()

    return html.Div(className="home-wrapper", children=[

        # 🔷 NAVBAR
        html.Div([

            # LEFT (empty for spacing)
            html.Div(className="nav-left"),

            # CENTER TITLE
            html.Div(
                "🏥 Multicare Hospital Analytics",
                className="nav-title"
            ),

            # RIGHT SIDE
            html.Div([
                html.Span("👤 Admin", className="nav-user"),
                html.Button("Logout", id="logout-btn")
            ], className="nav-links")

        ], className="navbar"),


        # 🔷 HERO
        html.Div(className="home-hero", children=[

            html.Div(className="home-content", children=[

                # KPI
                html.Div([
                    kpi_card("👥", "Patients", total_pat, "#2563eb", "kpi-blue"),
                    kpi_card("📅", "Appointments", total_app, "#0ea5e9", "kpi-blue"),
                    kpi_card("💰", "Revenue", f"₹{round(revenue,2)}", "#16a34a", "kpi-green"),
                    kpi_card("❌", "No-Show", f"{no_show}%", "#dc2626", "kpi-red"),
                ], className="home-kpis"),
               
                # DESCRIPTION
                html.Div([
                    html.P(
                        "This dashboard provides a comprehensive overview of hospital operations including",
                        className="home-about"
                    ),
                    html.P(
                        "patient volume, appointment trends, revenue generation, and no-show analysis.",
                        className="home-about"
                    ),
                    html.P(
                        "It enables healthcare administrators to identify inefficiencies, optimize scheduling,",
                        className="home-about"
                    ),
                    html.P(
                        "and improve patient retention using data-driven insights.",
                        className="home-about"
                    ),
                ]),

                # BUTTON
                dcc.Link("🚀 Explore Dashboard", href="/dashboard", className="home-btn"),

            ])
        ]),


        # 🔷 FOOTER (NOW PERFECTLY VISIBLE)
        html.Div(
            "📍 Pune | 📞 +91-9876543210 | ✉ support@multicare.com",
            className="home-footer"
        )

    ])


# ================= KPI CARD =================
def kpi_card(icon, title, value, color, extra_class=""):
    return html.Div([
        html.Div(icon, className="kpi-icon-home"),
        html.Div([
            html.P(title, className="kpi-title"),
            html.H2(value, style={
                "color": color,
                "fontWeight": "bold"
            })
        ])
    ], className=f"kpi-card-home {extra_class}")

# ================= CALLBACK =================
def register_home_callbacks(app):

    @app.callback(
        Output("username-display", "children"),
        Input("session-user", "data")
    )
    def show_user(user):
        if user:
            return f"👤 {user}"
        return "👤 Admin"