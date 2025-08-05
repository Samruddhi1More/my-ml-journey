import streamlit as st
import pandas as pd
from datetime import date, datetime
from io import BytesIO
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import pickle
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
#------------------ setup ---------------------
today = date.today()
Data_dir = "data"
pdf_dir = "PDFs"
os.makedirs(Data_dir, exist_ok=True)
os.makedirs(pdf_dir,exist_ok=True)

Data_file = os.path.join(Data_dir, f"Prospect_data_{today}.csv")

GOOGLE_FOLDER_ID = "Your Google Folder ID"

#----------------- Google Drive Config ------------------
SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Access only files created/uploaded by app

def authenticate():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    token_file = 'token_drive.pkl'
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    # Always check for validity
    if not creds or not creds.valid:
        # If expired AND refresh token present, refresh it
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:  # If refresh fails, remove token and start fresh
                os.remove(token_file)
                creds = None
        if not creds or not creds.valid:
            # New authentication flow, overwrites the old token file
            flow = InstalledAppFlow.from_client_secrets_file(
                'Your client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
    return creds

def upload_to_drive(file_obj, file_name, folder_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    media = MediaIoBaseUpload(file_obj, mimetype='text/csv')
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return file.get('id')

#------------------ Page Config --------------------------
st.set_page_config(page_title="Arogyasampda 360", layout="wide", initial_sidebar_state="collapsed")

#---------------- Full Width Header ----------------------
col1, col2 = st.columns([1,8])
with col1:
    st.image("Your Company Logo.png", width=100)
with col2:
    st.markdown("""
    <div style='background-color: #4CAF50; padding: 15px; color:white; border-radius: 6px: display: flex; alien-items: center;'>
    <div>
        <h3 style='margin: 0;'>🧘 Arogyasampda 360 - Data Entry </h3>
        <p style='margin: 4px 0 0; font-size: 18px;'>Health Assessment and Managment System</p>
    </div>
    </div>
""", unsafe_allow_html=True)
    
#------------------ Utility Functions -----------------

def calculate_wh_ratio(waist, hip):
    return round(waist/hip,2) if hip else 0

def draw_label(c, label, value, x, y, label_width=140):
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, f"{label}:")
    c.setFont("Helvetica", 12)
    c.drawString(x + label_width, y, str(value))

def generate_pdf(record, pdf_path, logo_path):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    LEFT_MARGIN = 50
    RIGHT_MARGIN = 50
    content_width = width - LEFT_MARGIN - RIGHT_MARGIN

    # --- Banner Section ---
    belt_height = 80
    light_green = (0.7, 0.9, 0.7)
    c.setFillColorRGB(*light_green)
    c.rect(0, height - belt_height, width, belt_height, fill=1, stroke=0)

    # Logo
    logo = ImageReader(logo_path)
    logo_width = 70
    logo_height = 70
    logo_x = 30
    logo_y = height - logo_height - 5
    c.drawImage(logo, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')

    # Title: Centered in 2 lines inside the belt
    title_center_x = width // 2
    title_line1 = "WE ARE CONCERNED ABOUT"
    title_line2 = "YOUR HEALTH"

    c.setFillColorRGB(0, 0.3, 0)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(title_center_x, height - 30, title_line1)

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(title_center_x, height - 52, title_line2)
    c.setFillColorRGB(0, 0, 0)

    # BODY CONTENT START
    content_left = 50
    section_gap = 30
    line_height = 22
    col1_x = 50
    col2_x = 230
    col3_x = 410
    y = height - belt_height - 35

    # Section: Personal Info
    c.setFont("Helvetica-Bold", 14)
    c.drawString(content_left, y, "PERSONAL INFORMATION & BCA:")
    y -= section_gap
    y -= section_gap
    draw_label(c, "NAME", record.get("Name", ""), col1_x, y)
    draw_label(c, "DATE", record.get("Timestamp", ""), col3_x, y, label_width=60)
    y -= line_height

    draw_label(c, "AGE", record.get("Real Age", ""), col1_x, y)
    draw_label(c, "GENDER", record.get("Gender", ""), col2_x, y, label_width=70)
    y -= line_height

    draw_label(c, "HEIGHT (CM)", record.get("Height", ""), col1_x, y)
    draw_label(c, "WEIGHT (KG)", record.get("Weight", ""), col2_x, y, label_width=85)
    draw_label(c, "BMI", f"{record.get('BMI', '')} (18.5 to 23.5)", col3_x, y, label_width=53)
    y -= line_height

    draw_label(c, "HEALTHY WEIGHT REQ.", " ", col1_x, y)
    draw_label(c, "WEIGHT LOSS REQ. (KG)", " ", col2_x, y, label_width=53)
    y -= line_height

    draw_label(c, "WAIST (INCHES)", record.get("Waist", ""), col1_x, y)
    draw_label(c, "HIP (INCHES)  :", record.get("Hip", ""), col2_x, y, label_width=100)
    y -= line_height

    draw_label(c, "WAIST: HIP RATIO", record.get("W/H Ratio", ""), col3_x, y)
    c.setFont("Helvetica", 10)
    c.drawString(col2_x, y, "(Female <0.85, Male <1.0)")
    y -= line_height

    draw_label(c, "BODY FAT (%)", record.get("Body Fat", ""), col1_x, y)
    c.drawString(col2_x, y, "(F: 20–29.9%, M: 10–19.9%)")
    y -= line_height

    draw_label(c, "VISCERAL FAT", record.get("Visceral Fat", ""), col1_x, y)
    c.drawString(col2_x, y, "Range: 1–9")
    y -= line_height

    draw_label(c, "SKELETAL MUSCLE (%) ", record.get("Skeletal Muscle", ""), col1_x, y)
    c.drawString(col2_x, y, "(F: 28%, M: 37%)")
    y -= line_height

    draw_label(c, "BODY AGE", record.get("Body Age", ""), col1_x, y)
    draw_label(c, "Resting Metabolism", record.get("RM", ""), col2_x, y)
    y -= section_gap
    y -= section_gap

    # Separator
    c.line(40, y, width - 40, y)
    y -= line_height
    y -= section_gap

    # Professional Info
    c.setFont("Helvetica-Bold", 13)
    c.drawString(content_left, y, "PROFESSIONAL INFORMATION:")
    y -= line_height
    
    c.setFont("Helvetica", 12)
    c.drawString(content_left, y, "PROFESSION: ________________   WORKING HRS: ______   SCREEN TIME: ______")
    y -= section_gap
    y -= section_gap

    # Daily Routine
    c.setFont("Helvetica-Bold", 13)
    c.drawString(content_left, y, "DAILY ROUTINE:")
    y -= line_height
    
    c.setFont("Helvetica", 12)
    c.drawString(content_left, y, "WAKE UP TIME: ______    SLEEPING TIME: ______   TOTAL HRS: ______")
    y -= line_height
    c.drawString(content_left, y, "DEEP SLEEP: YES / NO    MOTION TIME: ______   REGULAR / IRREGULAR")
    y -= line_height
    c.drawString(content_left, y, "EXERCISE: WALK / RUN / GYM / YOGA   HRS/WEEK: ________________")
    y -= line_height
    c.drawString(content_left, y, "ALLERGIC TO: _________________________________________________")
    y -= section_gap
    y -= section_gap

    # Health/Chronic Conditions
    c.setFont("Helvetica-Bold", 13)
    c.drawString(content_left, y, "HEALTH CHALLENGES:")
    y -= line_height
    
    c.setFont("Helvetica", 12)
    c.drawString(content_left, y, "DIABETES (YES/NO): ______   Fasting: ______   PP: ______")
    y -= line_height
    c.drawString(content_left, y, "HYPERTENSION (YES/NO): ______   BP: ________ / ________")
    y -= line_height
    c.drawString(content_left, y, "OTHERS (If any): _____________________________________________")

    c.showPage()
  
    # --- Banner Section ---
    belt_height = 80
    light_green = (0.7, 0.9, 0.7)
    c.setFillColorRGB(*light_green)
    c.rect(0, height - belt_height, width, belt_height, fill=1, stroke=0)

    # Logo
    logo = ImageReader(logo_path)
    logo_width = 70
    logo_height = 70
    logo_x = 30
    logo_y = height - logo_height - 5
    c.drawImage(logo, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')

    # Title: Centered in 2 lines inside the belt
    title_center_x = width // 2
    title_line1 = "WE ARE CONCERNED ABOUT"
    title_line2 = "YOUR HEALTH"

    c.setFillColorRGB(0, 0.3, 0)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(title_center_x, height - 30, title_line1)

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(title_center_x, height - 52, title_line2)
    c.setFillColorRGB(0, 0, 0)


    # --- Habits Section ---
    section_y = logo_y - logo_height - 20
    c.setFont("Helvetica-Bold", 15)
    c.drawString(LEFT_MARGIN, section_y, "HABITS:")

    gap = 24
    c.setFont("Helvetica", 13)
    habits = [
        "TOBACCO: YES / NO",
        "SMOKING: YES / NO (IF YES, HOW MANY CIGARETTES PER DAY _____)",
        "ALCOHOL: YES / NO (IF YES, FREQUENCY _______ / _______ ML)",
        "OTHERS (IF ANY): ____________________________________"
    ]

    for habit in habits:
        section_y -= gap
        c.drawString(LEFT_MARGIN, section_y, habit)

    # --- DIETERY HABITS Table Section ---
    section_y -= 40  # Extra space to avoid overlap
    c.setFont("Helvetica-Bold", 14)
    c.drawString(LEFT_MARGIN, section_y, "DIETERY HABITS:")

    # Table Setup
    table_row_height = 38
    table_col_time = LEFT_MARGIN
    table_col_activity = table_col_time + 70
    table_col_particulars = table_col_activity + 320
    table_widths = [70, 250, 180]
    num_rows = 6  # Header + 5 rows

    # Table Borders
    t_x0 = table_col_time
    t_y0 = section_y - 30 - (num_rows * table_row_height)
    t_x1 = t_x0 + sum(table_widths)
    t_y1 = t_y0 + num_rows * table_row_height

    c.setStrokeColor(colors.black)
    c.rect(t_x0, t_y0, t_x1 - t_x0, t_y1 - t_y0, fill=0, stroke=1)

    # Vertical lines
    x_positions = [t_x0]
    for w in table_widths:
        x_positions.append(x_positions[-1] + w)
    for x in x_positions[1:-1]:
        c.line(x, t_y0, x, t_y1)

    # Horizontal lines
    for i in range(1, num_rows):
        y = t_y0 + i * table_row_height
        c.line(t_x0, y, t_x1, y)

    # Table Headings
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(t_x0 + table_widths[0] // 2, t_y1 - table_row_height // 2, "TIME")
    c.drawCentredString(t_x0 + table_widths[0] + table_widths[1] // 2, t_y1 - table_row_height // 2, "ACTIVITY")
    c.drawCentredString(t_x0 + table_widths[0] + table_widths[1] + table_widths[2] // 2, t_y1 - table_row_height // 2, "PARTICULARS")

    # Table Rows Content
    c.setFont("Helvetica", 13)
    activities = ["WAKE UP", "BREAKFAST", "LUNCH", "EVENING SNACKS", "DINNER"]
    for idx, act in enumerate(activities):
        row_y = t_y1 - (idx + 2) * table_row_height + table_row_height // 2 - 5
        c.drawCentredString(t_x0 + table_widths[0] + table_widths[1] // 2, row_y, act)

    # --- Other Details Section ---
    details_y = t_y0 - 50
    c.setFont("Helvetica", 13)
    c.drawString(
        LEFT_MARGIN,
        details_y,
        "CONSUMPTION OF TEA ______ / COFFEE ______ / MILK ______   WATER: __________",
    )

    details_y -= gap
    c.drawString(
        LEFT_MARGIN,
        details_y,
        "DIET:  VEG / NON VEG ______ NON VEG TYPE ______ FREQUENCY ______ PER WEEK",
    )

    details_y -= gap
    c.drawString(
        LEFT_MARGIN,
        details_y,
        "FRUITS YOU EAT: _________________________________________",
    )
    #Separator
    separator_y = details_y - 20
    c.setLineWidth(1)
    c.line(40, separator_y, width - 40, separator_y)
    # --- Declaration & Signature Section ---
    declare_y = details_y - 35
    c.setFont("Helvetica-Bold", 13)
    c.drawString(
        LEFT_MARGIN,
        declare_y,
        "DECLARATION: AS PER MY KNOWLEDGE INFORMATION GIVEN ABOVE IS TRUE.",
    )

    sign_y = declare_y - 40
    c.setFont("Helvetica", 13)
    c.drawString(LEFT_MARGIN, sign_y, "SIGNATURE:")
    c.drawString(LEFT_MARGIN + 230, sign_y, "PLACE:")

    sign_y -= gap
    c.drawString(LEFT_MARGIN, sign_y, "NAME:")
    c.drawString(LEFT_MARGIN + 230, sign_y, "DATE:")

    
    c.save()

def save_record_csv(record):
    df = pd.DataFrame([record])
    if not os.path.exists(Data_file):
        df.to_csv(Data_file, index=False)
    else:
        df.to_csv(Data_file, mode='a', header=False, index=False)


# ---------------------- Form --------------------
st.text(" ")
st.text(" ")
st.text(" ")
col_left, col_center, col_right = st.columns([1,2,1])

with col_center.form("Entry Form", clear_on_submit=True, enter_to_submit=False):
    st.markdown("""
    <div style='background-color: #4CAF50; padding: 15px; color: white; border-radius: 6px; display: flex; align-items: center;'>
    <div>
        <p style='margin: 4px 0 0; font-size: 20px;'> + Prospect Registration Form </p>
    </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### ")  # Spacer
    col1,col2 = st.columns(2)
    with col1:
        serial = st.text_input("Serial No.")
        name = st.text_input("Name")
        real_age = st.number_input("Real Age", 0, 120)
        contact = st.number_input("Contact Number",0)
        # dob = st.date_input("Date of Birth")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height = st.number_input("Height (CM)", 0.0)
        weight = st.number_input("Weight (Kg)", 0.0)
        rmt = st.number_input("Resting Metabolism")
        
    with col2:
        waist = st.number_input("Waist (inches)", 0.0)
        hip = st.number_input("Hip (inches)", 0.0)
        body_fat = st.number_input("Body Fat (%)", 0.0)
        visc_fat = st.number_input("Visceral Fat", 0.0)
        muscle = st.number_input("Skeletal Muscle (%)", 0.0)
        bmi = st.number_input("BMI")
        body_age = st.number_input("Body Age")
    # st.markdown("### ")  # Spacer
    st.markdown("---")  # Horizontal line
    submitted = st.form_submit_button("Submit & Generate PDF", use_container_width=True)
# ------------- Handle Form Submission -------------
col1, col2 = st.columns([2,2],border=True)
with col1:
    st.subheader("📄Print PDF")
    if submitted:
        wh_ratio = calculate_wh_ratio(waist,hip)
        timestamp = datetime.now().strftime("%Y-%m-%d")
        record={
        "Name": name,
        "Timestamp": timestamp,
        "Real Age": real_age,
        "Gender": gender,
        "Height": height,
        "Weight": weight,
        "BMI": bmi,
        "Waist": waist,
        "Hip": hip,
        "W/H Ratio": wh_ratio,
        "Body Fat": body_fat,
        "Visceral Fat": visc_fat,
        "Skeletal Muscle": muscle,
        "Body Age": body_age,
        "RM": rmt,
        }
        logo_path="Arogyasampda_360_logo-removebg-preview.png"
        
        save_record_csv(record)
        pdf_filename = f"{name.replace(' ','_')}_{today}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        generate_pdf(record, pdf_path,logo_path)

        st.success("✅ PDF generated and saved!")

        with open(pdf_path, "rb")as f:
            st.download_button("📄 Download PDF", f, file_name=pdf_filename, mime="application/pdf")
        
        # st.session_state.submitted = True
    else:
        st.markdown("""
        <style>
        .disabled-button {
                    background-color: #ddd;
                    color: #888;
                    padding: 0.5em 1em;
                    border-radius: 6px;
                    cursor: not-allowed;
                    display: inline-block;
                    font-weight: bold;
                    }
        </style>
        <div class = 'diabled-button'>📄 Download PDF</div>
        """, unsafe_allow_html=True)
with col2:
    st.subheader("📊 Download All Patient Data")
    if os.path.exists(Data_file):
        df = pd.read_csv(Data_file, on_bad_lines='skip', delimiter=',')
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl")as writer:
            df.to_excel(writer, index=False, sheet_name="Prospects")
        buffer.seek(0)
        filename = f"Prospect_data_{today}.csv"
        st.download_button(
            "⬇️ Download Excel File",
            data = buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        if st.button("📤 Upload to Google Drive"):
            try:
                with open(Data_file, "rb") as f:
                    file_id = upload_to_drive(f, filename,folder_id=GOOGLE_FOLDER_ID)
                st.success("✅ Data generated, data saved, and uploaded to Google Drive!")
                st.info(f"📁 Google Drive File ID: {file_id}")
            except Exception as e:
                st.error(f"❌ Upload failed: {e}")
    else:
        st.markdown("""
            <style>
            .disabled-button {
                    background-color: #ddd;
                    color: #888;
                    padding: 0.5em 1em;
                    border-radius: 6px;
                    cursor: not-allowed;
                    display: inline-block;
                    font-weight: bold;
                    }
            </style>
            <div class= 'disabled-button'>⬇️ Download Excel File</div>
            """, unsafe_allow_html=True)
    