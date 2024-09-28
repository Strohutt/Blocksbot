import discord
from discord.ext import commands
from discord.commands import slash_command
import datetime
import time
import random


class wlc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_member_join(self, member):
        images = ["https://media.tenor.com/Dbi0cwZ4aYUAAAAC/anime-wave.gif,"
                  "https://media.tenor.com/svW4PXq7zDYAAAAC/nanami-waving.gif",
                  "https://i.pinimg.com/originals/f9/7c/c6/f97cc6c9b10b4e4a2ad74ff37431d952.gif",
                  "https://media.tenor.com/dessgik7ovcAAAAC/anime-wave.gif",
                  "https://gifdb.com/images/high/anime-yuri-waving-hand-dinhd6o73ssk8yqo.gif",
                  "https://media.tenor.com/L9frOQ90sU8AAAAC/welcome-home-anime.gif",
                  "https://thumbs.gfycat.com/AptIncompleteAllosaurus-size_restricted.gif",
                  "https://64.media.tumblr.com/30878de57a268683e1a510a9a17ffca7/tumblr_om6spdhLsk1vviqkjo1_540.gif",
                  "https://ineedanime.com/wp-content/uploads/2021/09/Rise-Matsumoto-Hello-YuruYuri.gif",
                  "https://ineedanime.com/wp-content/uploads/2021/09/Akane-Segawa-wave-never-girl-online.gif",
                  "https://image.myanimelist.net/ui/5LYzTBVoS196gvYvw3zjwP0G4-gP6b2rXqiFUVocLJ8",
                  "https://image.myanimelist.net/ui/5LYzTBVoS196gvYvw3zjwMoEck7i8Ve40Fw9G2AmPug",
                  "https://c.tenor.com/ywCocDUt31QAAAAC/anime-wave.gif",]
        embed = discord.Embed(
            title=f'<a:floating_hearts26:1086378949363388549> Willkommen auf {member.guild.name} {member.name} ! <a:floating_hearts26:1086378949363388549>',
            description=f' ',
            color=discord.Color.random()
        )
        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="Regeln", value=f' ', inline=False)
        embed.add_field(name=" ", value="Bitte lies dir die <#949011976699400202> durch! <:rules:1086378953587052615> ", inline=False)
        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="Fragen?", value=f' ', inline=False)
        embed.add_field(name=" ", value="Du kannst gerne ein <#949365533038481500> ! <:ticket:1086378956250431528>  ", inline=False)
        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="Und jetzt...", value=f' ', inline=False)
        embed.add_field(name=" ", value="Viel Spaß auf dem Server! <a:vibe:1086378958204969041>   ", inline=False)
        embed.add_field(name=" ", value=" ", inline=False)
        embed.set_image(url=random.choice(images))
        embed.set_footer(text=f'Du bist der {len(list(member.guild.members))}te User auf dem Server!')

        channel = await self.bot.fetch_channel(949011966486278225)
        await channel.send(f"{member.mention}", embed=embed)

def setup(bot):
    bot.add_cog(wlc(bot))



