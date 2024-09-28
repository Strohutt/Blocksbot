import datetime

import discord
from discord.ext import commands
from discord.commands import slash_command
import asyncio

class Spawn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# after you execute the /despawn command wih a specific user the bot will timeout the user for 10 minutes
    @slash_command(name="despawn", description="Timeoutet einen bösen Buben für 10 Minuten")
    @discord.default_permissions(moderate_members=True)

    async def despawn(self, ctx, user: discord.Member):

        if user == ctx.author:
            await ctx.respond(f"Du kannst dich nicht selbst timeouten <a:pingu_slap21:1077554437410795530> ")
            await asyncio.sleep(3)
            await ctx.delete()
            return
        if user.bot:
            await ctx.respond(f"Du kannst keine Bots timeouten ")
            await asyncio.sleep(3)
            await ctx.delete()
            return
        if user.top_role >= ctx.author.top_role:
            await ctx.respond(f"Du kannst keine User timeouten die dieselbe oder eine höhere Rolle als du haben du Noob <a:pingu_slap21:1077554437410795530> ")
            await asyncio.sleep(3)
            await ctx.delete()
            return
        if user.id == 832022453915090984:
            await ctx.respond(f"Denk nichtmal dran")
            await asyncio.sleep(3)
            await ctx.delete()
            return

        await ctx.respond(f"{user.mention} wurde für 10 Minuten getimeouted")
        await user.timeout(reason="Despawn", until=discord.utils.utcnow() + datetime.timedelta(seconds=600))
        #now we delete the response message
        await asyncio.sleep(3)
        await ctx.delete()


    @slash_command(name="respawn", description="Hebt einen Timeout auf")
    @discord.default_permissions(moderate_members=True)
    async def respawn(self, ctx, user: discord.Member):
        await ctx.respond(f"{user.mention} ist wieder da")
        await user.timeout(reason="Respawn", until=discord.utils.utcnow() + datetime.timedelta(seconds=0))
        #now we delete the response message
        await asyncio.sleep(3)
        await ctx.delete()

def setup(bot):
    bot.add_cog(Spawn(bot))
