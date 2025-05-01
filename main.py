import discord
import requests
import re
import random
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from discord.ext import commands

#TOEKN
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("BETA_TOKEN")
Guild = discord.Object(id=1359744875309830204) #測試ID

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="n-",intents=intents)
@client.event
async def on_ready():
    try:
        synced = await client.tree.sync(guild=Guild)
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing tree: {e}")



#D反 舊指令
@client.command()
async def sr(ctx):
    await ctx.send(f"❗ 指令已經更改了喔~ 使用 /nhelp 查看更多")
@client.command()
async def helpme(ctx):
    await ctx.send(f"❗ 指令已經更改了喔~ 使用 /nhelp 查看更多")


#幫助 nhelp
@client.tree.command(name="nhelp",description="幫助/指令教學")
async def nhelp(interaction: discord.Interaction):
    embed = discord.Embed(
        title="目前功能",
        description=(
            "\n"
            "### - 直接輸入完整nhentai網址 : 機器人會自動分析 \n"
            "### - /nhelp : 所有指令 \n"
            "### - /nsr <關鍵字> : 輸入你想要搜尋的東西 並顯示前五的結果 \n"
            "### - n <數字> : 直接輸入神的語言 \n"
            "\n"
            "有任何問題可以至 [群組](https://discord.gg/CA6mS8tChw) 回報\n"
            "\n"
            "這我寶 請對她輕聲細語 <3   [圖源](https://www.pixiv.net/artworks/117645492)"
        ),
        color=discord.Color.random()
    )
    file = discord.File("voyager.jpg", filename="voyager.jpg")

    embed.set_image(url="attachment://voyager.jpg")
    await interaction.response.send_message(file=file, embed=embed)


#搜尋指令 nsr
@client.tree.command(name="nsr",description="搜尋任何N站上的東西")
async def nsr(interaction: discord.Interaction, search: str):
    print(search)
    url = f"https://nhentai.net/search/?q={search}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_res = requests.get(url, headers=headers, timeout=5)
    search_soup = BeautifulSoup(search_res.text, 'html.parser')

    captions = search_soup.find_all("div", class_="caption")
    images = search_soup.find_all("img", class_="lazyload")
    links = search_soup.find_all("a", class_="cover")

    result_url = []
    result_image = []
    result_name = []
    search_ammount = 5
    random_image_selector = 0
    for i in range(search_ammount):
        try:
            title = captions[i].text.strip() #標
            result_name.append(title)
            
            img = images[i].get("data-src") #圖
            result_image.append(img)

            link = links[i].get("href")  #連
            result_url.append("https://nhentai.net"+link) 

        except Exception as e:
            break
        
    if(len(result_url)==0):
        await interaction.response.send_message("沒有找到任何結果 。･ﾟ･(つд`ﾟ)･ﾟ･ ")
        print("== 沒有結果 ==\n")
        return
    
    #done: find url and code
    #done: fix embed

    #todo: fix image embed (guess I'll never fix it >:3)
    random_image_selector = random.randint(0, len(result_image)-1)
    print("== " + str(random_image_selector) + " ==\n")

    embed_description = "## 搜尋結果 \n"
    for index, (name, url) in enumerate(zip(result_name, result_url), start=1):
        embed_description += f" {index}. [{name}]({url}) \n"
    embed_description += f"\n 第 {random_image_selector +1} 的縮圖 \n (抱歉我懶得做按鈕給你們每本都看 只好做成隨機的了 (・ε・) \n"
    embed = discord.Embed(
        description=embed_description,
        color=discord.Color.random()
    )
    embed.set_image(url=result_image[random_image_selector])
    await interaction.response.send_message(embed=embed)
    #清
    result_url.clear()
    result_image.clear()
    result_name.clear()


#直接樹入數字 code
url=[]
@client.tree.command(name="code",description="直接輸入數字", guild=Guild)
async def code(interaction: discord.Interaction, code: str):
    print(code)
    url.clear()
    url.append(f"https://nhentai.net/g/{code}/")

    from confirmURL_N import exist_confirm
    success_n = False
    author = interaction.user
    success_n, status = await exist_confirm(url, author)

    if success_n == True:
        #成功
        await interaction.response.send_message(embed=status)
        print("== 成功 ==\n")
        return
    elif success_n == False:
        await interaction.response.send_message(status)
        print("== 錯誤 ==\n")
        return


#訊息
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await client.process_commands(message)
    
    #篩選指定往玉
    url_regex = re.compile(r'https?://nhentai\.net/g/[^\s]+')
    url = []
    url = re.findall(url_regex, message.content)

    #測試方便用 直接打[n 數字]
    num_command = re.match(r"n \s*(\w+)", message.content)
    if num_command:
        num_command = num_command.group(1)
        url.append(f"https://nhentai.net/g/{num_command}/")
    if not url:
        return
    
    success_n = False
    from confirmURL_N import exist_confirm
    author = message.author
    success_n,status = await exist_confirm(url,author) #確認連結
    
    print(url)
    if success_n == True:
        #成功
        await message.delete() #刪除使用者傳送的訊息
        await message.channel.send(embed=status)
        print("== 成功 ==\n")
        return
    elif success_n == False:
        await message.channel.send(status)
        await message.remove_reaction("✅", client.user)
        await message.add_reaction("❌")
        print("== 錯誤 ==\n")
        return
        

client.run(TOKEN)