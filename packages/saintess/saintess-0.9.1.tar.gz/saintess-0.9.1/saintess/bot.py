import discord
from discord.ext import commands

class SaintBot(commands.Bot):
    def __init__(self, command_prefix, owners=None, token=None, intents=None):
        intents = intents or discord.Intents.default()
        self.owners = owners or []
        self.token = token
        super().__init__(command_prefix=command_prefix, intents=intents)
