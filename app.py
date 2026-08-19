import streamlit as st
import pyodbc
from google import genai

# ==========================================
# 🔌 PART 1: DATABASE CONNECTIONS & MAPPING FUNCTIONS
# ==========================================

def get_db_connection():
    """Establishes connection to your SQL Server database."""
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=diabetesselector-db-server.database.windows.net;"
        "Database=mn_diabetes_tt_gen-db;"
        "Uid=mnaithai;"
        "Pwd=Mann@1234;" # ⚠️ Replace with your actual database password
    )
    return pyodbc.connect(conn_str)

def map_inputs_to_ids(age, bmi, fbs, duration_text, complication_text):
    """Maps raw numeric interface inputs to your database category IDs."""
    
    # 1. Resolve Age ID (15-20=1, 21-30=2, 31-40=3, 41-65=4, 66-75=5, Else=7)
    if 15 <= age <= 20: age_id = 1
    elif 21 <= age <= 30: age_id = 2
    elif 31 <= age <= 40: age_id = 3
    elif 41 <= age <= 65: age_id = 4
    elif 66 <= age <= 75: age_id = 5
    else: age_id = 7
    
    # 2. Resolve BMI ID (17-23=1, 24-25=2, 26-28=3, 29-32=4, Else=5)
    if 17.0 <= bmi <= 23.0: bmi_id = 1
    elif 24.0 <= bmi <= 25.0: bmi_id = 2
    elif 26.0 <= bmi <= 28.0: bmi_id = 3
    elif 29.0 <= bmi <= 32.0: bmi_id = 4
    else: bmi_id = 5
    
    # 3. Resolve Fasting Blood Sugar (su_id) (100-125=1, 126-150=2, 151-175=3, 176-200=4, Else=5)
    if 100 <= fbs <= 125: su_id = 1
    elif 126 <= fbs <= 150: su_id = 2
    elif 151 <= fbs <= 175: su_id = 3
    elif 176 <= fbs <= 200: su_id = 4
    else: su_id = 5

    # 4. Resolve Context Dimensions
    duration_id = 1 if duration_text == "1-5" else 2
    comp_id = 1 if complication_text == "yes" else 0
    
    return duration_id, comp_id, age_id, bmi_id, su_id


# ==========================================
# 🎨 STREAMLIT INTERFACE SETUP (Your Existing Layout Codes)
# ==========================================

st.set_page_config(page_title="T2D Recommendation System", layout="centered")
st.title("🩺 Type 2 Diabetes Treatment Selector")
st.write("Enter raw patient metrics below. The application will compute ranges and query recommendations automatically.")

# 1. RAW NUMERIC INPUTS
age = st.number_input("Patient Age (years)", min_value=1, max_value=120, value=38, step=1)

col1, col2 = st.columns(2)
with col1:
    height_cm = st.number_input("Height (cm)", min_value=50, max_value=250, value=170, step=1)
with col2:
    weight_kg = st.number_input("Weight (kg)", min_value=10, max_value=300, value=70, step=1)

fbs_value = st.number_input("Fasting Blood Sugar (mg/dL)", min_value=50, max_value=500, value=110, step=1)

# Dropdown selections
duration_text = st.selectbox("Disease Duration (years)", ["1-5", "6-40"])
complication_text = st.selectbox("Co-morbidities / Cardiorenal Risk?", ["no", "yes"])


# ==========================================
# 🧮 AUTOMATED METRIC COMPUTATION
# ==========================================

# Dynamically calculate BMI based on user input height and weight
if height_cm > 0:
    height_m = height_cm / 100
    calculated_bmi = round(weight_kg / (height_m ** 2), 2)
else:
    calculated_bmi = 22.0

st.write(f"**Calculated BMI:** {calculated_bmi} kg/m²")


# ==========================================
# ⚡ PART 2: EXECUTE DYNAMIC RULES MATRIX
# ==========================================

st.subheader("📋 Personalized Treatment Protocol Orders")

# Execute database call using current live values from UI inputs above
try:
    # Get the correct category ids based on sliders
    d_id, c_id, a_id, b_id, s_id = map_inputs_to_ids(
        age, calculated_bmi, fbs_value, duration_text, complication_text
    )
    
    # Query your specific mapping junction table
    query = """
        SELECT r.display_order, d.drug
        FROM [dbo].[Copy of 7.29.2026 9.25.24 PM - data to import 3 rule data 3.3] r
        INNER JOIN [dbo].[Drug_Dosage_Rules] d ON r.drug_id = d.drug_id
        WHERE r.duration_id = ? 
          AND r.comp_id = ? 
          AND r.age_id = ? 
          AND r.bmi_id = ? 
          AND r.su_id = ?
        ORDER BY r.display_order ASC;
    """
    
    # Open connection, execute lookup, close connection safely
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (d_id, c_id, a_id, b_id, s_id))
    rows = cursor.fetchall()
    
    # Render rows into a styled output container
    if rows:
        for row in rows:
            st.markdown(f"**Step {row.display_order}:** {row.drug}")
    else:
        st.info("No explicit medicine mapping found in the database matrix for this specific criteria combination. Defaulting to general diet guidelines.")

    cursor.close()
    conn.close()

except Exception as e:
    st.error(f"Could not connect to database or fetch rules: {e}")
