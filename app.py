import streamlit as st
import pyodbc
from google import genai

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

duration = st.selectbox("Disease Duration (years)", ["1-5", "6-40"])
duration_id = 1 if duration == "1-5" else 2

complications = st.selectbox("Complications Status", ["No Complications", "yes"])
comp_id = 0 if complications == "No Complications" else 1


# =========================================================================
# 2. HIDDEN BACKGROUND LOGIC (Automated Formula Tracking)
# =========================================================================
bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
st.info(f"💡 Calculated Patient BMI: **{bmi}**") 

# Age Group Range Routing
if 15 <= age <= 20: age_id = 1
elif 21 <= age <= 30: age_id = 2
elif 31 <= age <= 40: age_id = 3
elif 41 <= age <= 65: age_id = 4
elif 66 <= age <= 75: age_id = 5
elif 1 <= age <= 14: age_id = 6
else: age_id = 7

# BMI Range Routing
if 17 <= bmi <= 23: bmi_id = 1
elif 24 <= bmi <= 25: bmi_id = 2
elif 26 <= bmi <= 30: bmi_id = 3
elif 29 <= bmi <= 32: bmi_id = 4
elif 33 <= bmi <= 40: bmi_id = 5
elif 17 <= bmi <= 40: bmi_id = 6
else: bmi_id = 7

# Fasting Blood Sugar Range Routing
if 100 <= fbs_value <= 125: su_id = 1
elif 126 <= fbs_value <= 150: su_id = 2
elif 151 <= fbs_value <= 175: su_id = 3
elif 176 <= fbs_value <= 200: su_id = 4
elif 201 <= fbs_value <= 300: su_id = 5
else: su_id = 6


# =========================================================================
# 3. ACTION TRIGGER: FETCH FROM AZURE & GENERATE DETAILED AI PROTOCOLS
# =========================================================================
if st.button("Get Recommended Treatment Plan", type="primary"):
    st.write("🔄 Querying database using hidden background IDs...")
    
    matched_drug = "Diet & Exercise" # Default Fallback
    
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
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        query = """
            SELECT d.drug
            FROM [dbo].[Copy of 7.29.2026 9.25.24 PM - data to import 3 rule data 3.3] r
            INNER JOIN [dbo].[Copy of 7.29.2026 9.25.24 PM - data to import 3-category-data drug] d 
                ON r.drug_id = d.drug_id
            WHERE r.age_id = ? 
              AND r.bmi_id = ? 
              AND r.su_id = ? 
              AND r.duration_id = ? 
              AND r.comp_id = ?
        """
        
        cursor.execute(query, (age_id, bmi_id, su_id, duration_id, comp_id))
        row = cursor.fetchone()
        if row:
            matched_drug = row[0]
            st.success("✅ Master record successfully matched inside database matrix!")
        else:
            st.warning("⚠️ No exact database match found. Defaulting to baseline guidelines.")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        st.error("❌ Live Database lookup failed. Proceeding with safety fallback protocols.")
        st.code(str(e))

    # =========================================================================
    # 4. AI CONTENT GENERATION ENGINE (Restores your detailed layouts)
    # =========================================================================
    st.write("🔄 Generating detailed clinical layout via Gemini AI engine...")

# 1. Get the API Key from secrets
api_key_string = st.secrets.get("gemini_api_key") or st.secrets.get("GEMINI_API_KEY")

# 2. Check if the key exists
if not api_key_string:
    st.error("⚠️ Configuration Error: Gemini API key is missing from Streamlit secrets setup.")
    st.stop()

# 3. Safely initialize the Gemini Client
try:
        client = genai.Client(api_key=api_key_string)
except Exception as e:
        st.error(f"❌ Failed to initialize Gemini Client: {e}")
        st.stop()

# 4. Set up your prompt (Leave line 132 and below exactly as they were)
ai_prompt = f"""
        You are an advanced medical assistant. Generate a highly detailed Type 2 Diabetes treatment printout based on the following verified database result:
        - Matched Treatment Strategy: {matched_drug}
        - Patient Metrics: Age {age}, BMI {bmi}, Fasting Blood Sugar {fbs_value} mg/dl.

        Format the output into exactly these three distinct sections:

        1. Treatment Protocol Order:
        Provide a clean numbered list starting with the strategy "{matched_drug}". Include clear review timelines (e.g., "REVIEW AFTER 1 WEEK WITH F,PP,RFT,LFT,LIPIDS WITH YOUR ENDOCRINOLOGIST").

        2. Hypoglycemia Alert Protocols (In Hindi language text):
        Provide a warning box layout detailing signs (sweating, fast heartbeat, hunger) and the explicit "Rule of 15" treatment step-by-step using sweet options in clear Hindi points.

        3. Lifestyle Prescription (In Hindi language text):
        Provide detailed personalized nutrition matrices (including complex carbs, protein targets, low glycemic indices) and tailored physical activity constraints (aerobic minutes targets, sedentary rules, and resistance exercises) entirely in clear Hindi text points.
"""
try:        
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=ai_prompt,
        )
        
        # Display the complete layout straight onto your screen panels
        st.markdown(response.text)
        st.success("🎉 Comprehensive management guidelines completely restored!")
        
    except Exception as ai_err:
        st.error("❌ Failed to communicate with the Gemini AI processing server.")
        st.code(str(ai_err))
