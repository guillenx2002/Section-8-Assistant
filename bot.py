import discord
from discord.ext import tasks, commands
from discord import app_commands
import datetime
import zoneinfo
from config import Config

EST = zoneinfo.ZoneInfo("US/Eastern")

class Section8Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all() # Using ALL intents to rule out permission issues
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.scheduled_announcement.start()
        # We will NOT sync here. We will do it manually to avoid rate limits.

    async def on_ready(self):
        print(f'✅ {self.user} is ONLINE.')

    @tasks.loop(time=[datetime.time(hour=0, minute=0, tzinfo=EST), datetime.time(hour=12, minute=0, tzinfo=EST)])
    async def scheduled_announcement(self):
        await self.wait_until_ready()
        now = datetime.datetime.now(EST)
        if now.weekday() in Config.SCHEDULED_DAYS:
            channel = self.get_channel(Config.ANNOUNCEMENT_CHANNEL_ID)
            if channel:
                embed = discord.Embed(title=Config.EMBED_TITLE, description="Scheduled Update", color=Config.EMBED_COLOR)
                await channel.send(embed=embed)

bot = Section8Bot()

# Simple Slash Command defined OUTSIDE to ensure it's clean
@bot.tree.command(name="test_now", description="Force a test announcement")
async def test_now(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Working!", ephemeral=True)

# Manual Sync Command (Prefix)
@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("🔄 Commands Synced!")

bot.run(Config.TOKEN)