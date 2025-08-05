import streamlit as st
import pandas as pd
from io import BytesIO
import os
from datetime import date
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io
st.cache_data.clear()

today = date.today()
st.set_page_config(page_title="Arogyasampda 360-Health Coach", layout="wide", initial_sidebar_state="collapsed")
# --------------- Setup --------------------

FOLDER_ID = 'Your Google Folder ID'

# ----------- Google Drive Authentication ------
def authenticate():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import os, pickle

    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    if os.path.exists('token_drive.pkl'):
        with open('token_drive.pkl', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('Your Client_Secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token_drive.pkl', 'wb') as token:
            pickle.dump(creds, token)
    return creds
def list_csv_files_in_folder(folder_id):
    

    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='text/csv'",
        spaces='drive',
        fields='files(id, name)',
        orderBy='name desc'
    ).execute()
    return results.get('files', [])

def download_file_from_drive(file_id):
    
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh
    
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

#--------------- UI ----------------------
col1, col2 = st.columns([1, 8])
with col1:
    st.image("Your Company Logo.png", width=100)
with col2:
    st.markdown("""
        <div style='background-color: #4CAF50; padding: 15px; color: white; border-radius: 6px; display: flex; align-items: center;'>
        <div>
            <h3 style='margin: 0;'> 🧘 Arogyasampada 360</h3>
            <p style='margin: 4px 0 0; font-size: 18px;'> Health Assessment & Management System </p>
        </div>
        </div>
        """, unsafe_allow_html=True)

st.text(" ")
st.text(" ")

col1, center, col2 = st.columns([1, 2, 1])
with center:
    st.markdown("<h2 style='color:#4CAF50;'> + Enter Post Consultation Notes</h2>", unsafe_allow_html=True)

    csv_files = list_csv_files_in_folder(FOLDER_ID)

    if not csv_files:
        st.warning("⚠️ No CSV files found in Google Drive folder.")
        st.stop()

    file_dates = [f['name'].replace('Prospect_data_', '').replace('.csv', '') for f in csv_files]
    date_options = [""] + file_dates
    selected_date = st.selectbox("📅 Select Date", date_options, format_func=lambda x: "Choose a date" if x == "" else x)

    if selected_date:
        selected_file = next((f for f in csv_files if selected_date in f['name']), None)

        if selected_file:
            # Use session_state to persist the DataFrame across interactions
            if f"df_{selected_file['id']}" not in st.session_state:
                file_content = download_file_from_drive(selected_file['id'])
                st.session_state[f"df_{selected_file['id']}"] = pd.read_csv(file_content, on_bad_lines='skip', delimiter=',')

            df = st.session_state[f"df_{selected_file['id']}"]

            st.success(f"✅ Loaded file: `{selected_file['name']}`")
            st.write("🔍 Available Prospects:", df["Name"].nunique())
            prospects = [""] + df["Name"].dropna().unique().tolist()
            selected_prospect = st.selectbox("👤 Select Prospect's Name", prospects, key="prospect", format_func=lambda x: "Choose a Name" if x == "" else x)

            if selected_prospect:
                row = df[df["Name"] == selected_prospect]
                st.dataframe(row)

                # Get any existing note to prefill textarea
                existing_note = row["Post Consultation"].values[0] if "Post Consultation" in row.columns and not row["Post Consultation"].isnull().values[0] else ""
                note = st.text_area("📝 Enter Health Coach Notes", value=existing_note, key="note_area")

                if st.button("💾 Save Notes", key="save_note"):
                    df.loc[df["Name"] == selected_prospect, "Post Consultation"] = note
                    st.session_state[f"df_{selected_file['id']}"] = df
                    st.success("✅ Notes updated and persisted in this session!")

            # File download always reflects all saved notes
            buffer = BytesIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                "⬇️ Download Updated CSV (all notes saved)",
                data=buffer,
                file_name=selected_file["name"],
                mime="text/csv"
            )
            if st.button("📤 Upload to Google Drive"):
                
                try:
                    df_updated = st.session_state[f"df_{selected_file['id']}"]
                    # Convert DataFrame to CSV in-memory
                    buffer = BytesIO()
                    df_updated.to_csv(buffer, index=False)
                    buffer.seek(0)
                    file_id = upload_to_drive(buffer,file_name=f"HealthCoach_Camp_{selected_file['name']}", folder_id=FOLDER_ID)
                    st.success("✅ Data generated, data saved, and uploaded to Google Drive!")
                    st.info(f"📁 Google Drive File ID: {file_id}")
                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")

    else:
        st.error("❌ File not found for selected date. Please try again.")
