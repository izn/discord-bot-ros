from dotenv import load_dotenv, find_dotenv
import discord
import asyncio
import json
import os
import requests
import re


load_dotenv(find_dotenv())

client = discord.Client()

ADMIN_ROLE_ID = '400770147922739200'
MODERATOR_ROLE_ID = '401477585038606347'
TWITCH_ROLE_ID = '402588361988243466'
ALLOWED_ROLES = [
    { 'role': 'Grand Master', 'term': ['grand master', 'master'] },
    { 'role': 'Diamond', 'term': ['diamond', 'diamante'] },
    { 'role': 'Platinum', 'term': ['platina', 'platinum'] },
    { 'role': 'Gold', 'term': ['ouro', 'gold'] },
    { 'role': 'Silver', 'term': ['prata', 'silver'] },
    { 'role': 'Bronze', 'term': ['bronze'] }
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

    content = message.content.strip()
    author_roles = [a.id for a in message.author.roles]

    if ADMIN_ROLE_ID in author_roles or MODERATOR_ROLE_ID in author_roles:
        return

    if message.attachments and message.channel.name == 'geral':
        msg = '{0.author.mention}, não é permitido enviar anexos (imagens, arquivos, etc) aqui!'.format(message)

        await client.send_message(message.channel, msg)
        await client.delete_message(message)

    pattern = 'https?:\/\/(?:www\.)?twitch\.tv\/(\w+)'
    twitch_match = re.search(pattern, content)

    if twitch_match:
        if TWITCH_ROLE_ID not in author_roles:
            await client.delete_message(message)

    pattern = 'https?:\/\/discord\.gg\/(\w+)'
    discord_match = re.search(pattern, content)

    if discord_match:
        code = discord_match.group(1)
        r = requests.get("https://discordapp.com/api/v6/invites/%s" % code)
        data = json.loads(r.text)

        if data.get('guild').get('id') != os.environ.get('DISCORD_MAIN_SERVER_ID'):
            await client.delete_message(message)

    if content.startswith('!elo'):
        entered_rank = content[5:].lower().strip()
        role_name = [item['role'] for item in ALLOWED_ROLES if entered_rank in item['term']]

        if role_name:
            role = discord.utils.get(message.server.roles, name=role_name[0])
            valid_roles = [i['role'] for i in ALLOWED_ROLES]

            user_roles = message.author.roles
            user_roles = [i for i in user_roles if i.name not in valid_roles]

            user_roles.append(role)

            msg = '{0.author.mention}, mudei seu elo para {1}!'.format(message, role.name)

            await client.replace_roles(message.author, *user_roles)
            await client.send_message(message.channel, msg)
        else:
            msg = '{0.author.mention}, os elos possíveis são: Grand Master, Diamond, Platinum, Gold, Silver ou Bronze.'.format(message)
            await client.send_message(message.channel, msg)


client.run(os.environ.get('DISCORD_TOKEN'))
