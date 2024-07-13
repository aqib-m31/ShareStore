import io
import os

import discord
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

            # Create a BytesIO object from the file data
            file_data = io.BytesIO()
            for chunk in file_p.chunks():
                file_data.write(chunk)
            file_data.seek(0)

            # Send the BytesIO instance as a file to the Discord channel
            await channel.send(file=discord.File(fp=file_data, filename=file_p.name))
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await client.close()

    await client.start(os.getenv("BOT_TOKEN"))
