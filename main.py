import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord.commands import slash_command
import asyncio

# Laden der Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Definieren der Intents (Berechtigungen für den Bot)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.guilds = True

# Erstellen des Bot-Objekts
bot = discord.Bot(
    intents=intents,
    status=discord.Status.dnd,
    activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="dem Schreien von Kindern zu"
    )
)

# Beim Start des Bots werden die Cogs geladen
if __name__ == "__main__":
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"[INFO] Cog {filename} wurde erfolgreich geladen.")
            except Exception as e:
                print(f"[ERROR] Fehler beim Laden des Cogs {filename}: {e}")

# Event, das beim Starten des Bots ausgelöst wird
@bot.event
async def on_ready():
    print(f'[INFO] Eingeloggt als: {bot.user.name}#{bot.user.discriminator}')
    print(f'[INFO] Bot-ID: {bot.user.id}')
    print(f'[INFO] Es sind momentan {len(set(bot.get_all_members()))} Member auf dem Server')
    print(f'[INFO] Verwende Pycord Version {discord.__version__}')

# Slash-Command zum Testen der Latenz
@slash_command(name="ping", description="Testet die Latenz zum Bot")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.respond(f"Pong! 🏓\nLatenz: {latency} ms", ephemeral=True)

# Bot starten mit dem Token aus der .env-Datei
bot.run(os.getenv("TOKEN"))
