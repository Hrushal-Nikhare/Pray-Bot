from discord.ext import commands, tasks
from discord import app_commands
import discord
from typing import Optional
import os
from dotenv import load_dotenv
import json
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
		impersonate.start()


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
	print(f'Logged in as {client.user} (ID: {client.user.id})')
	print('------')


# @client.tree.command()
# @app_commands.rename(text_to_send='text')
# @app_commands.describe(text_to_send='Text to send in the current channel')
# async def send(interaction: discord.Interaction, text_to_send: str):
#     """Sends the text into the current channel."""
#     await interaction.response.send_message(text_to_send)


@client.tree.command()
async def set_pray(ctx: discord.Interaction, user: discord.User):
	"""Sets a job to send a message to the current channel at a specific time."""
	with open("users.json","r+") as f:
		users = set(json.load(f))
		users = list(users)
		users.append(user.id)
		users = set(users)
		users = list(users)
		f.seek(0)
		json.dump(users,f)
	await ctx.response.send_message('Job Set!', ephemeral=True)



@tasks.loop(hours=12.0)
async def impersonate():
	# users = [282538758182797312,247041157148835840,741192494133280851]
	with open("users.json","r") as f:
		users = json.load(f)
	channel = await client.fetch_channel(1090865789877366794)
	for i in enumerate(users):
		user = await client.fetch_user(i[1])
		message = ":pray:"
		webhook = await channel.create_webhook(name=user.display_name)
		await webhook.send(message, username=user.display_name, avatar_url=user.display_avatar)
		await webhook.delete()




client.run(TOKEN)
