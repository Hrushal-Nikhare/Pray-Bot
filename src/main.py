from discord.ext import commands, tasks
import datetime
from discord import app_commands
import discord
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


MY_GUILD = discord.Object(id=834371471891496960)  # Testing guild
# MY_GUILD = discord.Object(id=856266812605988915) #Execute big guild


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


@client.tree.command()
@app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')


@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send in the current channel')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text into the current channel."""
    await interaction.response.send_message(text_to_send)


@client.tree.command()
async def set_pray(ctx: discord.Interaction, user: discord.User):
    """Sets a job to send a message to the current channel at a specific time."""
    await ctx.response.send_message('Job Set!', ephemeral=True)


utc = datetime.timezone.utc

# If no tzinfo is given then UTC is assumed.
time = datetime.time(hour=0, minute=20, tzinfo=utc)


@tasks.loop(time=time)
async def my_task(ctx: discord.Interaction):
    # read user.txt and set user to it
    # with open("user.txt", "r") as f:
    #     user = f.read()
    # get the user 741192494133280851
    user = await self.bot.fetch_user(741192494133280851)
    message = ":pray:"
    webhook = await ctx.channel.create_webhook(name=user.display_name)
    await webhook.send(message, username=user.display_name, avatar_url=user.display_avatar)
    await webhook.delete()


client.run(TOKEN)
