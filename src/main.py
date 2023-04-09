#!/usr/bin/python3
from discord.ext import commands, tasks
from discord import app_commands
import discord
from typing import Optional
import os
from dotenv import load_dotenv
import json
import asyncio
import random
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

mode = "Not Test"
if mode == "test":
    MY_GUILD = discord.Object(id=834371471891496960)  # Testing guild
    channel_id = 1090865789877366794
else:
    MY_GUILD = discord.Object(id=856266812605988915)  # Execute big guild
    channel_id = 856266813322428419


class MyClient(discord.Client):

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
        pray.start()


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def set_pray(ctx: discord.Interaction, user: Optional[discord.User] = None):
    """Sets a job to send a message to the current channel at a specific time."""

    if user is None:
        user = ctx.user

    with open("/home/carboncap/Pray-Bot/src/users.json", "r+") as f:
        users = set(json.load(f))
        users = list(users)
        users.append(user.id)
        users = set(users)
        users = list(users)
        f.seek(0)
        json.dump(users, f)
    await ctx.response.send_message(f'Done! added {user.name}#{user.discriminator} to the list', ephemeral=True)


@tasks.loop(hours=12.0)
async def pray():
    with open("/home/carboncap/Pray-Bot/src/users.json", "r") as f:
        users = json.load(f)

    channel = await client.fetch_channel(channel_id)
    for i in enumerate(users):
        user = await client.fetch_user(i[1])
        message = ":pray:"
        await asyncio.sleep(random.randint(900,3600))
        webhook = await channel.create_webhook(name=user.display_name)
        await webhook.send(message, username=user.display_name, avatar_url=user.display_avatar)
        await webhook.delete()

client.run(TOKEN)
