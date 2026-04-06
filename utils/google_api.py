import re
from googleapiclient.discovery import build
from google.oauth2 import service_account
import streamlit as st

class GoogleClient:
    def __init__(self):
        creds_dict = st.secrets["google_credentials"]
        self.creds = service_account.Credentials.from_service_account_info(
            creds_dict, 
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/documents.readonly'
            ]
        )

    def _extract_id(self, url):
        # Регулярка для витягування ID з посилань Google
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        return match.group(1) if match else None

    def read_doc(self, url):
        doc_id = self._extract_id(url)
        service = build('docs', 'v1', credentials=self.creds)
        doc = service.documents().get(documentId=doc_id).execute()
        
        full_text = ""
        for content in doc.get('body').get('content'):
            if 'paragraph' in content:
                elements = content.get('paragraph').get('elements')
                for element in elements:
                    if 'textRun' in element:
                        full_text += element.get('textRun').get('content')
        return full_text

    def read_sheet(self, url):
        sheet_id = self._extract_id(url)
        service = build('sheets', 'v4', credentials=self.creds)
        # Зчитуємо перший аркуш повністю
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="A1:Z100"
        ).execute()
        return result.get('values', [])