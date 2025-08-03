import json
import time
import os
import configparser
from urllib.parse import unquote

config = configparser.ConfigParser()
config.read("anime_rpc.conf")
DEBUG_LOGS = config["DEFAULT"]["debug_logs"] == "yes"

def get_mpv_property(property_name):
  pipe_path = r"\\.\pipe\mpvsocket"
  
  try:
    with open(pipe_path, 'r+', encoding='utf-8') as pipe:
      command = {'command': ['get_property', property_name]}
      pipe.write(json.dumps(command) + '\n')
      pipe.flush()
      
      response_data = json.loads(pipe.readline())
      
      if response_data.get("error") == "success":
        return response_data.get("data")
      else:
        if response_data.get("error") != "property_unavailable":
          if DEBUG_LOGS:
            print(f"Error getting property '{property_name}' : '{response_data.get("error")}'")
        return None
      
  except FileNotFoundError:
    return 'pipe_not_found'
  except Exception as e:
    print(f"Error occured: {e}")
    return None

def get_current_filedata():
  file_path = get_mpv_property("path")
  if file_path == "pipe_not_found":
    if DEBUG_LOGS:
      print("Error: could not connect to mpv.")
      print("Hint: Is MPV running with the '--input-ipc-server' flag?")
    return ["no_file",0]
  elif file_path:
    # Handle http streams
    if (file_path.startswith("http")):
      file_path = unquote(file_path)

    duration_seconds = get_mpv_property("duration") or 0

    filename = os.path.basename(file_path)
    duration_milliseconds = duration_seconds * 1000
    return [filename, duration_milliseconds]
  else:
    if DEBUG_LOGS:
      print("Player is not playing a file")
    return ["no_file", 0]

if __name__ == "__main__":
  last_filename = None
  print("Starting mpv Monitor (Press Ctrl+C to stop)")
  try:
    while True:
      [filename, duration] = get_current_filedata()
      if (filename != last_filename):
        print(f"Now Playing: {filename}, Duration: {duration}")
        last_filename = filename
        
      time.sleep(5)
  except KeyboardInterrupt:
    print("Monitor stopped")
