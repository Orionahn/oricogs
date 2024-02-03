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
        await ctx.author.send("Archiving messages, this may take some time... Please be patient.")

        # Calculate the date for 3 days ago
        three_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=3)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as tmpfile:
            file_path = tmpfile.name  # Store the file path to send later

            # Loop through each channel in the guild
            for channel in ctx.guild.text_channels:
                # Ensure the bot can read channel history
                if channel.permissions_for(ctx.guild.me).read_message_history:
                    try:
                        # Fetch messages from the past 3 days
                        async for message in channel.history(limit=None, after=three_days_ago):
                            # Write each message to the temporary file
                            tmpfile.write(f"{message.created_at} - {message.author.display_name}: {message.content}\n")
                    except discord.Forbidden:
                        await ctx.author.send(f"Permission denied to read history for {channel.mention}")
                    except Exception as e:
                        await ctx.author.send(f"Error fetching messages for {channel.mention}: {str(e)}")

        # Send the file via DM
        try:
            with open(file_path, 'rb') as file:
                await ctx.author.send("Here's the archive of messages from the past 3 days:", file=discord.File(file, "message_archive.txt"))
        except discord.HTTPException:
            await ctx.author.send("Failed to send the file. Please make sure you have DMs enabled from server members.")
        finally:
            os.remove(file_path)  # Clean up the file after sending

def setup(bot):
    bot.add_cog(archiver(bot))
