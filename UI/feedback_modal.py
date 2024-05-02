from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle, Embed, Color

from Database import feedback
import datetime

class FeedbackModal(Modal, title="Send us your feedback"):
    feedback_channel : int = None

    fb_title = TextInput(
        style=TextStyle.short,
        label="Title",
        required=False,
        placeholder="Give your feedback a title"
    )
    fb_msg = TextInput(
        style=TextStyle.long,
        label="Feedback",
        required=False,
        max_length=500,
        placeholder="Give your feedback"
    )
    async def on_submit(self, interaction: Interaction) -> None:
        channel = interaction.guild.get_channel(self.feedback_channel)
        name = self.user.nick if self.user.nick else self.user.name
        embed = Embed(
                color=Color.light_grey(),
                url=None,
                title=f"Feedback received :clipboard:",
                timestamp=datetime.datetime.now())
        embed.add_field(name=self.fb_title.value, value=self.fb_msg.value, inline=False)
        embed.add_field(name="from", value=f"{name}", inline=True)
        embed.set_footer(text=f"Moderators are not guaranteed to respond", icon_url=None)
        await channel.send(embed=embed)

        feedback.store(name, self.fb_title.value, self.fb_msg.value)
        await interaction.response.send_message(f"Thank you {name}", ephemeral=True)