from components import page_metadata, page_footer
from dash import html, dcc
import pandas as pd
import plotly.express as px

from dashboard import df

# ================= MONTH ORDER FIX =================
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

df['Month_Name'] = pd.Categorical(df['Month_Name'], categories=month_order, ordered=True)

# ================= CHARTS =================

# 1️⃣ Monthly Trend (Line)
monthly = df.groupby('Month_Name').size().reset_index(name='Count')
fig1 = px.line(monthly, x='Month_Name', y='Count', title="Monthly Trend")
fig1.update_traces(line=dict(color="#00b4d8", width=3), mode="lines+markers")

# 2️⃣ Time Slot (Colored Bar - Day Theme)
time_data = df['Time_Slot'].value_counts().reset_index()
time_data.columns = ['Time Slot', 'Count']
fig2 = px.bar(
    time_data,
    x='Time Slot',
    y='Count',
    title="Time Slot Load",
    color='Time Slot',
    color_discrete_map={
        "Morning": "#f39c12",
        "Afternoon": "#00cec9",
        "Evening": "#6c5ce7"
    }
)

# 3️⃣ Department Load (Horizontal Bar - Professional)
dept_data = df['dept_Name'].value_counts().reset_index()
dept_data.columns = ['Department', 'Count']
fig3 = px.bar(
    dept_data,
    x='Count',
    y='Department',
    orientation='h',
    title="Department Workload",
    color='Count',
    color_continuous_scale="Teal"
)

# 4️⃣ Top Doctors (Gradient Bar)
doc_data = df['Doctor_Name'].value_counts().head(5).reset_index()
doc_data.columns = ['Doctor', 'Count']
fig4 = px.bar(
    doc_data,
    x='Doctor',
    y='Count',
    title="Top Doctors",
    color='Count',
    color_continuous_scale="Blues"
)

# 5️⃣ Appointment Status (Donut Chart)
status_data = df['appointment_status'].value_counts().reset_index()
status_data.columns = ['Status', 'Count']
fig5 = px.pie(
    status_data,
    names='Status',
    values='Count',
    hole=0.5,
    title="Appointment Status"
)

# ================= LAYOUT FUNCTION =================
def appointment_layout():

    return html.Div([

        # ================= NAVBAR =================
        html.Div([
            html.Div(className="nav-left"),
            html.Div("🏥 Multicare Hospital Analytics", className="nav-title"),
            html.Div([
                html.Span("👤 Admin", className="nav-user"),
                html.Button("Logout", id="logout-btn")
            ], className="nav-links")
        ], className="navbar"),

        # ================= MAIN =================
        html.Div([

            # ================= SIDEBAR =================
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

                dcc.Dropdown(
                    id="app-month",
                    options=[{"label": m, "value": m} for m in month_order],
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

            # ================= CONTENT =================
            html.Div([

                html.H2("📊 Appointment Analysis", className="section-title"),
                html.P("Appointment trends, Workload distribution, and Efficiency Analysis Dashboard",
                       className="section-subtitle"),

                html.Div(id="app-kpi", className="kpi-container"),

                html.Div([
                    html.Div(dcc.Graph(id="app-chart1", figure=fig1), className="chart-card"),
                    html.Div(dcc.Graph(id="app-chart2", figure=fig2), className="chart-card"),
                ], className="charts"),

                html.Div([
                    html.Div(dcc.Graph(id="app-chart3", figure=fig3), className="chart-card"),
                    html.Div(dcc.Graph(id="app-chart4", figure=fig4), className="chart-card"),
                ], className="charts"),

                html.Div([
                    html.Div(dcc.Graph(id="app-chart5", figure=fig5), className="chart-card"),
                ], className="charts"),
                page_metadata(),
                page_footer(),

            ], className="content")

        ], className="main")

    ])