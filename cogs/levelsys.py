import discord
from discord.ext import commands, tasks
import aiosqlite 
import random
import time
from datetime import datetime

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        self.daily_xp = {}
        self.xp_min = 20  # Minimale XP
        self.xp_max = 50  # Maximale XP
        self.cooldown_time = 60  # Cooldown für Nachrichten in Sekunden
        self.voice_xp_interval = 360  # Voice XP Intervall: 360 Sekunden = 6 Minuten
        self.double_xp_weeks = []

        self.bot.loop.create_task(self.create_tables())  # Datenbanktabellen erstellen

    # Voice XP Task wird nach dem Start des Bots gestartet
    @commands.Cog.listener()
    async def on_ready(self):
        self.voice_xp_check.start()  # Voice-Chat-Check Task starten

    # SQLite: Datenbank-Tabellen erstellen
    async def create_tables(self):
        async with aiosqlite.connect("levels.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    xp INTEGER NOT NULL,
                    level INTEGER NOT NULL,
                    daily_bonus TEXT
                )
            """)
            await db.commit()

    # XP für Nachrichten sammeln
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = str(message.author.id)
        if user_id in self.cooldowns and time.time() - self.cooldowns[user_id] < self.cooldown_time:
            return

        xp_gain = random.randint(self.xp_min, self.xp_max)

        # Rollen-basierte XP-Boosts (IDs)
        boosted_roles = {
            123456789012345678: 1.5,  # ID der Rolle "Gold-Mitglied"
            234567890123456789: 1.2,  # ID der Rolle "Silber-Mitglied"
            345678901234567890: 1.1   # ID der Rolle "Bronze-Mitglied"
        }
        for role_id, multiplier in boosted_roles.items():
            role = message.guild.get_role(role_id)
            if role and role in message.author.roles:
                xp_gain = int(xp_gain * multiplier)

        if self.is_double_xp_week():
            xp_gain *= 2

        await self.update_user_data(user_id, xp_gain, message)

        self.cooldowns[user_id] = time.time()

    # Benutzer-Daten aktualisieren
    async def update_user_data(self, user_id, xp_gain, message):
        async with aiosqlite.connect("levels.db") as db:
            cursor = await db.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()

            if result:
                current_xp, current_level = result
                new_xp = current_xp + xp_gain
                xp_needed = self.calculate_xp_needed(current_level)

                if new_xp >= xp_needed:
                    new_xp -= xp_needed
                    current_level += 1
                    await message.channel.send(f"🎉 {message.author.mention} ist jetzt Level {current_level}!")
                    await self.check_and_assign_roles(message, current_level)

                await db.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (new_xp, current_level, user_id))
            else:
                await db.execute("INSERT INTO users (user_id, xp, level, daily_bonus) VALUES (?, ?, ?, ?)", (user_id, xp_gain, 1, None))

            await db.commit()

    # Berechnung der XP für den nächsten Level
    def calculate_xp_needed(self, current_level):
        return 5 * (current_level ** 2) + 50 * current_level + 100

    # Rollen bei bestimmten Levels vergeben (IDs)
    async def check_and_assign_roles(self, message, level):
        role_rewards = {
            10: 123456789012345678,  # ID der Rolle "Aktives Mitglied"
            20: 234567890123456789,  # ID der Rolle "Veteran"
            30: 345678901234567890   # ID der Rolle "Legende"
        }

        for level_threshold, role_id in role_rewards.items():
            if level == level_threshold:
                role = message.guild.get_role(role_id)
                if role:
                    await message.author.add_roles(role)
                    await message.channel.send(f"🎉 {message.author.mention} hat die Rolle **{role.name}** erhalten!")

    # Slash-Befehl: Leaderboard anzeigen (komplettes Embed)
    @discord.slash_command(name="leaderboard", description="Zeigt das Level- und XP-Leaderboard an.")
    async def leaderboard(self, ctx):
        async with aiosqlite.connect("levels.db") as db:
            cursor = await db.execute("SELECT user_id, xp, level FROM users ORDER BY level DESC, xp DESC LIMIT 10")
            top_users = await cursor.fetchall()

        embed = discord.Embed(title="📊 Leaderboard", color=discord.Color.gold())
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else "")

        for idx, (user_id, xp, level) in enumerate(top_users, start=1):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(name=f"{idx}. {user.name}", value=f"**Level**: {level} | **XP**: {xp}", inline=False)

        embed.set_footer(text=f"Angefragt von {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)

    # Slash-Befehl: XP für Benutzer anzeigen (komplettes Embed)
    @discord.slash_command(name="xp", description="Zeigt dein aktuelles XP und Level.")
    async def check_xp(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = str(member.id)

        async with aiosqlite.connect("levels.db") as db:
            cursor = await db.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()

        if result:
            xp, level = result
            embed = discord.Embed(title=f"{member.display_name}'s Profil", color=discord.Color.green())
            embed.set_thumbnail(url=member.avatar.url)
            embed.add_field(name="Level", value=f"{level}", inline=True)
            embed.add_field(name="XP", value=f"{xp}", inline=True)
            embed.set_footer(text=f"Angefragt von {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(f"{member.mention} hat noch keine XP gesammelt.")

    # Voice-Chat XP vergeben (alle 6 Minuten)
    @tasks.loop(seconds=360)
    async def voice_xp_check(self):
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                for member in channel.members:
                    if not member.bot:
                        user_id = str(member.id)
                        xp_gain = random.randint(5, 15)

                        if self.is_double_xp_week():
                            xp_gain *= 2

                        async with aiosqlite.connect("levels.db") as db:
                            cursor = await db.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
                            result = await cursor.fetchone()

                            if result:
                                current_xp, current_level = result
                                new_xp = current_xp + xp_gain
                                await db.execute("UPDATE users SET xp = ? WHERE user_id = ?", (new_xp, user_id))
                            else:
                                await db.execute("INSERT INTO users (user_id, xp, level, daily_bonus) VALUES (?, ?, ?, ?)", (user_id, xp_gain, 1, None))

                            await db.commit()

    # Doppelte XP-Wochen prüfen
    def is_double_xp_week(self):
        week_number = datetime.utcnow().isocalendar()[1]
        return week_number in self.double_xp_weeks

    # Slash-Befehl: Wöchentliche doppelte XP-Wochen festlegen (Admin-only)
    @discord.slash_command(name="set_double_xp_week", description="Setzt eine doppelte XP-Woche (nur Admin).")
    @commands.has_permissions(administrator=True)
    async def set_double_xp_week(self, ctx):
        today = datetime.utcnow()
        week_number = today.isocalendar()[1]
        if week_number not in self.double_xp_weeks:
            self.double_xp_weeks.append(week_number)
            await ctx.respond(f"Doppelte XP-Woche festgelegt!")
        else:
            await ctx.respond(f"Diese Woche ist bereits eine doppelte XP-Woche!")

# Cog-Setup
def setup(bot):
    bot.add_cog(LevelSystem(bot))
