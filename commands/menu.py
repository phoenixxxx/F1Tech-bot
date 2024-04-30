from typing import Final
import traceback
import os

from discord import Interaction, Message

from Moderation.moderation import report_message as moderation_report_message

REPORT_CHANNEL: Final[int] = int(os.getenv('FLAG_REPORT_CHANNEL'))
print(f"[commands][menu][Init] REPORT_CHANNEL is {REPORT_CHANNEL}")

def register(tree):
    @tree.context_menu()
    async def report_message(interaction: Interaction, message: Message) -> None:
        report_count, reporter_count = moderation_report_message(interaction, message, "Something upsetting")
        print("report_count", report_count, "reporter_count", reporter_count)
        if report_count == 1:
            # only on the first report do we post to the report channel
            channel = interaction.guild.get_channel(REPORT_CHANNEL)
            await channel.send(content=f"Message {message.jump_url} was reported")
        await interaction.response.send_message(content="Message successfully reported", ephemeral=True)