from typing import Final
import traceback

import os
import uuid
from dotenv import load_dotenv

from discord import Intents, Client, File, Message, Interaction, app_commands
from discord import RawReactionActionEvent, RawMessageDeleteEvent
from discord import Embed, Colour

import Moderation.moderation as Moderation
import Telemetry.gap_to_fastest as gap_to_fastest
import Telemetry.speed as speed
import Telemetry.team_race_pace as team_race_pace
from UI.ui import FeedbackModal

# Load the Bot token from the env file
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
CLIENT: Final[int] = os.getenv('DISCORD_CLIENT')
REPORT_CHANNEL: Final[int] = int(os.getenv('FLAG_REPORT_CHANNEL'))
FEEDBACK_CHANNEL: Final[int] = int(os.getenv('FEEDBACK_CHANNEL'))

# Bot setup
intents = Intents.default()
intents.message_content = True
client  = Client(intents=intents)
tree    = app_commands.CommandTree(client)

# Output dir
cache_dir = '.cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# Commands
@tree.command(name="feedback", description="Submit feedback to the moderators")
async def fastest(interaction: Interaction):
    feedback_modal = FeedbackModal()
    feedback_modal.feedback_channel = FEEDBACK_CHANNEL
    feedback_modal.user = interaction.user
    await interaction.response.send_modal(feedback_modal)

@tree.command(name="teams_race_pace", description="Rank team's race pace from the fastest to the slowest.")
@app_commands.describe(gp="The Grand Prix (Australia)")
@app_commands.describe(year="The Year (2022)")
async def pace_cmd(interaction: Interaction, gp: str, year: int):
    file_name = f"{gp}_{year}_R_{uuid.uuid1()}.png"
    file_full_path = os.path.join(cache_dir, file_name)
    await interaction.response.defer()
    try:
        event_name = team_race_pace.plot(year, gp, file_full_path)
        file: File = File(file_full_path, filename="result.png")
        # response
        embed = Embed(
            color=Colour.dark_purple(),
            description=f'Team median race pace',
            title=event_name,
        )
        embed.set_footer(text="Data from FastF1")
        embed.set_image(url="attachment://result.png")
        # edit the embed of the message
        await interaction.followup.send(embed=embed, file=file)
    except Exception as e:
        print(f"something went wrong: {e}")
        print(traceback.format_exc())
        await interaction.followup.send(content="An error has occurred")

@tree.command(name="speed_heatmap", description="Driver speed heatmap")
@app_commands.describe(gp="The Grand Prix (Australia)")
@app_commands.describe(year="The Year (2022)")
@app_commands.describe(session="The Session (R, Q, FP2)")
@app_commands.describe(driver="VER, PER, etc...")
async def fastest(interaction: Interaction, gp: str, year: int, session: str, driver:str):
    file_name = f"{gp}_{year}_{session}_{uuid.uuid1()}.png"
    file_full_path = os.path.join(cache_dir, file_name)
    await interaction.response.defer()
    try:
        event_name = speed.plot(year, gp, session, driver, file_full_path)
        file: File = File(file_full_path, filename="result.png")
        # response
        embed = Embed(
            color=Colour.dark_purple(),
            description=f'Speed heatmap',
            title=event_name,
        )
        embed.set_footer(text="Data from FastF1")
        embed.set_image(url="attachment://result.png")
        # edit the embed of the message
        await interaction.followup.send(embed=embed, file=file)
    except Exception as e:
        print(f"something went wrong: {e}")
        print(traceback.format_exc())
        await interaction.followup.send(content="An error has occurred")

@tree.command(name="gap_to_fastest", description="The gap to the fastest driver")
@app_commands.describe(gp="The Grand Prix (Australia)")
@app_commands.describe(year="The Year (2022)")
@app_commands.describe(session="The Session (R, Q, FP2)")
async def fastest(interaction: Interaction, gp: str, year: int, session: str):
    file_name = f"{gp}_{year}_{session}_{uuid.uuid1()}.png"
    file_full_path = os.path.join(cache_dir, file_name)
    await interaction.response.defer()
    try:
        event_name, driver_name, lap_time = gap_to_fastest.plot(year, gp, session, file_full_path)
        file: File = File(file_full_path, filename="result.png")
        # response
        embed = Embed(
            color=Colour.dark_purple(),
            description=f'{driver_name} fastest lap {lap_time}',
            title=event_name,
        )
        embed.set_footer(text="Data from FastF1")
        embed.set_image(url="attachment://result.png")
        # edit the embed of the message
        await interaction.followup.send(embed=embed, file=file)
    except Exception as e:
        print(f"something went wrong: {e}")
        print(traceback.format_exc())
        await interaction.followup.send(content="An error has occurred")

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

# Context menu
@tree.context_menu()
async def report_message(interaction: Interaction, message: Message) -> None:
    report_count, reporter_count = Moderation.report_message(interaction, message, "Something upsetting")
    print("report_count", report_count, "reporter_count", reporter_count)
    if report_count == 1:
        # only on the first report do we post to the report channel
        channel = client.get_channel(REPORT_CHANNEL)
        await channel.send(content=f"Message {message.jump_url} was reported")
    await interaction.response.send_message(content="Message successfully reported", ephemeral=True)


# Bot main entry point
if __name__ == '__main__':
    client.run(token=TOKEN)