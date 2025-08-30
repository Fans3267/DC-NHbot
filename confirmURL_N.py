import discord
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import cloudscraper

scraper = cloudscraper.create_scraper()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Referer": "https://nhentai.net/",
}
#下中腳確認連段
async def exist_confirm(url):
    #URL處理
    base_url = urlparse(url[0])
    path_parts = [part for part in base_url.path.split('/') if part]
    if len(path_parts) >= 2:
        #去除多餘
        base_path = '/'.join(path_parts[:2])
        main_url = f"{base_url.scheme}://{base_url.netloc}/{base_path}/"
        #神的語言
        code = path_parts[1]
    #soup獲取html
    print(main_url)
    res = scraper.get(main_url, headers=HEADERS)
    
    if res.status_code != 200:
        print(f"抓取失敗，Status: {res.status_code}")
        return False, f"防機器人又在搞我 狀態:{res.status_code}, 對不起我真的沒辦法繞過這個</3 請等等再嘗試"
    
    soup = BeautifulSoup(res.text, "html.parser")

    #圖片
    try:
        imgs = soup.find_all("img", class_="lazyload")  
        target_image = None
        for img in imgs:
            src = img.get("data-src") or img.get("src")
            if src and "cover.webp" in src:
                target_image = "https:" + src
                break
    except Exception as e:
        return False, "窩很包歉 拿不到圖片 >.<"
    
    #標題
    title = None
    try:
        title_span = soup.find("h2", class_="title")
        if title_span is None:
            title_span = soup.find("h1", class_="title")
            #檢查404
            if title_span.text.strip().find("404") != -1:
                return False, "錯誤連結 >:3 或是已經刪除的作品"
        title_artist = title_span.find("span", class_="before").text.strip()
        title_name = title_span.find("span", class_="pretty").text.strip()
        title = f"{title_artist} {title_name}"
    except Exception as e:
        print(soup.prettify()[:500])
        return False, "搜哩啦 ;-; 找不到標題"
        
    # 標籤
    artist = []
    character = []
    language = []
    tag = []
    try:
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

        embed = discord.Embed(
            description=(
                f"## [{title}]({main_url}) \n"
                f"### N - {code}\n"
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