from discordrp import Presence
import time
import anitopy
from anilist_api.graphql import graphql_request

query = """
query ($name: String) {
  Media(search: $name, type: ANIME) {
    coverImage {
      large
      extraLarge
    }
  }
}
"""

from mpris_monitor import get_current_filename

anitopy_options = {'parse_episode_title': False, 'parse_file_extension': False, 'parse_release_group': False}

client_id = "1401172822381826108"  # Replace this with your own client id

with Presence(client_id) as presence:
  print("Connected")
  last_filename = None

  while True:
    parsed_anime = anitopy.parse(get_current_filename())
    if (parsed_anime['anime_title'] != last_filename):
      try:
        fetched_anime = graphql_request(query, {"name": parsed_anime['anime_title']})
        cover_images = fetched_anime.get("Media", {}).get("coverImage", {})
      except Exception as e:
        print(f"Error while fetching anime from anilist api : {e}")
      presence.set(
          {
              "type":3,
              "status_display_type":2,
              "state": f"Episode {parsed_anime['episode_number']}",
              "details": parsed_anime['anime_title'],
              "timestamps": {"start": int(time.time())},
              "assets": {
                "large_image": cover_images.get("extraLarge", {}),
              }
          }
      )
      print(cover_images.get("extraLarge", {}))
      last_filename = parsed_anime['anime_title']
      print(f"Presence updated : {parsed_anime['anime_title']}")
    time.sleep(15)