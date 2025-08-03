from discordrp import Presence
import time
import anitopy
from anilist_api.graphql import graphql_request
from urllib.parse import unquote

query = """
query ($name: String) {
  Media(search: $name, type: ANIME) {
    episodes,
    format,
    title {
      english,
      romaji,
    },
    coverImage {
      extraLarge
    },
  }
}
"""

import platform

if platform.system() == "Linux":
    from monitors.linux.mpris_monitor import get_current_filedata
    print("Loaded Linux MPRIS monitor.")

elif platform.system() == "Windows":
    from monitors.windows.mpv_monitor import get_current_filedata
    print("Loaded Windows mpv IPC monitor.")

else:
    raise NotImplementedError(f"Unsupported platform: {platform.system()}")

client_id = "1401172822381826108"  # Replace this with your own client id

errors = ['no_player', 'no_file', 'connection_error', 'no_service']

if __name__ == "__main__":
  try:
    presence = Presence(client_id)
    print("Connected")
    last_filename = None

    while True:
      [current_filename, current_filelength] = get_current_filedata()
      current_timestamp = int(time.time() * 1000)
      if (current_filename in errors):
        presence.clear()
        time.sleep(15)
        continue

      parsed_anime = anitopy.parse(current_filename)
      if (current_filename != last_filename):
        try:
          fetched_anime = graphql_request(query, {"name": parsed_anime['anime_title']}).get("Media")
        except Exception as e:
          print(f"Error while fetching anime from anilist api : {e}") 
        
        if ('episode_number' in parsed_anime) and ('episode_title' in parsed_anime):
          episode_stats = f"Ep {parsed_anime['episode_number']}: {parsed_anime['episode_title']}"
        elif ('episode_number' in parsed_anime) and (fetched_anime.get("episodes")):
          episode_stats = f"Episode {parsed_anime['episode_number']}/{fetched_anime.get("episodes")}"
        elif ('episode_number' in parsed_anime):
          episode_stats = f"Episode {parsed_anime['episode_number']}"
        else:
          episode_stats = unquote(fetched_anime.get("format")).title()

        presence.set(
            {
                "type":3,
                "status_display_type":2,
                "state": episode_stats,
                "details": fetched_anime.get("title").get("romaji"),
                "timestamps": 
                {
                  "start" : current_timestamp,
                  "end": current_timestamp+current_filelength,
                },
                "assets": 
                {
                  "large_image": fetched_anime.get("coverImage").get("extraLarge"),
                  "large_text": fetched_anime.get("title").get("english")
                },
            }
        )

        last_filename = current_filename
        print(f"Presence updated : {parsed_anime['anime_title']}")
      time.sleep(15)
  except KeyboardInterrupt:
    presence.clear()
    presence.close()
    print("Presence closed")
