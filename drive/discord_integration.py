import os
from shutil import rmtree

import discord
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()


async def send_file_to_discord(file_p, channel_id):
    """
    Asynchronously sends a file to a specified Discord channel.

    Args:
        file_p (File): The file to be sent.
        channel_id (int): The ID of the Discord channel.

    Raises:
        Exception: If the guild or channel is not found.
    """
    intents = discord.Intents.default()
    intents.guilds = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        """
        An event handler that's called when the Discord client is ready.
        This function sends the file to the specified Discord channel.
        """
        try:
            # Get guild and channel
            guild = await client.fetch_guild(os.getenv("SERVER_ID"))
            if not guild:
                raise Exception("Guild not found.")

            channel = await guild.fetch_channel(channel_id)
            if not channel:
                raise Exception("Channel not found.")

            # Create a temporary directory and write the file to it
            file_dir = os.path.join(settings.BASE_DIR, "temp", file_p.name)
            os.makedirs(os.path.dirname(file_dir), exist_ok=True)
            with open(file_dir, "wb+") as destination:
                for chunk in file_p.chunks():
                    destination.write(chunk)

            # Send the file to discord channel
            await channel.send(file=discord.File(file_dir))

            # Remove the temporary directory
            rmtree(os.path.dirname(file_dir))
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await client.close()

    await client.start(os.getenv("BOT_TOKEN"))
