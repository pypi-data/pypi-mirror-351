from functools import wraps
import inspect
import logging
import discord
import asyncio
import unicodedata
from discord.ext import commands
from discord.gateway import DiscordWebSocket
from .bot import SaintBot
from .config_loader import load_config
from discord import app_commands
from discord import app_commands
BOT_INSTANCE = None
logging.basicConfig(level=logging.ERROR)
GLOBAL_COOLDOWN_MESSAGES = {
    "guild": "> This command is on cooldown for {time:.2f}",
    "user": "> You are on cooldown for {time:.2f}."
}
cooldown_messages = {}
async def mobile_identify(self):
    payload = {
        "op": self.IDENTIFY,
        "d": {
            "token": self.token,
            "properties": {
                "$os": "Discord iOS",
                "$browser": "Discord iOS",
                "$device": "iOS",
                "$referrer": "",
                "$referring_domain": "",
            },
            "compress": True,
            "large_threshold": 250,
        },
    }
    if self.shard_id is not None and self.shard_count is not None:
        payload["d"]["shard"] = [self.shard_id, self.shard_count]
    state = self._connection
    if state._activity is not None or state._status is not None:
        payload["d"]["presence"] = {
            "status": state._status,
            "activities": [
                {
                    "name": state._activity.name,
                    "type": state._activity.type,
                    "url": "https://www.youtube.com/watch?v=TMzs6GvsZXU"
                    if state._activity.type == discord.ActivityType.streaming
                    else None,
                }
            ],
            "since": 0,
            "afk": False,
        }
    if state._intents is not None:
        payload["d"]["intents"] = state._intents.value
    await self.call_hooks("before_identify", self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)
DiscordWebSocket.identify = mobile_identify
class User(discord.User):
    pass
class Embed(discord.Embed):
    pass
def init(path=None, token=None, prefix="!", owners=None):
    global BOT_INSTANCE
    if path:
        config = load_config(path)
        token = config.get("token", token)
        prefix = config.get("prefix", prefix)
        owners = config.get("owners", owners or [])
    if not token:
        raise ValueError("Bot token is required.")
    intents = discord.Intents.all()
    BOT_INSTANCE = SaintBot(command_prefix=prefix, owners=owners, token=token, intents=intents)
    return BOT_INSTANCE
def start(bot=None):
    global BOT_INSTANCE
    bot = bot or BOT_INSTANCE
    if not bot:
        raise ValueError("No bot instance found.")
    logging.getLogger("discord").setLevel(logging.CRITICAL)
    class BotWithSetup(bot.__class__):
        async def setup_hook(self):
            await self.tree.sync()
        async def on_message(self, message):
            if message.author.bot:
                return
            normalized_content = normalize_message(message.content)
            message.content = normalized_content
            await self.process_commands(message)
        async def on_command_error(self, ctx, error):
            pass
    bot.__class__ = BotWithSetup
    bot.run(bot.token)
def normalize_message(content):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', content)
        if not unicodedata.combining(c)
    ).lower()
def cmd(name, description):
    global BOT_INSTANCE
    if not BOT_INSTANCE:
        raise ValueError("Bot instance not initialized.")
    def decorator(func):
        allowed_installs = getattr(func, "allowed_installs", None)
        contexts = getattr(func, "contexts", None)
        command = commands.hybrid_command(name=name, description=description)(func)
        if allowed_installs:
            command.app_command.allowed_installs = allowed_installs
        if contexts:
            command.app_command.allowed_contexts = contexts
        command.app_command.guild_only = True  
        BOT_INSTANCE.add_command(command)
        return func
    return decorator
def desc(**kwargs):
    return app_commands.describe(**kwargs)
def ins(guilds, users):
    def decorator(command):
        command = app_commands.allowed_installs(guilds=guilds, users=users)(command)
        return command
    return decorator
def cnt(guilds, dms, private_channels):
    def decorator(command):
        command = app_commands.allowed_contexts(guilds=guilds, dms=dms, private_channels=private_channels)(command)
        return command
    return decorator
def only(data="owner"):
    def check(ctx):
        if data == "owner":
            return ctx.author.id == BOT_INSTANCE.owner_id
        elif callable(data):
            return data(ctx)
        return False
    def decorator(func):
        return commands.check(check)(func)
    return decorator
def event(func):
    global BOT_INSTANCE
    if not BOT_INSTANCE:
        raise ValueError("Bot instance not initialized.")
    BOT_INSTANCE.event(func)
    return func
def alias(*aliases):
    def decorator(func):
        for alias_name in aliases:
            alias_command = commands.Command(func, name=alias_name)
            BOT_INSTANCE.add_command(alias_command)
        return func
    return decorator
def cool(bucket_type, tries, seconds, ignore=None, custom_messages=None):
    def decorator(func):
        cooldown = commands.CooldownMapping.from_cooldown(
            tries, seconds, commands.BucketType.guild if bucket_type == "guild" else commands.BucketType.user
        )
        async def wrapper(ctx, *args, **kwargs):
            if ignore and callable(ignore):
                if ignore(ctx):
                    return await func(ctx, *args, **kwargs)
            bucket = cooldown.get_bucket(ctx.message)
            retry_after = bucket.update_rate_limit()
            if retry_after:
                if ctx.command.name not in cooldown_messages:
                    messages = custom_messages or GLOBAL_COOLDOWN_MESSAGES
                    msg_template = messages["guild"] if bucket_type == "guild" else messages["user"]
                    embed = discord.Embed(
                        description=msg_template.format(time=retry_after),
                        color=discord.Color.dark_gray()
                    )
                    msg = await ctx.send(embed=embed)
                    cooldown_messages[ctx.command.name] = msg
                    await asyncio.sleep(retry_after)
                    await msg.delete()
                    del cooldown_messages[ctx.command.name]
                return
            await func(ctx, *args, **kwargs)
        return wrapper
    return decorator
def alias(*aliases):
    def decorator(func):
        for alias_name in aliases:
            alias_command = commands.Command(func, name=alias_name)
            BOT_INSTANCE.add_command(alias_command)
        return func
    return decorator
def log(message):
    print(f"⚡ {message}")
__all__ = [
    "init", "start", "cmd", "alias", "normalize_message", "only", "desc", "event", "log", "cool", "ins", "cnt", "User", "Embed"
]