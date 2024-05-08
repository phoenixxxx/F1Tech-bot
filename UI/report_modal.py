from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle, Message, NotFound

from Database import message_reporting
from UI.report_view import ReportView

class ReportModal(Modal, title="Report message"):
    report_channel = None
    reported_message : Message = None

    report_msg = TextInput(
        style=TextStyle.long,
        label="Report",
        required=False,
        max_length=500,
        placeholder="Explain why you reported the message"
    )

    async def fetch_response_message(self, message_id : int) -> Message:
        message: Message = None
        try:
            message = await self.report_channel.fetch_message(message_id)
        except NotFound as e:
            print(f"Message {message_id} not found (likely deleted)")
        return message

    async def on_submit(self, interaction: Interaction):
        message_handle = self.reported_message.jump_url

        # Store message report
        message_reporting.store(
            self.reported_message.id, 
            self.reported_message.channel.id, 
            message_handle, 
            interaction.user.name, 
            interaction.user.id,  
            self.report_msg.value)

        # Get the response message for this report
        ack_message_id = message_reporting.get_response(message_handle)

        # if we have a stored message, check that it wasn't deleted
        if ack_message_id:
            ack_message: Message = await self.fetch_response_message(ack_message_id)

        if not ack_message_id or not ack_message:
            ack_message = await self.report_channel.send(content="[Empty]")
            message_reporting.store_response(message_handle, ack_message.id)

        view = ReportView()
        view.reported_message_handle = message_handle
        view.message = ack_message
        await view.reload_message()
        await interaction.response.send_message(f'Message successfully reported', ephemeral=True)