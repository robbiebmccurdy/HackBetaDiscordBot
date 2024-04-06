import discord
from discord.ext import tasks, commands
from discord.ui import View, Button
import random
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

description = '''Hack Beta's official Discord Bot! Feel free to use the '%' to specify your commands.

This bot is used for only official purposes by Hack Beta. Developed by @roei'''

# Parsing questions from questions.txt

def parse_questions(file_path):
    questions = []
    with open(file_path, 'r') as file:
        content = file.read().split('/') 
        for block in content:
            if block.strip():
                lines = block.split('\n') 
                question_text = lines[0].split('?')[0] + '?' 
                answers = [{'text': ans.replace('*', '').strip(), 'correct': '*' in ans} for ans in lines[1:] if ans.strip()]
                questions.append({'question': question_text, 'answers': answers})
    return questions

questions = parse_questions('questions.txt')

# Bot Class

class HackBetaBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('%'), description=description, intents=intents)
        self.last_message = None  # Track the last message sent by the bot

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('-------')
        self.ask_question.start()

    @tasks.loop(hours=1)
    async def ask_question(self):
        channel = self.get_channel(int(os.getenv('GENERAL_CHANNEL_ID')))
        if channel is not None:
            if self.last_message:  # Delete the last message if it exists
                try:
                    await self.last_message.delete()
                except discord.NotFound:
                    pass  # If message was already deleted or not found, pass
                self.last_message = None

            question = random.choice(questions)
            correct_answer = next((a for a in question['answers'] if a['correct']), None)
            view = QuestionView(question, correct_answer, self)
            message = await channel.send(question['question'], view=view)
            self.last_message = message  # Update the last message with the new one

            await asyncio.sleep(1200)  # Wait 20 minutes before deleting the message
            if self.last_message:  # Check if the last message still exists
                try:
                    await self.last_message.delete()
                    self.last_message = None
                    await channel.send(f"Nice answers everyone! The correct answer was: {correct_answer['text']}!")
                except discord.NotFound:
                    pass

# Custom view for questions using Discord UI's View

class QuestionView(View):
    def __init__(self, question, correct_answer, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        self.correct_answer = correct_answer
        self.bot = bot
        self.add_buttons()

    def add_buttons(self):
        for answer in self.question['answers']:
            button = Button(label=answer['text'], style=discord.ButtonStyle.primary)
            button.callback = self.make_callback(answer['correct'])
            self.add_item(button)

    def make_callback(self, correct):
        async def callback(interaction):
            if correct:
                await interaction.response.send_message("Correct!", ephemeral=True)
            else:
                await interaction.response.send_message("Sorry, that's incorrect.", ephemeral=True)
        return callback

# Calling the bot

discord_token = os.getenv('DISCORD_TOKEN')
bot = HackBetaBot()
bot.run(discord_token)
