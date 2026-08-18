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
        
        # SQL Query statement matching your map table exactly
        # ⚠️ CRITICAL: Replace 'your_table_name' with your actual Azure SQL database table name!
        query = """
            SELECT drug_recommendation, hypoglycemia_alert, lifestyle_prescription
            FROM [dbo].[Copy of 7.29.2026 9.25.24 PM - data to import 3.cvs rule data 5]
            WHERE age_id = ? 
              AND bmi_id = ? 
              AND su_id = ? 
              AND duration_id = ? 
              AND comp_id = ?
        """
        
        cursor.execute(query, (age_id, bmi_id, su_id, duration_id, comp_id))
        row = cursor.fetchone()
        
        if row:
            st.success("✅ Records successfully retrieved from database mapping matrices!")
            
            # Area 1: Treatment Protocol Order output
            st.header("💉 Recommended Treatment Plan")
            st.write(str(row[0]))
            
            # Area 2: Safety Hypoglycemia Alert output
            st.warning("⚠️ Critical Safety Monitor: Hypoglycemia Alert Protocols")
            st.write(str(row[1]))
            
            # Area 3: Lifestyle Prescription output
            st.header("🥗 Structured Lifestyle Prescription Matrix")
            st.write(str(row[2]))
            
        else:
            st.warning("⚠️ No exact clinical match found in the database matrix for these specific tracking ID configurations.")
            st.caption(f"Debug Matrix Tracker: Age ID:{age_id} | BMI ID:{bmi_id} | Sugar ID:{su_id} | Duration ID:{duration_id} | Comp ID:{comp_id}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        st.error("❌ Database Connection Error occurred.")
        st.code(str(e))
