from .archiver import archiver

async def setup(bot):
	await bot.add_cog(archiver(bot))