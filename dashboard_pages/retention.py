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

# 1️⃣ Retention Trend ✅ FIXED
retention_trend = df.groupby('Month_Name')['patient_Id'].nunique().reset_index()

fig1 = px.line(
    retention_trend,
    x='Month_Name',   # ✅ FIX HERE
    y='patient_Id',
    title="Patient Retention Trend"
)

fig1.update_traces(line=dict(color="#00b4d8", width=3), mode="lines+markers")


# 2️⃣ Returning vs New Patients
df['visit_count'] = df.groupby('patient_Id')['patient_Id'].transform('count')
df['Patient_Type'] = df['visit_count'].apply(lambda x: "Returning" if x > 1 else "New")

patient_type = df['Patient_Type'].value_counts().reset_index()
patient_type.columns = ['Type', 'Count']

fig2 = px.pie(
    patient_type,
    names='Type',
    values='Count',
    hole=0.5,
    title="New vs Returning Patients"
)


# 3️⃣ Department Retention
dept_ret = df.groupby('dept_Name')['patient_Id'].nunique().reset_index()

fig3 = px.bar(
    dept_ret,
    x='patient_Id',
    y='dept_Name',
    orientation='h',
    title="Retention by Department",
    color='patient_Id',
    color_continuous_scale="Teal"
)


# 4️⃣ Top Retained Doctors
doc_ret = df.groupby('Doctor_Name')['patient_Id'].nunique().reset_index() \
            .sort_values(by='patient_Id', ascending=False).head(5)

fig4 = px.bar(
    doc_ret,
    x='Doctor_Name',
    y='patient_Id',
    title="Top Doctors (Retention)",
    color='patient_Id',
    color_continuous_scale="Blues"
)


# 5️⃣ Visit Frequency Distribution
visit_freq = df['visit_count'].value_counts().reset_index()
visit_freq.columns = ['Visits', 'Count']

fig5 = px.bar(
    visit_freq,
    x='Visits',
    y='Count',
    title="Visit Frequency Distribution",
    color='Visits'
)


# ================= LAYOUT =================
def retention_layout():

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

                dcc.Dropdown(
                    id="ret-month",
                    options=[{"label": m, "value": m} for m in month_order if m in df['Month_Name'].unique()],
                    placeholder="Select Month",
                    clearable=True
                ),

                dcc.Dropdown(
                    id="ret-year",
                    options=[{"label": y, "value": y} for y in sorted(df['Year'].dropna().unique())],
                    placeholder="Select Year",
                    clearable=True
                ),

                dcc.Dropdown(
                    id="ret-doctor",
                    options=[{"label": d, "value": d} for d in df['Doctor_Name'].dropna().unique()],
                    placeholder="Select Doctor",
                    clearable=True
                ),

                dcc.Dropdown(
                    id="ret-dept",
                    options=[{"label": d, "value": d} for d in df['dept_Name'].dropna().unique()],
                    placeholder="Select Department",
                    clearable=True
                ),

            ], className="sidebar"),

            # CONTENT
            html.Div([

                html.H2("🔁 Patient Retention Analysis", className="section-title"),
                html.P("Analyze patient revisit trends, retention rate, and long-term engagement patterns",
                       className="section-subtitle"),

                html.Div(id="ret-kpi", className="kpi-container"),

                html.Div([
                    html.Div(dcc.Graph(id="ret-chart1", figure=fig1), className="chart-card"),
                    html.Div(dcc.Graph(id="ret-chart2", figure=fig2), className="chart-card"),
                ], className="charts"),

                html.Div([
                    html.Div(dcc.Graph(id="ret-chart3", figure=fig3), className="chart-card"),
                    html.Div(dcc.Graph(id="ret-chart4", figure=fig4), className="chart-card"),
                ], className="charts"),

                html.Div([
                    html.Div(dcc.Graph(id="ret-chart5", figure=fig5), className="chart-card"),
                ], className="charts"),
                page_metadata(),
                page_footer(),

            ], className="content")

        ], className="main")

    ])