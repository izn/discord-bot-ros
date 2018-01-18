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

    # Remove anexos das mensagens do #geral e notifica o usuário
    if message.attachments and message.channel.name == 'geral':
        msg = '{0.author.mention}, não é permitido enviar anexos (imagens, arquivos, etc) aqui!'.format(message)

        await client.send_message(message.channel, msg)
        await client.delete_message(message)

    # Remove mensagens de invites para outros Discords
    pattern = 'https?:\/\/discord\.gg\/(\w+)'
    match = re.search(pattern, content)

    if match:
        code = match.group(1)
        r = requests.get("https://discordapp.com/api/v6/invites/%s" % code)
        data = json.loads(r.text)

        if data.get('guild').get('id') != os.environ.get('DISCORD_MAIN_SERVER_ID'):
            await client.delete_message(message)


    # Troca de elo
    if content.startswith('!elo'):
        entered_rank = content[5:].lower().strip()
        role_name = [item['role'] for item in allowed_roles if entered_rank in item['term']]

        if role_name:
            role = discord.utils.get(message.server.roles, name=role_name[0])
            valid_roles = [i['role'] for i in allowed_roles]

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
