import discord
from discord.ext import tasks, commands
from discord import app_commands
import datetime
import zoneinfo
from config import Config

EST = zoneinfo.ZoneInfo("US/Eastern")

class Section8Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.scheduled_announcement.start()
        # This makes sure the commands below are attached to the bot
        self.tree.add_command(self.setup)
        self.tree.add_command(self.test_now)
        await self.tree.sync()

    async def on_ready(self):
        print(f'✅ Section 8 Helper is live.')

    # --- THE ALL-IN-ONE SETUP COMMAND ---
    @app_commands.command(name="setup", description="Configure the bot settings")
    @app_commands.describe(
        channel="Where to post", 
        title="The heading of the message",
        message="The main text",
        color="Hex color code (e.g. 0x00ff00 for green)"
    )
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, message: str, color: str = "0x00ff00"):
        await interaction.response.defer(ephemeral=True)
        
        # Update our Config settings in memory
        Config.ANNOUNCEMENT_CHANNEL_ID = channel.id
        Config.EMBED_TITLE = title
        Config.FOOTER_TEXT = message
        try:
            Config.EMBED_COLOR = int(color, 16)
        except:
            Config.EMBED_COLOR = 0x3498db # Default blue if hex is wrong
            
        await interaction.followup.send(f"✅ Settings Updated!\n**Channel:** {channel.mention}\n**Title:** {title}\n**Footer:** {message}")

    @app_commands.command(name="test_now", description="See the current announcement style")
    async def test_now(self, interaction: discord.Interaction):
        await interaction.response.defer()
        channel = self.get_channel(Config.ANNOUNCEMENT_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title=Config.EMBED_TITLE,
                description="🚀 **This is your current announcement style!**",
                color=Config.EMBED_COLOR
            )
            embed.set_footer(text=Config.FOOTER_TEXT)
            await channel.send(embed=embed)
            await interaction.followup.send("✅ Test Sent!")
        else:
            await interaction.followup.send("❌ Setup a channel first using /setup")

    @tasks.loop(time=[
        datetime.time(hour=0, minute=0, tzinfo=EST), 
        datetime.time(hour=12, minute=0, tzinfo=EST)
    ])
    async def scheduled_announcement(self):
        await self.wait_until_ready()
        now = datetime.datetime.now(EST)
        # Checks config.py for the days (0=Mon, 2=Wed, 4=Fri)
        if now.weekday() in Config.SCHEDULED_DAYS:
            channel = self.get_channel(Config.ANNOUNCEMENT_CHANNEL_ID)
            if channel:
                desc = "☀️ **Mid-day Update**" if now.hour == 12 else "🌙 **Midnight Update**"
                embed = discord.Embed(title=Config.EMBED_TITLE, description=desc, color=Config.EMBED_COLOR)
                embed.set_footer(text=Config.FOOTER_TEXT)
                await channel.send(embed=embed)

bot = Section8Bot()
bot.run(Config.TOKEN)