import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
import os
import random

load_dotenv()

description = '''Hack Beta's offical Discord Bot! Feel free to use the '%' to specify your commands.

This bot is used for only official purposes by Hack Beta. Developed by @roei'''

intents = discord.Intents.default()
intents.message_content = True

channel_id = os.getenv('GENERAL_CHANNEL_ID')

discord_token = os.getenv('DISCORD_TOKEN')

#client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='%', description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    printer.start()
    questionOfTheHour.start()

@tasks.loop(seconds=1.5)
async def printer():
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send('1 - Test');

@tasks.loop(seconds=5.0)
async def questionOfTheHour():
    channel = bot.get_channel(channel_id)
    if channel:
        # Post the poll
        poll_message = await channel.send("Poll: Which do you prefer? React to vote!\n🍎 Apple\n🍌 Banana")
        # Add reactions for voting
        await poll_message.add_reaction("🍎")
        await poll_message.add_reaction("🍌")

@bot.command(name='start_question')
async def start_question(ctx):
    questionOfTheHour.start()

bot.run(discord_token)