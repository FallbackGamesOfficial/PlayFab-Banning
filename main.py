import discord
from discord.ext import commands
import playfab.PlayFabServerAPI as PlayFabServer
import playfab.PlayFabSettings as PlayFabSettings
import os
from dotenv import load_dotenv

# loading variables
load_dotenv()

# Grab creds
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PLAYFAB_TITLE_ID = os.getenv("PLAYFAB_TITLE_ID")
PLAYFAB_SECRET_KEY = os.getenv("PLAYFAB_SECRET_KEY")

# Bot initialisation
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Login to PlayFab to call API
def login_to_playfab():
    if not PLAYFAB_TITLE_ID or not PLAYFAB_SECRET_KEY:
        raise ValueError("Credentials weren't provided.")
    PlayFabSettings.TitleId = PLAYFAB_TITLE_ID
    PlayFabSettings.DeveloperSecretKey = PLAYFAB_SECRET_KEY
    print("Logged into PlayFab.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    login_to_playfab()

@bot.command(name='ban_player')
@commands.has_permissions(manage_guild=True)
async def ban_player(ctx, playfab_id: str, reason: str = "VIOLATION OF RULES, MAKE A TICKET IN THE DISCORD SERVER FOR THE REASON YOU WERE BANNED!", duration: int = 24):
    await ctx.send(f"Attempting to ban player: {playfab_id} ...")
    try:
        # make request to ban the player
        ban_request = {
            "PlayFabIds": [playfab_id],
            "Bans": [{
                "PlayFabId": playfab_id,
                "Reason": reason,
                "DurationInHours": duration
            }]
        }

        def callback(response):
            print("BanUsers callback executed:", response)

            PlayFabServer.BanUsers(ban_request, callback)
            ctx.send(f"Player {playfab_id} ban request sent successfully. Reason: {reason}. Duration: {duration}.")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {str(e)}")


@ban_player.error
async def ban_player_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You do not have permission to use this command.")

bot.run(DISCORD_BOT_TOKEN)