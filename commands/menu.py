from typing import Final
import os

from discord import Interaction, Message

from UI.report_modal import ReportModal

REPORT_CHANNEL: Final[int] = int(os.getenv('MESSAGE_REPORT_CHANNEL'))
print(f"[commands][menu][Init] REPORT_CHANNEL is {REPORT_CHANNEL}")

def register(tree):
    @tree.context_menu()
    async def report_message(interaction: Interaction, message: Message) -> None:
        report_modal = ReportModal()
        report_modal.report_channel = interaction.guild.get_channel(REPORT_CHANNEL)
        report_modal.reported_message = message
        await interaction.response.send_modal(report_modal)

