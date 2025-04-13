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
TOKEN = os.getenv("BETA_TOKEN")

client = commands.Bot(command_prefix="!",intents=discord.Intents.all())
@client.event
async def on_ready():
    print("Running")

#訊息
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await client.process_commands(message)

    #辨別網址
    url_regex = re.compile(
    r'https?://nhentai\.net/g/[^\s]+'
    )
    url = re.findall(url_regex, message.content)

    #測試方便用 直接打[n 數字]
    num_command = re.match(r"n \s*(\w+)", message.content)
    if num_command:
        num_command = num_command.group(1)
        url.append(f"https://nhentai.net/g/{num_command}/")
        
    if not url:
        return
    
    #URL處理
    print(url)
    base_url = urlparse(url[0])
    path_parts = [part for part in base_url.path.split('/') if part]
    if len(path_parts) >= 2:
        #去除URL多餘的部分
        base_path = '/'.join(path_parts[:2])
        main_url = f"{base_url.scheme}://{base_url.netloc}/{base_path}/"

        #神的語言
        code = path_parts[1]
    
    #首圖路徑
    pic_url = main_url + "1/"

    #soup獲取html
    headers = {'User-Agent': 'Mozilla/5.0'}
    pic_res = requests.get(pic_url, headers=headers, timeout=5)
    pic_soup = BeautifulSoup(pic_res.text, 'html.parser')
    main_res = requests.get(main_url, headers=headers, timeout=5)
    main_soup = BeautifulSoup(main_res.text, 'html.parser')

    #反應
    if pic_url:
        '''await message.reply(f"{message.author.mention} 連結：{urls[0]}")'''
        await message.add_reaction("✅")

    #圖片
    try:
        imgs = pic_soup.find_all("img")
        target_image = None
        for img in imgs:
            src = img.get("src")
            if src and "galleries" in src:
                target_image = src
                break
    
    except Exception as e:
        await message.channel.send("窩很包歉 拿不到圖片 >.<")

    #標題
    title = None
    try:
        title_span = main_soup.find("h2", class_="title")
        if title_span is None:
            title_span = main_soup.find("h1")
            #檢查404
            if title_span.text.strip().find("404") != -1:
                await message.remove_reaction("✅", client.user)
                await message.add_reaction("❌")
                await message.channel.send(f"{main_url} ❌錯誤連結 >:3 或是已經刪除的作品❌")
                print("== 錯誤 ==\n")
                return
        title_artist = title_span.find("span", class_="before").text.strip()
        title_name = title_span.find("span", class_="pretty").text.strip()
        title = f"{title_artist} {title_name}"

    except Exception as e:
        await message.channel.send("搜哩啦 ;-; 找不到標題")

    # 標籤
    artist = []
    character = []
    language = []
    tag = []
    try:
        for all_tags in main_soup.find_all("span", class_="tags"):
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
        
        await message.delete() #刪除使用者傳送的訊息
        embed = discord.Embed(
            description=(
                f"## {title} \n"
                f"### N [{code}]({main_url})\n"
                f"- 由 {message.author.mention} 分享 \n"
                f"  - 繪師：{', '.join(f'`{a}`' for a in artist)}\n"
                f"  - 標籤：{', '.join(f'`{t}`' for t in tag)}\n"
                f"  - 角色：{', '.join(f'`{c}`' for c in character)}\n"
                f"  - 語言：{', '.join(f'`{l}`' for l in language)}"
            ),
            color=discord.Color.random() #亂色
        )
        #Embed
        embed.set_image(url=target_image)
        print("== 成功 ==\n")
        await message.channel.send(embed=embed)
        
    except Exception as e:
        await message.channel.send("對噗起嗚嗚 窩無法獲取標籤")

client.run(TOKEN)
