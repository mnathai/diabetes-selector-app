import streamlit as st
import pyodbc

st.set_page_config(page_title="T2D Recommendation System", layout="centered")

st.title("🏥 Type 2 Diabetes Treatment Selector")
st.write("Enter raw patient metrics below. The application will compute ranges and query recommendations automatically.")

# =========================================================================
# 1. RAW NUMERIC INPUTS (Hides the old range dropdown selectors)
# =========================================================================
age = st.number_input("Patient Age (years)", min_value=1, max_value=120, value=30, step=1)

col1, col2 = st.columns(2)
with col1:
    height_cm = st.number_input("Height (cm)", min_value=50, max_value=250, value=170, step=1)
with col2:
    weight_kg = st.number_input("Weight (kg)", min_value=10, max_value=300, value=70, step=1)

fbs_value = st.number_input("Fasting Blood Sugar (mg/dl)", min_value=50, max_value=500, value=110, step=1)

# Keep standard dropdown fields for text-based non-calculated properties
duration = st.selectbox("Disease Duration (years)", ["1-5", "6-40"])
duration_id = 1 if duration == "1-5" else 2

complications = st.selectbox("Complications Status", ["No Complications", "yes"])
comp_id = 0 if complications == "No Complications" else 1


# =========================================================================
# 2. HIDDEN BACKGROUND LOGIC (Automated Formula Tracking)
# =========================================================================
# Formula calculation for BMI
bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
st.info(f"💡 Calculated Patient BMI: **{bmi}**") 

# Background Mapping: Automatically directing values to correct table IDs
# Age Group Range Routing
if 15 <= age <= 20: 
    age_id = 1
elif 21 <= age <= 30: 
    age_id = 2
elif 31 <= age <= 40: 
    age_id = 3
elif 41 <= age <= 65: 
    age_id = 4
elif 66 <= age <= 75: 
    age_id = 5
elif 1 <= age <= 14: 
    age_id = 6
else: 
    age_id = 7  # 75-100 group

# BMI Range Routing
if 17 <= bmi <= 23: 
    bmi_id = 1
elif 24 <= bmi <= 25: 
    bmi_id = 2
elif 26 <= bmi <= 30: 
    bmi_id = 3
elif 29 <= bmi <= 32: 
    bmi_id = 4
elif 33 <= bmi <= 40: 
    bmi_id = 5
elif 17 <= bmi <= 40: 
    bmi_id = 6
else: 
    bmi_id = 7

# Fasting Blood Sugar Range Routing
if 100 <= fbs_value <= 125: 
    su_id = 1
elif 126 <= fbs_value <= 150: 
    su_id = 2
elif 151 <= fbs_value <= 175: 
    su_id = 3
elif 176 <= fbs_value <= 200: 
    su_id = 4
elif 201 <= fbs_value <= 300: 
    su_id = 5
else: 
    su_id = 6


# =========================================================================
# 3. ACTION TRIGGER: FETCH FROM AZURE DATABASE & DISPLAY EXACT FIELDS
# =========================================================================
if st.button("Get Recommended Treatment Plan", type="primary"):
    st.write("🔄 Querying database using hidden background IDs...")
    
    try:
        # Build the database connection string using your Streamlit Secrets variables
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={st.secrets['server']};"
            f"DATABASE={st.secrets['database']};"
            f"UID={st.secrets['username']};"
            f"PWD={st.secrets['password']};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        
        # Connect to server
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Combined SQL execution to find the correct text mappings
        query = """
            SELECT d.drug, s.SafetyAlertText, c.ContraindicationText
            FROM [dbo].[Copy of 7.29.2026 9.25.24 PM - data to import 3 rule data 3.3] r
            LEFT JOIN [dbo].[Copy of 7.29.2026 9.25.24 PM - data to import 3-category-data drug] d 
                ON r.drug_id = d.drug_id
            LEFT JOIN [dbo].[Biometric_Safety_Alerts] s 
                ON r.age_id = s.age_id
            LEFT JOIN [dbo].[Clinical_Contraindications] c 
                ON r.comp_id = c.comp_id
            WHERE r.age_id = ? 
              AND r.bmi_id = ? 
              AND r.su_id = ? 
              AND r.duration_id = ? 
              AND r.comp_id = ?
        """
        
        cursor.execute(query, (age_id, bmi_id, su_id, duration_id, comp_id))
        row = cursor.fetchone()
        
        if row:
            st.success("✅ Records successfully retrieved from database mapping matrices!")
            
            # Area 1: Treatment Protocol Output (Pulls the name from column 0)
            st.header("💉 Recommended Treatment Plan")
            st.write(f"The recommended drug for this metric profile is: **{row[0]}**")
            
            # Area 2: Safety Hypoglycemia Alert Output (Pulls the text from column 1)
            st.warning("⚠️ Critical Safety Monitor: Hypoglycemia Alert Protocols")
            st.write(row[1] if row[1] else "Standard glucose warning precautions apply.")
            
            # Area 3: Lifestyle Prescription Output (Pulls the text from column 2)
            st.header("🥗 Structured Lifestyle Prescription Matrix")
            st.write(row[2] if row[2] else "Engage in 150 minutes of moderate aerobic exercise weekly.")
            
        else:
            st.warning("⚠️ No exact clinical match found in the database matrix for these specific tracking ID configurations.")
            st.caption(f"Debug Matrix Tracker: Age ID:{age_id} | BMI ID:{bmi_id} | Sugar ID:{su_id} | Duration ID:{duration_id} | Comp ID:{comp_id}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        st.error("❌ Database Connection Error occurred.")
        st.code(str(e))
