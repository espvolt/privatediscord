import discord
import yt_dlp
from settingman import SettingMan
import validators
import requests
import dotenv
import os

dotenv.load_dotenv()

bot = discord.Bot()
setting_instance = SettingMan.get_instance()

class Queue:
    def __init__(self, voice_client: discord.client.VoiceClient):
        self.song_links: list[str] = []
        self.voice_client: discord.client.VoiceClient = voice_client
        self.current_song = ""
        self.settings = setting_instance.get_guild_settings(voice_client.guild.id)

        self.volume = self.settings["voice_client_volume"]
    
    def _play_queued(self) -> bool:
        if (self.current_song != ""):
            return False

        else:
            self.current_song = self.song_links.pop()
            audio_source = discord.FFmpegPCMAudio(self.current_song)
            self.voice_client.play(audio_source, after=self._song_finished)
            self.voice_client.source = discord.PCMVolumeTransformer(self.voice_client.source)
            self.voice_client.volume = self.volume
            return True
            

    def _song_finished(self, exc=None):
        self.current_song = ""
        if (len(self.song_links) > 0):
            self._play_queued()


    def add_song(self, link):
        self.song_links.append(link)

        self._play_queued()
        
    def set_volume(self, volume: float):
        volume = min(max(volume, 0.0), 1.0)

        self.volume = volume

        if (isinstance(self.voice_client.source, discord.PCMVolumeTransformer)):
            self.voice_client.source.volume = self.volume

queues: dict[int, Queue] = {}

@bot.event
async def on_ready():
    print("hell yeah")

@bot.command()
async def set_volume(ctx: discord.commands.context.ApplicationContext, volume: float):
    guild_id = ctx.author.guild.id
    settings = setting_instance.get_guild_settings(guild_id)
    volume = min(max(volume, 0.0), 1.0) # clamp

    settings["voice_client_volume"] = volume
    setting_instance.set_guild_settings(guild_id, settings)
    if (guild_id in queues):
        queues[guild_id].set_volume(volume)

@bot.command()
async def play(ctx: discord.commands.context.ApplicationContext, url: str):
    ydl_opts = {
        'format': 'opus/bestaudio/best',
        "noplaylist": "True",
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
        }]
    }

    voice_state = ctx.author.voice
    guild_id = ctx.author.guild.id

    if (voice_state):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if (not validators.url(url)):
                data = ydl.extract_info(f"ytsearch:{url}", download=False)["entries"][0]
            else:
                data = ydl.extract_info(url, download=False)
            selected_format = None
        
            for current_format in data["formats"]:
                if ("acodec" in current_format):
                    if (current_format["acodec"] == "opus"):
                        selected_format = current_format
                        break

            # selected_format = data["formats"][]
            if (guild_id in queues):
                queues[guild_id].add_song(selected_format["url"])
            
            else:
                channel: discord.channel.VoiceChannel = bot.get_channel(voice_state.channel.id)
                voice_client = await channel.connect()

                current_queue = Queue(voice_client)
                queues[guild_id] = current_queue
                current_queue.add_song(selected_format["url"])

            return await ctx.send("playing")
        
        return await ctx.send("something went wrong")
    
    return await ctx.send("you not in channel")

bot.run(os.environ.get("DISCORD_KEY"))