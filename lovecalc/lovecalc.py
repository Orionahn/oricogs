import discord
from redbot.core import commands
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import aiohttp
from io import BytesIO
import os

class LoveCalc(commands.Cog):
    """Calculate the love between two people."""

    def __init__(self, bot):
        self.bot = bot
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
        result = Image.composite(img, Image.new("RGBA", img.size, (0, 0, 0, 0)), mask)
        return result

    def add_outline(self, img, thickness=5, color=(255, 255, 255)):
        """Add outline to an image."""
        bg = Image.new('RGBA', (img.width + thickness * 2, img.height + thickness * 2), color)
        bg.paste(img, (thickness, thickness), img)
        return bg

    async def create_love_image(self, user1_name, user1_avatar_url, user2_name, user2_avatar_url, compatibility):
        # Load the background image
        bg_data = await self.fetch_image("https://i.postimg.cc/25XdjThY/SS19.png")
        bg_img = Image.open(BytesIO(bg_data))

        # Load avatars
        user1_avatar_data = await self.fetch_image(user1_avatar_url)
        user1_avatar = Image.open(BytesIO(user1_avatar_data))
        user2_avatar_data = await self.fetch_image(user2_avatar_url)
        user2_avatar = Image.open(BytesIO(user2_avatar_data))

        # Crop avatars to circular shape and resize
        user1_avatar = self.circular_crop(user1_avatar).resize((260, 260))
        user2_avatar = self.circular_crop(user2_avatar).resize((260, 260))

        # Place avatars on the background
        bg_img.paste(user1_avatar, (50, 100), user1_avatar)
        bg_img.paste(user2_avatar, (655, 100), user2_avatar)


        current_directory = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_directory, "times.ttf")
        font_large_path = os.path.join(current_directory, "times.ttf")
        # Write user names
        draw = ImageDraw.Draw(bg_img)
        font = ImageFont.truetype(font_path, 60)
        # For user2_name centered around (bg_img.width - 550, 350)
        user2_text_width, user2_text_height = draw.textsize(user2_name, font=font)
        user2_text_x = (bg_img.width - 550) - (user2_text_width / 2)
        user2_text_y = 350 - (user2_text_height / 2)
        draw.text((user2_text_x, user2_text_y), user2_name, font=font, fill="white")

        # For user1_name centered around (bg_img.width - 550, 45)
        user1_text_width, user1_text_height = draw.textsize(user1_name, font=font)
        user1_text_x = (bg_img.width - 550) - (user1_text_width / 2)
        user1_text_y = 45 - (user1_text_height / 2)
        draw.text((user1_text_x, user1_text_y), user1_name, font=font, fill="white")


        # Write compatibility with an outline
        font_large = ImageFont.truetype(font_large_path, 85)
        compatibility_str = f"{compatibility}%"
        text_position = (bg_img.width / 2 - 75, bg_img.height / 2 - 50)
        draw.text((text_position[0] - 2, text_position[1]), compatibility_str, font=font_large, fill="red")
        draw.text((text_position[0] + 2, text_position[1]), compatibility_str, font=font_large, fill="red")
        draw.text((text_position[0], text_position[1] - 2), compatibility_str, font=font_large, fill="red")
        draw.text((text_position[0], text_position[1] + 2), compatibility_str, font=font_large, fill="red")
        draw.text(text_position, compatibility_str, font=font_large, fill="white")

        # Save to a bytes buffer
        buffer = BytesIO()
        bg_img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    @commands.command()
    async def lovecalc(self, ctx, p1: discord.Member, p2: discord.Member=None):
        """
        Calculate the love between two people.
        If only one person is provided, the individual using the command will be used.
        """
        if p2 is None:
            p2 = ctx.author

        state = random.getstate()
        new_seed = str(p1.id + p2.id)
        random.seed(new_seed)
        compatibility = random.randint(0, 101)
        random.setstate(state)

        heart_emoji = "💔"  # Default: Broken heart
        if compatibility > 50:
            heart_emoji = "❤️"
        if compatibility > 75:
            heart_emoji = "💕"

        formatted_message = f"**{p1.display_name} + {p2.display_name}** = __{compatibility}%__ of Love {heart_emoji}"
        messages = {
            0: "It's a rocky road ahead!",
            25: "There's a tiny spark!",
            50: "There's potential!",
            75: "Things are heating up!",
            100: "A match made in heaven!"
        }
        compatibility_message = messages.get((compatibility // 25) * 25, "It's complicated.")
    
        # Create an embedded message
        embed = discord.Embed(
            title=f"❤️ Love Calculation for {p1.display_name} & {p2.display_name}",
            description=f"{formatted_message}\n{compatibility_message}",
            color=discord.Color.red()  # Setting the color to red
        )
		
        love_image = await self.create_love_image(p1.display_name, str(p1.avatar.url), p2.display_name, str(p2.avatar.url), compatibility)
	
        await ctx.send(embed=embed)
        await ctx.send(file=discord.File(love_image, "love.png"))
        
