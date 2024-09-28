import discord
from discord.ext import commands
from discord.commands import slash_command
import random

class Stuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Große Listen mit zufälligen Antworten, Lob, Witzen und Fakten
        self.waffle_list = [
            "Das Wetter ist echt verrückt heute!", "Schon wieder Montag... Zeit für einen neuen Kaffee!",
            "Ich frage mich, ob Katzen wirklich so mysteriös sind, wie sie aussehen...",
            "Hast du jemals daran gedacht, dass Enten vielleicht den Planeten regieren?",
            "Ich finde, wir sollten jeden Tag wie einen Sonntag behandeln.",
            "Ich frage mich, ob Bananen wirklich Beeren sind...",
            "Kaffee ist das Lebenselixier!", "Morgen ist auch noch ein Tag!",
            "Ob Einhörner wirklich irgendwo leben?", "Was ist das Geheimnis von Zeitreisen?", 
            "Stell dir vor, Pinguine könnten fliegen!","Ich glaube, ich brauche ein Nickerchen.", 
            "Ein heißer Kakao ist immer eine gute Idee!", "Was ist, wenn die Matrix real ist?",
            "Warum ist Pizza eigentlich so lecker?", "Schokolade ist wirklich das beste Essen!", 
            "Ich vermisse die Sommerferien!", "Zeit ist relativ, aber der Montag dauert ewig!",
            "Vielleicht gibt es ja wirklich eine geheime Unterwasser-Stadt?", "Warum können Kängurus nicht rückwärts hüpfen?"
        ]
        self.compliments = [
            "Du bist cooler als eine Klimaanlage im Hochsommer!", "Du bringst jeden Raum zum Strahlen!",
            "Dein Humor ist legendär!", "Du bist stärker als mein Morgenkaffee!", "Du bist cleverer als Google!",
            "Du bist so hell wie die Sonne am klaren Himmel!", "Du bist einzigartig!", "Du machst die Welt besser!",
            "Du bist mutiger als jeder Superheld!", "Du hast das Lächeln eines Champions!", "Du bist der Grund, warum heute ein guter Tag ist!",
            "Du bist ein wahres Original!", "Du rockst!", "Wenn du lächelst, wird die Welt heller!", 
            "Niemand kann dich ersetzen, du bist wirklich einzigartig!", "Du hast die Energie von 100 Sonnenscheinen!",
            "Mit dir wird jeder Tag zum Abenteuer!", "Du bist die Definition von Großartigkeit!"
        ]
        self.facts = [
            "Wusstest du, dass Schnecken bis zu 3 Jahre lang schlafen können?", "Ein Blitz ist fünfmal heißer als die Sonne!",
            "Octopusse haben drei Herzen!", "Bananen sind Beeren, aber Erdbeeren nicht!", 
            "Wasser macht nur 1% der Erdkruste aus, aber es bedeckt 70% der Erdoberfläche!", 
            "Honig verdirbt nie. Archäologen haben essbaren Honig in antiken Gräbern gefunden.", 
            "Die Zunge eines Blauwals wiegt so viel wie ein Elefant.", 
            "Menschen und Bananen teilen etwa 60% ihrer DNA!", "Das Auge eines Straußes ist größer als sein Gehirn!",
            "Ameisen können das 50-fache ihres Körpergewichts tragen!", "Ein Kolibri schlägt seine Flügel bis zu 80 Mal pro Sekunde!",
            "Kühe haben beste Freunde und werden gestresst, wenn sie voneinander getrennt werden.",
            "Goldfische können sich bis zu sechs Monate lang an Dinge erinnern!", 
            "Ein menschliches Haar kann bis zu 100 Gramm Gewicht tragen.", 
            "Die längste aufgezeichnete Flugzeit eines Huhns beträgt 13 Sekunden.",
            "Es gibt mehr Sterne im Universum als Sandkörner auf der Erde.", "Der größte Baum der Welt ist der General Sherman in Kalifornien."
        ]
        self.dad_jokes = [
            "Warum können Skelette nicht lügen? Weil man durch sie hindurchsieht!", 
            "Wie nennt man einen Bumerang, der nicht zurückkommt? Einen Stock.",
            "Ich habe heute ein unsichtbares Buch gelesen. Es war nicht besonders spannend.", 
            "Warum haben Giraffen so lange Hälse? Weil ihre Köpfe so weit weg von ihren Körpern sind!", 
            "Wie macht der Ozean? Er winkt!", 
            "Warum dürfen Geister keine Lügen erzählen? Weil sie durchscheinend sind!",
            "Ich wollte einen Witz über Zeitreisen machen, aber ihr habt ihn sowieso nicht verstanden.",
            "Warum spielen Bäcker keine Karten? Weil sie Angst vor den Krumen haben!", 
            "Hast du den Witz über das Flugzeug gehört? Er ist echt abgehoben!", 
            "Warum mögen Programmierer keine Natur? Weil es zu viele Bugs gibt!"
        ]
        self.random_emojis = ["😄", "😂", "😎", "🤔", "😢", "😡", "😍", "🙈", "🎉", "🥳", "🔥", "🌈", "🐧", "🐱", "🍕", "☕", "🌟"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Zufällige Chance (10%) für zufällige Nachricht
        if random.random() < 0.1:
            await message.channel.send(random.choice(self.waffle_list))

        # Zufällige Chance (5%) für ein Lob
        if random.random() < 0.05:
            await message.channel.send(f"{message.author.mention}, {random.choice(self.compliments)}")

        # Zufällige Chance (3%) für einen Dad-Joke
        if random.random() < 0.03:
            await message.channel.send(f"{random.choice(self.dad_jokes)}")

        # Zufällige Chance (3%) für einen zufälligen Emoji
        if random.random() < 0.03:
            await message.channel.send(random.choice(self.random_emojis))

    # 1. Kicktest-Befehl
    @slash_command()
    async def kicktest(self, ctx, member: discord.Member):
        await member.kick()
        await ctx.respond(f"{member.name} wurde gekickt!")

    # 2. Münzwurf-Befehl
    @slash_command(name="muenzwurf", description="Wirf eine Münze und sieh, ob du Kopf oder Zahl bekommst!")
    async def muenzwurf(self, ctx):
        result = random.choice(["Kopf", "Zahl"])
        await ctx.respond(f"Die Münze zeigt: **{result}**!")


    # 4. Rollenspiel "Hau den Bot"
    @slash_command(name="hau", description="Hau den Bot... aber sei vorsichtig!")
    async def hau(self, ctx):
        responses = [
            "Autsch! 😢", "Hör auf damit!", "Ich dachte, wir sind Freunde!", "Das tut weh! 😡", 
            "Okay, noch einmal und ich geh offline!", "Wirklich? Ich dachte, du magst mich!", "Na warte, ich merk's mir!"
        ]
        await ctx.respond(random.choice(responses))

    # 5. Zufälliger Dad-Joke Befehl
    @slash_command(name="dadjoke", description="Lass dir einen zufälligen Dad-Joke erzählen!")
    async def dadjoke(self, ctx):
        await ctx.respond(random.choice(self.dad_jokes))

    # 6. Zufälliger Fakt Befehl
    @slash_command(name="randomfact", description="Erhalte einen zufälligen, nutzlosen Fakt.")
    async def randomfact(self, ctx):
        await ctx.respond(f"**Wusstest du?** {random.choice(self.facts)}")

    # 7. Witz-Bewertungs-Befehl
    @slash_command(name="ratejoke", description="Der Bot bewertet deinen Witz!")
    async def ratejoke(self, ctx, joke: str):
        ratings = [
            "Das war großartig! 10/10!", "Hmm, eher 5/10.", "Okay, das war schlecht. 2/10.",
            "Nicht schlecht! 7/10.", "Das bringt mich zum Lachen! 8/10.", "Versuch's nochmal! 3/10."
        ]
        rating = random.choice(ratings)
        await ctx.respond(f"**Witz:** {joke}\n**Bewertung:** {rating}")

    # 8. Zufällige Emoji-Reaktion Befehl
    @slash_command(name="randomemoji", description="Der Bot sendet ein zufälliges Emoji!")
    async def randomemoji(self, ctx):
        await ctx.respond(random.choice(self.random_emojis))

    # 9. Befehl "Lob den Nutzer"
    @slash_command(name="lob", description="Lobe einen Nutzer auf lustige Weise!")
    async def lob(self, ctx, member: discord.Member):
        await ctx.respond(f"{member.mention}, {random.choice(self.compliments)}")

    # 10. Befehl "Stimmung heben"
    @slash_command(name="stimmung", description="Der Bot wird versuchen, deine Stimmung zu heben!")
    async def stimmung(self, ctx):
        uplifting_messages = [
            "Du bist wertvoll! 💪", "Mach weiter so, du schaffst das!", "Es gibt niemanden wie dich!",
            "Das Leben ist ein Abenteuer, und du rockst es!", "Lass dich nicht unterkriegen, du bist fantastisch!"
        ]
        await ctx.respond(random.choice(uplifting_messages))

def setup(bot):
    bot.add_cog(Stuff(bot))
