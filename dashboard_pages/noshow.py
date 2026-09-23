from components import page_metadata, page_footer
from dash import html, dcc
import pandas as pd
import plotly.express as px

from dashboard import df
# ================= MONTH ORDER FIX =================
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

df['Month_Name'] = pd.Categorical(df['Month_Name'], categories=month_order, ordered=True)
# ================= DEFAULT CHARTS =================

# 1️⃣ No-Show Trend (Line) ✅ FIXED
trend = df.groupby('Month_Name')['No_Show_Flag'].sum().reset_index()

fig1 = px.line(
    trend,
    x='Month_Name',   # ✅ FIX HERE
    y='No_Show_Flag',
    title="No-Show Trend"
)

fig1.update_traces(line=dict(color="#e74c3c", width=3), mode="lines+markers")


# 2️⃣ No-Show by Time Slot
time_data = df.groupby('Time_Slot')['No_Show_Flag'].sum().reset_index()

fig2 = px.bar(
    time_data,
    x='Time_Slot',
    y='No_Show_Flag',
    title="No-Show by Time Slot",
    color='Time_Slot',
    color_discrete_map={
        "Morning": "#f39c12",
        "Afternoon": "#00cec9",
        "Evening": "#6c5ce7"
    }
)


# 3️⃣ Department Impact
dept_data = df.groupby('dept_Name')['No_Show_Flag'].sum().reset_index()

fig3 = px.bar(
    dept_data,
    x='No_Show_Flag',
    y='dept_Name',
    orientation='h',
    title="Department No-Show Impact",
    color='No_Show_Flag',
    color_continuous_scale="Reds"
)


# 4️⃣ Top Doctors with No-Show
doc_data = df.groupby('Doctor_Name')['No_Show_Flag'].sum().nlargest(5).reset_index()

fig4 = px.bar(
    doc_data,
    x='Doctor_Name',
    y='No_Show_Flag',
    title="Doctors with Highest No-Show",
    color='No_Show_Flag',
    color_continuous_scale="Oranges"
)


# 5️⃣ No-Show Distribution
status_data = df['No_Show_Flag'].value_counts().reset_index()
status_data.columns = ['Status', 'Count']

fig5 = px.pie(
    status_data,
    names='Status',
    values='Count',
    hole=0.5,
    title="No-Show Distribution"
)


# ================= KPI =================
def kpi_card(icon, title, value, color):
    return html.Div([
        html.Div(icon, className="kpi-icon-home"),
        html.Div([
            html.P(title, className="kpi-title"),
            html.H3(value, style={
                "color": color,
                "fontWeight": "bold",
                "fontSize": "29px"
            })
        ])
    ], className="kpi-card-home")


# ================= LAYOUT =================
def noshow_layout():

    return html.Div([

        # NAVBAR
        html.Div([
            html.Div(className="nav-left"),
            html.Div("🏥 Multicare Hospital Analytics", className="nav-title"),
            html.Div([
                html.Span("👤 Admin", className="nav-user"),
                html.Button("Logout", id="logout-btn")
            ], className="nav-links")
        ], className="navbar"),

        # MAIN
        html.Div([

            # SIDEBAR
            html.Div([
                html.Img(
                    src="/assets/multicare2.png",
                    style={"width": "150px", "margin": "auto","margin-top":"1px", "display": "block"}
                ),
                html.H4("MULTICARE HOSPITAL", style={"textAlign": "center"}),
                html.Hr(),

                html.H3("Menu"),

                dcc.Link("🏠 Dashboard Overview", href="/dashboard", className="nav-item"),
                dcc.Link("📊 Appointment Analysis", href="/appointment", className="nav-item"),
                dcc.Link("🚫 No-Show Analysis", href="/noshow", className="nav-item"),
                dcc.Link("🔁 Patient Retention", href="/retention", className="nav-item"),
                dcc.Link("👨‍⚕️ Doctor Performance", href="/doctor", className="nav-item"),

                html.Hr(),

                html.H4("Filters"),

                # ✅ MATCHED IDs
                dcc.Dropdown(
                    id="app-month",
                    options=[{"label": m, "value": m} for m in month_order if m in df['Month_Name'].unique()],
                    placeholder="Select Month",
                    clearable=True
                ),

                dcc.Dropdown(
                    id="app-year",
                    options=[{"label": y, "value": y} for y in sorted(df['Year'].dropna().unique())],
                    placeholder="Select Year",
                    clearable=True
                ),

                dcc.Dropdown(
                    id="doctor-filter",
                    options=[{"label": d, "value": d} for d in df['Doctor_Name'].dropna().unique()],
                    placeholder="Select Doctor",
                    clearable=True
                ),

                dcc.Dropdown(
                    id="dept-filter",
                    options=[{"label": d, "value": d} for d in df['dept_Name'].dropna().unique()],
                    placeholder="Select Department",
                    clearable=True
                ),

            ], className="sidebar"),

            # CONTENT
            html.Div([

                html.H2("🚫 No-Show Analysis", className="section-title"),
                html.P("Analysis of Missed Appointments and Identify Risk Patterns",
                       className="section-subtitle"),

                html.Div(id="noshow-kpi", className="kpi-container"),

                html.Div([
                    html.Div(dcc.Graph(id="noshow-chart1", figure=fig1), className="chart-card"),
                    html.Div(dcc.Graph(id="noshow-chart2", figure=fig2), className="chart-card"),
                ], className="charts"),

                html.Div([
                    html.Div(dcc.Graph(id="noshow-chart3", figure=fig3), className="chart-card"),
                    html.Div(dcc.Graph(id="noshow-chart4", figure=fig4), className="chart-card"),
                ], className="charts"),

                html.Div([
                    html.Div(dcc.Graph(id="noshow-chart5", figure=fig5), className="chart-card"),
                ], className="charts"),
                page_metadata(),
                page_footer(),

            ], className="content")

        ], className="main")

    ])