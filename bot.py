import discord
from discord.ext import tasks, commands
import datetime
import zoneinfo
from config import Config

# Set the timezone to Eastern Standard Time
EST = zoneinfo.ZoneInfo("US/Eastern")

class Section8Bot(commands.Bot):
    def __init__(self):
        # We must enable message_content intent to see "!test"
        intents = discord.Intents.default()
        intents.message_content = True 
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.scheduled_announcement.start()

    # --- NEW TEST COMMAND ---
    @commands.command()
    async def test(self, ctx):
        await ctx.send("✅ **Section 8 Helper is online!** Commands are working correctly.")

    @tasks.loop(time=[
        datetime.time(hour=0, minute=0, tzinfo=EST), 
        datetime.time(hour=12, minute=0, tzinfo=EST)
    ])
    async def scheduled_announcement(self):
        await self.wait_until_ready()
        
        now = datetime.datetime.now(EST)
        if now.weekday() in Config.SCHEDULED_DAYS:
            channel = self.get_channel(Config.ANNOUNCEMENT_CHANNEL_ID)
            if channel:
                time_label = "Noon" if now.hour == 12 else "Midnight"
                
                desc = "☀️ **Mid-day Update:** Check the latest housing listings." if time_label == "Noon" else "🌙 **Midnight Update:** New portal updates processed."

                embed = discord.Embed(
                    title=Config.EMBED_TITLE,
                    description=desc,
                    color=Config.EMBED_COLOR
                )
                embed.set_footer(text=Config.FOOTER_TEXT)
                
                await channel.send(embed=embed)
                print(f"Sent {time_label} announcement.")

    async def on_ready(self):
        print(f'Logged in as {self.user}.')

bot = Section8Bot()
bot.run(Config.TOKEN)