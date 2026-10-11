import os
import json
import sys

def upload_file_to_gdrive(file_path, file_name, folder_id, credentials_json_str):
    """
    Uploads a file to Google Drive using a Service Account JSON credentials string.
    Works seamlessly in GitHub Actions cloud runners.
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        print("google-api-python-client not installed. Skipping cloud upload.")
        return False

    try:
        creds_dict = json.loads(credentials_json_str)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(
            file_path,
            mimetype='video/mp4',
            resumable=True
        )

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

        print(f"Successfully uploaded to Google Drive! File ID: {file.get('id')}")
        return True
    except Exception as e:
        print(f"Google Drive upload error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload_to_gdrive.py <file_path> <file_name>")
        sys.exit(1)
        
    f_path = sys.argv[1]
    f_name = sys.argv[2]
    f_id = os.environ.get("GDRIVE_FOLDER_ID")
    c_json = os.environ.get("GDRIVE_CREDENTIALS_JSON")
    
    if f_id and c_json:
        upload_file_to_gdrive(f_path, f_name, f_id, c_json)
    else:
        print("GDRIVE_FOLDER_ID or GDRIVE_CREDENTIALS_JSON environment variable missing.")
