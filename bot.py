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
        # We use ! as a backup prefix
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Only start the loop here, do NOT sync here
        self.scheduled_announcement.start()

    async def on_ready(self):
        print(f'🚀 {self.user} is online and waiting for !sync')

    # --- THE MANUAL SYNC COMMAND ---
    # Type !sync in your Discord server to fix the / commands
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await ctx.send("Syncing commands... please wait.")
        try:
            synced = await self.tree.sync()
            await ctx.send(f"✅ Successfully synced {len(synced)} commands!")
        except Exception as e:
            await ctx.send(f"❌ Sync failed: {e}")

    # --- SLASH COMMANDS ---
    @app_commands.command(name="test_now", description="Force a test announcement")
    async def test_now(self, interaction: discord.Interaction):
        # We defer FIRST to stop the "not responding" error
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
            await interaction.followup.send("✅ Sent!")
        else:
            await interaction.followup.send("❌ Error: Channel not found.")

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
                desc = f"☀️ **{time_label} Update**"
                embed = discord.Embed(title=Config.EMBED_TITLE, description=desc, color=Config.EMBED_COLOR)
                await channel.send(embed=embed)

bot = Section8Bot()

# Manually add the slash command to the tree
bot.tree.add_command(bot.test_now)

bot.run(Config.TOKEN)