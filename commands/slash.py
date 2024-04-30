from typing import Final
import traceback

import uuid
import os

from UI.feedback_modal import FeedbackModal

from discord import File, Interaction, app_commands
from discord import Embed, Colour

import Telemetry.gap_to_fastest as gap_to_fastest
import Telemetry.speed as speed
import Telemetry.team_race_pace as team_race_pace

FEEDBACK_CHANNEL: Final[int] = int(os.getenv('FEEDBACK_CHANNEL'))
print(f"[commands][slash][Init] FEEDBACK_CHANNEL is {FEEDBACK_CHANNEL}")

# Output dir
cache_dir = '.cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

def register(tree):
    @tree.command(name="feedback", description="Submit feedback to the moderators")
    async def feedback_cmd(interaction: Interaction):
        feedback_modal = FeedbackModal()
        feedback_modal.feedback_channel = FEEDBACK_CHANNEL
        print("user:", interaction.user, "submitting feedback")
        feedback_modal.user = interaction.user
        await interaction.response.send_modal(feedback_modal)

    @tree.command(name="teams_race_pace", description="Rank team's race pace from the fastest to the slowest.")
    @app_commands.describe(gp="The Grand Prix (Australia)")
    @app_commands.describe(year="The Year (2022)")
    async def teams_race_pace_cmd(interaction: Interaction, gp: str, year: int):
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
    async def speed_heatmap_cmd(interaction: Interaction, gp: str, year: int, session: str, driver:str):
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
    async def gap_to_fastest_cmd(interaction: Interaction, gp: str, year: int, session: str):
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
