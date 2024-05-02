from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle, Embed, Colour, Message, NotFound
from typing import Final
import traceback
import os
import datetime

from Database import message_reporting

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
        
        # get message report stats
        report_count, reporter_count, latest_report = message_reporting.get_stats(message_handle)

        # Get the response message for this report
        ack_message_id = message_reporting.get_response(message_handle)

        # if we have a stored message, check that it wasn't deleted
        if ack_message_id:
            ack_message: Message = await self.fetch_response_message(ack_message_id)

        # create the embed
        embed = Embed(
                color=Colour.red(),
                url=message_handle,
                title=f"Message report :warning:",
                timestamp=datetime.datetime.now())
        embed.add_field(name="comment", value=self.report_msg.value, inline=False)
        embed.add_field(name="from", value=f"{interaction.user.nick if interaction.user.nick else interaction.user.name}", inline=True)
        embed.set_footer(text=f"{report_count} times from {reporter_count} user(s)", icon_url=None)

        if not ack_message_id or not ack_message:
            ack_message = await self.report_channel.send(embed=embed)
            message_reporting.store_response(message_handle, ack_message.id)
        else:
            await ack_message.edit(embed=embed)

        await interaction.response.send_message(f'Message successfully reported', ephemeral=True)