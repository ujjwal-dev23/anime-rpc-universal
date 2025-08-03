import dbus
import os
import time
from urllib.parse import urlparse, unquote

def get_current_filename():
  try:
    session_bus = dbus.SessionBus()
    
    player_services = [
      service for service in session_bus.list_names() if service.startswith('org.mpris.MediaPlayer2.')
    ]
    if not player_services:
      return "No active MPRIS player found."
    
    player_service = player_services[0]
    player_object = session_bus.get_object(player_service, '/org/mpris/MediaPlayer2')
    properties_interface = dbus.Interface(player_object, 'org.freedesktop.DBus.Properties')
    
    metadata = properties_interface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
    
    file_url = metadata.get('xesam:url')
    if not file_url:
      return "Player is not playing a file"

    path = unquote(urlparse(file_url).path)
    filename = os.path.basename(path)
    
    return filename
  except dbus.exceptions.DBusException:
    return "D-Bus connection error."
  except IndexError:
    return "Could not find player service."


if __name__ == "__main__":
  last_filename = None
  print("Starting MPRIS Monitor (Press Ctrl+C to stop)")
  try:
    while True:
      current_filename = get_current_filename()
      if (current_filename != last_filename):
        print(f"Now Playing: {current_filename}")
        last_filename = current_filename
        
      time.sleep(2)
  except KeyboardInterrupt:
    print("Monitor stopped")