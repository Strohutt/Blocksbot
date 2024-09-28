import discord
from datetime import datetime
from discord.ext import commands
from discord import AuditLogAction


excluded_roles = [949005895172513812, 949262522945511486, 949646082793693184, 949263471130849290, 949262829637230632, 1034195136839700501, 949632742218416158]

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Logs when a message is deleted
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return True
        log_channel = self.bot.get_channel(1087088195595935835)
        embed = discord.Embed(
            title=f"{message.author} hat eine Nachricht gelöscht <:delte:1086650069589172296>",
            colour=discord.Colour.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Nachricht", value=f"```{message.content}```", inline=False)
        embed.add_field(name="User ID", value=f"```{message.author.id}```", inline=False)
        embed.add_field(name="Message ID", value=f"```{message.id}```", inline=False)
        embed.add_field(name="Gelöscht in", value=f"{message.channel.mention}", inline=False)
        embed.set_thumbnail(url=message.author.display_avatar.url)
        if message.attachments:
            embed.add_field(name="Angehängte Dateien", value=f"```{message.attachments[0].url}```", inline=False)
        embed.set_footer(text=f"Nachricht gelöscht am {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        await log_channel.send(embed=embed)

    # Logs when a message is edited
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return True
        log_channel = self.bot.get_channel(1087088195595935835)
        embed = discord.Embed(
            title=f"{before.author} hat eine Nachricht bearbeitet <:message_edit:1086650071594053653>",
            colour=discord.Colour.purple(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Vorher", value=f"```{before.content}```", inline=False)
        embed.add_field(name="Nachher", value=f"```{after.content}```", inline=False)
        embed.add_field(name="User ID", value=f"```{before.author.id}```", inline=False)
        embed.add_field(name="Message ID", value=f"```{before.id}```", inline=False)
        embed.add_field(name="Zur Nachricht", value=f"[Hier klicken]({after.jump_url})", inline=False)
        embed.set_thumbnail(url=after.author.display_avatar.url)
        embed.set_footer(text=f"Nachricht bearbeitet am {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        await log_channel.send(embed=embed)

    # Logs when a member joins the server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = self.bot.get_channel(1087088195595935835)
        embed = discord.Embed(
            title="Ein neues Mitglied ist beigetreten! <:join:1086650123450882051>",
            colour=discord.Colour.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Mitglied", value=f"{member.name}#{member.discriminator}", inline=False)
        embed.add_field(name="User ID", value=f"```{member.id}```", inline=False)
        embed.add_field(name="Beitrittszeit", value=f"```{datetime.now().strftime('%d.%m.%Y %H:%M')}```", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Mitgliedsbeitrag: {member.guild.name}")
        await log_channel.send(embed=embed)

    # Logs when a member leaves the server
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_channel = self.bot.get_channel(1087088195595935835)
        embed = discord.Embed(
            title="Ein Mitglied hat den Server verlassen! <:leave:1086650134567637100>",
            colour=discord.Colour.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Mitglied", value=f"{member.name}#{member.discriminator}", inline=False)
        embed.add_field(name="User ID", value=f"```{member.id}```", inline=False)
        embed.add_field(name="Verlassenszeit", value=f"```{datetime.now().strftime('%d.%m.%Y %H:%M')}```", inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Server verlassen: {member.guild.name}")
        await log_channel.send(embed=embed)

    # Logs when a role is created
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        log_channel = self.bot.get_channel(1087088195595935835)
        embed = discord.Embed(
            title=f"Eine Rolle wurde erstellt <a:writing:1086673456839544884>",
            colour=discord.Colour.gold(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Rollen Name", value=f"```{role.name}```", inline=False)
        embed.add_field(name="Rollen ID", value=f"```{role.id}```", inline=False)
        embed.add_field(name="Rollen Farbe", value=f"```{role.colour}```", inline=False)
        embed.add_field(name="Rollen Position", value=f"```{role.position}```", inline=False)
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
            if entry.target.id == role.id:
                embed.set_author(name=entry.user, icon_url=entry.user.display_avatar.url)
                break
        embed.set_footer(text=f"Guild: {role.guild.name}")
        await log_channel.send(embed=embed)

    # Logs when a role is deleted
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        log_channel = self.bot.get_channel(1087088195595935835)
        embed = discord.Embed(
            title="Eine Rolle wurde gelöscht ❌",
            colour=discord.Colour.dark_gold(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Rollen Name", value=f"```{role.name}```", inline=False)
        embed.add_field(name="Rollen ID", value=f"```{role.id}```", inline=False)
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if entry.target.id == role.id:
                embed.set_author(name=entry.user, icon_url=entry.user.display_avatar.url)
                break
        embed.set_footer(text=f"Guild: {role.guild.name}")
        await log_channel.send(embed=embed)

    # Logs when a member is banned
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        log_channel = self.bot.get_channel(1087088195595935835)
        embed = discord.Embed(
            title="Ein User wurde gebannt! <a:banbutton:1086650068368633916>",
            colour=discord.Colour.dark_red(),
            timestamp=datetime.now()
        )
        ban_entry = await guild.fetch_ban(user)
        reason = ban_entry.reason if ban_entry.reason else "Kein Grund angegeben"
        embed.add_field(name="Betroffener User", value=f"```{user}```", inline=False)
        embed.add_field(name="Betroffene User ID", value=f"```{user.id}```", inline=False)
        embed.add_field(name="Grund", value=f"```'{reason}'```", inline=False)
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                embed.set_author(name=entry.user, icon_url=entry.user.display_avatar.url)
                break
        embed.set_footer(text=f"Guild: {guild.name}")
        await log_channel.send(embed=embed)

    # Logs when a member is unbanned
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        log_channel = self.bot.get_channel(1087088195595935835)
        embed = discord.Embed(
            title="Ein User wurde entbannt! <a:apepewild:1086662139210637382>",
            colour=discord.Colour.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Betroffener User", value=f"```{user}```", inline=False)
        embed.add_field(name="Betroffene User ID", value=f"```{user.id}```", inline=False)
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            if entry.target.id == user.id:
                embed.set_author(name=entry.user, icon_url=entry.user.display_avatar.url)
                break
        embed.set_footer(text=f"Guild: {guild.name}")
        await log_channel.send(embed=embed)

    # Logs channel creation
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        log_channel = self.bot.get_channel(1087088195595935835)
        embed = discord.Embed(
            title="Ein Kanal wurde erstellt! <:create_channel:1086650129395431435>",
            colour=discord.Colour.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Kanal Name", value=f"```{channel.name}```", inline=False)
        embed.add_field(name="Kanal ID", value=f"```{channel.id}```", inline=False)
        embed.add_field(name="Kanal Typ", value=f"```{channel.type}```", inline=False)
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            if entry.target.id == channel.id:
                embed.set_author(name=entry.user, icon_url=entry.user.display_avatar.url)
                break
        embed.set_footer(text=f"Guild: {channel.guild.name}")
        await log_channel.send(embed=embed)

    # Logs channel deletion
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel = self.bot.get_channel(1087088195595935835)
        embed = discord.Embed(
            title="Ein Kanal wurde gelöscht! <:delete_channel:1086650133454665731>",
            colour=discord.Colour.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Kanal Name", value=f"```{channel.name}```", inline=False)
        embed.add_field(name="Kanal ID", value=f"```{channel.id}```", inline=False)
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                embed.set_author(name=entry.user, icon_url=entry.user.display_avatar.url)
                break
        embed.set_footer(text=f"Guild: {channel.guild.name}")
        await log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Logging(bot))
