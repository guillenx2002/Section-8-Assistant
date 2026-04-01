import discord
from discord.ext import tasks, commands
from discord import app_commands
import datetime
import zoneinfo
from config import Config

# Set the timezone to Eastern Standard Time
EST = zoneinfo.ZoneInfo("US/Eastern")

class Section8Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        # We define the command prefix, but we'll focus on Slash Commands
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Start background task
        self.scheduled_announcement.start()
        # Syncing here ensures Discord knows about your commands
        await self.tree.sync()

    async def on_ready(self):
        print(f'✅ Logged in as {self.user} (ID: {self.user.id})')
        print("Slash commands are synced and ready!")

    # --- SLASH COMMANDS ---
    @app_commands.command(name="setup", description="Change the announcement channel")
    @app_commands.describe(channel="The channel where updates should be posted")
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Tell Discord to wait (Fixes "Application did not respond")
        await interaction.response.defer(ephemeral=True)
        
        Config.ANNOUNCEMENT_CHANNEL_ID = channel.id
        await interaction.followup.send(f"✅ Announcement channel updated to {channel.mention}!")

    @app_commands.command(name="test_now", description="Force a test announcement right now")
    async def test_now(self, interaction: discord.Interaction):
        # Tell Discord to wait
        await interaction.response.defer()
        
        channel = self.get_channel(Config.ANNOUNCEMENT_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title=Config.EMBED_TITLE,
                description="🚀 **Manual Test:** Your scheduled updates are working!",
                color=Config.EMBED_COLOR
            )
            embed.set_footer(text=Config.FOOTER_TEXT)
            await channel.send(embed=embed)
            await interaction.followup.send("✅ Test announcement sent!")
        else:
            await interaction.followup.send("❌ Error: Could not find the channel. Please try /setup again.")

    # --- SCHEDULED TASK ---
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
                desc = "☀️ **Mid-day Update**" if time_label == "Noon" else "🌙 **Midnight Update**"
                
                embed = discord.Embed(title=Config.EMBED_TITLE, description=desc, color=Config.EMBED_COLOR)
                embed.set_footer(text=Config.FOOTER_TEXT)
                await channel.send(embed=embed)
                print(f"Sent {time_label} announcement.")

# Initialize the bot
bot = Section8Bot()

# NOTE: We do NOT need bot.tree.add_command here because 
# @app_commands.command is already inside the Section8Bot class.

# Run the bot
bot.run(Config.TOKEN)