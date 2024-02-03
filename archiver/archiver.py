from redbot.core import commands
import discord
import datetime
import tempfile
import os

class archiver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def archive_messages(self, ctx):
        """Archives messages from the past 3 days and DMs the file to the user."""
        # Inform the user that the process has started
        dm_channel = await ctx.author.create_dm()
        await dm_channel.send("Starting the archiving process. This may take some time, please be patient.")

        # Calculate the timestamp for 3 days ago
        three_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=3)

        # Create a temporary file to store the messages
        with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as temp_file:
            file_path = temp_file.name  # Save the file path for later use

            # Loop through each text channel in the guild
            for channel in ctx.guild.text_channels:
                # Ensure the bot has permission to read the channel history
                if channel.permissions_for(ctx.guild.me).read_message_history:
                    try:
                        # Fetch messages from the last 3 days
                        async for message in channel.history(limit=None, after=three_days_ago):
                            # Write each message to the temporary file
                            # Now includes the real username and discriminator
                            temp_file.write(f"{message.created_at} - {message.author.name}#{message.author.discriminator}: {message.content}\n")
                    except discord.Forbidden:
                        await dm_channel.send(f"Permission denied to read history for {channel.mention}.")
                    except Exception as e:
                        await dm_channel.send(f"Error fetching messages for {channel.mention}: {str(e)}.")

        # Send the file via DM
        try:
            with open(file_path, 'rb') as file:
                await dm_channel.send("Here's the archive of messages from the past 3 days:", file=discord.File(file, "message_archive.txt"))
        except discord.HTTPException:
            await dm_channel.send("Failed to send the file. Please make sure you have DMs enabled from server members.")
        finally:
            os.remove(file_path)  # Ensure the temporary file is deleted after sending

def setup(bot):
    bot.add_cog(archiver(bot))
