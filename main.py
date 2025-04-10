import discord
import requests
import re
from bs4 import BeautifulSoup
from discord.ext import commands

client = commands.Bot(command_prefix='!',intents=discord.Intents.all())
@client.event
async def on_ready():
    print("Running")

'''@client.command()
async def hello(ctx):
    await ctx.send("Hello!")'''

url_regex = re.compile(
    r'https?://nhentai\.net/g/[^\s]+'
)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    match = re.findall(url_regex, message.content)
    match[0] += "1/"
    print(match)

    if match:
        '''await message.reply(f"{message.author.mention} 連結：{urls[0]}")'''
        await message.add_reaction("🔗")

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(match[0], headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        imgs = soup.find_all("img")
        target_image = None

        for img in imgs:
            src = img.get("src")
            if src and "galleries" in src:
                target_image = src
                break
        await message.channel.send(target_image)
    except Exception as e:
        await message.channel.send("窩很包歉 無法獲取圖片 :<")

        

client.run('MTM1OTc0MTUxODI2NDQwMTk2Mg.G6ssJ_.lcaRW7P7aMo7J1MMTzRcBZYQ77C5uCAaS4yKOo')
