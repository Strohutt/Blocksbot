import discord
from discord.ext import commands
from discord.commands import slash_command
import asyncio
import datetime


class Bewerbungmodal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="bewerben", description="Bewirb dich als T-Supporter")
    async def bewerben(self, ctx):
        modal = BewerbungsModal(title="Bewerbung für ValoHS als T-Supporter", )
        await ctx.send_modal(modal)


class BewerbungsModal(discord.ui.Modal):

    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Onlinezeit",
                placeholder="Bspw. 4h am Tag",
                style=discord.InputTextStyle.short
            ),
            discord.ui.InputText(
                label="Infos über dich",
                placeholder="Bspw. Hobbys, Alter, etc.",
                style=discord.InputTextStyle.long,
                min_length=150
            ),
            discord.ui.InputText(
                label="Warum möchtest du T-Supporter werden?",
                placeholder="Nenne uns einfach deine Gründe und Motivation",
                style=discord.InputTextStyle.paragraph,
                min_length=60
            ),
            discord.ui.InputText(
                label="Hast du Erfahrung mit dem Moderieren?",
                placeholder="Ja/Nein und wenn ja, auf welchen Servern?",
                style=discord.InputTextStyle.paragraph
            ),
            discord.ui.InputText(
                label="Warum genau wir?",
                placeholder="",
                style=discord.InputTextStyle.long,
                min_length=60
            ),
            *args,
            **kwargs
        )

    def stop(self):
        return self

    async def callback(self, interaction):
        embed = discord.Embed(
            title=f"Bewerbung von {interaction.user.name}#{interaction.user.discriminator}",
            description="",
            color=discord.Color.green()
        )
        embed.add_field(name="Onlinezeit", value=f"```{self.children[0].value}```", inline=True)
        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="Infos über dich", value=f"```{self.children[1].value}```", inline=True)
        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="Warum möchtest du T-Supporter werden?", value=f"```{self.children[2].value}```", inline=True)
        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="Hast du Erfahrung mit dem Moderieren?", value=f"```{self.children[3].value}```", inline=True)
        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="Warum genau wir?", value=f"```{self.children[4].value}```", inline=True)
        embed.add_field(name=" ", value=" ", inline=False)
        embed.set_footer(text=f"ID: {interaction.user.id} | {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

        guild = interaction.guild
        bewerb_channel = guild.get_channel(1091404761695268876)
        await interaction.response.send_message("Deine Bewerbung wurde erfolgreich abgeschickt!", ephemeral=True)
        await bewerb_channel.send(embed=embed)
        await asyncio.sleep(5)
        await interaction.delete_original_response()


def setup(bot):
    bot.add_cog(Bewerbungmodal(bot))