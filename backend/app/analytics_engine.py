import os
import pandas as pd
from datetime import datetime, timezone
from app.config import settings

def log_user_activity(song_name: str, action_type: str):
    """
    Appends real-time user interaction events (streaming or downloading)
    directly into a structured CSV time-series log for analytics data ingestion.
    """
    # Safeguard: Ensure the target tracking data directory exists
    os.makedirs(os.path.dirname(settings.ANALYTICS_FILE), exist_ok=True)
    
    # Construct a snapshot payload of the user interaction event
    event_payload = {
        "timestamp": [datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")],
        "song_name": [song_name],
        "action": [action_type]
    }
    
    df = pd.DataFrame(event_payload)
    
    try:
        # If the dataset file doesn't exist yet, write it along with structural column headers
        if not os.path.isfile(settings.ANALYTICS_FILE):
            df.to_csv(settings.ANALYTICS_FILE, index=False)
        else:
            # If it exists, append the user tracking event row quietly without rewriting headers
            df.to_csv(settings.ANALYTICS_FILE, mode='a', header=False, index=False)
    except Exception as e:
        # Prevent analytics failures from causing system crashes or blocking music streaming
        print(f"[-] Telemetry Engine Logging Error: {str(e)}")