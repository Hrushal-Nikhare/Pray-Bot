#!/usr/bin/python3
from discord.ext import commands, tasks
from discord import app_commands, Webhook
import discord
from typing import Optional
import os
from dotenv import load_dotenv
import json
import asyncio
import datetime
import random
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

mode = "prod"
# mode = "test"

if mode == "test":
    MY_GUILD = discord.Object(id=834371471891496960)  # Testing guild
    channel_id = 1090865789877366794
    path = "users.json"
else:
    MY_GUILD = discord.Object(id=856266812605988915)  # Execute big guild
    channel_id = 856266813322428419
    path = "/home/carboncap/Pray-Bot/src/users.json"


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

    with open(path, "r+") as f:
        users = set(json.load(f))
        users = list(users)
        users.append(user.id)
        users = set(users)
        users = list(users)
        f.seek(0)
        json.dump(users, f)
    await ctx.response.send_message(f'Done! added {user.name}#{user.discriminator} to the list', ephemeral=True)


@client.tree.command()
async def list_pray(ctx: discord.Interaction):
    """ Lists all the users who have a job """
    with open(path, "r") as f:
        users = json.load(f)
    embed = discord.Embed(
        title="List of users who have a job",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.utcnow(),
    )
    await ctx.response.send_message("Hold on to your seats, folks, because it's coming! With lightning-fast speed and the force of a hurricane, it's barreling towards us, ready to make its grand entrance. Brace yourselves for the epic arrival of the one and only...", ephemeral=True)
    start_time = datetime.datetime.utcnow()
    for i in enumerate(users):
        user = await client.fetch_user(i[1])
        embed.add_field(name=f"{i[0]+1}. {user.name}#{user.discriminator}",
                        value=f"```json\n{user.id}```", inline=False)
    end_time = datetime.datetime.utcnow()
    await ctx.followup.send(embed=embed, ephemeral=True)


@client.tree.command()
async def ping(ctx: discord.Interaction):
    """ Pong! """
    # have to convert code
    latency = round(client.latency * 1000)
    if latency < 250:
        color = discord.Color.blue()
    elif latency < 450 and latency > 250:
        color = discord.Color.green()
    elif latency < 600 and latency > 450:
        color = discord.Color.orange()
    elif latency < 800 and latency > 600:
        color = discord.Color.red()
    else:
        color = discord.Color.dark_red()
    embed = discord.Embed(
        title=":ping_pong: Pong!",
        color=color,
        timestamp=datetime.datetime.utcnow(),
    )
    embed.add_field(name="Latency",
                    value=f"```json\n{latency} ms```", inline=False)
    await ctx.response.send_message(embed=embed, ephemeral=True)


@tasks.loop(hours=12.0)
async def pray():
    with open(path, "r") as f:
        users = json.load(f)

    channel = await client.fetch_channel(channel_id)

    # instead of making and deleting the webhook every time, we can just edit the webhook
    webhooks = await channel.webhooks()
    webhook = next(
        (
            webhooks[i]
            for i in range(len(webhooks))
            if webhooks[i].name == "Pray Bot"
        ),
        None,
    )
    if webhook is None:
        webhook = await channel.create_webhook(name="Pray Bot")

    # instead of making and deleting the webhook every time, we can just edit the webhook
    for i in enumerate(users):
        user = await client.fetch_user(i[1])
        message = ":pray:"
        await asyncio.sleep(random.randint(900, 3600))
        await webhook.send(message, username=user.display_name, avatar_url=user.display_avatar)


client.run(TOKEN)
