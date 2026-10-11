import os
import sys
import glob
import json
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from topics_data import TOPICS

base = os.path.dirname(os.path.abspath(__file__))

def get_youtube_service():
    creds_json = os.environ.get("YOUTUBE_TOKEN_JSON")
    if creds_json:
        try:
            creds_data = json.loads(creds_json)
            creds = Credentials.from_authorized_user_info(creds_data)
            return build("youtube", "v3", credentials=creds)
        except Exception as e:
            print("Error loading credentials from YOUTUBE_TOKEN_JSON:", e)

    # Local fallback
    local_token_paths = [
        os.path.join(base, "token.json"),
        r"C:\Users\DELL\youtube_projects\data_race\token.json"
    ]
    for p in local_token_paths:
        if os.path.exists(p):
            try:
                creds_data = json.load(open(p, encoding="utf-8"))
                creds = Credentials.from_authorized_user_info(creds_data)
                return build("youtube", "v3", credentials=creds)
            except Exception as e:
                print(f"Error loading {p}: {e}")

    print("No valid YouTube credentials found!")
    return None

def upload_video(yt, file_path, title, description, tags):
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:4500],
            "tags": tags,
            "categoryId": "27" # Education
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, chunksize=1024*1024*4, resumable=True, mimetype="video/mp4")
    request = yt.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    print(f"Uploading '{title}' to YouTube...")
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%...")

    video_id = response.get("id")
    print(f"SUCCESS! Video live on YouTube: https://youtube.com/shorts/{video_id}")
    return video_id

def main():
    yt = get_youtube_service()
    if not yt:
        print("Skipping YouTube upload: service unavailable.")
        sys.exit(0)

    # Allow passing specific file or folder
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        mp4_files = [sys.argv[1]]
    else:
        # Find videos in output_batch
        mp4_files = sorted(glob.glob(os.path.join(base, "output_batch", "*.mp4")))
    if not mp4_files:
        print("No videos found in output_batch to upload.")
        sys.exit(0)

    for f in mp4_files:
        basename = os.path.basename(f)
        # Parse topic ID from filename like 01_USA_vs_China.mp4
        prefix = basename.split("_")[0]
        try:
            topic_id = int(prefix)
            topic = next((t for t in TOPICS if t["id"] == topic_id), None)
        except:
            topic = None

        if topic:
            c1_name = topic["c1"]["name"]
            c2_name = topic["c2"]["name"]
            hook = topic["hook_text"]
            title = f"{c1_name} vs {c2_name}: Who Has a Better Life? #Shorts"
            description = (
                f"{hook}\n\n"
                f"Comparing real quality-of-life data between {c1_name} and {c2_name}!\n\n"
                f"ROUND 1: {topic['r1']['lbl']}: {topic['r1']['c1_val']} vs {topic['r1']['c2_val']}\n"
                f"ROUND 2: {topic['r2']['lbl']}: {topic['r2']['c1_val']} vs {topic['r2']['c2_val']}\n"
                f"ROUND 3: {topic['r3']['lbl']}: {topic['r3']['c1_val']} vs {topic['r3']['c2_val']}\n\n"
                f"Which country would you rather live in? Drop a comment below!\n\n"
                f"#Shorts #Geography #GeoFacts #Comparison #DataFlux #Viral"
            )
            tags = [
                "shorts", "geofacts", "geography", "comparison", "dataflux",
                topic["c1"]["iso"].lower(), topic["c2"]["iso"].lower(), "facts", "viral"
            ]
        else:
            title = f"{basename.replace('.mp4', '').replace('_', ' ')} #Shorts"
            description = "Quality of life country comparison! #Shorts #GeoFacts #DataFlux"
            tags = ["shorts", "geofacts", "geography", "comparison", "dataflux"]

        # YouTube strictly forbids < and > in title and description
        title = title.replace("<", "").replace(">", "")
        description = description.replace("<", "").replace(">", "")

        try:
            upload_video(yt, f, title, description, tags)
        except Exception as e:
            print(f"Error uploading {basename}: {e}")

if __name__ == "__main__":
    main()
