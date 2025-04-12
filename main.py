import discord
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from discord.ext import commands

#TOEKN
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

    #URL處理
    url = re.findall(url_regex, message.content)
    print(url)
    base_url = urlparse(url[0])
    path_parts = [part for part in base_url.path.split('/') if part]
    if len(path_parts) >= 2:
        # 組合主路徑
        base_path = '/'.join(path_parts[:2])
        main_url = f"{base_url.scheme}://{base_url.netloc}/{base_path}/"

        # 取得目標段落
        code = path_parts[1]

    print(base_url)
    print(main_url)
    pic_url = main_url + "1/"

    #反應
    if pic_url:
        '''await message.reply(f"{message.author.mention} 連結：{urls[0]}")'''
        await message.add_reaction("✅")

    #圖片
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(pic_url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        imgs = soup.find_all("img")
        target_image = None
        for img in imgs:
            src = img.get("src")
            if src and "galleries" in src:
                target_image = src
                break
    
    except Exception as e: #失敗
        await message.channel.send("窩很包歉 無法獲取圖片>.<")

    #標籤
    artist = []
    character = []
    language = []
    tag = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(main_url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
         
        for all_tags in soup.find_all("span", class_="tags"):
            for tags in all_tags.find_all("a"):

                href = tags.get("href", "")
                name = tags.find("span", class_="name").text.strip()
                
        
                if "/artist/" in href:
                    artist.append(name)
                if "/character/" in href:
                    character.append(name)
                if "/language/" in href:
                    language.append(name)
                if "/tag/" in href:
                    tag.append(name)
        
        await message.delete() #刪除
        embed = discord.Embed(
            description=(
                f"## <{main_url}>\n"
                f"- 由 {message.author.mention} 分享 \n"
                f"  - 繪師：{', '.join(f'`{a}`' for a in artist)}\n"
                f"  - 標籤：{', '.join(f'`{t}`' for t in tag)}\n"
                f"  - 角色：{', '.join(f'`{c}`' for c in character)}\n"
                f"  - 語言：{', '.join(f'`{l}`' for l in language)}"
            ),
            color=discord.Color.random()
        )
        #Embed
        embed.set_image(url=target_image)
        await message.channel.send(embed=embed)
    
    except Exception as e: #失敗
        await message.channel.send("對噗起 窩無法獲取標籤 :<")

client.run(TOKEN)
