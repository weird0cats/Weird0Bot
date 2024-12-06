#+=-=+=============================+=-=+
#-=+=- Minecraft, memes, and more! -=+=-
#+=-=+=============================+=-=+
#imports
import logging
import nextcord
import tracemalloc
import config
import os
import jsonfs
import sys
from nextcord.ext import commands, tasks, application_checks  #type:ignore
from nextcord import Interaction
from mcstatus import JavaServer
#config
#find stored token
token=jsonfs.read("token.json")["token"]
#establish log handlers
tracemalloc.start()
handler=logging.FileHandler(
    filename='./nextcord.log',
    encoding='utf-8',
    mode='w'
    )
logging.basicConfig(
    filename="./bot.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - [{levelname}]: {message}",
    style="{",
    datefmt="%Y/%m/%d - %H:%M"
)
#======== Establish Connection =========
try:
    jserver=JavaServer(config.ip,config.port) 
    jstatus=jserver.status()
except (TimeoutError) as e:
    logging.critical(e)
    print(e)
    exit()
except (NameError,Exception) as e:
    logging.error(e)
    print(e)
except OSError as e:
    logging.error(e)
    print(f"{e} server is probably inactive")
finally:
    logging.info(f"Successfully conected to {jserver.address.host}:{jserver.address.port}")
    print(f"Successfully connected to {jserver.address.host}:{jserver.address.port}!")
#=======================================
def motd():
    if type(jstatus.motd.raw) is dict:
        return jstatus.motd.raw['text']
    else:
        return jstatus.motd.raw
#=======================================
intents=nextcord.Intents.default()
intents.members=True
intents.message_content=True

bot=commands.Bot(command_prefix="§",intents=intents)
botlog=bot.get_channel(config.bot_log_id)
#=============== Boot ==================
@bot.event
async def on_ready():
    print("      ___    __   __   __   __       ___  __  ")
    print("|  | |__  | |__) |  \\ /  \\ /  `  /\\   |  /__` ")
    print(f"|/\\| |___ | |  \\ |__/ \\__/ \\__, /--\\  |  .__/ {config.version}")
    print("──────────────────────────────────────────────────────────────────────")
    print(f"Connected to {config.lnk} as {jserver.address.host}:{jserver.address.port}")
    try:
        print(f"ping: {int(jserver.ping())}ms")
        await bot.change_presence(activity=nextcord.CustomActivity(config.lnk))
    except (NameError,IOError) as e:
        logging.error(e)
        print("Server is probably offline")
        await bot.change_presence(activity=nextcord.CustomActivity("The server's probably offline."))
    loop.start()
#================ Tasks ================
@tasks.loop(minutes=1)
async def loop():
    try:
        jserver=JavaServer(config.ip,config.port)
        jstatus=jserver.status()
        await bot.change_presence(activity=nextcord.CustomActivity(f"Watching {config.lnk}. Online:{jstatus.players.online}/{jstatus.players.max}"))
    except:
        await bot.change_presence(activity=nextcord.CustomActivity("The server's probably offline."))
#=============== Commands ==============
#Help
@bot.slash_command(description="Lists all commands available")
async def help(interaction:Interaction):
    logging.info(f"{interaction.user.name} used \033[32;1m/help\033[0m")
    embed=nextcord.Embed(
        colour=nextcord.Colour.blurple(),
        title="Commands",
        description=(
            f"**/help** - displays this list.\n"
            f"**/checkserver** - checks the status of the server.\n"
            f"**/pingserver** - gets the server latency.\n"
            f"**/report** - reports a user for any server violation"
        )
    )
    await interaction.send(embed=embed,ephemeral=True)
#Checkserver
@bot.slash_command(description="Checks on the server")
async def checkserver(interaction:Interaction):
    logging.info(f"{interaction.user.name} used \033[32;1m/checkserver\033[0m")
    try:
        embed = nextcord.Embed(
            colour=nextcord.Colour.blurple(),
            title=f"Details for {config.lnk}",
            description=(
                f"**Description: **{motd()}\n"
                f"**Version: **{jstatus.version.name}\n"
                f"**Online: **{jstatus.players.online}/{jstatus.players.max}\n"
                f"**Ping: **{int(jserver.ping())}ms"
            )
        )
        await interaction.send(embed=embed,ephemeral=True)
    except (Exception, TimeoutError, OSError) as e:
        logging.error(e)
        print(e)
        await interaction.send(f"Error: {e}",ephemeral=True)
#Pingserver
@bot.slash_command(description="Gets the server latency")
async def pingserver(interaction:Interaction):
    logging.info(f"{interaction.user.name} used \033[32;1m/pingserver\033[0m")
    try:
        ping=jserver.ping()
        await interaction.send(f"Ping:{int(ping)}",ephemeral=True)
    except:  # noqa: E722
        await interaction.send("Failed to ping, server likely offline")
#Restart
@bot.slash_command(description="restarts the bot")
@application_checks.has_any_role("Admin","Server owner")
async def restart(interaction:Interaction):
    logging.info(f"{interaction.user.name} used \033[32;1m/restart\033[0m")
    await interaction.send("restarting the bot",ephemeral=True)
    os.execv(sys.executable, ['python'] + sys.argv)
#Report
@bot.slash_command(description="report a user")
async def report(interaction:Interaction,user:nextcord.User,reason:str):
    logging.info(f"{interaction.user.name} used \033[32;1m/report\033[0m")
    await interaction.send(f"reported {user} for {reason}")
    report=f"{interaction.user.name} reported {user} for {reason}"
    await botlog.send(report)
    print(report)
    logging.info(report)
#============ Error handler ============
@bot.event
async def on_application_command_error(interaction:Interaction, error):
    if isinstance(error, application_checks.ApplicationBotMissingPermissions):
        await interaction.send(f"You don't have permission to run that!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await interaction.send("You forgot something...")
    else:
        await interaction.send(error)
#=============== Run bot ===============
bot.run(token)
