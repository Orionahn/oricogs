from .fournine import fournine

async def setup(bot):
	await bot.add_cog(fournine(bot))