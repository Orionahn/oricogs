from redbot.core import commands
import discord
import datetime
import os
import tempfile

class archiver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def archive_messages(self, ctx):
        """Archives messages from the past 3 days and DMs the file to the user."""
        await ctx.author.send("Starting the archiving process. This may take some time, please be patient.")

        # Calculate the timestamp for 3 days ago
        three_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=3)

        # Use tempfile to avoid permission issues
        with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as temp_file:
            # Loop through each text channel in the guild
            for channel in ctx.guild.text_channels:
                # Ensure the bot has permission to read the channel history
                if channel.permissions_for(ctx.guild.me).read_message_history:
                    try:
                        # Fetch messages from the last 3 days
                        async for message in channel.history(limit=None, after=three_days_ago):
                            # Write each message to the temporary file, including username and discriminator
                            temp_file.write(f"{message.created_at} - {message.author.name}#{message.author.discriminator}: {message.content}\n")
                    except discord.Forbidden:
                        await ctx.author.send(f"Permission denied to read history for {channel.mention}.")
                    except Exception as e:
                        await ctx.author.send(f"Error fetching messages for {channel.mention}: {str(e)}.")

            # Remember to flush data to disk before reading or sending the file
            temp_file.flush()

        # Send the file via DM after collecting messages
        try:
            await ctx.author.send(
                "Here's the archive of messages from the past 3 days:",
                file=discord.File(temp_file.name, "message_archive.txt")
            )
        except discord.HTTPException:
            await ctx.author.send("Failed to send the file. Please make sure you have DMs enabled from server members.")
        finally:
            # Ensure the temporary file is deleted after sending
            os.remove(temp_file.name)

def setup(bot):
    bot.add_cog(archiver(bot))
