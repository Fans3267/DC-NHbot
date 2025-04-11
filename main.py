import discord
import requests
import re
from bs4 import BeautifulSoup
from discord.ext import commands

import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


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

    main_url = re.findall(url_regex, message.content)
    match = [main_url[0] + "1/"]

    if match:
        '''await message.reply(f"{message.author.mention} 連結：{urls[0]}")'''
        await message.add_reaction("🔗")

    #圖片
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
        
        all_tags = soup.find_all("span",class_="tags")
        print(all_tags)
        for tag_group in all_tags:
            tag = tag_group.get("href")
            if tag and "tag/" in tag:
                await message.channel.send(tag)
            
        #發送圖片    
        await message.channel.send(target_image)
    except Exception as e: #失敗
        await message.channel.send("窩很包歉 無法獲取圖片>.<")

    #標籤
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(main_url[0], headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        all_tags = soup.find_all("span",class_="name")
        print(all_tags)
        for tag_group in all_tags:
            tag = tag_group.get("href")
            if tag and "tag/" in tag:
                await message.channel.send(tag)
            
    except Exception as e: #失敗
        await message.channel.send("對噗起 窩無法獲取標籤 :<")

client.run(TOKEN)
