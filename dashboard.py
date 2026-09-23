from components import page_metadata, page_footer
from dash import html, dcc
import pandas as pd
import plotly.express as px

# =================== LOAD DATA ===================
file_path = "CareFlow_Analytics_Final_Dataset.xlsx"

appointments = pd.read_excel(file_path, sheet_name="Appointment")
patients = pd.read_excel(file_path, sheet_name="Patients")
doctors = pd.read_excel(file_path, sheet_name="Doctor")
departments = pd.read_excel(file_path, sheet_name="Department")
medical_record = pd.read_excel(file_path, sheet_name="MedicalRecord")

# ==================== CLEAN DATA =================

for df_ in [appointments, patients, doctors, departments, medical_record]:
    df_.columns = df_.columns.str.strip()

appointments['appointment_Date'] = pd.to_datetime(
    appointments['appointment_Date'], errors='coerce'
)

# =========================
# 🔗 MERGE DATA
# =========================
df = appointments.merge(doctors, on="doct_Id", how="left")
df = df.merge(patients, on="patient_Id", how="left")
df = df.merge(departments, on="dept_Id", how="left")

### add diagnosis data safely
medical_record.columns = medical_record.columns.str.strip()

# Find diagnosis column automatically
diagnosis_col = None
for col in medical_record.columns:
    if str(col).strip().lower() in [
        "diagnosis",
        "diagnosis_name",
        "disease",
        "disease_name",
        "condition",
        "medical_condition"
    ]:
        diagnosis_col = col
        break

# Merge only if diagnosis column exists
if diagnosis_col:
    # Combine all diagnoses of each patient into one string
    diagnosis_summary = (
        medical_record
        .dropna(subset=[diagnosis_col])
        .groupby("patient_Id")[diagnosis_col]
        .apply(lambda x: ", ".join(sorted(set(x.astype(str)))))
        .reset_index()
        .rename(columns={diagnosis_col: "Diagnosis"})
    )

    # Merge one row per patient only
    df = df.merge(
        diagnosis_summary,
        on="patient_Id",
        how="left"
    )
else:
    # Create blank column if diagnosis not found
    df["Diagnosis"] = None


df.rename(columns={
    "Gender_x": "Doctor_Gender",
    "Gender_y": "Patient_Gender"
}, inplace=True)

# =========================
# 📅 BETTER DATE FEATURES
# =========================
df['Month_Name'] = df['appointment_Date'].dt.strftime('%b')   # Jan, Feb
df['Month_Num'] = df['appointment_Date'].dt.month
df['Year'] = df['appointment_Date'].dt.year

month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

df['Month_Name'] = pd.Categorical(df['Month_Name'], categories=month_order, ordered=True)

# =========================
# 📊 KPI LOGIC
# =========================
total_app = len(df)
total_pat = df['patient_Id'].nunique()
no_show_rate = round((df['No_Show_Flag'].sum() / total_app) * 100, 2)

df['appointment_status'] = df['appointment_status'].astype(str).str.lower()

attended_df = df[df['appointment_status'].isin(["completed", "attended"])]
lost_df = df[df['appointment_status'].isin(["no show", "cancelled", "canceled"])]

total_revenue = attended_df['payment_amount'].sum()
revenue_loss = lost_df['payment_amount'].sum()

# =========================
# 📈 CHARTS
# =========================
monthly = df.groupby('Month_Name').size().reset_index(name='Count')
fig1 = px.line(monthly, x='Month_Name', y='Count', title="Monthly Appointment Trend")

noshow = df['No_Show_Flag'].value_counts().reset_index()
noshow.columns = ['Status', 'Count']
fig2 = px.pie(noshow, names='Status', values='Count', title="No-Show Distribution by Gender")

doctor_data = df['Doctor_Name'].value_counts().head(5).reset_index()
doctor_data.columns = ['Doctor', 'Count']
fig3 = px.bar(doctor_data, x='Doctor', y='Count', title="Top Doctors by Appointment Trend")

gender_data = df['Patient_Gender'].value_counts().reset_index()
gender_data.columns = ['Gender', 'Count']
fig4 = px.pie(gender_data, names='Gender', values='Count', title="Appointment Distribution by Patient Gender")

dept_data = df['dept_Name'].value_counts().reset_index()
dept_data.columns = ['Department', 'Count']
fig5 = px.bar(dept_data, x='Department', y='Count', title="Department Load")

time_data = df['Time_Slot'].value_counts().reset_index()
time_data.columns = ['Time Slot', 'Count']
fig6 = px.bar(time_data, x='Time Slot', y='Count', title="Time Slot Distribution")

# =========================
# 🔥 KPI CARD FUNCTION (HOME STYLE)
# =========================
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

# =========================
# 🏥 DASHBOARD LAYOUT
# =========================
def dashboard_layout():
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
                dcc.Link("🏠 Dashboard", href="/dashboard", className="nav-item"),
                dcc.Link("📊 Appointment Analysis", href="/appointment", className="nav-item"),
                dcc.Link("🚫 No-Show Analysis", href="/noshow", className="nav-item"),
                dcc.Link("🔁 Patient Retention", href="/retention", className="nav-item"),
                dcc.Link("👨‍⚕️ Doctor Performance", href="/doctor", className="nav-item"),

                html.Hr(),

                html.H3("Filters"),

                dcc.Dropdown(
                    id="month-filter",
                    options=[{"label": m, "value": m} for m in month_order],
                    placeholder="Select Month",
                    clearable=True
                ),

                dcc.Dropdown(
                    id="year-filter",
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

                dcc.Dropdown(
                    id="gender-filter",
                    options=[{"label": g, "value": g} for g in df['Patient_Gender'].dropna().unique()],
                    placeholder="Select Gender",
                    clearable=True
                ),

                dcc.Dropdown(
                    id="time-filter",
                    options=[{"label": t, "value": t} for t in df['Time_Slot'].dropna().unique()],
                    placeholder="Select Time Slot",
                    clearable=True
                ),

                # ================= PATIENT FILTER =================
                dcc.Dropdown(
                    id="patient-filter",
                    options=[
                        {
                            "label": f"{int(pid)} - {name}",
                            "value": pid
                        }
                        for pid, name in (
                            df[['patient_Id', 'Patient_Name']]
                            .dropna()
                            .drop_duplicates(subset=['patient_Id'])
                            .sort_values('patient_Id')
                            .values
                        )
                    ],
                    placeholder="Select Patient",
                    clearable=True,
                    searchable=True
                ),
            ], className="sidebar"),

            # CONTENT
            html.Div([

                html.H2("📊 Executive Overview Dashboard", className="section-title"),
                html.P(
                    "Hospital Appointment Performance, Patient Retention and No-Show Analysis Dashboard",
                    className="section-subtitle"
                ),

                # ✅ ONLY ONE KPI CONTAINER
                html.Div(id="kpi-container", className="kpi-container"),

                # CHARTS
                html.Div([
                    html.Div(dcc.Graph(id="chart1"), className="chart-card"),
                    html.Div(dcc.Graph(id="chart2"), className="chart-card"),
                ], className="charts"),

                html.Div([
                    html.Div(dcc.Graph(id="chart3"), className="chart-card"),
                    html.Div(dcc.Graph(id="chart4"), className="chart-card"),
                ], className="charts"),

                html.Div([
                    html.Div(dcc.Graph(id="chart5"), className="chart-card"),
                    html.Div(dcc.Graph(id="chart6"), className="chart-card"),
                ], className="charts"),

                html.Div([
                    html.Div(dcc.Graph(id="chart7"),className="chart-card"),
                ], className="charts"),
                page_metadata(),
                page_footer(),
                
            ], className="content")

        ], className="main")
    ])
