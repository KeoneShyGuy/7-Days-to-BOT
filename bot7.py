import discord
from interactions import Client, CommandContext
from telnet_connection import TelnetConnection
import os

# Load the configuration
def load_config():
    config = {}
    with open('config.txt', 'r') as f:
        for line in f:
            try:
                name, value = line.strip().split('=', 1)
                config[name] = value
            except ValueError:
                print(f"Skipping malformed config line: {line.strip()}")
    return config

config = load_config()

# Discord bot token
DISCORD_TOKEN = config.get('DISCORD_TOKEN')

telnet_connection = TelnetConnection()

bot = Client(token=DISCORD_TOKEN)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.me.name}')
    telnet_connection.connect()
    telnet_connection.load_server_info()

@bot.command(
    name="serverday",
    description="Get the current server day"
)
async def serverday(ctx: CommandContext):
    await ctx.defer()
    server_time = telnet_connection.send_command("gettime")
    if server_time:
        if "Day" in server_time:
            day_info = server_time.split("Day", 1)[1].strip()
            await ctx.send(f'Day {day_info}')
        else:
            await ctx.send('Could not retrieve server day information.')
    else:
        await ctx.send('Could not retrieve server day information.')

@bot.command(
    name="listplayerids",
    description="List player IDs currently in the server"
)
async def listplayerids(ctx: CommandContext):
    await ctx.defer()
    player_list = telnet_connection.send_command("listplayerids")
    if player_list:
        # Extract relevant lines from the response
        lines = player_list.splitlines()
        relevant_lines = [line for line in lines if "id=" in line or "Total of" in line]
        relevant_output = "\n".join(relevant_lines)
        await ctx.send(f'Players:\n{relevant_output}')
    else:
        await ctx.send('Could not retrieve player list.')

@bot.command(
    name="joinserver",
    description="Get the server information to join"
)
async def joinserver(ctx: CommandContext):
    await ctx.defer()
    ip_address = telnet_connection.server_info.get('IP_ADDRESS', 'N/A')
    port_number = telnet_connection.server_info.get('PORT_NUMBER', 'N/A')
    password = telnet_connection.server_info.get('PASSWORD', 'N/A')
    server_info = f"IP Address: {ip_address}\nPort: {port_number}\nPassword: {password}"
    await ctx.send(server_info)

@bot.command(
    name="servermods",
    description="Get the mods download link and installation guide"
)
async def servermods(ctx: CommandContext):
    await ctx.defer()
    google_drive_link = telnet_connection.server_info.get('GOOGLE_DRIVE_LINK', 'N/A')
    install_guide_link = "https://7daystodiemods.com/how-to-install-7-days-to-die-mods/"
    message = (
        f"Download the mods from the following link: {google_drive_link}\n"
        f"Follow the installation guide here: {install_guide_link}"
    )
    await ctx.send(message)

bot.start()
