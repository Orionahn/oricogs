from redbot.core import commands
from discord.errors import Forbidden

class fournine(commands.Cog):
    """A cog for changing all member's nicknames to '49ERS SUPERFAN'."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    async def superfan(self, ctx):
        """Change all member nicknames to '49ERS SUPERFAN'."""
        failed_changes = 0
        for member in ctx.guild.members:
            try:
                # Skip if the member is a bot or if the bot cannot change the member's nickname
                if member.bot or member == ctx.guild.owner:
                    continue
                await member.edit(nick="Happy Black History Month")
            except Forbidden:
                failed_changes += 1
                continue

        if failed_changes:
            await ctx.send(f"Changed nicknames, but {failed_changes} members were skipped due to permissions.")
        else:
            await ctx.send("Successfully changed all possible nicknames to '49ERS SUPERFAN'!")

def setup(bot):
    bot.add_cog(fournine(bot))
