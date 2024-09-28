import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import asyncio
import random


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user in message.mentions:
            await message.channel.send(f"Was los {message.author.mention} <:1685nerd:1082674870762094652> ?")

    @slash_command(name="help", description="Zeigt dir alle Befehle an")
    async def help(self, ctx):
        embed = discord.Embed(
            title="Help Menü",
            description="Bitte wähle eine Kategorie aus, um die entsprechenden Befehle zu sehen.",
            color=0x7FFFD4
        )
        embed.set_footer(text="Wähle die entsprechende Kategorie!")
        await ctx.respond(embed=embed, view=HelpView(ctx.author), ephemeral=True)


# Dropdown für verschiedene Hilfe-Kategorien
class HelpDropdown(discord.ui.Select):
    def __init__(self, is_mod: bool, is_admin: bool):
        options = [
            discord.SelectOption(label="General Help", description="Allgemeine Befehle", emoji="ℹ️"),
            discord.SelectOption(label="Economy Help", description="Economy-System-Befehle", emoji="💰"),
            discord.SelectOption(label="Ticket Help", description="Ticket-System-Befehle", emoji="🎫"),
            discord.SelectOption(label="Jobs Help", description="Jobs-System-Befehle", emoji="💼"),
        ]

        # Mods sehen Moderation-Option
        if is_mod:
            options.append(discord.SelectOption(label="Moderation Help", description="Moderations-Befehle", emoji="🔨"))
        
        # Admins sehen die Admin-Option
        if is_admin:
            options.append(discord.SelectOption(label="Admin Help", description="Admin-spezifische Befehle", emoji="🛠️"))

        super().__init__(placeholder="Wähle eine Kategorie", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "General Help":
            await interaction.response.send_message(embed=self.general_help_embed(), ephemeral=True)
        elif self.values[0] == "Economy Help":
            await interaction.response.send_message(embed=self.economy_help_embed(), ephemeral=True)
        elif self.values[0] == "Ticket Help":
            await interaction.response.send_message(embed=self.ticket_help_embed(), ephemeral=True)
        elif self.values[0] == "Jobs Help":
            await interaction.response.send_message(embed=self.jobs_help_embed(), ephemeral=True)
        elif self.values[0] == "Moderation Help":
            await interaction.response.send_message(embed=self.moderation_help_embed(), ephemeral=True)
        elif self.values[0] == "Admin Help":
            await interaction.response.send_message(embed=self.admin_help_embed(), ephemeral=True)

    def general_help_embed(self):
        embed = discord.Embed(title="Allgemeine Befehle", description="Hier sind alle allgemeinen Befehle:", color=0x7FFFD4)
        embed.add_field(name="/help", value="Zeigt dir alle Befehle an", inline=False)
        embed.add_field(name="/ping", value="Testet die Latenz zum Bot (in ms)", inline=False)
        embed.set_footer(text="Mehr allgemeine Befehle folgen bald!")
        return embed

    def economy_help_embed(self):
        embed = discord.Embed(title="Economy-System Befehle", description="Hier sind alle Befehle für das Economy-System:", color=0xFFD700)
        embed.add_field(name="/balance", value="Zeigt dein aktuelles Guthaben an", inline=False)
        embed.add_field(name="/daily", value="Erhalte deine täglichen Coins", inline=False)
        embed.add_field(name="/shop", value="Zeigt den Shop an", inline=False)
        embed.add_field(name="/buy", value="Kaufe ein Item im Shop", inline=False)
        embed.add_field(name="/slots", value="Spiele an der Slotmaschine", inline=False)
        embed.set_footer(text="Viel Erfolg beim Sparen!")
        return embed

    def ticket_help_embed(self):
        embed = discord.Embed(title="Ticket-System Befehle", description="Hier sind alle Befehle für das Ticket-System:", color=0x00FF7F)
        embed.add_field(name="/ticketsetup", value="Erstellt das Setup für das Ticket-System", inline=False)
        embed.add_field(name="Buttons im Ticket-Channel", value="• Support: Erstellt ein Support-Ticket\n• Beschwerde: Erstellt eine Beschwerde\n• Booster: Anfrage für eine Custom Role\n• Content Creator: Bewerbung als Content Creator", inline=False)
        embed.set_footer(text="Benutze das Ticket-System verantwortungsbewusst!")
        return embed

    def jobs_help_embed(self):
        embed = discord.Embed(title="Jobs-System Befehle", description="Hier sind alle Befehle für das Jobs-System:", color=0xADFF2F)
        embed.add_field(name="/work", value="Arbeite und verdiene Coins basierend auf deinem Level", inline=False)
        embed.add_field(name="/jobrank", value="Zeigt deinen Rang und Job-Level", inline=False)
        embed.add_field(name="/workupgrades", value="Zeigt verfügbare Job-Upgrades, die du freischalten kannst", inline=False)
        embed.set_footer(text="Werde reich durch harte Arbeit!")
        return embed

    def moderation_help_embed(self):
        embed = discord.Embed(title="Moderations-Befehle", description="Hier sind alle Moderations-Befehle:", color=0xFF4500)
        embed.add_field(name="/despawn", value="Timeoutet einen Nutzer für 10 Minuten", inline=False)
        embed.add_field(name="/respawn", value="Hebt einen Timeout auf", inline=False)
        embed.add_field(name="/ban", value="Bannt einen Nutzer", inline=False)
        embed.add_field(name="/kick", value="Kickt einen Nutzer", inline=False)
        embed.add_field(name="/warn", value="Verwarnt einen Nutzer", inline=False)
        embed.set_footer(text="Sei verantwortlich mit deiner Macht!")
        return embed

    def admin_help_embed(self):
        embed = discord.Embed(title="Admin Befehle", description="Hier sind alle Admin-spezifischen Befehle:", color=0x8B0000)
        embed.add_field(name="/addxp", value="Fügt einem Benutzer XP hinzu", inline=False)
        embed.add_field(name="/setxp", value="Setzt die XP eines Benutzers", inline=False)
        embed.add_field(name="/2xp", value="Aktiviert doppelten XP-Gewinn für alle Benutzer", inline=False)
        embed.add_field(name="/removejob", value="Entfernt einen Job oder ein Level von einem Benutzer", inline=False)
        embed.set_footer(text="Achtung: Diese Befehle haben große Auswirkungen!")
        return embed


class HelpView(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        is_mod = user.guild_permissions.moderate_members  # Prüfe, ob der Benutzer Mod ist
        is_admin = user.guild_permissions.administrator  # Prüfe, ob der Benutzer Admin ist
        self.add_item(HelpDropdown(is_mod, is_admin))


def setup(bot):
    bot.add_cog(Help(bot))
