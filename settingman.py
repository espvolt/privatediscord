import json
import os

class SettingMan:
    INSTANCE = None
    PERSISTENT_FOLDER = "./persistent"
    def __init__(self):
        if (SettingMan.INSTANCE is not None):
            return
        
        self.data = {}

    def _create_guild_settings(self):
        return {
            "voice_client_volume": 1
        }
    
    def _save_data(self):
        if (os.path.exists(f"{SettingMan.PERSISTENT_FOLDER}")):
            with open(f"{SettingMan.PERSISTENT_FOLDER}/guild_settings.json", "w") as f:
                json.dump(self.data, f)

    def _load_persistent(self):
        if (os.path.exists(f"{SettingMan.PERSISTENT_FOLDER}") and os.path.exists(f"{SettingMan.PERSISTENT_FOLDER}/guild_settings.json")):
            with open(f"{SettingMan.PERSISTENT_FOLDER}/guild_settings.json", "r") as f:
                self.data = json.load(f)

        elif (os.path.exists(f"{SettingMan.PERSISTENT_FOLDER}")):
            with open(f"{SettingMan.PERSISTENT_FOLDER}/guild_settings.json", "w") as f:
                self.data = {}

                json.dump(self.data, f)
        else:
            
            raise Exception("Persistent files not configured correctly")

    def get_guild_settings(self, guild_id: int):
        _guild_id_str = str(guild_id)
        if (_guild_id_str in self.data):
            return self.data[_guild_id_str]
        
        else:
            self.data[_guild_id_str] = self._create_guild_settings()
            return self.data[_guild_id_str]
    
    def set_guild_settings(self, guild_id: int, settings: dict):
        _guild_id_str = str(guild_id)

        self.data[_guild_id_str] = settings
        self._save_data()
    def get_instance():
        if (SettingMan.INSTANCE is None):
            SettingMan.INSTANCE = SettingMan()
            SettingMan.INSTANCE._load_persistent()

        return SettingMan.INSTANCE