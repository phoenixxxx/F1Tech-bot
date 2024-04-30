from discord.ui import Modal, TextInput
from discord import Interaction, TextStyle, Embed, Color

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
    async def on_error(self, interaction: Interaction, error: Exception) -> None:
       pass

    async def on_submit(self, interaction: Interaction) -> None:
        channel = interaction.guild.get_channel(self.feedback_channel)
        embed = Embed(title="New Feedback", 
                      description=self.fb_msg.value,
                      color=Color.green())
        embed.set_author(name=self.user.nick)
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Thank you {self.user.nick}", ephemeral=True)