import discord
from discord.ext import tasks, commands
from discord import app_commands
import datetime
import zoneinfo
from config import Config

EST = zoneinfo.ZoneInfo("US/Eastern")

class Section8Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This sends your / commands to Discord's servers
        await self.tree.sync()
        self.scheduled_announcement.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print("Slash commands synced!")

bot = Section8Bot()

# --- SLASH COMMANDS ---

@bot.tree.command(name="setup", description="Change the announcement channel")
@app_commands.describe(channel="The channel where updates should be posted")
async def setup(interaction: discord.Interaction, channel: discord.TextChannel):
    # This updates the ID in memory (you'll still want to update config.py for permanent changes)
    Config.ANNOUNCEMENT_CHANNEL_ID = channel.id
    await interaction.response.send_message(f"✅ Announcement channel updated to {channel.mention}!")

@bot.tree.command(name="test_now", description="Force a test announcement right now")
async def test_now(interaction: discord.Interaction):
    channel = bot.get_channel(Config.ANNOUNCEMENT_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title=Config.EMBED_TITLE,
            description="🚀 **Manual Test:** This is what your scheduled updates will look like!",
            color=Config.EMBED_COLOR
        )
        embed.set_footer(text=Config.FOOTER_TEXT)
        await channel.send(embed=embed)
        await interaction.response.send_message("Sent!")
    else:
        await interaction.response.send_message("Error: Could not find the channel. Use /setup first.")

# --- SHARED TASK ---
@tasks.loop(time=[
    datetime.time(hour=0, minute=0, tzinfo=EST), 
    datetime.time(hour=12, minute=0, tzinfo=EST)
])
async def scheduled_announcement():
    now = datetime.datetime.now(EST)
    if now.weekday() in Config.SCHEDULED_DAYS:
        channel = bot.get_channel(Config.ANNOUNCEMENT_CHANNEL_ID)
        if channel:
            desc = "☀️ **Mid-day Update**" if now.hour == 12 else "🌙 **Midnight Update**"
            embed = discord.Embed(title=Config.EMBED_TITLE, description=desc, color=Config.EMBED_COLOR)
            embed.set_footer(text=Config.FOOTER_TEXT)
            await channel.send(embed=embed)

bot.run(Config.TOKEN)