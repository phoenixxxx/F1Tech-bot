from discord.ui import View, Button
from discord import Interaction, Message, Embed, Colour
import datetime
import discord
from Database.message_reporting import get_reports as database_get_reports
from Database.message_reporting import get_report_count as database_get_report_count

class ReportView(View):
    # The message onto which the view goes
    current_report_index : int = 0
    current_report_count : int = 0
    message : Message = None
    reported_message_handle : str = None

    def update_button_visibility(self) -> None:
        if self.current_report_index > 0:
            self.prev_button.disabled = False
        else:
            self.prev_button.disabled = True
    
        if self.current_report_index < self.current_report_count - 1:
            self.next_button.disabled = False
        else:
            self.next_button.disabled = True

    @discord.ui.button(label="<",
                       style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction:Interaction, button:Button):
        await interaction.response.defer()
        if self.current_report_index > 0:
            self.current_report_index = self.current_report_index - 1
        self.update_button_visibility()
        await self.update_message()

    @discord.ui.button(label=">",
                       style=discord.ButtonStyle.primary)
    async def next_button(self, interaction:Interaction, button:Button):
        await interaction.response.defer()
        if self.current_report_index < self.current_report_count - 1:
            self.current_report_index = self.current_report_index + 1
        self.update_button_visibility()
        await self.update_message()

    async def reload_message(self):
        self.current_report_count = database_get_report_count()
        print(f"{self.current_report_count} report(s)")
        self.current_report_index = self.current_report_count - 1
        self.update_button_visibility()
        await self.update_message()

    async def update_message(self):
        await self.message.edit(content="", embed=self.create_embed(), view=self)

    def create_embed(self):
        reports = database_get_reports(self.reported_message_handle)
        current = reports[self.current_report_index]
        print("self.current_report_index", self.current_report_index)
        embed = Embed(
                color=Colour.red(),
                url=None,
                title=f"Message report :warning:",
                description=current[5],
                timestamp=datetime.datetime.now())
        # embed.add_field(name="comment", value=self.report_msg.value, inline=False)
        # embed.add_field(name="from", value=f"{interaction.user.nick if interaction.user.nick else interaction.user.name}", inline=True)
        embed.set_footer(text=f"{len(reports)} time(s)", icon_url=None)

        return embed