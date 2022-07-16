
# база
import discord
from discord.ext import commands, tasks
from config import token, mongotok
from pymongo import MongoClient
from discord.utils import get

# всякое разное
from math import ceil
import random
import asyncio
import requests
import pytz
import datetime

# для анекдотов
from bs4 import BeautifulSoup
from googletrans import Translator

# для ебучих редисов
import json
import urllib.request
import urllib.parse

client = commands.Bot(command_prefix = "?")

# монгодб
cluster = MongoClient(mongotok)
deml = cluster["GMDOBOT"]["demonlist"]
plrs = cluster["GMDOBOT"]["players"]
mmbrs = cluster["GMDOBOT"]["members"]
brthds = cluster["GMDOBOT"]["birthdays"]

editor = 927634802096611469
moder = 886682255211253760
translator = Translator(service_urls=['translate.googleapis.com'])
API_KEY = 'AIzaSyCiet7DWMafTzv-hTelx6pd1JUV_cTQOZE'
SEARCH_ENGINE_ID = '9f1f6320d8ce8bef8'

points = [250, 228, 210, 195, 180, 170, 160, 151, 144, 137, 132, 127, 123.6, 120.2, 117.4, 115, 112.9, 111,
          109.5, 108.2, 107, 105.7, 104.5, 103.23, 101.94, 100.6, 99.3, 98, 96.6, 95.2, 94, 92.5, 91.5, 89.6, 88.2,
          86.6, 85.1, 83.6, 82, 80.5, 78.9, 77.3, 75.7, 74, 72.3, 70.7, 69, 67.2, 65.5, 63.7, 61.9, 60.1, 58.5, 56.9,
          55.3, 53.9, 52.3, 50.8, 49.4, 48, 46.7, 45.4, 44.2, 43, 41.8, 40.7, 39.5, 38.5, 37.4, 36.4, 35.4, 34.4, 33.5,
          32.6, 31.7, 30.9, 30, 29.2, 28.4, 27.7, 27, 26.2, 25.6, 25, 24.2, 23.5, 23, 22.3, 21.7, 21.2, 20.6, 20, 19.5,
          19, 18.5, 18, 17.6, 17.1, 16.7, 16.3]

def calc_lb():
    victors = {}
    for lvl in deml.find():
        for victor in lvl["victors"]:
            if victor[0] not in victors.keys():
                victors[victor[0]] = points[lvl["position"]-1] if lvl["position"] <= 100 else 3
            else:
                victors[victor[0]] += points[lvl["position"]-1] if lvl["position"] <= 100 else 3
    return {k: v for k, v in sorted(victors.items(), reverse=True, key=lambda item: item[1])}

async def browse_pages(ctx, pg, pages, embeds, more_buttons=True):
    msg = await ctx.send(embed=embeds[pg - 1])

    if pages > 1:
        reactionslist = ["⏪", "◀", "▶", "⏩"] if more_buttons else ["◀", "▶"]
        for i in reactionslist:
            await msg.add_reaction(i)

        while True:
            try:
                reaction, user = await client.wait_for('reaction_add', timeout=30.0,
                                                       check=lambda reaction, user: user == ctx.author and str(
                                                           reaction.emoji) in reactionslist)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                break
            else:

                if str(reaction.emoji) == (reactionslist[1] if more_buttons else reactionslist[0]):
                    if pg != 1:
                        pg -= 1
                elif str(reaction.emoji) == (reactionslist[2] if more_buttons else reactionslist[1]):
                    if pg != pages:
                        pg += 1

                if more_buttons:
                    if str(reaction.emoji) == reactionslist[3]:
                        pg = pages
                    elif str(reaction.emoji) == reactionslist[0]:
                        pg = 1
                await msg.remove_reaction(str(reaction.emoji), ctx.author)
                await msg.edit(embed=embeds[pg - 1])

def get_passed_levels(player):
    passedlevels = []
    proofs = []
    for lvl in deml.find():
        for victor in lvl["victors"]:
            if victor[0].lower() == player.lower():
                passedlevels.append(lvl)
                proofs.append(victor[1])
                break
    passedlevels.sort(key=lambda x: x['position'])
    return passedlevels, proofs

def randimg(search):
    q = urllib.parse.quote_plus(search, safe='?&=')

    request = urllib.request.Request(
        'https://www.googleapis.com/customsearch/v1?key=' + API_KEY + '&cx=' +
        SEARCH_ENGINE_ID + '&q=' + q + '&start=' + str(
            random.choice([i * 10 + 1 for i in range(20)])) + '&searchType=image')

    with urllib.request.urlopen(request) as f:
        data = f.read().decode('utf-8')

    return random.choice(json.loads(data)['items'])

def gk(d):
    return [i for i in d]

@client.event
async def on_ready():
    print("Бот запущен!")
    checkday.start()

@client.event
async def on_message(message):
    gmobot = get(client.get_all_members(), id=993896677092106240)
    if gmobot.mention in message.content:
        await message.channel.send("<:VK_WTF:997209990278422598>")
    if message.channel.id == 997728986807406652:
        if len(message.content) == 5 and message.content[2] == ".":
            if brthds.find_one({"member": message.author.id}) is None:
                brthds.insert_one({"member": message.author.id, "day": int(message.content[:2]), "month": int(message.content[3:]), "pozdravlen": False})
            else:
                brthds.update_one({"member": message.author.id}, {"$set": {"day": int(message.content[:2]), "month": int(message.content[3:])}})

    await client.process_commands(message)

@tasks.loop(seconds = 60)
async def checkday():
    moscow_time = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
    birthchannel = client.get_channel(886678288704090193)
    if moscow_time.hour >= 10:
        for birth in brthds.find():
            imeninnik = await client.fetch_user(birth["member"])
            if birth["day"] == moscow_time.day and birth["month"] == moscow_time.month:
                if not birth["pozdravlen"]:
                    await birthchannel.send(f"У {imeninnik.mention} сегодня день рождения! ПОЗДРАВЛЯЕМ! 🎉🎊")
                    await birthchannel.send(randimg("открытки с днём рождения забавные")["link"])
                    brthds.update_one({"member": imeninnik.id}, {"$set": {"pozdravlen": True}})
            else:
                brthds.update_one({"member": imeninnik.id}, {"$set": {"pozdravlen": False}})

@client.command(aliases=['дл', 'demonlist', 'демонлист', 'Демонлист', 'дЛ', 'Дл', 'Dl', 'dL', 'DL', 'ДЛ'])
async def dl(ctx, pg: int = 1):

    lvlsamount = len([lvl for lvl in deml.find()])
    pages = ceil(lvlsamount/10) if lvlsamount <= 100 else 10
    if pg <= pages:
        embeds = list()
        for page in range(1,pages+1 if lvlsamount <= 100 else 11):
            embed = discord.Embed(title="Офицальный топ игроков Подполья", colour=0x766ce5, description="**Место | Название | Автор | Поинты**")
            for i in range(10*(page-1)+1, (page*10 if lvlsamount > 10 and (lvlsamount - (page-1)*10) >= 10 else lvlsamount)+1):
                lvl = deml.find_one({"position": i})
                embed.add_field(name=f"""**#{i}** | **{lvl["name"]}** by **{lvl["author"]}** | {points[i-1]}"<:GD_STAR:997218626006425690>"\n""",
                                value=f"Victors: {', '.join([f'**[{vic[0]}]({vic[1]})**' for vic in lvl['victors']]) if len(lvl['victors']) != 0 else 'нет'}",
                                inline=False)
            embed.set_footer(text=f"Страница {page}/{pages}. (C) Official Podpol'e Demonlist")
            embeds.append(embed)

        await browse_pages(ctx, pg, pages, embeds)
    else:
        await ctx.send("На этой странице ещё нет уровней!")

@client.command(aliases=['легаси'])
async def legacy(ctx, pg: int = 1):

    lvlsamount = len([lvl for lvl in deml.find()])
    if lvlsamount > 100:
        pages = ceil((lvlsamount-100)/10)
        if pg <= pages:
            embeds = list()
            for page in range(11,pages+11):
                embed = discord.Embed(title="Офицальный топ игроков Подполья", colour=0x766ce5, description="*За каждый уровень из легаси даётся 3<:GD_STAR:997218626006425690>*\n**Место | Название | Автор**")
                for i in range(10*(page-1)+1, (page*10 if lvlsamount > 10 and (lvlsamount - (page-1)*10) >= 10 else lvlsamount)+1):
                    lvl = deml.find_one({"position": i})
                    embed.add_field(name=f"""**#{i}** | **{lvl["name"]}** by **{lvl["author"]}**\n""",
                                    value=f"Victors: {', '.join([f'**[{vic[0]}]({vic[1]})**' for vic in lvl['victors']]) if len(lvl['victors']) != 0 else 'нет'}",
                                    inline=False)
                embed.set_footer(text=f"Страница {page-10}/{pages}. (C) Official Podpol'e Demonlist")
                embeds.append(embed)

            await browse_pages(ctx, pg, pages, embeds)
        else:
            await ctx.send("На этой странице ещё нет уровней!")
    else:
        await ctx.send("мужик легаси не существует")

# ГОТОВО
@client.command(aliases=['add','добавить','добавитьуровень'])
@commands.has_role(editor)
async def addlevel(ctx, lvlname, lvlauthor, pos: int):
    lvlsamount = len([lvl for lvl in deml.find()])
    if pos <= lvlsamount+1:
        for name in [i["name"] for i in deml.find() if i["position"] >= int(pos)]:
            deml.update_one({"name": name}, {"$inc": {"position": 1}})
        deml.insert_one({"name": lvlname, "author": lvlauthor, "victors": [], "position": int(pos)})
        if pos == 1:
            await ctx.send(f"{lvlname} добавлен на {pos} позицию, сместив при этом {deml.find_one({'position': pos + 1})['name']} на вторую строчку листа!")
        elif pos == lvlsamount+1:
            await ctx.send(f"{lvlname} добавлен на {pos} позицию, то есть на последнюю, ничего при этом не обогнав и не сместив :(")
        else:
            await ctx.send(f"{lvlname} добавлен на {pos} позицию, выше {deml.find_one({'position': pos + 1})['name']}, но ниже {deml.find_one({'position': pos - 1})['name']}!")
    else:
        await ctx.send(f'Мужик, ты чего? В демонлисте пока что всего {lvlsamount} уровней, а ты собрался на {pos} место что-то ставить. Подумай об этом на досуге.')

# ГОТОВО
@client.command(aliases=['del','remove','удалитьуровень', 'удалить'])
@commands.has_role(editor)
async def dellevel(ctx, pos: int):
    lvl = deml.find_one({"position": pos})
    if lvl is not None:
        deml.delete_one({"position": pos})
        for name in [i["name"] for i in deml.find() if i["position"] > pos]:
            deml.update_one({"name": name}, {"$inc": {"position": -1}})
        await ctx.send(f"{lvl['name']} удалён. GG.")
    else:
        await ctx.send('Такого уровня не существует!')

# ГОТОВО
@client.command(aliases=['victor','виктор','добавитьвиктора'])
@commands.has_role(editor)
async def addvictor(ctx, pos: int, victor, video = None):
    lvl = deml.find_one({"position": pos})
    if lvl is not None:
        victors = lvl["victors"]
        if victor.lower() not in [i[0].lower() for i in victors]:
            victors.append([victor, video])
            deml.update_one({"position": pos}, {"$set": {"victors": victors}})
            plrs.insert_one({"nick": victor, "discordtag": None, "curpercent": 0, "roulettelvls": []})
            await ctx.send(f"{victor} добавлен к викторам {lvl['name']}.")
        else:
            await ctx.send(f"{victor} уже является виктором уровня {lvl['name']}!")
    else:
        await ctx.send('Такого уровня не существует!')

# ГОТОВО
@client.command()
@commands.has_role(editor)
async def delvictor(ctx, pos: int, vctr):
    lvl = deml.find_one({"position": pos})
    if lvl is not None:
        victors = lvl["victors"]
        realname = None
        a=-1
        for victor in victors:
            a+=1
            if victor[0].lower() == vctr.lower():
                realname = victor[0]
                victors.pop(a)
                deml.update_one({"position": lvl["position"]}, {"$set": {"victors": victors}})
                break

        await ctx.send(f"{realname} удалён из викторов {lvl['name']}.")

        a=0
        for l in deml.find():
            for victor in l["victors"]:
                if victor[0].lower() == vctr.lower():
                    a+=1
                    break
        if a==0:
            plrs.delete_one({"nick": realname})
    else:
        await ctx.send('Такого уровня не существует!')

# ГОТОВО
@client.command(aliases=['proof','пруф','добавитьпруф'])
@commands.has_role(editor)
async def addproof(ctx, pos: int, victor, video):
    lvl = deml.find_one({"position": pos})
    if lvl is not None:
        victors = lvl["victors"]
        vict = [vic for vic in victors if vic[0].lower() == victor.lower()]
        print(vict)
        if len(vict) > 0:
            victors.pop(victors.index(vict[0]))
            victors.append([victor, video])
            deml.update_one({"position": pos}, {"$set": {"victors": victors}})
            await ctx.send(f"Пруф игрока {vict[0]} на уровень {lvl['name']} успешно добавлен.")
        else:
            await ctx.send('Данный игрок не является виктором этого уровня.')
    else:
        await ctx.send('Такого уровня не существует!')

# ГОТОВО
@client.command(aliases=['удалитьпруф'])
@commands.has_role(editor)
async def delproof(ctx, pos: int, victor):
    lvl = deml.find_one({"position": pos})
    if lvl is not None:
        victors = lvl["victors"]
        vict = [vic for vic in victors if vic[0].lower() == victor.lower()]
        print(vict)
        if len(vict) > 0:
            if vict[1] is not None:
                victors.pop(victors.index(vict[0]))
                victors.append([victor, None])
                deml.update_one({"position": pos}, {"$set": {"victors": victors}})
                await ctx.send(f"Пруф игрока {vict[0]} на уровень {lvl['name']} удалён.")
            else:
                await ctx.send('У этого игрока итак не привязаны никакие пруфы к этому уровню.')
        else:
            await ctx.send('Данный игрок не является виктором этого уровня.')
    else:
        await ctx.send('Такого уровня не существует!')

# ГОТОВО
@client.command(aliases=['изменить','изменитьуровень'])
@commands.has_role(editor)
async def edit(ctx, pos: int, new_pos: int):
    lvl = deml.find_one({"position": pos})
    swapped_lvl = deml.find_one({"position": new_pos})
    if lvl is not None:
        if pos != new_pos:

            if pos > new_pos:
                for name in [i["name"] for i in deml.find() if i["position"] < pos and i["position"] >= new_pos]:
                    deml.update_one({"name": name}, {"$inc": {"position": 1}})
            else:
                for name in [i["name"] for i in deml.find() if i["position"] > pos and i["position"] <= new_pos]:
                    deml.update_one({"name": name}, {"$inc": {"position": -1}})
            deml.update_one({"name": lvl["name"]}, {"$set": {"position": new_pos}})
            await ctx.send(f'Уровень {lvl["name"]} перенесён на позицию {new_pos} с позиции {pos}!')
        else:
            await ctx.send('Чо творишь')
    else:
        await ctx.send('Такого уровня не существует!')

# ГОТОВО
@client.command(aliases=['длбан'])
@commands.has_role(editor)
async def dlban(ctx, player):
    isplayerexists = False
    realname = None
    for lvl in deml.find():
        victors = lvl["victors"]
        a = -1
        for victor in victors:
            a+=1
            if victor[0].lower() == player.lower():
                isplayerexists = True
                realname = victor[0]
                victors.pop(a)
                deml.update_one({"position": lvl["position"]}, {"$set": {"victors": victors}})
                break
    if isplayerexists:
        plrs.delete_one({"name": realname})
        await ctx.send(f'{realname} был полностью уничтожен в демонлисте!')
    else:
        await ctx.send('Такого игрока нет в демонлисте!')


@client.command(aliases=['привязать'])
@commands.has_role(editor)
async def connect(ctx, player, member: discord.Member):
    realname = [plr["nick"] for plr in plrs.find() if plr["nick"].lower()==player.lower()]

    if len(realname) > 0:
        realname = realname[0]
        if len([i for i in plrs.find({"nick": realname})]) == 1:
            plrs.update_one({"nick": realname}, {"$set": {"discordtag": member.id}})
            await ctx.send(f"{member.display_name} успешно привязан к своему профилю в демонлисте.")
        else:
            await ctx.send(f"{member.display_name} уже привязан к демомнлисту.")
    else:
        await ctx.send("Такого игрока нет в демонлисте!")

@client.command(aliases=['отвязать'])
@commands.has_role(editor)
async def disconnect(ctx, member: discord.Member):
    player = plrs.find_one({"discordtag": member.id})
    if player != None:
        plrs.update_one({"nick": player["nick"]}, {"$set": {"discordtag": None}})
        await ctx.send(f"{member.display_name} успешно отвязан от демонлиста.")
    else:
        await ctx.send(f"Участник {member.display_name} не привязан к демонлисту!")

@client.command(aliases=['уровень','lvl','лвл'])
async def level(ctx, *, posname = None):
    if posname is not None:
        try:
            lvl = deml.find_one({"position": int(posname)})
        except:
            lvl = deml.find_one({"name": [lvl["name"] for lvl in deml.find() if lvl["name"].lower() == posname.lower()][0]})

        if lvl is not None:
            embed = discord.Embed(title=f"{lvl['name']}", colour=0x6ad96e)
            embed.add_field(name='📑 Позиция:', value=f"**#{lvl['position']}**", inline=False)
            embed.add_field(name='👨‍💻 Автор:', value=f"**{lvl['author']}**", inline=False)
            embed.add_field(name=f'👨‍👨‍👦 Викторы ({len(lvl["victors"])}):', value=',\n'.join([f'**[{vic[0]}]({vic[1]})**' for vic in lvl['victors']]) if len(lvl['victors']) != 0 else 'нет', inline=False)
            embed.set_footer(text="(C) Official Podpol'e Demonlist")
            await ctx.send(embed=embed)
        else:
            await ctx.send('На этой позиции ничего нет!')
    else:
        await ctx.send(f'чо')

async def playercommand(ctx, player):
    passedlevels, proofs = get_passed_levels(player)

    if len(passedlevels) > 0:
        player = player.lower()
        leaderboard = calc_lb()
        leaderboardlower = {i.lower(): leaderboard[i] for i in leaderboard}

        main = 0
        legacy = 0
        passedlevelsf = list()
        for lvl in passedlevels:
            if lvl["position"] <= 50:
                passedlevelsf.append(f"**[{lvl['name']}]({proofs[passedlevels.index(lvl)]})**")
                main += 1
            elif lvl["position"] <= 100:
                passedlevelsf.append(f"[{lvl['name']}]({proofs[passedlevels.index(lvl)]})")
            else:
                passedlevelsf.append(f"*[{lvl['name']}]({proofs[passedlevels.index(lvl)]})*")
                legacy += 1
        passedlevelsf = ", ".join(passedlevelsf)

        embed = discord.Embed(title=f"Профиль {gk(leaderboard)[gk(leaderboardlower).index(player)]}", colour=0x82e0da)
        embed.add_field(name='📊 Место в топе:', value=f"**#{gk(leaderboardlower).index(player) + 1}**", inline=True)
        embed.add_field(name='📈 Поинтов:', value=f"**{round(leaderboardlower[player], 1)}**<:GD_STAR:997218626006425690>", inline=True)
        embed.add_field(name='🧮 Пройдено уровней:', value=f"**{len(passedlevels)}**", inline=True)
        embed.add_field(name='🟥 Main:', value=f"**{main}**", inline=True)
        embed.add_field(name='🟧 Extended:', value=f"**{len(passedlevels) - main - legacy}**", inline=True)
        embed.add_field(name='🟩 Legacy:', value=f"**{legacy}**", inline=True)
        embed.add_field(name='🃏 Хардест:', value=f"**{passedlevels[0]['name']}** by **{passedlevels[0]['author']}**",
                        inline=False)
        if len(passedlevels) < 33:
            embed.add_field(name='📜 Пройденные уровни:', value=passedlevelsf, inline=False)
            embed.set_footer(text="(C) Official Podpol'e Demonlist")

        await ctx.send(embed=embed)
        if len(passedlevels) >= 33:
            embed2 = discord.Embed(title="📜 Пройденные уровни:", description=passedlevelsf, colour=0x4ac4d4)
            embed2.set_footer(text="(C) Official Podpol'e Demonlist")
            await ctx.send(embed=embed2)
    else:
        await ctx.send("Такого игрока нет в топе!")

@client.command(aliases=['profile','игрок','профиль','player'])
async def __player(ctx, player: discord.User):
    plr = plrs.find_one({"discordtag": player.id})
    if plr is not None:
        await playercommand(ctx, plr["nick"])
    else:
        await ctx.send("Этот участник не привязан к демонлисту!")

@__player.error
async def __player_error(ctx, error):
    if isinstance(error, commands.UserNotFound):
        await playercommand(ctx, str(error)[6:-12])
    else:
        print(error)

@client.command(aliases=['stats','стата','игроки','players','leaderboard'])
async def lb(ctx, pg: int = 1):
    leaderboard = calc_lb()
    playersamount = len(leaderboard)
    pages = ceil(playersamount / 10)

    if pg <= pages:
        victors = [key for key in leaderboard.keys()]
        embeds = list()
        for page in range(1, pages + 1):
            places = list()
            for i in range(10 * (page - 1) + 1,
                           (page * 10 if playersamount > 10 and (playersamount - (page - 1) * 10) >= 10 else playersamount) + 1):
                passedlevels = get_passed_levels(victors[i-1])[0]
                places.append(f"**#{i}** **{victors[i-1]}** — {round(leaderboard[victors[i-1]], 1)}p | {len(passedlevels)} <:GD_DEMON:997529124656664697>")
            embed = discord.Embed(title="Офицальный топ игроков Подполья", description="\n\n".join(places), colour=0x766ce5)
            embed.set_footer(text=f"Страница {page}/{pages}. (C) Official Podpol'e Demonlist")
            embeds.append(embed)

        await browse_pages(ctx, pg, pages, embeds)
    else:
        await ctx.send("На этой странице ещё нет уровней!")

@client.command(aliases=['r', 'р', 'рулетка'])
async def roulette(ctx, percent = None):
    if percent == None:
        percent = 0
    if mmbrs.find_one({"discordtag": ctx.author.id}) is None:
        mmbrs.insert_one({"discordtag": ctx.author.id, "curpercent": 0, "roulettelvls": []})
    prevrecord = mmbrs.find_one({"discordtag": ctx.author.id})["curpercent"]
    roulettelvls = [i for i in mmbrs.find_one({"discordtag": ctx.author.id})["roulettelvls"]]
    if percent == "сброс":
        if len(roulettelvls) == 0:
            await ctx.send("чо творишь")
        else:
            await ctx.send(f"Ваша игра в рулетку завершается на {prevrecord}%, спустя {translator.translate(f'{len(roulettelvls)-1} progresses', dest='ru').text if len(roulettelvls) != 0 else '0 уровней =)'}. Вызовите еще раз команду чтоб начать игру!")
            mmbrs.update_one({"discordtag": ctx.author.id}, {"$set": {"curpercent": 0, "roulettelvls": []}})
    elif percent in ["текущий", "тек", "уровень", "лвл"]:
        embed=discord.Embed(title="Текущий уровень",
                            description=f"Уровень #{len(roulettelvls)}: **{roulettelvls[-1]['name']}** by **{roulettelvls[-1]['author']}**. Вам нужно поставить **{prevrecord+1}%**{' или больше.' if prevrecord != 99 else '.'}",
                            colour=0x8533d6)
        embed.set_footer(text="(C) Official Podpol'e Demonlist")
        await ctx.send(embed=embed)
    elif int(percent) > 100 or (int(percent) > 0 and len(roulettelvls) == 0):
        await ctx.send("ты кому пиздиш падла")
    elif int(percent) == 100:
        await ctx.send(f"Вы прошли рулетку демонов! Поздравляю! Всего на вашем пути был{'о' if len(roulettelvls) > 1 else ''} {translator.translate(f'{len(roulettelvls)} levels', dest='ru').text}. Вызовите еще раз команду чтобы начать игру!")
        mmbrs.update_one({"discordtag": ctx.author.id}, {"$set": {"curpercent": 0, "roulettelvls": []}})
    elif int(percent) <= prevrecord and (int(percent) !=0 or len(roulettelvls)):
        await ctx.send(f"Указанный вами процент меньше или равен вашему предыдущему рекорду в {prevrecord}%!")
    else:
        while True:
            lvl = random.choice([i for i in deml.find()])
            if lvl not in roulettelvls:
                break
        roulettelvls.append(lvl)
        mmbrs.update_one({"discordtag": ctx.author.id}, {"$set": {"curpercent": int(percent), "roulettelvls": roulettelvls}})
        embed=discord.Embed(title="Рулетка подпольных уровней",
                        description=f"Уровень #{len(roulettelvls)}: **{lvl['name']}** by **{lvl['author']}**. Вам нужно поставить **{int(percent)+1}%**{' или больше.' if int(percent) != 99 else '.'}",
                        colour=discord.Colour.random())
        embed.set_footer(text="(C) Official Podpol'e Demonlist")
        await ctx.send(embed=embed)

@client.command(aliases=["анекдот", "анек", "anek"])
async def anekdot(ctx):
    parse = "https://www.anekdot.ru/random/anekdot"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.206 (Edition Yx GX)"}

    page = requests.get(parse, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    anekdot = soup.find("div", "text").get_text("\n", strip=True)
    date = soup.find("p", "title").get_text("\n", strip=True)

    embed = discord.Embed(description=anekdot, colour=discord.Colour.random())
    embed.set_author(name="Случайный анекдот", url=parse)
    embed.set_footer(text=f"Дата: {date}. (C) Official Podpol'e Demonlist")

    await ctx.send(embed=embed)

@client.command(aliases=["редис", "radish", "редиска", "редиски"])
async def redis(ctx):
    redis = randimg(random.choice(["смешная редиска", "забавная редиска", "редиска", "редиска", "сок из редиски", "красная редиска"]))

    embed = discord.Embed(title="Случайный редисный", description=redis["title"], colour=discord.Colour.random())
    embed.set_image(url=redis["link"])
    embed.set_footer(text=f"(C) Official Podpol'e Demonlist")

    await ctx.send(embed=embed)

@redis.error
async def redis_error(error, ctx):
    await ctx.send("Произошла неизвестная ошибка =)")

@client.command(aliases=["картинка", "img", "имг"])
async def image(ctx, *, arg):
    redis = randimg(arg)

    embed = discord.Embed(title=f"Случайная картинка по запросу **{arg}**", description=redis["title"], colour=discord.Colour.random())
    embed.set_image(url=redis["link"])
    embed.set_footer(text=f"(C) Official Podpol'e Demonlist")

    await ctx.send(embed=embed)

@image.error
async def image_error(error, ctx):
    await ctx.send("Произошла неизвестная ошибка =)")

client.remove_command('help')
@client.command(aliases=["хелп"])
async def help(ctx, arg=None):
    if arg in ["рулетка", "roulette", "r", "р"]:
        embed1 = discord.Embed(title='?рулетка <рекорд/"сброс">', description='Для того, чтобы начать рулетку, достаточно написать команду `?рулетка`, после чего бот отправит вам уровень, который вы должны будете пройти на 1% или более. Далее вам нужно будет прописать `?рулетка [поставленный вами рекорд]`, и, соответственно, на следующем выпавшем демоне вы уже должны будете поставить рекорд больше предыдущего хотя бы на 1%. Ровно такой же принцип действует и далее, пока вы не дойдете до значения 100.'
                                                                              '\nТак же при желании начать игру с самого начала - вам стоит написать `?рулетка сброс`. Таким образом вы сбросите весь ваш прогресс и сможете начать игру по новой.', colour=0xff4747)
        embed1.set_footer(text=f"(C) Official Podpol'e Demonlist")
        await ctx.send(embed=embed1)
    elif arg is None:
        embed1=discord.Embed(title="📜 Демонлист", description="**P.s.:** [] - обязательный аргумент, <> - необязательный аргумент", colour=0xff4747)
        embed1.set_author(name="Текущие команды:")
        embed1.add_field(name="?dl <страница>",
                        value="```Показывает топ 100 сложнейших демонов, пройденных в Подполье.```",
                        inline=True)
        embed1.add_field(name="?стата <страница>",
                        value="```Показывет топ игроков Подполья относительно поинтов из демонлиста.```",
                        inline=True)
        embed1.add_field(name="?легаси <страница>",
                        value="```Показывает топ уровней, вылетевших из основного топа 100 (сюда прохождения больше не принимаются).```",
                        inline=True)
        embed1.add_field(name="?профиль [ник в листе/тег игрока в дискорде]",
                        value="```Показывает всю информацию об игроке в демонлисте (позицию в топе, все пройденные уровни, хардест демон и т.д.)```",
                        inline=True)
        embed1.add_field(name="?уровень [позиция в листе/название уровня]",
                        value="```Показывает всю информацию об уровне из демонлиста (позицию в топе, кол-во поинтов за прохождение и т.д.)```",
                        inline=True)
        embed1.add_field(name='?рулетка <рекорд/"сброс">',
                        value=f'```Начинает так называемую "рулетку" демонов пройденных в Подполье. Чтобы узнать, как играть - пропишите \n?{ctx.message.content[1:5]} рулетка.```',
                        inline=True)
        embed1.add_field(name='?dlrools',
                         value=f'```Показывает правила для попадания вашего прохождения в демонлист.```',
                         inline=False)
        embed1.set_footer(text=f"Страница 1/2. (C) Official Podpol'e Demonlist")

        embed2 = discord.Embed(title="😜 Приколы", description="**P.s.:** [] - обязательный аргумент, <> - необязательный аргумент", colour=0xff4747)
        embed2.set_author(name="Текущие команды:")
        embed2.add_field(name='?анекдот',
                         value=f'```Выдаёт случайный анекдот с сайта anekdot.ru.```',
                         inline=True)
        embed2.add_field(name='?img [запрос]',
                         value=f'```Выдаёт случайную картинку по запросу из Google картинок.```',
                         inline=True)
        embed2.add_field(name='?редис',
                         value=f'```Выдаёт случайный редис из тех же Google картинок (да, для этого обязательно нужна отдельная команда).```',
                         inline=False)
        embed2.set_footer(text=f"Страница 2/2. (C) Official Podpol'e Demonlist")

        await browse_pages(ctx, 1, 2, [embed1,embed2], False)
    else:
        await ctx.send("чо творишь")

@client.command()
async def dlrools(ctx):
    embed = discord.Embed(title="📕 Правила демонлиста Подполья Гдшеров", colour=0xff4747)
    embed.add_field(name="Правило 1.1", value="```Инсейн демоны и легче - по доверию, но пруфы лишними не будут. На экстрим демоны - видео с кликами. Но если вы не смогли записать ваше прохождение, то всё равно можете попасть в лист, если вы проверенный участник сервера или имеете запись с 55%+ .```", inline=False)
    embed.add_field(name="Правило 1.2", value="```Если редактор демонлиста заподозрил что-либо неладное в пруфе прохождения - он в праве вас допросить, и в случае чего убрать ваши прохождения с демонлиста.```", inline=True)
    embed.add_field(name="Правило 1.3",
                    value="```Если вы использовали различного рода сикрет веи и другие нечестные пути заполучить преимущество в сложности в уровне - ваше прохождение не будет добавлено в демонлист.```", inline=True)
    embed.add_field(name="Правило 1.4", value="```В демонлист вы можете попасть только при наличии 10+ уровня на сервере.```", inline=True)
    embed.set_footer(text=f"(C) Official Podpol'e Demonlist")
    await ctx.send(embed=embed)



client.run(token)
