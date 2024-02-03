from .fournine import LoveCalc

async def setup(bot):
	await bot.add_cog(fournine(bot))