import discord
import asyncio
import json
import os
import requests
import re

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

client = discord.Client()
allowed_roles = [
    'Grand Master',
    'Diamond',
    'Platinum',
    'Gold',
    'Silver',
    'Bronze'
]

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Remove mensagens de invites para outros Discords
    pattern = 'https?:\/\/discord\.gg\/(\w+)'
    match = re.search(pattern, message.content)

    if match:
        code = match.group(1)
        r = requests.get("https://discordapp.com/api/v6/invites/%s" % code)
        data = json.loads(r.text)

        if data.get('guild').get('id') != os.environ.get('DISCORD_MAIN_SERVER_ID'):
            await client.delete_message(message)


    # Troca de elo
    if message.content.strip().startswith('!elo'):
        entered_rank = message.content[5:].lower().title().strip()
        role = discord.utils.get(message.server.roles, name=entered_rank)

        roles = discord.utils.get(message.server.roles)
        valid_roles = [i for i in message.server.roles if i.name in allowed_roles]

        if entered_rank in allowed_roles:
            user_roles = message.author.roles
            user_roles = [i for i in user_roles if i not in valid_roles]

            user_roles.append(role)

            msg = '{0.author.mention}, mudei seu elo para {1}!'.format(message, entered_rank)

            await client.replace_roles(message.author, *user_roles)
            await client.send_message(message.channel, msg)
        else:
            msg = '{0.author.mention}, os elos possíveis são: Grand Master, Diamond, Platinum, Gold, Silver ou Bronze.'.format(message)
            await client.send_message(message.channel, msg)

client.run(os.environ.get('DISCORD_TOKEN'))
