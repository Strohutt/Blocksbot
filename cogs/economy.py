import discord
from discord.ext import commands
import aiosqlite
import random
from datetime import datetime

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.create_tables())  # Economy-Datenbank erstellen

    # Economy-Datenbank-Tabellen erstellen
    async def create_tables(self):
        async with aiosqlite.connect("economy.db") as db:
            # Benutzer-Coin-Tabelle
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    coins INTEGER NOT NULL
                )
            """)
            # Shop-Items-Tabelle
            await db.execute("""
                CREATE TABLE IF NOT EXISTS shop (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    item_price INTEGER NOT NULL,
                    item_type TEXT NOT NULL
                )
            """)
            # Inventar-Tabelle
            await db.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    user_id TEXT,
                    item_name TEXT,
                    UNIQUE(user_id, item_name)
                )
            """)
            await db.commit()

    # Zugriff auf die Level-Datenbank für den Level eines Benutzers
    async def get_user_level(self, user_id):
        async with aiosqlite.connect("levels.db") as db:  # Zugriff auf die bestehende Level-Datenbank
            cursor = await db.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            if result:
                return result[0]  # Gib das Level des Benutzers zurück
            return None  # Kein Level gefunden

    # Coins für Benutzer prüfen (balance)
    @discord.slash_command(name="balance", description="Zeigt dein Coins-Guthaben an.")
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = str(member.id)

        async with aiosqlite.connect("economy.db") as db:
            cursor = await db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()

        if result:
            coins = result[0]
            embed = discord.Embed(
                title=f"💰 {member.display_name}'s Konto",
                description="Hier ist dein aktuelles Coins-Guthaben:",
                color=discord.Color.green()
            )
            embed.add_field(name="💸 Coins", value=f"**{coins}**", inline=True)
            embed.set_thumbnail(url=member.avatar.url)  # Nutzer-Avatar als Thumbnail
            embed.set_footer(text=f"Angefragt von {ctx.author.name}", icon_url=ctx.author.avatar.url)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(f"{member.mention} hat noch keine Coins!")

    # Coins verdienen (daily)
    @discord.slash_command(name="daily", description="Erhalte deine täglichen Coins.")
    async def daily(self, ctx):
        user_id = str(ctx.author.id)
        coins_earned = random.randint(100, 300)  # Zufällige tägliche Coins

        async with aiosqlite.connect("economy.db") as db:
            cursor = await db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()

            if result:
                current_coins = result[0]
                new_coins = current_coins + coins_earned
                await db.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_coins, user_id))
            else:
                await db.execute("INSERT INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins_earned))

            await db.commit()

        embed = discord.Embed(
            title="🎁 Tägliche Belohnung",
            description=f"{ctx.author.mention}, hier sind deine täglichen Coins!",
            color=discord.Color.blue()
        )
        embed.add_field(name="Verdiente Coins", value=f"💰 **{coins_earned} Coins**", inline=True)
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.set_footer(text="Morgen kannst du wieder Coins beanspruchen!", icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)

    # Arbeiten basierend auf dem Level (freischaltbare Jobs)
    @discord.slash_command(name="work", description="Arbeite, um Coins zu verdienen basierend auf deinem Level.")
    async def work(self, ctx):
        user_id = str(ctx.author.id)

        # Level des Benutzers abrufen aus der Level-Datenbank
        user_level = await self.get_user_level(user_id)
        if user_level is None:
            await ctx.respond(f"{ctx.author.mention}, du hast noch kein Level. Verdiene zuerst XP im Levelsystem.")
            return

        # Verschiedene Jobs basierend auf dem Level
        jobs = {
            1: {"job": "Postbote", "coins": random.randint(50, 100)},  # Job für Level 1
            5: {"job": "Verkäufer", "coins": random.randint(100, 200)},  # Job ab Level 5
            10: {"job": "Manager", "coins": random.randint(200, 300)},  # Job ab Level 10
            20: {"job": "Unternehmer", "coins": random.randint(300, 500)}  # Job ab Level 20
        }

        available_jobs = {level: data for level, data in jobs.items() if user_level >= level}
        selected_job = max(available_jobs.values(), key=lambda x: x['coins'])  # Bestmöglicher Job

        coins_earned = selected_job['coins']

        async with aiosqlite.connect("economy.db") as db:
            cursor = await db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()

            if result:
                current_coins = result[0]
                new_coins = current_coins + coins_earned
                await db.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_coins, user_id))
            else:
                await db.execute("INSERT INTO users (user_id, coins) VALUES (?, ?)", (user_id, coins_earned))

            await db.commit()

        embed = discord.Embed(
            title=f"🛠 {ctx.author.display_name} hat gearbeitet",
            description=f"Job: **{selected_job['job']}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Verdiente Coins", value=f"💰 **{coins_earned} Coins**", inline=True)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/847/847969.png")
        embed.set_footer(text="Arbeiten lohnt sich!", icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)

    # Coins an einen anderen Benutzer übertragen
    @discord.slash_command(name="transfer", description="Übertrage Coins an einen anderen Benutzer.")
    async def transfer(self, ctx, amount: int, member: discord.Member):
        user_id = str(ctx.author.id)
        target_id = str(member.id)

        if amount <= 0:
            await ctx.respond("Der Betrag muss größer als 0 sein!")
            return

        async with aiosqlite.connect("economy.db") as db:
            cursor = await db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()

            if not result or result[0] < amount:
                await ctx.respond(f"{ctx.author.mention}, du hast nicht genug Coins!")
                return

            new_balance = result[0] - amount
            await db.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))

            cursor = await db.execute("SELECT coins FROM users WHERE user_id = ?", (target_id,))
            target_result = await cursor.fetchone()

            if target_result:
                target_new_balance = target_result[0] + amount
                await db.execute("UPDATE users SET coins = ? WHERE user_id = ?", (target_new_balance, target_id))
            else:
                await db.execute("INSERT INTO users (user_id, coins) VALUES (?, ?)", (target_id, amount))

            await db.commit()

        embed = discord.Embed(
            title="💸 Transfer erfolgreich",
            description=f"{ctx.author.mention} hat **{amount} Coins** an {member.mention} übertragen!",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2331/2331970.png")
        await ctx.respond(embed=embed)

    # Shop anzeigen
    @discord.slash_command(name="shop", description="Zeigt den Shop an, in dem du Items kaufen kannst.")
    async def shop(self, ctx):
        async with aiosqlite.connect("economy.db") as db:
            cursor = await db.execute("SELECT item_name, item_price, item_type FROM shop")
            items = await cursor.fetchall()

        if not items:
            await ctx.respond("Der Shop ist leer.")
            return

        embed = discord.Embed(title="🛒 Shop", description="Hier sind die verfügbaren Items:", color=discord.Color.green())
        for item in items:
            name, price, item_type = item
            embed.add_field(name=f"{name}", value=f"Preis: **{price} Coins** - Typ: {item_type}", inline=False)
        await ctx.respond(embed=embed)

    # Item kaufen und ins Inventar hinzufügen
    @discord.slash_command(name="buy", description="Kaufe ein Item aus dem Shop.")
    async def buy(self, ctx, item_name: str):
        user_id = str(ctx.author.id)

        async with aiosqlite.connect("economy.db") as db:
            cursor = await db.execute("SELECT item_price, item_type FROM shop WHERE item_name = ?", (item_name,))
            item = await cursor.fetchone()

            if not item:
                await ctx.respond(f"Das Item **{item_name}** existiert nicht.")
                return

            price, item_type = item
            cursor = await db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            user_coins = await cursor.fetchone()

            if not user_coins or user_coins[0] < price:
                await ctx.respond(f"{ctx.author.mention}, du hast nicht genug Coins!")
                return

            new_balance = user_coins[0] - price
            await db.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))

            # Item dem Inventar hinzufügen
            await db.execute("INSERT OR IGNORE INTO inventory (user_id, item_name) VALUES (?, ?)", (user_id, item_name))

            await db.commit()

        await ctx.respond(f"{ctx.author.mention} hat **{item_name}** für **{price} Coins** gekauft!")

    # Admin: Coins hinzufügen
    @commands.has_permissions(administrator=True)
    @discord.slash_command(name="addcoins", description="Fügt einem Benutzer Coins hinzu (nur Admin).")
    async def add_coins(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.respond("Die Menge der Coins muss größer als 0 sein.")
            return

        user_id = str(member.id)

        async with aiosqlite.connect("economy.db") as db:
            cursor = await db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()

            if result:
                new_coins = result[0] + amount
                await db.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_coins, user_id))
            else:
                await db.execute("INSERT INTO users (user_id, coins) VALUES (?, ?)", (user_id, amount))

            await db.commit()

        await ctx.respond(f"💰 {member.mention} hat **{amount} Coins** erhalten!")

    # Minispiel: 8-Ball
    @discord.slash_command(name="8ball", description="Stelle eine Frage und erhalte eine Antwort.")
    async def eight_ball(self, ctx, *, question: str):
        responses = ["Ja", "Nein", "Vielleicht", "Wahrscheinlich", "Definitiv", "Unwahrscheinlich", "Versuch es später erneut"]
        answer = random.choice(responses)
        embed = discord.Embed(
            title="🎱 8-Ball",
            description=f"**Frage**: {question}",
            color=discord.Color.purple()
        )
        embed.add_field(name="Antwort", value=f"**{answer}**", inline=False)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/130/130540.png")
        embed.set_footer(text=f"Angefragt von {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embed)

    # Minispiel: Slotmaschine mit 5 Symbolen und 3 gleichen für Gewinn
    @discord.slash_command(name="slots", description="Spiele an der Slotmaschine um Coins.")
    async def slots(self, ctx, bet: int):
        user_id = str(ctx.author.id)

        if bet <= 0:
            await ctx.respond("Der Einsatz muss größer als 0 sein!")
            return

        async with aiosqlite.connect("economy.db") as db:
            cursor = await db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()

            if not result or result[0] < bet:
                await ctx.respond(f"{ctx.author.mention}, du hast nicht genug Coins!")
                return

            symbols = ["🍒", "🍋", "🍊", "🍉", "🍇"]
            slot_result = [random.choice(symbols) for _ in range(5)]  # 5 Symbole in einer Reihe

            # Mindestens 3 gleiche Symbole für Gewinn
            if len(set(slot_result[:3])) == 1 or len(set(slot_result[1:4])) == 1 or len(set(slot_result[2:])) == 1:
                winnings = bet * 5
                new_balance = result[0] + winnings
                await db.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))
                embed = discord.Embed(
                    title="🎰 Slotmaschine",
                    description="Dreifacher Gewinn!",
                    color=discord.Color.gold()
                )
                embed.add_field(name="Ergebnis", value=f"{slot_result[0]} {slot_result[1]} {slot_result[2]} {slot_result[3]} {slot_result[4]}", inline=False)
                embed.add_field(name="Gewinn", value=f"💰 **{winnings} Coins**!", inline=False)
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/929/929444.png")
                await ctx.respond(embed=embed)
            else:
                new_balance = result[0] - bet
                await db.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))
                embed = discord.Embed(
                    title="🎰 Slotmaschine",
                    description="Leider kein Gewinn.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Ergebnis", value=f"{slot_result[0]} {slot_result[1]} {slot_result[2]} {slot_result[3]} {slot_result[4]}", inline=False)
                embed.add_field(name="Verloren", value=f"💸 **{bet} Coins**", inline=False)
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/929/929444.png")
                await ctx.respond(embed=embed)

            await db.commit()

    # Minispiel: Gamble mit max 500 Coins und 70% Gewinnchance
    @discord.slash_command(name="gamble", description="Setze bis zu 500 Coins und gewinne mit einer 70% Chance.")
    async def gamble(self, ctx, bet: int):
        user_id = str(ctx.author.id)

        if bet <= 0 or bet > 500:
            await ctx.respond("Dein Einsatz muss zwischen 1 und 500 Coins liegen!")
            return

        async with aiosqlite.connect("economy.db") as db:
            # Prüfen, ob der Benutzer genug Coins hat
            cursor = await db.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()

            if not result or result[0] < bet:
                await ctx.respond(f"{ctx.author.mention}, du hast nicht genug Coins!")
                return

            # 70% Gewinnchance
            is_winner = random.random() <= 0.7

            if is_winner:
                winnings = bet * 2
                new_balance = result[0] + winnings
                await db.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))
                embed = discord.Embed(
                    title="🎲 Gamble gewonnen!",
                    description=f"Herzlichen Glückwunsch! Du hast **{winnings} Coins** gewonnen!",
                    color=discord.Color.gold()
                )
                embed.add_field(name="Dein Gewinn", value=f"💰 **{winnings} Coins**", inline=True)
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1779/1779875.png")  # Würfel-Icon
                await ctx.respond(embed=embed)
            else:
                new_balance = result[0] - bet
                await db.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_balance, user_id))
                embed = discord.Embed(
                    title="😢 Leider verloren!",
                    description=f"Du hast **{bet} Coins** verloren. Versuche es später noch einmal!",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1779/1779875.png")  # Würfel-Icon
                await ctx.respond(embed=embed)

            await db.commit()

# Cog Setup
def setup(bot):
    bot.add_cog(Economy(bot))
