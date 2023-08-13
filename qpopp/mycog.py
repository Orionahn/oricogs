from redbot.core import commands
from discord import Member, Status, Embed
from datetime import datetime, timedelta
import asyncio

class MyCog(commands.Cog):
    """QupRanked bot"""

    def __init__(self, bot):
        self.bot = bot
        self.players = {}  # {('datacenter', 'rank'): {Member}}
        self.data_centers = ['Aether', 'Primal', 'Crystal']
        self.ranks = ['Bronze-Silver', 'Gold-Plat', 'Diamond-Crystal']
        self.bot.loop.create_task(self.send_updates())

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        """Update player queue based on their roles."""
        # role names must be exact
        in_queue_role = "In Queue"
        out_of_queue_role = "Out of Queue"

        queue_role = None
        if in_queue_role in [role.name for role in after.roles]:
            queue_role = in_queue_role
        elif out_of_queue_role in [role.name for role in after.roles]:
            queue_role = out_of_queue_role

        if queue_role:
            data_center_role = next((role.name for role in after.roles if role.name in self.data_centers), None)
            rank_role = next((role.name for role in after.roles if role.name in self.ranks), None)

            if data_center_role and rank_role:
                if queue_role == in_queue_role:
                    if (data_center_role, rank_role) in self.players:
                        self.players[(data_center_role, rank_role)].add(after)
                    else:
                        self.players[(data_center_role, rank_role)] = {after}
                elif queue_role == out_of_queue_role:
                    if (data_center_role, rank_role) in self.players:
                        self.players[(data_center_role, rank_role)].discard(after)

    async def send_updates(self):
        """Send queue updates every 30 seconds."""
        channel_id = 1132840071893102625  # replace with your channel id
        channel = self.bot.get_channel(channel_id)
        message = None

        while True:
            if message:
                await message.delete()

            embed = Embed(title="Queue Status", timestamp=datetime.utcnow())
            for data_center in self.data_centers:
                for rank in self.ranks:
                    count = len(self.players.get((data_center, rank), []))
                    embed.add_field(name=f"{data_center} - {rank}", value=str(count), inline=False)
            
            message = await channel.send(embed=embed)
            await asyncio.sleep(30)
