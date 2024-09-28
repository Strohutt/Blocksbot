import discord
from discord.ext import commands
from discord.commands import slash_command
import asyncio
import os


class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="purge", description="Löscht eine bestimmte Anzahl an Nachrichten")
    @discord.default_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if amount > 500:
            await ctx.respond("Du kannst nicht mehr als 500 Nachrichten auf einmal löschen! ", ephemeral=True)
            return
        if amount < 1:
            await ctx.respond("Du musst mindestens 1 Nachricht löschen!", ephemeral=True)
            return


        await ctx.respond(f"Lösche {amount} Nachrichten <a:multiload:1086652800085278780> ")
        await asyncio.sleep(2)
        deleted_messages = await ctx.channel.purge(limit=amount+1)
        if deleted_messages and len(deleted_messages) > 20:


            if deleted_messages:
                with open("deleted_messages.txt", "w", encoding="utf-8") as f:
                    for message in deleted_messages:
                        f.write(f"{message.author}: {message.content}\n\n")

                log_channel = self.bot.get_channel(1087099258974503013)
                if log_channel:
                    with open("deleted_messages.txt", "rb") as f:
                        await log_channel.send(f"**Purge Command durchgeführt von {ctx.author.mention}**", file=discord.File(f, filename="deleted_messages.txt"))

                os.remove("deleted_messages.txt")
            else:
                await ctx.respond("Keine Nachrichten gefunden, die gelöscht werden konnten.", ephemeral=True)
        else:
            pass


def setup(bot):
    bot.add_cog(Purge(bot))
