import discord
from redbot.core import commands, Config
from PIL import Image, ImageDraw, ImageFont
import aiohttp
from io import BytesIO
import random
import os

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {"welcome_channel_id": None}
        self.config.register_guild(**default_guild)
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def fetch_image(self, url):
        async with self.session.get(url) as response:
            return await response.read()

    def circular_crop(self, img):
        """Crops the image into a circular shape."""
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img.size, fill=255)
        result = Image.composite(img, Image.new("RGBA", img.size), mask)
        return result

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        welcome_channel_id = await self.config.guild(guild).welcome_channel_id()

        if welcome_channel_id is None:
            return  # No welcome channel set, do nothing

        welcome_channel = guild.get_channel(welcome_channel_id)
        if welcome_channel is None:
            return  # Invalid channel or channel not found

        member_count = member.guild.member_count

        # Choose a random background image
        bg_urls = [
            "https://i.postimg.cc/0yTRTJhY/WElcome-1.png"
        ]
        bg_url = random.choice(bg_urls)
        bg_data = await self.fetch_image(bg_url)
        background = Image.open(BytesIO(bg_data))

        # Fetch and process the profile picture
        avatar_data = await self.fetch_image(str(member.display_avatar.url))
        avatar = Image.open(BytesIO(avatar_data))
        avatar = self.circular_crop(avatar).resize((222, 222))

        # Place the avatar onto the background
        avatar_position = (502, 118)  
        background.paste(avatar, avatar_position, avatar)

        # Add the member count text
        draw = ImageDraw.Draw(background)
        text = f"{member_count}"
        current_directory = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_directory, "timesi.ttf")
        font = ImageFont.truetype(font_path, 30)  
        text_position = (158, 560)  
        draw.text(text_position, text, (255, 255, 255), font=font)

        username_text = member.display_name
        font_username = ImageFont.truetype(font_path, 45)

        # Calculate text width and height using textbbox
        left, top, right, bottom = draw.textbbox((0, 0), username_text, font=font_username)
        text_width = right - left
        text_height = bottom - top


        center_x, center_y = 623, 400


        username_position = (center_x - text_width // 2, center_y - text_height // 2)

        draw.text(username_position, username_text, (255, 255, 255), font=font_username)


        buffer = BytesIO()
        background.save(buffer, format="PNG")
        buffer.seek(0)

        await welcome_channel.send(file=discord.File(buffer, "welcome_image.png"))

    @commands.guild_only()
    @commands.admin()
    @commands.command(name="setwelcomechannel")
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        """
        Sets the welcome channel for this server.
        """
        await self.config.guild(ctx.guild).welcome_channel_id.set(channel.id)
        await ctx.send(f"Welcome channel has been set to {channel.mention}")

def setup(bot):
    bot.add_cog(Welcomer(bot))
