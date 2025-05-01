import discord
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


#下中腳確認連段
async def exist_confirm(url, author):
    #URL處理
    base_url = urlparse(url[0])
    path_parts = [part for part in base_url.path.split('/') if part]
    if len(path_parts) >= 2:
        #去除多餘
        base_path = '/'.join(path_parts[:2])
        main_url = f"{base_url.scheme}://{base_url.netloc}/{base_path}/"
        #神的語言
        code = path_parts[1]
    #首圖
    pic_url = main_url + "1/"
    #soup獲取html
    headers = {'User-Agent': 'Mozilla/5.0'}
    pic_res = requests.get(pic_url, headers=headers, timeout=5)
    pic_soup = BeautifulSoup(pic_res.text, 'html.parser')
    main_res = requests.get(main_url, headers=headers, timeout=5)
    main_soup = BeautifulSoup(main_res.text, 'html.parser')

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
        return False, "窩很包歉 拿不到圖片 >.<"
    
    #標題
    title = None
    try:
        title_span = main_soup.find("h2", class_="title")
        if title_span is None:
            title_span = main_soup.find("h1")
            #檢查404
            if title_span.text.strip().find("404") != -1:
                return False, "❌錯誤連結 >:3 或是已經刪除的作品❌"
        title_artist = title_span.find("span", class_="before").text.strip()
        title_name = title_span.find("span", class_="pretty").text.strip()
        title = f"{title_artist} {title_name}"
    except Exception as e:
        return False, "搜哩啦 ;-; 找不到標題"
        
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
        
        embed = discord.Embed(
            description=(
                f"## [{title}]({main_url}) \n"
                f"### N - {code}\n"
                f"- 由 {author.mention} 分享 \n"
                f"  - 繪師：{', '.join(f'`{a}`' for a in artist)}\n"
                f"  - 標籤：{', '.join(f'`{t}`' for t in tag)}\n"
                f"  - 角色：{', '.join(f'`{c}`' for c in character)}\n"
                f"  - 語言：{', '.join(f'`{l}`' for l in language)}"
            ),
            color=discord.Color.random() #亂色
        )
        #Embed
        embed.set_image(url=target_image)
        return True, embed
       
    except Exception as e:
        return False, "對噗起嗚嗚 窩無法獲取標籤"