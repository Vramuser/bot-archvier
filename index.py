import discord
from discord.ext import commands
from datetime import datetime
import json
import os

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

SETTINGS_FILE = "settings.json"
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        settings = json.load(f)
else:
    settings = {}

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def forward(ctx, source_channel_id: int, target_channel_id: int, limit: int = 100):
    """
    Forward messages from one channel to another.
    Usage: !forward <source_channel_id> <target_channel_id> [limit]
    """
    source_channel = bot.get_channel(source_channel_id)
    target_channel = bot.get_channel(target_channel_id)

    if not source_channel or not target_channel:
        await ctx.send("❌ Source or target channel not found.")
        return

    messages = []
    async for msg in source_channel.history(limit=limit, oldest_first=True):
        messages.append(msg)

    forwarded_count = 0
    for msg in messages:
        content = f"**{msg.author}** at {msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}:\n{msg.content or ''}"
        files = [await attachment.to_file() for attachment in msg.attachments]

        try:
            await target_channel.send(content=content, files=files)
            forwarded_count += 1
        except Exception as e:
            await ctx.send(f"❌ Failed to forward message: {e}")

    await ctx.send(f"✅ Forwarded {forwarded_count}/{len(messages)} messages from <#{source_channel_id}> to <#{target_channel_id}>")

@bot.command()
async def setglobe(ctx, globe_value: str):
    guild_id = str(ctx.guild.id)
    if guild_id not in settings:
        settings[guild_id] = {}
    settings[guild_id]["globe"] = globe_value
    save_settings()
    await ctx.send(f"🌐 Globe value for this server set to: `{globe_value}`")

@bot.command()
async def showglobe(ctx):
    guild_id = str(ctx.guild.id)
    globe_value = settings.get(guild_id, {}).get("globe", "Not set")
    await ctx.send(f"🌐 Current globe value for this server: `{globe_value}`")

@bot.command()
async def setglobal(ctx, key: str, value: str):
    guild_id = str(ctx.guild.id)
    if guild_id not in settings:
        settings[guild_id] = {}
    settings[guild_id][key] = value
    save_settings()
    await ctx.send(f"⚙️ Global setting `{key}` set to `{value}`")

@bot.command()
async def getglobal(ctx, key: str):
    guild_id = str(ctx.guild.id)
    value = settings.get(guild_id, {}).get(key, None)
    if value is None:
        await ctx.send(f"⚠️ No value found for `{key}`")
    else:
        await ctx.send(f"⚙️ Global setting `{key}` = `{value}`")

@bot.command()
async def helpme(ctx):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
    embed.add_field(name="!forward", value="Forward messages from one channel to another\n`!forward <source_channel_id> <target_channel_id> [limit]`", inline=False)
    embed.add_field(name="!setglobe", value="Set the globe value for this server\n`!setglobe <value>`", inline=False)
    embed.add_field(name="!showglobe", value="Show the current globe value\n`!showglobe`", inline=False)
    embed.add_field(name="!setglobal", value="Set a generic global value for this server\n`!setglobal <key> <value>`", inline=False)
    embed.add_field(name="!getglobal", value="Get a generic global value for this server\n`!getglobal <key>`", inline=False)
    embed.add_field(name="!helpme", value="Show this help message", inline=False)
    await ctx.send(embed=embed)

bot.run("UR TOKEN HERE")
