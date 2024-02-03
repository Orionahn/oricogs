from .welcomer import Welcomer


async def setup(bot):
    await bot.add_cog(Welcomer(bot))