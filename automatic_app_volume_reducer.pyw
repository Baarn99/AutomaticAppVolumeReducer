import time
import json
import os
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

TARGET_VOLUME = 0.10
DB_FILE = "known_apps.json"

def monitor_and_cap_volume():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, DB_FILE)

    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            known_apps = set(json.load(f))
    else:
        known_apps = set()

    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process:
            known_apps.add(session.Process.name())

    with open(db_path, "w") as f:
        json.dump(list(known_apps), f)

    while True:
        try:
            sessions = AudioUtilities.GetAllSessions()
            updated = False

            for session in sessions:
                if session.Process:
                    app_name = session.Process.name()
                    
                    if app_name not in known_apps:
                        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                        current_vol = volume.GetMasterVolume()
                        
                        if current_vol > TARGET_VOLUME:
                            volume.SetMasterVolume(TARGET_VOLUME, None)
                        
                        known_apps.add(app_name)
                        updated = True

            if updated:
                with open(db_path, "w") as f:
                    json.dump(list(known_apps), f)

        except Exception:
            pass

        time.sleep(1)

if __name__ == "__main__":
    monitor_and_cap_volume()
