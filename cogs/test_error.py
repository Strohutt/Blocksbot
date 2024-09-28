import discord
from discord.ext import commands
from discord.commands import slash_command, Option

class Error(commands.Cog):
    def __init__(self, bot):

        self.bot = bot
 #   @commands.Cog.listener()
 #   async def on_application_command_error(self, ctx, error):
 #       if isinstance(error, commands.CommandOnCooldown):
 #           await ctx.respond(f"Du kannst diesen Command erst in {round(error.retry_after, 2)} Sekunden wieder benutzen")
 #          await error_channel.send(f"```{error}```")
   #         await ctx.respond("Ups.. hier ist ein Fehler passiert. Ich habe den Fehler weitergeleitet und er wird so schnell wie möglich behoben. Bitte gedulde dich etwas")
  #          raise error






def setup(bot):
    bot.add_cog(Error(bot))