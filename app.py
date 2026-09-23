import dash
from dash import html, dcc, Input, Output, State
from dash import no_update
import pandas as pd
import plotly.express as px

from login import login_layout
from dashboard import dashboard_layout, df
from dashboard_pages.appointment import appointment_layout
from dashboard_pages.noshow import noshow_layout
from dashboard_pages.retention import retention_layout
from dashboard_pages.doctor import doctor_layout

from home import home_layout, register_home_callbacks

app = dash.Dash(__name__, suppress_callback_exceptions=True)
register_home_callbacks(app)

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id="session-user", data="Admin"),  
    html.Div(id='page-content')
])

# ================= PAGE ROUTING =================
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):

    if pathname == '/dashboard':
        return dashboard_layout()
    elif pathname == '/home':
        return home_layout()
    elif pathname == '/appointment':
        return appointment_layout()
    elif pathname == '/noshow':
        return noshow_layout()
    elif pathname == '/retention':
        return retention_layout()
    elif pathname == '/doctor':
        return doctor_layout()
    elif pathname == '/':
        return login_layout
    return login_layout

# =================== global chart stle ===========
def apply_chart_theme(fig):
    fig.update_layout(
        # ===== BACKGROUND =====
        plot_bgcolor="#f6faff",   # ultra soft blue (premium look)
        paper_bgcolor="white",

        # ===== TITLE =====
        title={
            "x": 0.02,
            "xanchor": "left",
            "font": {"size": 17, "color": "#1f2937"}
        },

        # ===== FONT =====
        font=dict(
            family="Segoe UI",
            size=13,
            color="#374151"
        ),

        # ===== MARGINS =====
        margin=dict(l=30, r=20, t=50, b=30),

        # ===== LEGEND =====
        legend=dict(
            orientation="h",
            y=-0.2,
            x=0,
            bgcolor="rgba(0,0,0,0)"
        ),

        # ===== HOVER =====
        hovermode="x unified"
    )

    # ===== AXIS STYLE =====
    fig.update_xaxes(
        showgrid=False,
        linecolor="#d1d5db"
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(0,0,0,0.06)",  # very soft lines
        zeroline=False
    )

    return fig
# ================= LOGIN =================
@app.callback(
    Output('url', 'pathname'),
    Output('error-popup', 'displayed'),
    Output('session-user', 'data'),   
    Input('login-btn', 'n_clicks'),
    State('username', 'value'),
    State('password', 'value')
)
def login(n, username, password):
    if n:
        if username == "admin" and password == "1234":
            return '/home', False, username   # ✅ STORE USERNAME
        else:
            return no_update, True, None
    return no_update, False, None

# ================= LOGOUT =================
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-btn', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n):
    if n:
        return '/'
    return dash.no_update

# ================= DASHBOARD LOGIC =================
import plotly.express as px 
from dashboard import df

@app.callback(
    Output("kpi-container", "children"),
    Output("chart1", "figure"),
    Output("chart2", "figure"),
    Output("chart3", "figure"),
    Output("chart4", "figure"),
    Output("chart5", "figure"),
    Output("chart6", "figure"),
    Output("chart7", "figure"),

    Input("month-filter", "value"),
    Input("year-filter", "value"),
    Input("doctor-filter", "value"),
    Input("dept-filter", "value"),
    Input("gender-filter", "value"),
    Input("time-filter", "value"),
    Input("patient-filter", "value"),          
)
def update_dashboard(month, year, doctor, dept, gender, time, patient):

    dff = df.copy()

    # ===== FILTERS =====
    if month:
        dff = dff[dff['Month_Name'] == month]
    if year:
        dff = dff[dff['Year'] == year]
    if doctor:
        dff = dff[dff['Doctor_Name'] == doctor]
    if dept:
        dff = dff[dff['dept_Name'] == dept]
    if gender:
        dff = dff[dff['Patient_Gender'] == gender]
    if time:
        dff = dff[dff['Time_Slot'] == time]
    if patient:
        dff = dff[dff['patient_Id'] == patient]


    # ===== IF NO DATA (SAFE FIX) =====
    if dff.empty:
        empty_fig = px.bar(title="No Data Available")
        return dash.no_update, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # ===== KPI =====
    total_app = len(dff)
    total_pat = dff['patient_Id'].nunique()
    no_show = round((dff['No_Show_Flag'].sum() / total_app) * 100, 2) if total_app else 0

    dff['appointment_status'] = dff['appointment_status'].astype(str).str.lower()

    attended_df = dff[dff['appointment_status'].isin(["completed", "attended"])]
    lost_df = dff[dff['appointment_status'].isin(["no show", "cancelled", "canceled"])]

    total_revenue = attended_df['payment_amount'].sum()
    revenue_loss = lost_df['payment_amount'].sum()

    def kpi_card(icon, title, value, color, extra_class=""):
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
        ], className=f"kpi-card-home {extra_class}")

    kpi = [
        kpi_card("👥", "Patients", total_pat, "#2563eb", "kpi-blue"),
        kpi_card("📅", "Appointments", total_app, "#0ea5e9", "kpi-blue"),
        kpi_card("💰", "Revenue", f"₹{round(total_revenue,2)}", "#16a34a", "kpi-green"),
        kpi_card("📉", "Loss", f"₹{round(revenue_loss,2)}", "#f59e0b", "kpi-yellow"),
        kpi_card("❌", "No-Show", f"{no_show}%", "#dc2626", "kpi-red"),
    ]

    # ================= CHART 1 (LINE - TREND) =================
    monthly_df = dff.groupby("Month_Name").agg(
        Total_Appointments=("Month_Name", "count"),
        No_Show=("No_Show_Flag", "sum")
    ).reset_index()
    monthly_long = monthly_df.melt(
        id_vars="Month_Name",
        value_vars=["Total_Appointments", "No_Show"],
        var_name="Metric",
        value_name="Count"
    )
    fig1 = px.line(
        monthly_long,
        x="Month_Name",
        y="Count",
        color="Metric",
        title="Monthly Appointment vs No-Show Trend",
        markers=True,
        color_discrete_map={
            "Total_Appointments": "#00b4d8",
            "No_Show": "#ef4444"
        }
    )
    apply_chart_theme(fig1)

    # ================= CHART 2 (BAR + TREND LINE OVERLAY) =================
    dff['visit_count'] = dff.groupby('patient_Id')['patient_Id'].transform('count')
    dff['patient_type'] = dff['visit_count'].apply(lambda x: "Returning" if x > 1 else "New")

    dept_retention = dff.groupby(['dept_Name', 'patient_type']).size().reset_index(name='Count')

    fig2 = px.bar(
        dept_retention,
        x='dept_Name',
        y='Count',
        color='patient_type',
        barmode='group',
        title="Department wise Patient Retention (New vs Returning Patients)",
        color_discrete_map={
            "New": "#00b4d8",
            "Returning": "#02722c"
        }
    )
    apply_chart_theme(fig2)

    # ================= CHART 3 (PROFESSIONAL TOP DOCTORS - HORIZONTAL) =================
    doc = dff['Doctor_Name'].value_counts().head(5).reset_index()
    doc.columns = ['Doctor', 'Count']

    doc = doc.sort_values('Count', ascending=True)  # important for horizontal look

    fig3 = px.bar(
        doc,
        x='Count',
        y='Doctor',
        orientation='h',
        title="Top Doctors by Appointments and Revenue",
        text='Count',
        color='Count',
        color_continuous_scale=[
            "#59b5f2",
            "#0463bc",
            "#045398",
            "#054a82"
        ]
    )

    fig3.update_traces(textposition='outside')
    apply_chart_theme(fig3)

    # ================= CHART 4 (FILLED PIE - DONUT STYLE) =================
    dff['appointment_status'] = dff['appointment_status'].astype(str).str.lower().str.strip()
    fig4 = px.sunburst(
        dff,
        path=['Patient_Gender', 'appointment_status'],
        title="Gender-wise Appointment Outcomes (Completed / No-show / Cancelled)"
    )
    apply_chart_theme(fig4)


    # ================= CHART 5 (STACKED BAR - DEPARTMENT LOAD) =================
    dept_df = dff.groupby(['dept_Name', 'appointment_status']).size().reset_index(name='Count')

    # normalize status (VERY IMPORTANT for consistency)
    dept_df['appointment_status'] = dept_df['appointment_status'].str.lower()

    fig5 = px.bar(    
        dept_df,
        x='dept_Name',
        y='Count',
        color='appointment_status',
        title="Department Load (Stacked View)",
        barmode='stack',
        color_discrete_map={
            "completed": "#16a34a",   
            "No_Show": "#ef1a1a",
            "cancelled": "#cd2c31",
            "scheduled": "#5fccea"
        }
    )
    apply_chart_theme(fig5)

# ================= CHART 6 (TIME SLOT DISTRIBUTION) =================
    time_df = dff.groupby("Time_Slot").agg(
        Total_Appointments=("Time_Slot", "count"),
        No_Show=("No_Show_Flag", "sum")
    ).reset_index()

    time_long = time_df.melt(
        id_vars="Time_Slot",
        value_vars=["Total_Appointments", "No_Show"],
        var_name="Metric",
        value_name="Count"
    )

    fig6 = px.bar(
        time_long,
        x="Time_Slot",
        y="Count",
        color="Metric",
        barmode="group",
        title="Time Slot Efficiency (Appointments vs No-Show)",
        color_discrete_map={
            "Total_Appointments": "#1f77b4",
            "No_Show": "#ef4444"
        }
    )
    apply_chart_theme(fig6)

    # ================= CHART 7 (TOP MEDICAL CONDITIONS) =================
    if 'Diagnosis' in dff.columns:

        # Split combined diagnosis strings into separate diagnoses
        diagnosis_series = (
            dff[['patient_Id', 'Diagnosis']]
            .dropna()
            .assign(Diagnosis=lambda x: x['Diagnosis'].str.split(','))
            .explode('Diagnosis')
        )

        # Clean spaces
        diagnosis_series['Diagnosis'] = diagnosis_series['Diagnosis'].str.strip()

        # Count unique patients for each diagnosis
        diagnosis_df = (
            diagnosis_series
            .groupby('Diagnosis')['patient_Id']
            .nunique()
            .reset_index(name='Patient_Count')
            .sort_values('Patient_Count', ascending=False)
            .head(10)
        )

        # Create professional horizontal bar chart
        fig7 = px.bar(
            diagnosis_df,
            x='Patient_Count',
            y='Diagnosis',
            orientation='h',
            title="Top Most Common Diagnoses by Patient Count",
            text='Patient_Count',
            color='Patient_Count',
            color_continuous_scale=[
                "#59b5f2",
                "#0463bc",
                "#045398",
                "#054a82"
            ]
        )

        # Show highest value at top
        fig7.update_layout(yaxis={'categoryorder': 'total ascending'})

        # Position labels outside bars
        fig7.update_traces(textposition='outside')

        apply_chart_theme(fig7)

    else:
        fig7 = px.bar(title="Diagnosis Data Not Available")
        apply_chart_theme(fig7)

    return kpi, fig1, fig2, fig3, fig4, fig5, fig6, fig7

# =================appointment===============
@app.callback(
    Output("app-kpi", "children"),
    Output("app-chart1", "figure"),
    Output("app-chart2", "figure"),
    Output("app-chart3", "figure"),
    Output("app-chart4", "figure"),
    Output("app-chart5", "figure"),

    Input("app-month", "value"),
    Input("app-year", "value"),
    Input("doctor-filter", "value"),
    Input("dept-filter", "value"),
)
def update_appointment(month, year, doctor, dept):

    dff = df.copy()

    # ================= FILTERS =================
    if month:
        dff = dff[dff["Month_Name"] == month]

    if year:
        dff = dff[dff["Year"] == year]

    if doctor:
        dff = dff[dff["Doctor_Name"] == doctor]

    if dept:
        dff = dff[dff["dept_Name"] == dept]

    # ================= SAFETY =================
    if dff.empty:
        empty_fig = px.bar(title="No Data Available")
        return [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # ================= KPI LOGIC =================
    total_app = len(dff)

    completed = len(dff[dff['appointment_status'].str.lower() == "completed"])

    cancelled = len(dff[dff['appointment_status'].str.lower().isin(["cancelled","canceled"])])

    avg_per_day = round(
        total_app / dff['appointment_Date'].dt.date.nunique(), 2
    )

    # 🔥 ADVANCED KPI
    busiest_dept = dff['dept_Name'].mode()[0] 
    top_doctor = dff['Doctor_Name'].mode()[0] 

    # ================= KPI UI =================
    def kpi_card(icon, title, value, color, extra_class=""):
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
        ], className=f"kpi-card-home {extra_class}")

    kpi = [
        kpi_card("📅", "Appointments", total_app, "#0ea5e9", "kpi-blue"),
        kpi_card("✅", "Completed", completed, "#16a34a", "kpi-green"),
        kpi_card("❌", "Cancelled", cancelled, "#dc2626", "kpi-red"),
        kpi_card("🏥", "Top Dept", busiest_dept, "#6366f1", "kpi-purple"),
        kpi_card("👨‍⚕️", "Top Doctor", top_doctor, "#8b5cf6", "kpi-purple"),
    ]

    # ================= CHARTS =================

    # 1️⃣ Monthly Trend (Line)
    monthly = dff.groupby('Month_Name').size().reset_index(name='Count')
    fig1 = px.line(monthly, x='Month_Name', y='Count', title="Monthly Trend")
    fig1.update_traces(line=dict(color="#00b4d8", width=3), mode="lines+markers")
    apply_chart_theme(fig1)

    # 2️⃣ Time Slot (Colored)
    time_df = dff['Time_Slot'].value_counts().reset_index()
    time_df.columns = ['Time Slot', 'Count']

    fig2 = px.bar(
        time_df,
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
    apply_chart_theme(fig2)

    # 3️⃣ Department (Horizontal)
    dept_df = dff['dept_Name'].value_counts().reset_index()
    dept_df.columns = ['Department', 'Count']

    fig3 = px.bar(
        dept_df,
        x='Count',
        y='Department',
        orientation='h',
        title="Department Workload",
        color='Count',
        color_continuous_scale=[
            "#59b5f2",
            "#0463bc",
            "#045398",
            "#054a82"
        ]
    )
    apply_chart_theme(fig3)

    # 4️⃣ Top Doctors (Gradient)
    doc_df = dff['Doctor_Name'].value_counts().head(5).reset_index()
    doc_df.columns = ['Doctor', 'Count']

    fig4 = px.bar(
        doc_df,
        x='Doctor',
        y='Count',
        title="Top Doctors",
        color='Count',
        color_continuous_scale=[
            "#59b5f2",
            "#0463bc",
            "#045398",
            "#054a82"
        ]
    )
    apply_chart_theme(fig4)

    # 5️⃣ Status (Donut)
    status_df = dff['appointment_status'].value_counts().reset_index()
    status_df.columns = ['Status', 'Count']

    fig5 = px.pie(
        status_df,
        names='Status',
        values='Count',
        hole=0.5,
        title="Appointment Status"
    )
    apply_chart_theme(fig5)

    return kpi, fig1, fig2, fig3, fig4, fig5

# ================= NO-SHOW callback =================
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

@app.callback(
    Output("noshow-kpi", "children"),
    Output("noshow-chart1", "figure"),
    Output("noshow-chart2", "figure"),
    Output("noshow-chart3", "figure"),
    Output("noshow-chart4", "figure"),
    Output("noshow-chart5", "figure"),

    Input("app-month", "value"),
    Input("app-year", "value"),
    Input("doctor-filter", "value"),
    Input("dept-filter", "value"),
)
def update_noshow(month, year, doctor, dept):

    dff = df.copy()

    # ================= FILTERS =================
    if month:
        dff = dff[dff["Month_Name"] == month]

    if year:
        dff = dff[dff["Year"] == year]

    if doctor:
        dff = dff[dff["Doctor_Name"] == doctor]

    if dept:
        dff = dff[dff["dept_Name"] == dept]

    # ================= SAFETY =================
    if dff.empty:
        empty_fig = px.bar(title="No Data Available")
        return [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # ================= KPI LOGIC =================
    total_app = len(dff)

    no_show_count = dff["No_Show_Flag"].sum()

    no_show_rate = round((no_show_count / total_app) * 100, 2) if total_app else 0

    lost_revenue = dff[dff['No_Show_Flag'] == 1]['payment_amount'].sum()
    
    # ⚠️ Risk Prediction (High Risk Patients %)
    high_risk_df = dff[dff['No_Show_Flag'] == 1]
    risk_score = round((len(high_risk_df) / total_app) * 100, 2) if total_app else 0
    # Risk Label
    if risk_score > 40:
        risk_label = "High"
    elif risk_score > 20:
        risk_label = "Medium"
    else:
        risk_label = "Low"

    # 🔥 ADVANCED KPIs
    worst_dept = dff.groupby("dept_Name")["No_Show_Flag"].sum().idxmax()
    worst_doctor = dff.groupby("Doctor_Name")["No_Show_Flag"].sum().idxmax()

    # ================= KPI UI =================
    def kpi_card(icon, title, value, color, extra_class=""):
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
        ], className=f"kpi-card-home {extra_class}")

    # ================= KPI UI =================
    kpi = [
        kpi_card("🚫", "No-Show Count", no_show_count, "#dc2626", "kpi-red"),
        kpi_card("⚠️", "Risk Level", f"{risk_label} ({risk_score}%)", "#8b5cf6", "kpi-purple"),
        kpi_card("📉", "Lost Revenue", f"₹{round(lost_revenue,2)}", "#ef4444", "kpi-red"),
        kpi_card("🏥", "Worst Dept", worst_dept, "#6366f1", "kpi-purple"),
        kpi_card("👨‍⚕️", "Worst Doctor", worst_doctor, "#10b981", "kpi-green"),
    ]
    
    # ================= CHARTS =================

    # 1️⃣ Trend
    trend = dff.groupby('Month_Name')["No_Show_Flag"].sum().reset_index()
    fig1 = px.line(trend, x='Month_Name', y='No_Show_Flag', title="No-Show Trend")
    fig1.update_traces(line=dict(color="#e74c3c", width=3), mode="lines+markers")
    apply_chart_theme(fig1)

    # 2️⃣ Time Slot
    time_df = dff.groupby("Time_Slot")["No_Show_Flag"].sum().reset_index()
    fig2 = px.bar(
        time_df,
        x="Time_Slot",
        y="No_Show_Flag",
        title="No-Show by Time Slot",
        color="Time_Slot",
        color_discrete_map={
            "Morning": "#f39c12",
            "Afternoon": "#00cec9",
            "Evening": "#6c5ce7"
        }
    )
    apply_chart_theme(fig2)

    # 3️⃣ Department (Horizontal)
    dept_df = dff.groupby("dept_Name")["No_Show_Flag"].sum().reset_index()
    fig3 = px.bar(
        dept_df,
        x="No_Show_Flag",
        y="dept_Name",
        orientation="h",
        title="Department No-Show Impact",
        color="No_Show_Flag",
        color_continuous_scale=[
            "#F4697B",
            "#D5374C",
            "#AC1C2F",
            "#810314"
        ]
    )
    apply_chart_theme(fig3)

    # 4️⃣ Doctor
    doc_df = dff.groupby("Doctor_Name")["No_Show_Flag"].sum().nlargest(5).reset_index()
    fig4 = px.bar(
        doc_df,
        x="Doctor_Name",
        y="No_Show_Flag",
        title="Top No-Show Doctors",
        color="No_Show_Flag",
        color_continuous_scale=[
            "#F4697B",
            "#D5374C",
            "#AC1C2F",
            "#810314"
        ]
    )
    apply_chart_theme(fig4)

    # 5️⃣ Donut
    status_df = dff["No_Show_Flag"].value_counts().reset_index()
    status_df.columns = ["Status", "Count"]

    fig5 = px.pie(
        status_df,
        names="Status",
        values="Count",
        hole=0.5,
        title="No-Show Distribution"
    )
    apply_chart_theme(fig5)

    return kpi, fig1, fig2, fig3, fig4, fig5

#================== Retention callback ===================
@app.callback(
    Output("ret-kpi", "children"),
    Output("ret-chart1", "figure"),
    Output("ret-chart2", "figure"),
    Output("ret-chart3", "figure"),
    Output("ret-chart4", "figure"),
    Output("ret-chart5", "figure"),

    Input("ret-month", "value"),
    Input("ret-year", "value"),
    Input("ret-doctor", "value"),
    Input("ret-dept", "value"),
)
def update_retention(month, year, doctor, dept):

    dff = df.copy()

    # ================= FILTERS =================
    if month:
        dff = dff[dff["Month_Name"] == month]

    if year:
        dff = dff[dff["Year"] == year]

    if doctor:
        dff = dff[dff["Doctor_Name"] == doctor]

    if dept:
        dff = dff[dff["dept_Name"] == dept]

    # ================= SAFETY =================
    if dff.empty:
        empty_fig = px.bar(title="No Data Available")
        return [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # ================= RETENTION LOGIC =================

    # Visit count per patient
    dff['visit_count'] = dff.groupby('patient_Id')['patient_Id'].transform('count')

    total_patients = dff['patient_Id'].nunique()

    returning_patients = dff[dff['visit_count'] > 1]['patient_Id'].nunique()

    new_patients = total_patients - returning_patients

    # Retention Rate
    retention_rate = round((returning_patients / total_patients) * 100, 2) if total_patients else 0

    # Avg Visits per Patient
    avg_visits = round(dff['visit_count'].mean(), 2)

    # Loyalty Score (🔥 impressive KPI)
    loyalty_score = round((avg_visits * retention_rate) / 100, 2)

    # Top Dept / Doctor (Retention)
    top_dept = dff.groupby('dept_Name')['patient_Id'].nunique().idxmax()
    top_doctor = dff.groupby('Doctor_Name')['patient_Id'].nunique().idxmax()

    # ================= KPI UI =================
    def kpi_card(icon, title, value, color, extra_class=""):
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
        ], className=f"kpi-card-home {extra_class}")

    # ================= KPI UI =================
    kpi = [
        kpi_card("👥", "Total Patients", total_patients, "#2563eb", "kpi-blue"),
        kpi_card("🔁", "Returning", returning_patients, "#0ea5e9", "kpi-blue"),
        kpi_card("🆕", "New Patients", new_patients, "#f59e0b", "kpi-yellow"),
        kpi_card("📊", "Retention Rate", f"{retention_rate}%", "#16a34a", "kpi-green"),
        kpi_card("👨‍⚕️", "Top Doctor", top_doctor, "#8b5cf6", "kpi-purple"),
    ]

    # ================= CHARTS =================

    # 1️⃣ Retention Trend
    trend = dff.groupby('Month_Name')['patient_Id'].nunique().reset_index()
    fig1 = px.line(trend, x='Month_Name', y='patient_Id', title="Retention Trend")
    fig1.update_traces(line=dict(color="#00b4d8", width=3), mode="lines+markers")
    apply_chart_theme(fig1)

    # 2️⃣ New vs Returning (Donut)
    dff['Patient_Type'] = dff['visit_count'].apply(lambda x: "Returning" if x > 1 else "New")

    type_df = dff['Patient_Type'].value_counts().reset_index()
    type_df.columns = ['Type', 'Count']

    fig2 = px.sunburst(
    dff,
    path=['Patient_Type', 'dept_Name'],
    title="Patient Distribution (New vs Returning by Department)"
)
    apply_chart_theme(fig2)

    # 3️⃣ Dept Retention (Horizontal)
    dept_df = dff.groupby('dept_Name')['patient_Id'].nunique().reset_index()

    # ✅ Rename column for clarity
    dept_df.columns = ['Department', 'Patient_Count']

    fig3 = px.bar(
        dept_df,
        x='Patient_Count',
        y='Department',
        orientation='h',
        title="Department-wise Retention Trend",
        color='Patient_Count',
        color_continuous_scale="Teal"
    )
    apply_chart_theme(fig3)

    # 4️⃣ Top Doctors
    doc_df = dff.groupby('Doctor_Name')['patient_Id'].nunique().reset_index()
    doc_df.columns = ['Doctor_Name', 'Patient_Count']   # ✅ rename

    fig4 = px.scatter(
        doc_df,
        x='Doctor_Name',
        y='Patient_Count',
        size='Patient_Count',
        color='Patient_Count',
        title="Doctor Retention Performance",
        size_max=40
    )
    apply_chart_theme(fig4)

    # 5️⃣ Visit Frequency
    freq_df = dff['visit_count'].value_counts().reset_index()
    freq_df.columns = ['Visits', 'Count']
    
    fig5 = px.histogram(
    dff,
    x='visit_count',
    nbins=10,
    title="Patient Visit Frequency Distribution"
)
    apply_chart_theme(fig5)

    return kpi, fig1, fig2, fig3, fig4, fig5

# ================= DOCTOR PERFORMANCE =================
@app.callback(
    Output("doc-kpi", "children"),
    Output("doc-chart1", "figure"),
    Output("doc-chart2", "figure"),
    Output("doc-chart3", "figure"),
    Output("doc-chart4", "figure"),
    Output("doc-chart5", "figure"),

    Input("doc-month", "value"),
    Input("doc-year", "value"),
    Input("doc-filter", "value"),
    Input("dept-filter", "value"),
)
def update_doctor(month, year, doctor, dept):
    dff = df.copy()

    # ================= FILTERS =================
    if month:
        dff = dff[dff["Month_Name"] == month]
    if year:
        dff = dff[dff["Year"] == year]
    if doctor:
        dff = dff[dff["Doctor_Name"] == doctor]
    if dept:
        dff = dff[dff["dept_Name"] == dept]

    # ================= SAFETY =================
    if dff.empty:
        empty_fig = px.bar(title="No Data Available")
        return [], empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    # ================= KPI LOGIC =================
    total_docs = dff['Doctor_Name'].nunique()
    top_doc = dff['Doctor_Name'].value_counts().idxmax()
    avg_patients = round(
        dff.groupby('Doctor_Name')['patient_Id'].nunique().mean(), 2
    )

    completed_df = dff[dff['appointment_status'].str.lower().isin(["completed", "attended"])]
    efficiency = round((len(completed_df) / len(dff)) * 100, 2)

    revenue_per_doc = round(
        dff.groupby('Doctor_Name')['payment_amount'].sum().mean(), 2
    )

    # ================= KPI UI =================
    def kpi_card(icon, title, value, color, extra_class=""):
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
        ], className=f"kpi-card-home {extra_class}")

    # ================= KPI UI =================
    kpi = [
        kpi_card("👨‍⚕️", "Doctors", total_docs, "#2563eb", "kpi-blue"),
        kpi_card("🏆", "Top Doctor", top_doc, "#16a34a", "kpi-green"),
        kpi_card("📊", "Avg Patients/Doctor", avg_patients, "#0ea5e9", "kpi-blue"),
        kpi_card("⚡", "Efficiency", f"{efficiency}%", "#f59e0b", "kpi-yellow"),
        kpi_card("💰", "Avg Revenue/Doctor", f"₹{revenue_per_doc}", "#16a34a", "kpi-green"),
    ]

    # ================= CHARTS =================

    # Patient Count per doctor
    doc_df = dff.groupby('Doctor_Name')['patient_Id'].nunique().reset_index()
    doc_df.columns = ['Doctor_Name', 'Patient_Count']

    # ================= CHART 1 =================
    # Doctor Workload Trend (clean & meaningful)
    trend = dff.groupby(['Month_Name', 'Doctor_Name'])['patient_Id'].nunique().reset_index()
    trend.columns = ['Month_Name', 'Doctor_Name', 'Patient_Count']

    fig1 = px.line(
        trend,
        x='Month_Name',
        y='Patient_Count',
        color='Doctor_Name',
        title="Doctor Workload Trend (Patient Count)"
    )
    fig1.update_traces(line=dict(width=3), mode="lines+markers")
    apply_chart_theme(fig1)

    # ================= CHART 2 =================
    # Doctor Performance (Bubble - Patient Count)
    fig2 = px.scatter(
        doc_df,
        x='Doctor_Name',
        y='Patient_Count',
        size='Patient_Count',
        color='Patient_Count',
        title="Doctor Performance (Patient Count)",
        size_max=40
    )
    apply_chart_theme(fig2)

    # ================= CHART 3 =================
    # Revenue by Doctor
    rev_df = dff.groupby('Doctor_Name')['payment_amount'].sum().reset_index()

    fig3 = px.bar(
        rev_df,
        x='Doctor_Name',
        y='payment_amount',
        title="Revenue Generated by Doctors",
        color='payment_amount',
        color_continuous_scale=[
            "#59b5f2",
            "#0463bc",
            "#045398",
            "#054a82"
        ]
    )
    apply_chart_theme(fig3)

    # ================= CHART 4 =================
    # No-show Impact (clean + meaningful)
    noshow_df = dff.groupby('Doctor_Name')['No_Show_Flag'].sum().reset_index()
    noshow_df.columns = ['Doctor_Name', 'No_Show_Count']

    fig4 = px.bar(
        noshow_df,
        x='No_Show_Count',
        y='Doctor_Name',
        orientation='h',
        title="No-Show Impact by Doctor",
        color='No_Show_Count',
        color_continuous_scale=[
            "#F4697B",
            "#D5374C",
            "#AC1C2F",
            "#810314"
        ]
    )
    apply_chart_theme(fig4)

    # ================= CHART 5 =================
    # Status Distribution (better than messy sunburst)
    status_df = dff.groupby(['Doctor_Name', 'appointment_status']).size().reset_index(name='Count')

    fig5 = px.bar(
        status_df,
        x='Doctor_Name',
        y='Count',
        color='appointment_status',
        title="Doctor Appointment Status Distribution",
        barmode='stack'
    )
    apply_chart_theme(fig5)
    return kpi, fig1, fig2, fig3, fig4, fig5

if __name__ == '__main__':
    app.run(debug=True)    