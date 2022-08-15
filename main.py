# база
import disnake
from disnake.ext import commands, tasks
from simpledemotivators import Demotivator
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

client = commands.Bot(command_prefix=commands.when_mentioned_or('?'), intents=disnake.Intents.all())
converter = commands.MemberConverter()

# монгодб
cluster = MongoClient(mongotok)
deml = cluster["GMDOBOT"]["demonlist"]
plrs = cluster["GMDOBOT"]["players"]
mmbrs = cluster["GMDOBOT"]["members"]
brthds = cluster["GMDOBOT"]["birthdays"]
wkds = cluster["GMDOBOT"]["weekdays"]
pcks = cluster["GMDOBOT"]["demonpacks"]

editor = 927634802096611469
gmdoguild = None
translator = Translator(service_urls=['translate.googleapis.com'])
API_KEY = 'AIzaSyCiet7DWMafTzv-hTelx6pd1JUV_cTQOZE'
SEARCH_ENGINE_ID = '9f1f6320d8ce8bef8'

points = [250, 228, 210, 194, 180, 169, 159, 150, 143, 137, 132, 127.5, 123.6, 120, 117.4, 114, 112.6, 111, 109, 108, 106,
	 105.5, 104, 102.8, 101, 100.1, 98, 97, 96.3, 95, 93.8, 92.5, 91, 90, 88.9, 86.7, 84, 82.5, 80, 78.6, 76.7, 74, 73,
	 71.5, 69.9, 68, 66, 65.4, 64, 62.65, 61, 60, 58.8, 57, 56.5, 55.2, 53.9, 52, 51, 50.1, 48, 47, 46, 45.5, 44,
	 43.4, 42, 41.5, 40.54, 39, 38.7, 37.8, 34, 36.16, 35.3, 34, 33.8, 33.06, 32, 31, 30.9, 30.2, 29.6, 29, 28.3, 27.82,
	 27, 26.6, 26.09, 25.5, 25, 24.5, 24, 23.55, 23, 22.6, 22.1, 21.7, 21.3, 20.9, 20.5, 20, 19.78, 19.4, 19, 18.7,
	 18.38, 18, 17.7, 17.42, 17.1, 16.83, 16.5, 16.2, 16, 15.74, 15.5, 15.2, 15, 14.7, 14.52, 14.3, 14, 13.87, 13.6,
	 13.47, 13.2, 13, 12.9, 12.72]


async def browse_pages(ctx, pg, pages, embeds, more_buttons=True):
	msg = await ctx.edit_original_message(embed=embeds[pg - 1])

	if pages > 1:
		reactionslist = ["⏪", "◀", "▶", "⏩"] if more_buttons else ["◀", "▶"]
		for i in reactionslist:
			await msg.add_reaction(i)

		while True:
			try:
				reaction, user = await client.wait_for('reaction_add', timeout=60.0,
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
				await ctx.edit_original_message(embed=embeds[pg - 1])


def get_passed_levels(player):
	passedlevels = []
	for lvl in deml.find():
		for victor in lvl["victors"]:
			if victor[0].lower() == player.lower():
				lvl["proof"] = victor[1]
				passedlevels.append(lvl)
				break
	passedlevels.sort(key=lambda x: x['position'])
	return passedlevels

def calc_lb():
	victors = {}
	for lvl in deml.find():
		for victor in lvl["victors"]:
			if victor[0] not in victors.keys():
				victors[victor[0]] = [points[lvl["position"] - 1] if lvl["position"] <= 100 else 3, 0]
			else:
				victors[victor[0]][0] += points[lvl["position"] - 1] if lvl["position"] <= 100 else 3

	for victor in victors:
		if victors[victor][0] >= 9:
			for item in pcks.find():
				passedlevels = [i["name"] for i in get_passed_levels(victor)]
				if len(item["levels"]) == len(list(filter(lambda i: i in passedlevels, item["levels"]))):
					victors[victor][1] += 1
					victors[victor][0] += item["points"]
	return {k: v for k, v in sorted(victors.items(), reverse=True, key=lambda item: item[1])}

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
	global gmdoguild
	checkday.start()
	gmdoguild = client.get_guild(886678201387073607)
	await client.change_presence(activity=disnake.Game(name="лучший сервер!"))
	print("Бот запущен!")


@client.event
async def on_message(message):
	gmobot = get(client.get_all_members(), id=993896677092106240)
	emojis = {e.name: str(e) for e in gmdoguild.emojis}
	if gmobot.mention in message.content:
		await message.channel.send(emojis["VK_WTF"])
	if message.channel.id == 997728986807406652 and message.author.id != 993896677092106240:
		if len(message.content) == 5 and message.content[2] == ".":
			if brthds.find_one({"member": message.author.id}) is None:
				brthds.insert_one(
					{"member": message.author.id, "day": int(message.content[:2]), "month": int(message.content[3:]),
					 "pozdravlen": False})
			else:
				brthds.update_one({"member": message.author.id},
								  {"$set": {"day": int(message.content[:2]), "month": int(message.content[3:])}})
			await message.add_reaction("✅")
		else:
			msg = await message.channel.send("чо")
			await asyncio.sleep(3)
			await message.delete()
			await msg.delete()
	print(message.content)
	await client.process_commands(message)


@tasks.loop(seconds=60)
async def checkday():
	moscow_time = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
	birthchannel = client.get_channel(886678288704090193)
	chat = client.get_channel(886680631239663707)
	imeninnikrole = get(gmdoguild.roles, id=1001748951529164810)

	if moscow_time.hour >= 7:
		for birth in brthds.find():
			imenin = await client.fetch_user(birth["member"])
			imeninnik = gmdoguild.get_member(imenin.id)
			if birth["day"] == moscow_time.day and birth["month"] == moscow_time.month:
				if not birth["pozdravlen"]:
					parse = "https://pozdraff.ru/pozdravleniya/5?for=man&count=2"
					headers = {
						"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.206 (Edition Yx GX)"}

					page = requests.get(parse, headers=headers)
					soup = BeautifulSoup(page.content, "html.parser")
					pozdravlenie = soup.find("p", "lead greeting").get_text("\n", strip=True)

					embed = disnake.Embed(colour=0xfff94a)
					embed.set_image(randimg("открытки с днём рождения забавные")["link"])

					await birthchannel.send(f"У {imenin.mention} сегодня день рождения! ПОЗДРАВЛЯЕМ! 🎉🎊\n{pozdravlenie}", embed=embed)
					await imeninnik.add_roles(imeninnikrole)
					brthds.update_one({"member": imenin.id}, {"$set": {"pozdravlen": True}})
			else:
				brthds.update_one({"member": imenin.id}, {"$set": {"pozdravlen": False}})
				await imeninnik.remove_roles(imeninnikrole)

	if moscow_time.weekday() == 4:
		if not wkds.find_one({"pisya": True})["friday"]:
			await chat.send("УРА!!!!! ПЯТНИЦА!!!!!")
			await chat.send(randimg("пятница открытки")["link"])
			wkds.update_one({"pisya": True}, {"$set": {"friday": True}})
	else:
		wkds.update_one({"pisya": True}, {"$set": {"friday": False}})


@client.slash_command(name='дл',
					  description='Показывает топ 100 сложнейших демонов, пройденных в Подполье.',
					  options=[disnake.Option("страница", description="Номер страницы", required=False,
											  type=disnake.OptionType.integer)])
async def дл(inter, страница: int = 1):
	await inter.response.defer()
	emojis = {e.name: str(e) for e in gmdoguild.emojis}
	if random.randint(1, 10) == 1:
		await inter.edit_original_message(content="ХУЙ ТЕБЕ А НЕ ДЕМОНЛИСТ")
	else:
		lvlsamount = len([lvl for lvl in deml.find()])
		pages = ceil(lvlsamount / 10) if lvlsamount <= 120 else 12
		if страница <= pages:
			embeds = list()
			for page in range(1, pages + 1 if lvlsamount <= 120 else 13):
				embed = disnake.Embed(title="Офицальный топ игроков Подполья", colour=0x766ce5,
									  description="**Место | Название | Автор | Поинты**")
				for i in range(10 * (page - 1) + 1, (page * 10 if lvlsamount > 10 and (
						lvlsamount - (page - 1) * 10) >= 10 else lvlsamount) + 1):
					lvl = deml.find_one({"position": i})
					embed.add_field(
						name=f"""**#{i}** | **{lvl["name"]}** by **{lvl["author"]}** | {points[i - 1]}{emojis['GD_STAR']}\n""",
						value=f"Victors: {', '.join([f'**[{vic[0]}]({vic[1]})**' if vic[1] != None else vic[0] for vic in lvl['victors']]) if len(lvl['victors']) != 0 else 'нет'}",
						inline=False)
				embed.set_footer(text=f"Страница {page}/{pages}. (C) Official Podpol'e Demonlist")
				embeds.append(embed)

			await browse_pages(inter, страница, pages, embeds)
		else:
			await inter.edit_original_message(content="На этой странице ещё нет уровней ❌")


@client.slash_command(name='легаси',
					  description='Показывает топ уровней, вылетевших из основного топа 100 (сюда прохождения больше не принимаются).',
					  options=[disnake.Option("страница", description="Номер страницы", required=False,
											  type=disnake.OptionType.integer)])
async def легаси(inter, страница: int = 1):
	await inter.response.defer()
	emojis = {e.name: str(e) for e in gmdoguild.emojis}
	lvlsamount = len([lvl for lvl in deml.find()])
	if lvlsamount > 100:
		pages = ceil((lvlsamount - 120) / 10)
		if страница <= pages:
			embeds = list()
			for page in range(13, pages + 13):
				embed = disnake.Embed(title="Офицальный топ игроков Подполья", colour=0x766ce5,
									  description=f"*За каждый уровень из легаси даётся 3*{emojis['GD_STAR']}\n**Место | Название | Автор**")
				for i in range(10 * (page - 1) + 1, (page * 10 if lvlsamount > 10 and (
						lvlsamount - (page - 1) * 10) >= 10 else lvlsamount) + 1):
					lvl = deml.find_one({"position": i})
					embed.add_field(name=f"""**#{i}** | **{lvl["name"]}** by **{lvl["author"]}**\n""",
									value=f"Victors: {', '.join([f'**[{vic[0]}]({vic[1]})**' if vic[1] != None else vic[0] for vic in lvl['victors']]) if len(lvl['victors']) != 0 else 'нет'}",
									inline=False)
				embed.set_footer(text=f"Страница {page - 12}/{pages}. (C) Official Podpol'e Demonlist")
				embeds.append(embed)

			await browse_pages(inter, страница, pages, embeds)
		else:
			await inter.edit_original_message(content="На этой странице ещё нет уровней ❌")
	else:
		await inter.edit_original_message(content="мужик легаси не существует")


# ГОТОВО
@client.command(aliases=['add', 'добавить', 'добавитьуровень'])
@commands.has_role(editor)
async def addlevel(ctx, lvlname, lvlauthor, pos: int):
	lvlsamount = len([lvl for lvl in deml.find()])
	if pos <= lvlsamount + 1:
		for name in [i["name"] for i in deml.find() if i["position"] >= int(pos)]:
			deml.update_one({"name": name}, {"$inc": {"position": 1}})
		deml.insert_one({"name": lvlname, "author": lvlauthor, "victors": [], "position": int(pos)})
		if pos == 1:
			await ctx.send(
				f"{lvlname} добавлен на {pos} позицию, сместив при этом {deml.find_one({'position': pos + 1})['name']} на вторую строчку листа ✅")
		elif pos == lvlsamount + 1:
			await ctx.send(
				f"{lvlname} добавлен на {pos} позицию, то есть на последнюю, ничего при этом не обогнав и не сместив 😜")
		else:
			await ctx.send(
				f"{lvlname} добавлен на {pos} позицию, выше {deml.find_one({'position': pos + 1})['name']}, но ниже {deml.find_one({'position': pos - 1})['name']} ✅")
	else:
		await ctx.send(
			f'Мужик, ты чего? В демонлисте пока что всего {lvlsamount} уровней, а ты собрался на {pos} место что-то ставить. Подумай об этом на досуге ❌')


# ГОТОВО
@client.command(aliases=['del', 'remove', 'удалитьуровень', 'удалить'])
@commands.has_role(editor)
async def dellevel(ctx, pos: int):
	lvl = deml.find_one({"position": pos})
	if lvl is not None:
		deml.delete_one({"position": pos})
		for name in [i["name"] for i in deml.find() if i["position"] > pos]:
			deml.update_one({"name": name}, {"$inc": {"position": -1}})
		await ctx.send(f"{lvl['name']} удалён. GG ✅")
	else:
		await ctx.send('Такого уровня не существует ❌')

# ГОТОВО
@client.command(aliases=['furry'])
async def фурри(ctx):
	await ctx.send(file=disnake.File('vjlink.gif'))

# ГОТОВО
@client.command(aliases=['victor', 'виктор', 'добавитьвиктора'])
@commands.has_role(editor)
async def addvictor(ctx, pos: int, victor, video=None):
	lvl = deml.find_one({"position": pos})
	if lvl is not None:
		victors = lvl["victors"]
		if victor.lower() not in [i[0].lower() for i in victors]:
			victors.append([victor, video])
			deml.update_one({"position": pos}, {"$set": {"victors": victors}})
			if plrs.find_one({"nick": victor}) is None:
				plrs.insert_one({"nick": victor, "discordtag": None})
			await ctx.send(f"{victor} добавлен к викторам {lvl['name']} ✅")
		else:
			await ctx.send(f"{victor} уже является виктором уровня {lvl['name']} ❌")
	else:
		await ctx.send('Такого уровня не существует ❌')


# ГОТОВО
@client.command()
@commands.has_role(editor)
async def delvictor(ctx, pos: int, vctr):
	lvl = deml.find_one({"position": pos})
	if lvl is not None:
		victors = lvl["victors"]
		realname = None
		a = -1
		for victor in victors:
			a += 1
			if victor[0].lower() == vctr.lower():
				realname = victor[0]
				victors.pop(a)
				deml.update_one({"position": lvl["position"]}, {"$set": {"victors": victors}})
				break

		await ctx.send(f"{realname} удалён из викторов {lvl['name']} ✅")

		a = 0
		for l in deml.find():
			for victor in l["victors"]:
				if victor[0].lower() == vctr.lower():
					a += 1
					break
		if a == 0:
			plrs.delete_one({"nick": realname})
	else:
		await ctx.send('Такого уровня не существует ❌')


# ГОТОВО
@client.command(aliases=['proof', 'пруф', 'добавитьпруф'])
@commands.has_role(editor)
async def addproof(ctx, pos: int, victor, video):
	lvl = deml.find_one({"position": pos})
	if lvl is not None:
		victors = lvl["victors"]
		vict = [vic for vic in victors if vic[0].lower() == victor.lower()]
		if len(vict) > 0:
			vict = vict[0]
			victors.pop(victors.index(vict))
			victors.append([victor, video])
			deml.update_one({"position": pos}, {"$set": {"victors": victors}})
			await ctx.send(f"Пруф игрока {vict[0]} на уровень {lvl['name']} успешно добавлен ✅")
		else:
			await ctx.send('Данный игрок не является виктором этого уровня ❌')
	else:
		await ctx.send('Такого уровня не существует ❌')


# ГОТОВО
@client.command(aliases=['удалитьпруф'])
@commands.has_role(editor)
async def delproof(ctx, pos: int, victor):
	lvl = deml.find_one({"position": pos})
	if lvl is not None:
		victors = lvl["victors"]
		vict = [vic for vic in victors if vic[0].lower() == victor.lower()]
		if len(vict) > 0:
			vict = vict[0]
			if vict[1] is not None:
				victors.pop(victors.index(vict))
				victors.append([victor, None])
				deml.update_one({"position": pos}, {"$set": {"victors": victors}})
				await ctx.send(f"Пруф игрока {vict[0]} на уровень {lvl['name']} удалён ✅")
			else:
				await ctx.send('У этого игрока итак не привязаны никакие пруфы к этому уровню ❌')
		else:
			await ctx.send('Данный игрок не является виктором этого уровня ❌')
	else:
		await ctx.send('Такого уровня не существует ❌')


# ГОТОВО
@client.command(aliases=['изменить', 'изменитьуровень'])
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
			await ctx.send(f'Уровень {lvl["name"]} перенесён на позицию {new_pos} с позиции {pos} ✅')
		else:
			await ctx.send('чо творишь')
	else:
		await ctx.send('Такого уровня не существует ❌')


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
			a += 1
			if victor[0].lower() == player.lower():
				isplayerexists = True
				realname = victor[0]
				victors.pop(a)
				deml.update_one({"position": lvl["position"]}, {"$set": {"victors": victors}})
				if len(deml.find_one({"position": lvl["position"]})["victors"]) == 0:
					deml.delete_one({"position": lvl["position"]})
					for name in [i["name"] for i in deml.find() if i["position"] > lvl["position"]]:
						deml.update_one({"name": name}, {"$inc": {"position": -1}})
				break
	if isplayerexists:
		plrs.delete_one({"nick": realname})
		await ctx.send(f'{realname} был полностью уничтожен в демонлисте ✅')
	else:
		await ctx.send('Такого игрока нет в демонлисте ❌')


@client.command(aliases=['привязать'])
@commands.has_role(editor)
async def connect(ctx, player, member: disnake.Member):
	realname = [plr["nick"] for plr in plrs.find() if plr["nick"].lower() == player.lower()]

	if len(realname) > 0:
		realname = realname[0]
		if len([i for i in plrs.find({"nick": realname})]) == 1:
			plrs.update_one({"nick": realname}, {"$set": {"discordtag": member.id}})
			await ctx.send(f"{member.display_name} успешно привязан к своему профилю в демонлисте ✅")
		else:
			await ctx.send(f"{member.display_name} уже привязан к демомнлисту ❌")
	else:
		await ctx.send("Такого игрока нет в демонлисте ❌")


@client.command(aliases=['отвязать'])
@commands.has_role(editor)
async def disconnect(ctx, member: disnake.Member):
	player = plrs.find_one({"discordtag": member.id})
	if player != None:
		plrs.update_one({"nick": player["nick"]}, {"$set": {"discordtag": None}})
		await ctx.send(f"{member.display_name} успешно отвязан от демонлиста ✅")
	else:
		await ctx.send(f"Участник {member.display_name} не привязан к демонлисту ❌")

@client.slash_command(name='паки',
					  description='Показывает список паков с уровнями из демонлиста',
					  options=[disnake.Option("страница", description="Номер страницы", required=False,
											  type=disnake.OptionType.integer)]
					  )
async def паки(inter, страница: int = 1):
	await inter.response.defer()
	emojis = {e.name: str(e) for e in gmdoguild.emojis}

	packs = [f"{emojis['VK_GRUST']} Temple Пак", f"{emojis['VK_KRUT']} OLD NC Пак", f"{emojis['VK_CLOWN']} CraZy Пак", f"{emojis['VK_glasses']} Sonic Пак", f"{emojis['VK_SHOCK']} SW Пак", f"{emojis['VK_XblX']} Фановый Пак", f"{emojis['VK_EDY']} Пак уровней с быстрым темпом", f"{emojis['VK_GAMER']} XL Пак", f"{emojis['Cube_Angara']} Пак Ангараривера", f"{emojis['scary']} Кансерный Пак", f"🇷🇺 РК Пак", f"{emojis['GD_DEMONSLAYER']} Хелл Пак"]
	player = plrs.find_one({"discordtag": inter.author.id})
	embeds = list()
	pages = ceil(len(packs) / 9)

	if player != None:
		passedlevels=list()
		for j in range(len([q for q in pcks.find()])):
			item = pcks.find_one({"id": j})
			passedlevels.extend([i for i in item["levels"] if player["nick"] in [i[0] for i in deml.find_one({"name": i})["victors"]]])
	for page in range(1, pages + 1):
		if player != None:
			embed = disnake.Embed(title="Демон-паки", description=f"Пока что вы прошли всего **{translator.translate(f'{len(passedlevels)} levels', dest='ru').text if len(passedlevels) > 0 else '0 уровней'}** из паков.\n`P.S.` ***Название уровня жирным шрифтом*** - пройденный вами уровень.", colour=0x766ce5)
		else:
			embed = disnake.Embed(title="Демон-паки", colour=0x766ce5)
		for j in range(9 * (page - 1), page * 9 if len(packs) > 9 and (len(packs) - (page - 1) * 9) >= 9 else len(packs)):
			item = pcks.find_one({"id": j})
			if player != None:
				passedlevels2 = [i for i in item["levels"] if player["nick"] in [i[0] for i in deml.find_one({"name": i})["victors"]]]
				embed.add_field(name=f"""{packs[item["id"]]}{' ✅' if len(passedlevels2) == len(item["levels"]) else ''}\n(+{item["points"]}{emojis['GD_STAR']} за 100%)""",
								value='Уровни: ' + ", ".join([f"***{i}***" if i in passedlevels2 else i for i in item["levels"]]) + f"\n`Пройденно {round(len(passedlevels2)*100/len(item['levels']))}%/100%`", inline=True)
			else:
				embed.add_field(name=packs[item["id"]] + f'\n(+{item["points"]}{emojis["GD_STAR"]} за 100%)', value=", ".join(item["levels"]), inline=True)
		embed.set_footer(text=f"Страница {page}/{pages}. (C) Official Podpol'e Demonlist")
		embeds.append(embed)

	await browse_pages(inter, страница, pages, embeds)
	await inter.edit_original_message(embed=embed)

@client.slash_command(name='уровень',
					  description='Показывает всю информацию об игроке в демонлисте.',
					  options=[disnake.Option("уровень",
											  description="Можно указать как и позицию уровня, так и его название",
											  required=True, type=disnake.OptionType.string)])
async def уровень(inter, *, уровень=None):
	await inter.response.defer()
	emojis = {e.name: str(e) for e in gmdoguild.emojis}
	if уровень is not None:
		try:
			lvl = deml.find_one({"position": int(уровень)})
		except:
			lvlname = [lvl["name"] for lvl in deml.find() if lvl["name"].lower() == уровень.lower()]
			if len(lvlname) > 0:
				lvl = deml.find_one({"name": lvlname[0]})
			else:
				lvl = None

		if lvl is not None:
			print(lvl["position"])
			embed = disnake.Embed(title=lvl['name'] + f' ({points[lvl["position"] -1]}{emojis["GD_STAR"]})' if lvl["position"] <= 120 else lvl['name'] + f' (3 {emojis["GD_STAR"]})', colour=0x6ad96e)
			embed.add_field(name='📑 Позиция:', value=f"**#{lvl['position']}**", inline=False)
			embed.add_field(name='👨‍💻 Автор:', value=f"**{lvl['author']}**", inline=False)
			embed.add_field(name=f'👨‍👨‍👦 Викторы ({len(lvl["victors"])}):',
							value=', '.join([f'**[{vic[0]}]({vic[1]})**' if vic[1] != None else f'**{vic[0]}**' for vic in lvl['victors']]) if len(lvl['victors']) != 0 else 'нет', inline=False)
			embed.set_footer(text="(C) Official Podpol'e Demonlist")
			await inter.edit_original_message(embed=embed)
		else:
			await inter.edit_original_message(content='(netu takova)')
	else:
		await inter.edit_original_message(content=f'чо')


@client.slash_command(name='профиль',
					  description='Показывает всю информацию об игроке в демонлисте.',
					  options=[disnake.Option("игрок",
											  description="Можно указать как и тег игрока в дискорде, так и его ник в листе",
											  required=False)])
async def профиль(inter, игрок: disnake.User = None):
	await inter.response.defer()
	emojis = {e.name: str(e) for e in gmdoguild.emojis}
	chzh = False
	if игрок == None:
		player = plrs.find_one({"discordtag": inter.author.id})
		if player is not None:
			player = player["nick"]
		else:
			player = None
			chzh = True
	else:
		# говнокод космических масштабов
		try:
			player = await converter.convert(inter, игрок[3:-1])
		except:
			try:
				player = await converter.convert(inter, игрок)
			except:
				player = игрок
		if player != игрок:
			player = plrs.find_one({"discordtag": player.id})
			if player is not None:
				player = player["nick"]

	if player is not None:
		passedlevels = get_passed_levels(player)

		if len(passedlevels) > 0:
			player = player.lower()
			leaderboard = calc_lb()
			leaderboardlower = {i.lower(): leaderboard[i] for i in leaderboard}

			main = 0
			legacy = 0
			passedlevelsf = list()
			for lvl in passedlevels:
				if lvl["position"] <= 50:
					passedlevelsf.append(f"**[{lvl['name']}]({lvl['proof']})**" if lvl['proof'] != None else f"**{lvl['name']}**")
					main += 1
				elif lvl["position"] <= 100:
					passedlevelsf.append(f"[{lvl['name']}]({lvl['proof']})" if lvl['proof'] != None else lvl['name'])
				else:
					passedlevelsf.append(f"*[{lvl['name']}]({lvl['proof']})*" if lvl['proof'] != None else f"*{lvl['name']}*")
					legacy += 1
			passedlevelsf = ", ".join(passedlevelsf)

			embed = disnake.Embed(title=f"Профиль {gk(leaderboard)[gk(leaderboardlower).index(player)]} (**{round(leaderboardlower[player][0], 1)}**{emojis['GD_STAR']})",
								  colour=0x82e0da)
			embed.add_field(name='📊 Место в топе:', value=f"**#{gk(leaderboardlower).index(player) + 1}**",
							inline=True)
			embed.add_field(name='🧮 Пройдено уровней:', value=f"**{len(passedlevels)}**", inline=True)
			embed.add_field(name='📁 Пройдено паков:', value=f"**{leaderboardlower[player][1]}**", inline=True)
			embed.add_field(name='🟥 Main:', value=f"**{main}**", inline=True)
			embed.add_field(name='🟧 Extended:', value=f"**{len(passedlevels) - main - legacy}**", inline=True)
			embed.add_field(name='🟩 Legacy:', value=f"**{legacy}**", inline=True)
			embed.add_field(name='🃏 Хардест:',
							value=f"**{passedlevels[0]['name']}** by **{passedlevels[0]['author']}**",
							inline=False)
			if len(passedlevelsf) < 999:
				embed.add_field(name='📜 Пройденные уровни:', value=passedlevelsf, inline=False)
				embed.set_footer(text="(C) Official Podpol'e Demonlist")
			msg = await inter.edit_original_message(embed=embed)
			if len(passedlevelsf) >= 999:
				embed2 = disnake.Embed(title="📜 Пройденные уровни:", description=passedlevelsf, colour=0x4ac4d4)
				embed2.set_footer(text="(C) Official Podpol'e Demonlist")
				await msg.channel.send(embed=embed2)
		else:
			if chzh:
				await inter.edit_original_message(content="Ваш аккаунт в дискорде не привязан к профилю в демонлисте ❌")
			else:
				await inter.edit_original_message(content="Такого игрока нет в топе ❌")
	else:
		await inter.edit_original_message(content="Этот участник не привязан к демонлисту ❌")


@client.slash_command(name='стата',
					  description='Показывет топ игроков Подполья относительно поинтов.',
					  options=[disnake.Option("страница", description="Номер страницы", required=False,
											  type=disnake.OptionType.integer)])
async def стата(inter, страница: int = 1):
	await inter.response.defer()
	emojis = {e.name: str(e) for e in gmdoguild.emojis}
	leaderboard = calc_lb()
	playersamount = len(leaderboard)
	pages = ceil(playersamount / 10)

	if страница <= pages:
		victors = [key for key in leaderboard.keys()]
		embeds = list()
		for page in range(1, pages + 1):
			places = list()
			for i in range(10 * (page - 1) + 1,
						   (page * 10 if playersamount > 10 and (
								   playersamount - (page - 1) * 10) >= 10 else playersamount) + 1):
				passedlevels = get_passed_levels(victors[i - 1])
				places.append(
					f"**#{i}** **{victors[i - 1]}** — {round(leaderboard[victors[i - 1]][0], 1)}{emojis['GD_STAR']} | {len(passedlevels)} {emojis['GD_DEMON']}")
			embed = disnake.Embed(title="Офицальный топ игроков Подполья", description="\n\n".join(places),
								  colour=0x766ce5)
			embed.set_footer(text=f"Страница {page}/{pages}. (C) Official Podpol'e Demonlist")
			embeds.append(embed)

		await browse_pages(inter, страница, pages, embeds)
	else:
		await inter.edit_original_message(content="На этой странице ещё нет уровней ❌")


@client.slash_command(name='рулетка',
					  description='Начинает "рулетку" демонов. Пишите /хелп рулетка - чтобы научиться играть.',
					  options=[disnake.Option('рекорд',
											  description="Поставленный рекорд. Для сброса рулетки 'сброс', либо 'тек' для просмотра предыдущего рекорда.",
											  required=False, type=disnake.OptionType.string)])
async def рулетка(inter, рекорд=None):
	await inter.response.defer()
	if рекорд == None:
		рекорд = 0
	if mmbrs.find_one({"discordtag": inter.author.id}) is None:
		mmbrs.insert_one({"discordtag": inter.author.id, "curpercent": 0, "roulettelvls": []})
	prevrecord = mmbrs.find_one({"discordtag": inter.author.id})["curpercent"]
	roulettelvls = [i for i in mmbrs.find_one({"discordtag": inter.author.id})["roulettelvls"]]
	if рекорд == "сброс":
		if len(roulettelvls) == 0:
			await inter.edit_original_message(content="чо творишь")
		else:
			await inter.edit_original_message(
				content=f"Ваша игра в рулетку завершается на {prevrecord}%, спустя {translator.translate(f'{len(roulettelvls) - 1} progresses', dest='ru').text if len(roulettelvls) > 1 else '0 прогрессов =)'}. Вызовите еще раз команду чтоб начать игру!")
			mmbrs.update_one({"discordtag": inter.author.id}, {"$set": {"curpercent": 0, "roulettelvls": []}})
	elif рекорд in ["текущий", "тек", "уровень", "лвл"]:
		embed = disnake.Embed(title="Текущий уровень",
							  description=f"Уровень #{len(roulettelvls)}: **{roulettelvls[-1]['name']}** by **{roulettelvls[-1]['author']}** (Топ {roulettelvls[-1]['position']} в листе).\nВам нужно поставить **{prevrecord + 1}%**{' или больше.' if prevrecord != 99 else '.'}",
							  colour=0x8533d6)
		embed.set_footer(text="(C) Official Podpol'e Demonlist")
		await inter.edit_original_message(embed=embed)
	elif int(рекорд) > 100 or (int(рекорд) > 0 and len(roulettelvls) == 0):
		await inter.edit_original_message(content="ты кому пиздиш падла")
	elif int(рекорд) == 100:
		await inter.edit_original_message(
			content=f"Вы прошли рулетку демонов! Поздравляю! Всего на вашем пути был{'о' if len(roulettelvls) > 1 else ''} {translator.translate(f'{len(roulettelvls)} levels', dest='ru').text if len(roulettelvls) > 0 else '0 уровней =)'}. Вызовите еще раз команду чтобы начать игру!")
		mmbrs.update_one({"discordtag": inter.author.id}, {"$set": {"curpercent": 0, "roulettelvls": []}})
	elif int(рекорд) <= prevrecord and (int(рекорд) != 0 or len(roulettelvls)):
		await inter.edit_original_message(
			content=f"Указанный вами процент меньше или равен вашему предыдущему рекорду в {prevrecord}% ❌")
	else:
		while True:
			lvl = random.choice([i for i in deml.find()])
			if lvl not in roulettelvls:
				break
		roulettelvls.append(lvl)
		mmbrs.update_one({"discordtag": inter.author.id},
						 {"$set": {"curpercent": int(рекорд), "roulettelvls": roulettelvls}})
		embed = disnake.Embed(title="Рулетка подпольных уровней",
							  description=f"Уровень #{len(roulettelvls)}: **{lvl['name']}** by **{lvl['author']}** (Топ {lvl['position']} в листе).\nВам нужно поставить **{int(рекорд) + 1}%**{' или больше.' if int(рекорд) != 99 else '.'}",
							  colour=disnake.Colour.random())
		embed.set_footer(text="(C) Official Podpol'e Demonlist")
		await inter.edit_original_message(embed=embed)


@client.slash_command(name='анекдот',
					  description='Выдаёт случайный анекдот с сайта anekdot.ru.')
async def анекдот(inter):
	await inter.response.defer()
	parse = "https://www.anekdot.ru/random/anekdot"
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.206 (Edition Yx GX)"}

	page = requests.get(parse, headers=headers)
	soup = BeautifulSoup(page.content, "html.parser")
	anekdot = soup.find("div", "text").get_text("\n", strip=True)
	date = soup.find("p", "title").get_text("\n", strip=True)

	embed = disnake.Embed(description=anekdot, colour=disnake.Colour.random())
	embed.set_author(name="Случайный анекдот", url=parse)
	embed.set_footer(text=f"Дата: {date}. (C) Official Podpol'e Bot")

	await inter.edit_original_message(embed=embed)


@client.slash_command(name='редис',
					  description='Выдаёт случайный редис из тех же Google картинок.')
async def редис(inter):
	await inter.response.defer()
	redis = randimg(random.choice(["смешная редиска", "забавная редиска", "редиска", "редиска", "красная редиска"]))

	embed = disnake.Embed(title="Случайный редисный", description=redis["title"], colour=disnake.Colour.random())
	embed.set_image(url=redis["link"])
	embed.set_footer(text=f"(C) Official Podpol'e Bot")

	await inter.edit_original_message(embed=embed)


@client.slash_command(name='имг',
					  description='Выдаёт случайную картинку по запросу из Google картинок.',
					  options=[disnake.Option('запрос', description="Запрос, по которому нужно будет искать картинку.",
											  required=True, type=disnake.OptionType.string)])
async def имг(inter, *, запрос):
	await inter.response.defer()
	redis = randimg(запрос)

	embed = disnake.Embed(title=f"Случайная картинка по запросу **{запрос}**", description=redis["title"],
						  colour=disnake.Colour.random())
	embed.set_image(url=redis["link"])
	embed.set_footer(text=f"(C) Official Podpol'e Bot")

	await inter.edit_original_message(embed=embed)


@client.slash_command(name='хелп',
					  description='Помощь по командам бота.',
					  options=[disnake.Option('страница',
											  description="Номер страницы. Для просмотра помощи по рулетке, укажите здесь 'рулетка' (без кавычек).",
											  required=False, type=disnake.OptionType.string)])
async def хелп(inter, страница=None):
	await inter.response.defer()
	if страница in ["рулетка", "roulette", "r", "р"]:
		embed1 = disnake.Embed(title='/рулетка <рекорд/"сброс"/"тек">',
							   description='`1.` Для того, чтобы начать рулетку, достаточно написать команду `/рулетка`, после чего бот отправит вам уровень, который вы должны будете пройти на 1% или более.\n`2.` Далее вам нужно будет прописать `/рулетка [поставленный вами рекорд]`, и, соответственно, на следующем выпавшем демоне вы уже должны будете поставить рекорд больше предыдущего хотя бы на 1%.\n`3.` Ровно такой же принцип действует и далее, пока вы не дойдете до значения 100.'
										   '\n\n**Для того, чтобы сбросить игру - напишите `/рулетка сброс`**\n**Для того, чтобы узнать текущий уровень, на котором вам нужно поставить прогресс - напишите `/рулетка текущий`**',
							   colour=0xff4747)
		embed1.set_footer(text=f"(C) Official Podpol'e Bot")
		await inter.edit_original_message(embed=embed1)
	elif страница in ["1", "2", None]:
		if страница in ["1", "2"]:
			страница = int(страница)
		else:
			страница = 1
		embed1 = disnake.Embed(title="📜 Демонлист",
							   description="**P.s.:** [] - обязательный аргумент, <> - необязательный аргумент",
							   colour=0xff4747)
		embed1.set_author(name="Текущие команды:")
		embed1.add_field(name="/дл <страница>",
						 value="```Показывает топ 100 сложнейших демонов, пройденных в Подполье.```",
						 inline=True)
		embed1.add_field(name="/стата <страница>",
						 value="```Показывет топ игроков Подполья относительно поинтов из демонлиста.```",
						 inline=True)
		embed1.add_field(name="/легаси <страница>",
						 value="```Показывает топ уровней, вылетевших из основного топа 100.```",
						 inline=True)
		embed1.add_field(name="/профиль <ник в листе/тег игрока в дискорде>",
						 value="```Показывает всю информацию об игроке в демонлисте (позицию в топе, все пройденные уровни, хардест демон и т.д.)```",
						 inline=True)
		embed1.add_field(name="/уровень [позиция в листе/название уровня]",
						 value="```Показывает всю информацию об уровне из демонлиста (позицию в топе, кол-во поинтов за прохождение и т.д.)```",
						 inline=True)
		embed1.add_field(name='/рулетка <рекорд/"сброс"/"тек">',
						 value=f'```Начинает так называемую "рулетку" демонов пройденных в Подполье. Чтобы узнать, как играть - пропишите \n/хелп рулетка.```',
						 inline=True)
		embed1.add_field(name='/паки <страница>',
						 value=f'```Показывает список имеющихся на данный момент паков с уровнями из демонлиста.```',
						 inline=True)
		embed1.add_field(name='/длправила',
						 value=f'```Показывает правила для попадания вашего прохождения в демонлист.```',
						 inline=True)
		embed1.set_footer(text=f"Страница 1/2. (C) Official Podpol'e Bot")

		embed2 = disnake.Embed(title="😜 Приколы",
							   description="**P.s.:** [] - обязательный аргумент, <> - необязательный аргумент",
							   colour=0xff4747)
		embed2.set_author(name="Текущие команды:")
		embed2.add_field(name='/анекдот',
						 value=f'```Выдаёт случайный анекдот с сайта anekdot.ru.```',
						 inline=True)
		embed2.add_field(name='/имг [запрос]',
						 value=f'```Выдаёт случайную картинку по запросу из Google картинок.```',
						 inline=True)
		embed2.add_field(name='/редис',
						 value=f'```Выдаёт случайный редис из тех же Google картинок (да, для этого обязательно нужна отдельная команда).```',
						 inline=True)
		embed2.set_footer(text=f"Страница 2/2. (C) Official Podpol'e Bot")

		await browse_pages(inter, страница, 2, [embed1, embed2], False)
	else:
		await inter.edit_original_message(content="чо творишь")


@client.slash_command(name='длправила',
					  description='Показывает правила для попадания вашего прохождения в демонлист.', )
async def длправила(inter):
	await inter.response.defer()
	embed = disnake.Embed(title="📕 Правила демонлиста Подполья Гдшеров", colour=0xff4747)
	embed.add_field(name="Правило 1.1",
					value="```Инсейн демоны и легче - по доверию, но пруфы лишними не будут. На экстрим демоны - видео с кликами. Но если вы не смогли записать ваше прохождение, то всё равно можете попасть в лист, если вы проверенный участник сервера или имеете запись с 55%+ .```",
					inline=False)
	embed.add_field(name="Правило 1.2",
					value="```Если редактор демонлиста заподозрил что-либо неладное в пруфе прохождения - он в праве вас допросить, и в случае чего убрать ваши прохождения с демонлиста.```",
					inline=True)
	embed.add_field(name="Правило 1.3",
					value="```Если вы использовали различного рода сикрет веи и другие нечестные пути заполучить преимущество в сложности в уровне - ваше прохождение не будет добавлено в демонлист.```",
					inline=True)
	embed.add_field(name="Правило 1.4",
					value="```В демонлист вы можете попасть только при наличии 10+ уровня на сервере.```", inline=True)
	embed.set_footer(text=f"(C) Official Podpol'e Demonlist")
	await inter.edit_original_message(embed=embed)


client.run(token)
