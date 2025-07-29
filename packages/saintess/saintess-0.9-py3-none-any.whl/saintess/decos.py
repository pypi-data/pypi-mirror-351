from discord.ext import commands

def saintess(name, desc):
    def decorator(func):
        return commands.hybrid_command(name=name, description=desc)(func)
    return decorator

def guild(enabled, disabled):
    def decorator(func):
        async def wrapper(ctx, *args, **kwargs):
            if ctx.guild and not enabled:
                return
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator

def user(guild, dms, private):
    def decorator(func):
        async def wrapper(ctx, *args, **kwargs):
            if not any([guild and ctx.guild, dms and ctx.author.dm_channel, private and ctx.channel.is_private]):
                return
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator

def only(role):
    def decorator(func):
        async def wrapper(ctx, *args, **kwargs):
            if role.lower() == "owner" and ctx.author.id not in ctx.bot.owners:
                return
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator

def cool(bucket_type, rate, per):
    def decorator(func):
        return commands.cooldown(rate, per, commands.BucketType.user if bucket_type == "user" else commands.BucketType.guild)(func)
    return decorator
