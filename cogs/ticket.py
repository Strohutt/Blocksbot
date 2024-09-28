import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ui import View, button
from discord import ButtonStyle
import io
import os
import time
import asyncio

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="ticketsetup", description="Erstellt ein Setup für ein Ticket System")
    @discord.default_permissions(administrator=True)
    async def ticket(self, ctx):
        ticket_embed = discord.Embed(
            title="Fragen? Anliegen? Erstell ein Ticket!",
            color=discord.Colour.dark_grey()
        )
        ticket_embed.set_thumbnail(url="https://media.tenor.com/adDmUZWJDcYAAAAC/sova-sova-valorant.gif")
        ticket_embed.add_field(name=" ", value=" ", inline=False)
        ticket_embed.add_field(name="Erklärung Support Ticket", value="> Du hast **generelle Fragen zum Server** oder möchtest jemanden melden?\n > Dann erstelle ein **Support Ticket**", inline=False)
        ticket_embed.add_field(name=" ", value=" ", inline=False)
        ticket_embed.add_field(name="Erklärung Beschwerde", value="> **Dir gefällt es nicht wie** ein Teammitglied **mit dir umgegangen** ist oder wie gewisse Sachen im Server ablaufen??\n > Dann erstell eine **Beschwerde**!", inline=False)
        ticket_embed.add_field(name=" ", value=" ", inline=False)
        ticket_embed.add_field(name="Erklärung Booster", value="> Du hast **geboostet** und möchtest deine **Custom Role**??\n > Dann erstell ein **Booster Ticket**!", inline=False)
        ticket_embed.add_field(name=" ", value=" ", inline=False)
        ticket_embed.add_field(name="Erklärung Content Creator Anfrage", value="> Du möchtest dich als **Content Creator** bewerben??\n > Dann erstell ein **Content Creator Ticket**!", inline=False)
        await ctx.send(view=TicketView(), embed=ticket_embed)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView())
        self.bot.add_view(ButtonTicketView())
        self.bot.add_view(ConfirmTicketView())


class ConfirmTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label=' ',
        style=discord.ButtonStyle.primary,
        emoji='<a:CH_IconVoteYes:711765210607779872>',
        custom_id='yes'
    )
    async def yes_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Ticket wird geschlossen...<a:loading_dots:1086374291165163640>", ephemeral=True)
        guild = interaction.guild
        log_channel = guild.get_channel(1096798491268878357)

        file_name = f"ticket-{interaction.user.name}.txt"

        with io.StringIO() as file:
            async for message in interaction.channel.history(limit=None, oldest_first=True):
                if message.author.bot:
                    continue
                time = message.created_at.strftime("%d.%m.%Y %H:%M")
                file.write(f"{time} - {message.author}: {message.content}\n")
            file.seek(0)
            file_content = file.read()
        file = discord.File(io.BytesIO(file_content.encode()), filename=file_name)
        await log_channel.send(file=file, content=f"Ticket wurde von {interaction.user.mention} geschlossen.")

        file_path = f"/{file_name}"
        if os.path.exists(file_path):
            os.remove(file_path)

        await asyncio.sleep(3)
        await interaction.channel.delete()

    @discord.ui.button(
        label=' ',
        style=discord.ButtonStyle.danger,
        emoji='<a:b_no:606562703917449226>',
        custom_id='no'
    )
    async def no_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(f"Ticket wird nicht geschlossen <a:loading_dots:1086374291165163640>", ephemeral=True)
        await asyncio.sleep(3)
        await interaction.delete_original_response()


class ButtonTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(
        label='Ticket schließen',
        style=discord.ButtonStyle.danger,
        emoji='<:lock:1086349246699163800>',
        custom_id='close'
    )
    async def close_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed_close = discord.Embed( 
            title=f"Ticket von {interaction.user.name}",
            color=discord.Colour.random()
        )
        embed_close.add_field(name=" ", value=" ", inline=False)
        embed_close.add_field(name="Bist du dir sicher das du das Ticket schließen möchtest?", value=" ", inline=False)
        embed_close.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.response.send_message(embed=embed_close, view=ConfirmTicketView())
        await asyncio.sleep(10)
        await interaction.delete_original_response()


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label=' Support',
        style=discord.ButtonStyle.green,
        emoji='<a:pepesup:1086350452054044683>',
        custom_id='support'
    )
    async def support_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = await interaction.guild.create_text_channel(
            name=f"Ticket-von-{interaction.user.name}",
            category=interaction.guild.get_channel(949646734605287474),
            topic=f"Ticket von **{interaction.user.name}**",
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.get_role(948916609848848384): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                interaction.guild.get_role(948916140065841222): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                interaction.guild.get_role(948916215265505350): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )
        support_embed = discord.Embed(
            title=f"Ticket von {interaction.user.name}",
            color=discord.Colour.random()
        )
        support_embed.add_field(name="Willkommen", value="Hey, bitte hab etwas Geduld es wird sich gleich jemand um dich kümmern!", inline=False)
        support_embed.add_field(name=" ", value=" ", inline=False)
        support_embed.add_field(name="Bitte formuliere dein Anliegen/Fragen konkret!", value=" ", inline=False)
        support_embed.set_footer(text=f"Ticket erstellt am {time.strftime('%d.%m.%Y %H:%M')}")
        support_embed.set_thumbnail(url=interaction.user.avatar)
        message = await channel.send(content=f"{interaction.user.mention} {interaction.guild.get_role(948916609848848384).mention} {interaction.guild.get_role(948916215265505350).mention}", embed=support_embed)
        await message.edit(content=" ")
        await message.edit(view=ButtonTicketView())

        await interaction.response.send_message(f"Dein Support Ticket wurde erstellt: {channel.mention}", ephemeral=True)
        await asyncio.sleep(7)
        await interaction.delete_original_response()

    @discord.ui.button(
        label=' Beschwerde',
        style=discord.ButtonStyle.danger,
        emoji='<a:mad:1086350563098243154>',
        custom_id='beschwerde'
    )
    async def beschwerde_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = await interaction.guild.create_text_channel(
            name=f"Beschw-von-{interaction.user.name}",
            category=interaction.guild.get_channel(949646734605287474),
            topic=f"Beschwerde von **{interaction.user.name}**",
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.get_role(948912560932003870): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                interaction.guild.get_role(1085672843242635405): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True)
            }
        )
        beschwerde_embed = discord.Embed(
            title=f"Ticket von {interaction.user.name}",
            color=discord.Colour.random()
        )
        beschwerde_embed.add_field(name="Willkommen", value="Bitte hab etwas Geduld es wird sich gleich jemand um dich kümmern!", inline=False)
        beschwerde_embed.add_field(name=" ", value=" ", inline=False)
        beschwerde_embed.add_field(name="Bitte schildere uns genau was dir nicht passt!", value=" ", inline=False)
        beschwerde_embed.set_footer(text=f"Ticket erstellt am {time.strftime('%d.%m.%Y %H:%M')}")
        beschwerde_embed.set_thumbnail(url=interaction.user.avatar)
        message = await channel.send(content=f"{interaction.user.mention} {interaction.guild.get_role(1085672843242635405).mention} {interaction.guild.get_role(948912560932003870).mention}", embed=beschwerde_embed)
        await message.edit(content=" ")
        await message.edit(view=ButtonTicketView())

        await interaction.response.send_message(f"Deine Beschwerde wurde erstellt: {channel.mention}", ephemeral=True)
        await asyncio.sleep(7)
        await interaction.delete_original_response()

    @discord.ui.button(
        label=' Custom Role',
        style=discord.ButtonStyle.blurple,
        emoji='<a:Booster:931212289237999726>',
        custom_id='custom_role'
    )
    async def content_creator_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = await interaction.guild.create_text_channel(
            name=f"CR-{interaction.user.name}",
            category=interaction.guild.get_channel(949646734605287474),
            topic=f"Custom Role Anfrage von **{interaction.user.name}**",
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.get_role(948916140065841222): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                interaction.guild.get_role(1085672843242635405): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True)
            }
        )
        booster_embed = discord.Embed(
            title=f"Ticket von {interaction.user.name}",
            color=discord.Colour.random()
        )
        booster_embed.add_field(name="Willkommen", value="Hey, bitte hab etwas Geduld es wird sich gleich jemand um dich kümmern!", inline=False)
        booster_embed.add_field(name=" ", value=" ", inline=False)
        booster_embed.add_field(name="Bitte sende uns deinen Namen der Rolle mit der Farbe (ggf. Color Code)!", value=" ", inline=False)
        booster_embed.set_footer(text=f"Ticket erstellt am {time.strftime('%d.%m.%Y %H:%M')}")
        booster_embed.set_thumbnail(url=interaction.user.avatar)
        message = await channel.send(content=f"{interaction.user.mention} {interaction.guild.get_role(948915476023640095).mention} {interaction.guild.get_role(1085672843242635405).mention}", embed=booster_embed)
        await message.edit(content=" ")
        await message.edit(view=ButtonTicketView())

        await interaction.response.send_message(f"Dein Ticket wurde erstellt: {channel.mention}", ephemeral=True)
        await asyncio.sleep(7)
        await interaction.delete_original_response()

    @discord.ui.button(
        label='Content Creator',
        style=discord.ButtonStyle.grey,
        emoji='<a:content_creator:1086769102493851800>',
        custom_id='content_creator'
    )
    async def custom_role_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = await interaction.guild.create_text_channel(
            name=f"CC-{interaction.user.name}-",
            category=interaction.guild.get_channel(949646734605287474),
            topic=f"Content Creator Anfrage von **{interaction.user.name}**",
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.get_role(1085672843242635405): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                interaction.guild.get_role(1078040570641010800): discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True)
            }
        )
        content_creator_embed = discord.Embed(
            title=f"Ticket von {interaction.user.name}",
            color=discord.Colour.random()
        )
        content_creator_embed.add_field(name="Willkommen", value="Hey, bitte hab etwas Geduld es wird sich gleich jemand um dich kümmern!", inline=False)
        content_creator_embed.add_field(name=" ", value=" ", inline=False)
        content_creator_embed.add_field(name="Bitte schicke deinen jeweiligen Channel und deine Analytics von den letzten 30 Tagen", value=" ", inline=False)
        content_creator_embed.set_footer(text=f"Ticket erstellt am {time.strftime('%d.%m.%Y %H:%M')}")
        content_creator_embed.set_thumbnail(url=interaction.user.avatar)
        message = await channel.send(content=f"{interaction.user.mention} {interaction.guild.get_role(1078040570641010800).mention}", embed=content_creator_embed)
        await message.edit(content=" ")
        await message.edit(view=ButtonTicketView())

        await interaction.response.send_message(f"Dein Ticket wurde erstellt: {channel.mention}", ephemeral=True)
        await asyncio.sleep(7) 
        await interaction.delete_original_response()


def setup(bot):
    bot.add_cog(Ticket(bot))
