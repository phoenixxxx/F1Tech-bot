from typing import Final

import os
from dotenv import load_dotenv

from discord import Intents, Client, Message, app_commands
from discord import RawReactionActionEvent, RawMessageDeleteEvent
from discord import Embed, Colour

# Load the Bot token from the env file
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
CLIENT: Final[int] = os.getenv('DISCORD_CLIENT')
print(f"[main][Init] TOKEN is {TOKEN} CLIENT is {CLIENT}")

# importing the command files
from Commands.slash import register as register_slash_commands
from Commands.menu import register as register_menu_commands

# Bot setup
intents = Intents.default()
intents.message_content = True
client  = Client(intents=intents)
tree    = app_commands.CommandTree(client)

# register the commands
register_slash_commands(tree)
register_menu_commands(tree)

# Handle bot startup
@client.event
async def on_ready() -> None:
    try:
        print(f'{client.user} syncing tree')
        await tree.sync()
    except Exception as e:
        print(e)
    print(f'{client.user} is now running')

# Handle incoming message
@client.event
async def on_message(message: Message) -> None:
    # author message is the bot
    if message.author == client.user:
        return
    
    user_message: str = str(message.content)
    if user_message[0] == '!':
        user_message = user_message[1:]
        embed = Embed(
            color=Colour.teal(),
            title="Announcement",
        )
        embed.add_field(name="Info", value=user_message, inline=False)
        channel = message.channel# message.channel.send(embed=embed)
        await message.delete()
        await channel.send(embed=embed)

# Handle message deletion
@client.event
async def on_raw_message_delete(event: RawMessageDeleteEvent) -> None:
    print("Deleting message")

@client.event
async def on_raw_reaction_add(event: RawReactionActionEvent) -> None:
    print("Adding reaction")

@client.event
async def on_raw_reaction_remove(event: RawReactionActionEvent) -> None:
    print("Removing reaction")

# Bot main entry point
if __name__ == '__main__':
    client.run(token=TOKEN)