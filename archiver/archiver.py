from redbot.core import commands
import discord
import datetime
import os

class archiver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def archive_messages(self, ctx):
        """Archives messages from the past 3 days and DMs the file to the user."""
        # Notify the command invoker via DM that the process is starting.
        dm_channel = await ctx.author.create_dm()
        await dm_channel.send("Archiving messages, this may take some time... Please be patient.")

        # Calculate the date for 3 days ago
        three_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=3)
        file_path = 'message_archive.txt'

        # Open a file to save messages
        with open(file_path, 'w', encoding='utf-8') as file:
            # Loop through each channel in the guild
            for channel in ctx.guild.text_channels:
                # Ensure the bot can read channel history
                if channel.permissions_for(ctx.guild.me).read_message_history:
                    try:
                        # Fetch messages from the past 3 days
                        async for message in channel.history(limit=None, after=three_days_ago):
                            # Write each message to the file
                            file.write(f"{message.created_at} - {message.author.display_name}: {message.content}\n")
                    except discord.Forbidden:
                        await dm_channel.send(f"Permission denied to read history for {channel.mention}")
                    except Exception as e:
                        await dm_channel.send(f"Error fetching messages for {channel.mention}: {str(e)}")

        # Send the file via DM
        try:
            await dm_channel.send("Here's the archive of messages from the past 3 days:", file=discord.File(file_path))
        except discord.HTTPException:
            await dm_channel.send("Failed to send the file. Please make sure you have DMs enabled from server members.")
        
        # Clean up the file after sending
        os.remove(file_path)

def setup(bot):
    bot.add_cog(archiver(bot))
