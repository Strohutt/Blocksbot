import discord
from discord.commands import slash_command
from discord.ext import commands, tasks
import aiosqlite
import uuid
import datetime


class PunishSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.create_warn_table())  # Warn-Datenbank erstellen
        self.reset_weekly_stats.start()  # Startet das Zurücksetzen der wöchentlichen Statistiken

    # Tabelle für Warnungen und Mod-Statistiken erstellen
    async def create_warn_table(self):
        try:
            async with aiosqlite.connect("punish.db") as db:
                # Erstelle die Tabelle falls sie nicht existiert
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS warnings (
                        warn_id TEXT PRIMARY KEY,
                        user_id TEXT,
                        mod_id TEXT,
                        reason TEXT,
                        timestamp TEXT
                    )
                """)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS mod_stats (
                        mod_id TEXT PRIMARY KEY,
                        warns INTEGER DEFAULT 0
                    )
                """)
                await db.commit()

        except Exception as e:
            print(f"[ERROR] Fehler beim Erstellen der Tabellen: {e}")

    # Warnung hinzufügen
    async def add_warn(self, user_id, mod_id, reason):
        warn_id = str(uuid.uuid4())  # Eindeutige Warn-ID erstellen
        timestamp = datetime.datetime.utcnow().strftime("%d.%m.%Y %H:%M")
        try:
            async with aiosqlite.connect("punish.db") as db:
                await db.execute("""
                    INSERT INTO warnings (warn_id, user_id, mod_id, reason, timestamp) 
                    VALUES (?, ?, ?, ?, ?)
                """, (warn_id, user_id, mod_id, reason, timestamp))
                await db.execute("""
                    INSERT INTO mod_stats (mod_id, warns)
                    VALUES (?, 1) 
                    ON CONFLICT(mod_id) 
                    DO UPDATE SET warns = warns + 1
                """, (mod_id,))
                await db.commit()
            return warn_id
        except Exception as e:
            print(f"[ERROR] Fehler beim Hinzufügen der Warnung: {e}")

    # Warnungen eines bestimmten Nutzers abrufen
    async def get_warns(self, user_id):
        try:
            async with aiosqlite.connect("punish.db") as db:
                cursor = await db.execute("""
                    SELECT warn_id, mod_id, reason, timestamp 
                    FROM warnings 
                    WHERE user_id = ? ORDER BY timestamp ASC
                """, (user_id,))
                results = await cursor.fetchall()
                return results
        except Exception as e:
            print(f"[ERROR] Fehler beim Abrufen der Warnungen: {e}")
            return []

    # Neueste Warnung abrufen
    async def get_latest_warn(self, user_id):
        try:
            async with aiosqlite.connect("punish.db") as db:
                cursor = await db.execute("""
                    SELECT warn_id, mod_id, reason, timestamp 
                    FROM warnings 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC LIMIT 1
                """, (user_id,))
                return await cursor.fetchone()
        except Exception as e:
            print(f"[ERROR] Fehler beim Abrufen der neuesten Warnung: {e}")
            return None

    # Warnung anhand der Warn-ID löschen
    async def remove_warn(self, warn_id):
        try:
            async with aiosqlite.connect("punish.db") as db:
                cursor = await db.execute("DELETE FROM warnings WHERE warn_id = ?", (warn_id,))
                await db.commit()
                return cursor.rowcount > 0  # Gibt True zurück, wenn eine Warnung gelöscht wurde
        except Exception as e:
            print(f"[ERROR] Fehler beim Löschen der Warnung: {e}")
            return False

    # Top 10 Moderatoren nach Anzahl der Verwarnungen anzeigen
    @slash_command(name="modstats", description="Zeigt die Top 10 Moderatoren mit den meisten Warns an.")
    async def mod_stats(self, ctx):
        try:
            async with aiosqlite.connect("punish.db") as db:
                cursor = await db.execute("SELECT mod_id, warns FROM mod_stats ORDER BY warns DESC LIMIT 10")
                top_mods = await cursor.fetchall()

            if not top_mods:
                await ctx.respond("Es wurden keine Verwarnungen ausgesprochen.", ephemeral=True)
                return

            embed = discord.Embed(
                title="🔝 Top 10 Moderatoren der Woche",
                description="Basierend auf der Anzahl der ausgesprochenen Verwarnungen.",
                color=discord.Color.blue()
            )

            for i, (mod_id, warns) in enumerate(top_mods, start=1):
                moderator = await self.bot.fetch_user(int(mod_id))
                embed.add_field(name=f"{i}. {moderator.name}", value=f"Verwarnungen: **{warns}**", inline=False)

            embed.set_footer(text="Statistik wird jede Woche zurückgesetzt.")
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1828/1828843.png")
            await ctx.respond(embed=embed, ephemeral=True)
        except Exception as e:
            await ctx.respond(f"Fehler beim Abrufen der Mod-Statistiken: {e}", ephemeral=True)

    # Automatisches Zurücksetzen der wöchentlichen Statistik
    @tasks.loop(time=datetime.time(0, 0))  # Jeden Sonntag um Mitternacht
    async def reset_weekly_stats(self):
        try:
            async with aiosqlite.connect("punish.db") as db:
                await db.execute("UPDATE mod_stats SET warns = 0")
                await db.commit()
                print("[DEBUG] Wöchentliche Mod-Statistiken zurückgesetzt.")
        except Exception as e:
            print(f"[ERROR] Fehler beim Zurücksetzen der Mod-Statistiken: {e}")

    @reset_weekly_stats.before_loop
    async def before_reset_weekly_stats(self):
        await self.bot.wait_until_ready()

    # Warnungen anzeigen (Admins)
    @slash_command(name="warns", description="Zeigt die Warnungen eines Nutzers an.")
    async def warns(self, ctx, user: discord.Member):
        warns = await self.get_warns(str(user.id))
        
        if warns:
            embed = discord.Embed(
                title=f"Warnungen für {user.name}#{user.discriminator}",
                color=discord.Color.orange()
            )
            for i, (warn_id, mod_id, reason, timestamp) in enumerate(warns, start=1):
                moderator = await self.bot.fetch_user(int(mod_id))  # Moderator-Name abrufen
                embed.add_field(
                    name=f"Warnung {i}:",
                    value=f"**Warn-ID:** {warn_id}\n**Grund:** {reason}\n**Moderator:** {moderator.name}\n**Zeit:** {timestamp}",
                    inline=False
                )
            embed.set_thumbnail(url=user.avatar.url)
            embed.set_footer(text="Warnübersicht")
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            await ctx.respond(f"{user.mention} hat keine Warnungen.", ephemeral=True)

    # Warnung löschen (Admins)
    @slash_command(name="removewarn", description="Löscht eine Warnung anhand der Warn-ID.")
    @discord.default_permissions(moderate_members=True)
    async def remove_warn_cmd(self, ctx, warn_id: str):
        success = await self.remove_warn(warn_id)
        if success:
            await ctx.respond(f"Warnung mit ID `{warn_id}` wurde erfolgreich gelöscht.", ephemeral=True)
        else:
            await ctx.respond(f"Warnung mit ID `{warn_id}` konnte nicht gefunden werden.", ephemeral=True)

    # Warnbefehl für Moderatoren
    @slash_command(name="warn", description="Verwarnt einen Benutzer mit einem bestimmten Grund.")
    @discord.default_permissions(moderate_members=True)
    async def warn(self, ctx, user: discord.Member, reason: str):
        mod_id = str(ctx.author.id)
        warn_id = await self.add_warn(str(user.id), mod_id, reason)

        # Warn-Embed für den gewarnten Nutzer
        warn_embed = discord.Embed(
            title="⚠️ Du wurdest verwarnt!",
            description=f"**Grund:** {reason}\n**Server:** {ctx.guild.name}",
            color=discord.Color.red()
        )
        warn_embed.set_thumbnail(url=ctx.guild.icon.url)
        warn_embed.set_footer(text=f"Verwarnt von {ctx.author.name}", icon_url=ctx.author.avatar.url)

        # Versuche, den Nutzer zu benachrichtigen
        try:
            await user.send(embed=warn_embed)
        except discord.Forbidden:
            await ctx.respond(f"{user.mention} konnte nicht privat benachrichtigt werden.", ephemeral=True)

        # Antwort-Embed für den Moderator
        response_embed = discord.Embed(
            title="✅ Verwarnung erfolgreich",
            description=f"{user.mention} wurde verwarnt für ```{reason}```.\n**Warn-ID:** `{warn_id}`",
            color=discord.Color.green()
        )
        response_embed.set_footer(text=f"Verwarnt von {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=response_embed, ephemeral=True)

    # Punish-View
    @slash_command(name="punish", description="Verwalte die Sanktionen eines Nutzers.")
    @discord.default_permissions(moderate_members=True)
    async def punish(self, ctx, user: discord.Member, reason: str):
        warns = await self.get_warns(str(user.id))
        warn_count = len(warns)

        warn_list = ""
        for warn in warns:
            mod = await self.bot.fetch_user(int(warn[1]))  # Moderator abrufen
            warn_list += f"Warn-ID: {warn[0]}, Grund: {warn[2]}, Zeit: {warn[3]}, Moderator: {mod.name}\n"
        
        warn_list = warn_list or "Keine Warnungen"
        
        overview_embed = discord.Embed(
            title=f"Wie möchtest du {user.name}#{user.discriminator} sanktionieren?",
            color=discord.Color.dark_red()
        )
        overview_embed.add_field(name="Server beigetreten", value=user.joined_at.strftime("%d.%m.%Y %H:%M"), inline=True)
        overview_embed.add_field(name="Account erstellt", value=user.created_at.strftime("%d.%m.%Y %H:%M"), inline=True)
        overview_embed.add_field(name="Top-Rolle", value=user.top_role.mention, inline=True)
        overview_embed.add_field(name="Grund:", value=f"```{reason}```", inline=False)
        overview_embed.add_field(name="Warnungen", value=f"```{warn_count}```", inline=True)
        overview_embed.add_field(name="Bisherige Warnungen", value=f"```{warn_list}```", inline=False)
        
        if user.avatar:
            overview_embed.set_thumbnail(url=user.avatar.url)
        else:
            overview_embed.set_thumbnail(url=user.default_avatar.url)

        overview_embed.set_footer(text=f"Timestamp: {datetime.datetime.utcnow()}")

        view = PunishView(self, reason, user, ctx)
        await ctx.respond(embed=overview_embed, view=view, ephemeral=True)


class PunishView(discord.ui.View):
    def __init__(self, cog, reason, user, ctx):
        super().__init__(timeout=180)
        self.cog = cog
        self.reason = reason
        self.user = user
        self.ctx = ctx

    @discord.ui.button(label="Warn", style=discord.ButtonStyle.gray, custom_id="warn", emoji="⚠️")
    async def warn(self, button: discord.ui.Button, interaction: discord.Interaction):
        mod_id = str(interaction.user.id)
        warn_id = await self.cog.add_warn(str(self.user.id), mod_id, self.reason)

        warn_embed = discord.Embed(
            title="⚠️ Du wurdest verwarnt!",
            description=f"**Grund:** {self.reason}\n**Server:** {self.ctx.guild.name}",
            color=discord.Color.red()
        )
        warn_embed.set_thumbnail(url=self.ctx.guild.icon.url)
        warn_embed.set_footer(text=f"Moderiert von {interaction.user.name}", icon_url=interaction.user.avatar.url)

        try:
            await self.user.send(embed=warn_embed)
        except discord.Forbidden:
            await interaction.response.send_message(f"{self.user.mention} konnte nicht privat benachrichtigt werden.", ephemeral=True)
            return

        response_embed = discord.Embed(
            title="✅ Verwarnung erfolgreich",
            description=f"{self.user.mention} wurde verwarnt für ```{self.reason}```.\n**Warn-ID:** `{warn_id}`",
            color=discord.Color.green()
        )
        response_embed.set_footer(text=f"Verwarnt von {interaction.user.name}", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=response_embed, ephemeral=True)

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.red, custom_id="ban", emoji="🚫")
    async def ban(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.user.guild_permissions.ban_members:
            await interaction.response.send_message("Du kannst keine Moderatoren bannen.", ephemeral=True)
            return
        if self.user.id == interaction.user.id:
            await interaction.response.send_message("Du kannst dich nicht selbst bannen!", ephemeral=True)
            return
        if interaction.user.top_role.position <= self.user.top_role.position:
            await interaction.response.send_message("Du kannst keinen Nutzer bannen, der eine höhere Rolle hat als du!", ephemeral=True)
            return
        await self.user.ban(reason=self.reason, delete_message_days=7)
        await interaction.response.send_message(f"{self.user.mention} wurde gebannt für ```{self.reason}```", ephemeral=True)

    @discord.ui.button(label="Remove Latest Warn", style=discord.ButtonStyle.blurple, custom_id="remove_warn", emoji="❌")
    async def remove_warn(self, button: discord.ui.Button, interaction: discord.Interaction):
        latest_warn = await self.cog.get_latest_warn(str(self.user.id))
        if latest_warn:
            warn_id = latest_warn[0]
            success = await self.cog.remove_warn(warn_id)
            if success:
                await interaction.response.send_message(f"Warnung mit ID `{warn_id}` wurde erfolgreich gelöscht.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Warnung mit ID `{warn_id}` konnte nicht gelöscht werden.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{self.user.mention} hat keine Warnungen.", ephemeral=True)


# Setup-Funktion für den Cog
def setup(bot):
    bot.add_cog(PunishSystem(bot))
