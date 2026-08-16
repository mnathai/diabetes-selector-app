import streamlit as st

st.set_page_config(page_title="T2D Recommendation System", layout="centered")

st.title("🏥 Type 2 Diabetes Treatment Selector")
st.write("Enter raw patient metrics below. The application will compute ranges and query recommendations automatically.")

# 1. Clean Numeric User Inputs (Hides the old range dropdowns)
age = st.number_input("Patient Age (years)", min_value=1, max_value=120, value=30, step=1)

col1, col2 = st.columns(2)
with col1:
    height_cm = st.number_input("Height (cm)", min_value=50, max_value=250, value=170, step=1)
with col2:
    weight_kg = st.number_input("Weight (kg)", min_value=10, max_value=300, value=70, step=1)

fbs_value = st.number_input("Fasting Blood Sugar (mg/dl)", min_value=50, max_value=500, value=110, step=1)

# 2. Hidden Background Logic: Calculating BMI automatically
bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
st.info(f"💡 Calculated Patient BMI: **{bmi}**") 

# 3. Background Mapping: Sorting inputs into your table's IDs
# Age Group ID Mapping
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

# BMI Range ID Mapping
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

# Fasting Blood Sugar ID Mapping
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

# Keep standard dropdown fields for text-based properties
duration = st.selectbox("Disease Duration (years)", ["1-5", "6-40"])
duration_id = 1 if duration == "1-5" else 2

complications = st.selectbox("Complications Status", ["No Complications", "yes"])
comp_id = 0 if complications == "No Complications" else 1

# Action Trigger Button
if st.button("Get Recommended Treatment Plan", type="primary"):
    st.write("Querying database using background IDs...")
    st.write(f"Parameters sent: Age ID: {age_id} | BMI ID: {bmi_id} | Sugar ID: {su_id} | Duration ID: {duration_id} | Comp ID: {comp_id}")
    # Your pyodbc / st.connection logic goes here using these ID integers
