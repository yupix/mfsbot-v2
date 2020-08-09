#!  /usr/bin/env python
# 本体
import discord
from discord.ext import tasks
# 基本
import os
import sys
import time
import threading
import asyncio
from halo import Halo
# 色
from etc.mfsbot_v2 import Color
# 言語設定
from lang import ja
import requests# 設定
import settings
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import json
import requests
import re
client = discord.Client()  # インスタンス化

def check_json_file():  # 起動時に一度実行jsonがあるか確認ないなら作成する関数
	if os.path.exists("./db/blocklist.json"):
		print(f'[main/INFO] blocklist.jsonチェックに成功')
	else:
		with open('./db/blocklist.json', mode='x') as f:
			f.write('{}')
	if os.path.exists("./db/bloglist.json"):
		print(f'[main/INFO] bloglist.jsonチェックに成功')
	else:
		with open('./db/bloglist.json', mode='x') as f:
			f.write('{}')


async def update_json_data():  # blogの情報を更新する用の関数
	with open('db/bloglist.json', "r") as json_file:
		json_data = json.load(json_file)
	return json_data

async def update_blocklist_json_data(): # ブロックリストの情報を更新する用の関数
	with open('db/blocklist.json', "r") as blocklist_json_file:
		blocklist_json_data = json.load(blocklist_json_file)
	return blocklist_json_data

async def overide_blocklist_json_data(blocklist_json_data): # ブロックリストの情報を保存
	with open('db/blocklist.json', 'w') as f:
		json.dump(blocklist_json_data, f, indent=4, ensure_ascii=False)

@tasks.loop(seconds=60)
async def loop():
	blocklist_json_data = await update_blocklist_json_data()
	get_blocklist_json_latest_update = blocklist_json_data.get('latest_update')
	print(get_blocklist_json_latest_update)
	now = datetime.now()
	string_date = f'{now}'
	dt = datetime.strptime(get_blocklist_json_latest_update, '%Y-%m-%d %H:%M:%S.%f')
	print(datetime(dt) < now)


@client.event
async def on_ready():
	await client.change_presence(activity=discord.Game(name="{0}" .format(settings.bot_status), type=1))
	spinner.stop()
	print('\r' + Color.BOLD + Color.GREEN + ja.startup_message + '{0}!'.format(client.user) + Color.END)
	check_json_file()
	print(settings.bot_name + 'インフォメーション')
	print(' ・Discord.py Version:' + discord.__version__)
	loop.start()

@client.event
async def on_member_join(member):
	with open('db/blocklist.json', "r") as blocklist_json_file:
		blocklist_json_data = json.load(blocklist_json_file)
	server_id = member.guild.id
	user_id = member.id
	print(user_id)
	check_blacklist_user_id = blocklist_json_data.get(f'{user_id}').get('user_id')
	check_blacklist_count = blocklist_json_data.get(f'{user_id}').get('count')
	if check_blacklist_user_id is not None:
		print(f'{check_blacklist_user_id}\n{check_blacklist_count}')
		print('ブロックリストの人が来たよ')
		new_count_data = int(check_blacklist_count + 1)
		print(new_count_data)
		blocklist_json_data[f'{user_id}']['count'] = new_count_data
		print(blocklist_json_data)
		user_info = client.get_user(member.id)
		await overide_blocklist_json_data(blocklist_json_data)
		if new_count_data == 5:
			dm = await user_info.create_dm()
			#blogwar_embed = discord.Embed(title='')
			await dm.send(f': ')
		elif 1 < new_count_data < 4:
			dm = await user_info.create_dm()
			#blogwar_embed = discord.Embed(title='')
			await dm.send(f'警告: サーバーへの出入りを検知しました。1ヵ月の間に5回入りなおすとBAN処置を自動で行います')
		elif new_count_data == 4:
			dm = await user_info.create_dm()
			#blogwar_embed = discord.Embed(title='')
			await dm.send(f'最終通告: サーバーへの出入りを検知しました。残り1回入るとBAN処置を行います')

	else:
		role = discord.utils.find(lambda r: r.name == f'{settings.bot_add_role}', member.guild.roles)
		await member.add_roles(role)


@client.event
async def on_message(message):
	print('Message from {0.author}: {0.content}'.format(message))
	if message.author.bot:  # メッセージ送信者がBotだった場合は無視する
		return
	get_message_author_name = message.author
	get_server_id = message.guild.id  # 発言があったサーバーのIDを取得
	get_category_id = message.channel.category.id  # 発言のあったチャンネルのカテゴリーIDを取得
	get_channel_id = message.channel.id  # 発言があったチャンネルIDを取得
	get_message_created_at = message.created_at #発言した時間
	json_data = await update_json_data()
	get_bloglist_server_id = json_data.get('{0}'.format(get_server_id), {}).get('server_id')
	if get_bloglist_server_id is not None:  # 変数に文字列が入っているか確認
		for mykey in json_data[f'{get_server_id}']['blog_list'].keys():
			print(f'aaaaaa{mykey}')
			if f'{get_category_id}' == f'{mykey}':
				break
		get_blog_reply_channel = json_data.get('{0}'.format(get_server_id), {}).get('blog_list', {}).get(mykey, {}).get('blog_reply_channel') # ブログに対する返信チャンネルを取得(カテゴリ別)
		if get_blog_reply_channel is not None:
			if get_channel_id == get_blog_reply_channel: #ブログに対する返信チャンネルか否か
				if '<#' in message.content:
					get_message_content = message.content # メッセージ内容を変数に
					get_message_content_ = get_message_content.split()
					get_message_content_channel = (get_message_content_[0]) # チャンネル部分を取る
					get_message_content_count = len(get_message_content_)
					re_get_message_content = (get_message_content_channel.replace('<#', '').replace('>', ''))
					get_target_channel_name = client.get_channel(int(re_get_message_content)) # チャンネルIDからチャンネル名を取得
					get_json_embed_color = json_data[f'{get_server_id}']['blog_list'][f'{mykey}'][f'{get_target_channel_name}']['embed_color']
					print(f'ああああ{get_json_embed_color}')
					for i in range(1,get_message_content_count):
						get_message_main_content_channel = (get_message_content_[i]) # チャンネル部分を取る
						print(get_message_main_content_channel)
					await message.channel.send(get_message_content_channel)
					print(f'再取得前{re_get_message_content}\n再取得{get_message_content_channel}')
					print(get_target_channel_name)

					#embed.set_footer(text=f"{get_message_created_at}")

					get_json_reply_webhook_url = json_data[f'{get_server_id}']['blog_list'][f'{mykey}']['blog_reply_webhook_url']
					get_message_author_user_icon = message.author.avatar_url_as(format="png")
					url = f"{get_json_reply_webhook_url}" #webhook url, from here: https://i.imgur.com/aT3AThK.png

					data = {}
					#for all params, see
					#https://discordapp.com/developers/docs/resources/webhook#execute-webhook
					reformat_message_author_name = get_message_author_name
					data["username"] = f"{reformat_message_author_name}"
					data["avatar_url"] = f"{get_message_author_user_icon}"
					#leave this out if you dont want an embed
					data["embeds"] = []
					embed = {}
					embed["color"] = f"{get_json_embed_color}"
					#for all params, see
					#https://discordapp.com/developers/docs/resources/channel#embed-object
					embed["description"] = f"{get_message_main_content_channel}"
					embed["title"] = f"{get_target_channel_name} への返信"
					data["embeds"].append(embed)

					result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})

				#else:
				#	await message.channel.send('blogに返信する際は#〇〇を使用するようにしてください')
			print(get_blog_reply_channel)
		else:
			if f'{settings.bot_prefix}set-blog-reply-channel' not in message.content:
				await message.channel.send('カテゴリは登録されていますが返信チャンネルが登録されていません')

	if message.content == settings.bot_prefix + 'set-blog-reply-channel':
		print(f'bloglist.jsonの{mykey}\n実際に実行されたところ{get_category_id}')
		if f'{mykey}' == f'{get_category_id}':
			get_channel_id = message.channel.id  # 発言があったチャンネルIDを取得
			get_target_channel_name = client.get_channel(int(get_channel_id)) # チャンネルIDからチャンネル名を取得
			web = await get_target_channel_name.create_webhook(name='DummyUser')
			json_data[f'{get_server_id}']['blog_list'][mykey].setdefault('blog_reply_channel', get_channel_id)
			json_data[f'{get_server_id}']['blog_list'][mykey].setdefault('blog_reply_webhook_url', web.url)
			with open('db/bloglist.json', 'w') as f:
				json.dump(json_data, f, indent=4, ensure_ascii=False)
		else:
			embed = discord.Embed(title="ERROR", description="登録されていないカテゴリです。\nサーバー管理者に**" + settings.bot_prefix + 'blog-category-setup**を実行するようにお願いしてください', color=0xff0000)  # 16進数カラーコード
			await message.channel.send(embed=embed)
	if message.content.startswith(settings.bot_prefix + 'pso2-emergency '):

		async def update_pso2_emergency_json_data(get_message_data):
			jsonData = {
				"EventDate": f"{get_message_data}",
				"EventType": "緊急"
			}
			return jsonData
		url = "https://pso2.akakitune87.net/api/emergency" # POSTURL
		message_data = message.content
		message_data_ = message_data.split()
		get_message_data = (message_data_[1])
		print(get_message_data) # 引数に何が入ってるか出力
		dt_now = datetime.datetime.now()
		get_today_time = f'{dt_now.month}{dt_now.day}{dt_now.hour}{dt_now.minute}'
		if 'today' in get_message_data: # todayと後ろについてる場合は今日の緊急を出す
			format_dt_now = dt_now.strftime('%Y%m%d')
			print(format_dt_now)
			jsonData = await update_pso2_emergency_json_data(format_dt_now)
			print(jsonData)
			embed_title_days = '今日の'
		else:
			jsonData = await update_pso2_emergency_json_data(get_message_data)
			embed_title_days = f'{get_message_data}の'
		#POST送信
		response = requests.post(url,
			data = json.dumps(jsonData)    #dataを指定する
			)
		resDatas = response.json()
		#print(resDatas)
		get_resDatas_len = len(resDatas)
		get_all_res_datas = "" # 空の変数定義
		get_alldatas_time = ""
		embed = discord.Embed(title=f"{embed_title_days}緊急イベント情報", description="※この情報は正確ではない可能性があります", color=0x29b6f6)  # 16進数カラーコード]
		now = datetime.datetime.now()
		now + datetime.timedelta(minutes=30)
		now_txt = f'{now}'
		now_txt = now_txt.partition('.')[0]
		now_txt = now_txt.replace('-','').replace(':','') #.replace(' ','')
		now_txt = now_txt.split() # 配列化
		now_txt = now_txt[0] # 秒以外を取得
		print(f'{now_txt}hokokwokwokowk')
		dt1 = datetime.datetime(2016, 7, 1, 22, 30)
		dt2 = datetime.datetime(2018, 7, 5, 13, 45)

		print(dt1 == dt2, dt1 != dt2, dt1 < dt2, dt1 > dt2, dt2 <= dt1, dt1 >= dt2)


		await message.channel.send(now_txt)
		for i in range(int(get_resDatas_len)):
			print(resDatas[i])
			get_res_datas_month = resDatas[i]['Month'] # 月を取得
			get_res_datas_date = resDatas[i]['Date'] # 日付を取得
			get_res_datas_hour = resDatas[i]['Hour'] # 時を取得
			get_res_datas_minute = resDatas[i]['Minute'] # 分を取得
			get_res_datas_eventname = resDatas[i]['EventName'] # イベントを取得

			#get_len_res_datas_month = len(get_res_datas_month)#文字列の桁を取得
			#get_len_res_datas_date = len(get_res_datas_date)
			#get_len_res_datas_hour = len(get_res_datas_hour)
			#get_len_res_datas_minute = len(get_res_datas_minute)
			raw_alldatas_time = f'{get_res_datas_month}{get_res_datas_date}{get_res_datas_hour}{get_res_datas_minute}'
			get_alldatas_time = f'⌚{get_res_datas_month}月{get_res_datas_date}日{get_res_datas_hour}時{get_res_datas_minute}分'
			get_all_res_datas += f'{get_res_datas_month}月{get_res_datas_date}日{get_res_datas_hour}時{get_res_datas_minute}分{get_res_datas_eventname}\n'
			embed.add_field(name=f"{get_alldatas_time}",
							value=f"{get_res_datas_eventname}", inline=True)
		await message.channel.send(embed=embed)
		#await message.channel.send(f'{get_all_res_datas}')
	if message.content.startswith(settings.bot_prefix + 'addblocklist '):
		if message.author.guild_permissions.administrator:
			with open('db/blocklist.json', "r") as blocklist_json_file:
				blocklist_json_data = json.load(blocklist_json_file)
			delcmd = message.content
			delcmd_ = delcmd.split()
			get_message_delcmd = (delcmd_[1])
			server_id = message.guild.id
			get_user_name = await client.fetch_user(get_message_delcmd)
			now = datetime.now()
			now = now + relativedelta(months=1)
			blocklist_json_data.setdefault('latest_update', f'{now}')
			blocklist_json_data.setdefault(get_message_delcmd, {})
			blocklist_json_data[get_message_delcmd].setdefault('user_id', get_message_delcmd)
			blocklist_json_data[get_message_delcmd].setdefault('count', 0)

			await message.channel.send('ブロックリストに登録しました')
			with open('db/blocklist.json', 'w') as f:
				json.dump(blocklist_json_data, f, indent=4, ensure_ascii=False)
		else:
			await message.channel.send('このコマンドには管理者権限が必要です')
	if message.content == settings.bot_prefix + 'ping':
		await message.channel.send(f'ping: {round(client.latency * 1000)}ms ')
	if message.content == settings.bot_prefix + 'cleanup':
		if message.author.guild_permissions.administrator:
			await message.channel.purge()
			await message.channel.send('ログを削除しました(このメッセージは3秒後に自動で削除されます)')
			await asyncio.sleep(3)
			await message.channel.purge(limit=1)
		else:
			await message.channel.send('このコマンドには管理者権限が必要です')
	if message.content == settings.bot_prefix + 'help':
		embed = discord.Embed(title="BOTヘルプ一覧", colour=discord.Colour(0x112f43), url="https://discordapp.com", description="```Prefix:{0}```".format(settings.bot_prefix))
		embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/424758866165891072/a0b5caf9c968acb6d1f6f9286baff558.webp?size=128")
		embed.set_author(name=settings.bot_name, url="https://discordapp.com",
						 icon_url="https://cdn.discordapp.com/avatars/424758866165891072/a0b5caf9c968acb6d1f6f9286baff558.webp?size=128")
		embed.set_footer(text="©2020 Team Yupix",
						 icon_url="https://cdn.discordapp.com/avatars/424758866165891072/a0b5caf9c968acb6d1f6f9286baff558.webp?size=128")
		embed.add_field(name=settings.bot_prefix + "help", value="ヘルプを表示")
		embed.add_field(name=settings.bot_prefix + "version", value="バージョンを表示")
		embed.add_field(name=settings.bot_prefix + "cleanup", value="チャンネルのテキストを50個削除")
		embed.add_field(name=settings.bot_prefix + "addblocklist ```USERID```",
						value="このBOTが参加しているサーバー内でのブロックリストにユーザーを追加します", inline=True)
		embed.add_field(name="ComingSoon...", value="none", inline=True)
		await message.channel.send(embed=embed)
	if message.content == settings.bot_prefix + 'version':
		await message.channel.send('この' + settings.bot_name + 'は現在**' + settings.bot_version + '**で稼働中です')
	if message.content.startswith(settings.bot_prefix + "blog-category-setup"):
		if message.author.guild_permissions.administrator:
			json_data = {}
			name = message.author
			user_id = message.author.id
			channel_id = message.channel.id
			category_id = message.channel.category.id
			server_id = message.guild.id
			owner_id = message.guild.owner.id
			channel_name = client.get_channel(channel_id)
			keyA = f'{server_id}'
			keyB = f'{category_id}'
			word = f'{server_id}'
			word2 = f'{channel_name}'
			with open('db/bloglist.json', "r") as json_file:
				json_data = json.load(json_file)
				json_data.setdefault(word, {})
				json_data[word].setdefault("server_id", keyA)
				json_data[word].setdefault('blog_list', {})
				json_data[word]['blog_list'].setdefault(keyB, {})
				print(json_data)
			with open('db/bloglist.json', 'w') as f:
				json.dump(json_data, f, indent=4, ensure_ascii=False)
			embed = discord.Embed(title="SUCCESS", description="カテゴリの登録に成功しました!", color=0x8bc34a)  # 16進数カラーコード
			await message.channel.send(embed=embed)
		else:
			await message.channel.send('このコマンドには管理者権限が必要です')
	if message.content.startswith(settings.bot_prefix + "blog-register"):
		json_data = await update_json_data()
		name = message.author
		user_id = message.author.id
		channel_id = message.channel.id
		server_id = message.guild.id
		category_id = message.channel.category.id
		owner_id = message.guild.owner.id
		channel_name = client.get_channel(channel_id)
		hoge = json_data.get('{0}'.format(server_id), {}).get('server_id')
		if hoge is None:
			embed = discord.Embed(title="ERROR", description="サーバーが登録されていません！\nサーバー管理者に**" + settings.bot_prefix + 'blog-category-setup**を実行するようにお願いしてください', color=0xff0000)  # 16進数カラーコード
			await message.channel.send(embed=embed)
		else:
			check_category_id = json_data.get('{0}'.format(server_id), {}).get('blog_list', {}).get('{0}'.format(category_id))
			if check_category_id is not None:
				hoge3 = json_data.get('{0}'.format(server_id), {}).get('blog_list', {}).get(category_id, {}).get('{0}'.format(channel_name))
				print(hoge3)
				if hoge3 is None:
					check_blog_list = json_data.get('{0}'.format(server_id), {}).get('blog_list', {})
					if check_blog_list is not None:
						hoge = json_data.get('{0}'.format(server_id), {}).get('server_id')
						await message.channel.send('サーバーが登録されています')
						json_data = {}
						name = message.author
						user_id = message.author.id
						channel_id = message.channel.id
						category_id = message.channel.category.id
						server_id = message.guild.id
						owner_id = message.guild.owner.id
						channel_name = client.get_channel(channel_id)
						keyA = f'{server_id}'
						keyB = f'{category_id}'
						key_category_id = f'{category_id}'
						keyC = 'prate'
						keyD = 'nrate'
						word = f'{server_id}'
						word2 = f'{channel_name}'
						json_data = await update_json_data()
						json_data[word].setdefault('blog_list', {})
						json_data[word]['blog_list'][keyB].setdefault(word2, {})
						json_data[word]['blog_list'][keyB][word2].setdefault('user_id', user_id)
						json_data[word]['blog_list'][keyB][word2].setdefault('channel_id', channel_id)
						json_data[word]['blog_list'][keyB][word2].setdefault('embed_color', '5620992')
						print(json_data)
						with open('db/bloglist.json', 'w') as f:
							json.dump(json_data, f, indent=4,
									  ensure_ascii=False)
						embed = discord.Embed(title="SUCCESS", description="個人ブログの登録に成功しました!", color=0x8bc34a)  # 16進数カラーコード
						await message.channel.send(embed=embed)
					else:
						embed = discord.Embed(title="ERROR", description="既に登録されているチャンネルです", color=0xff0000)  # 16進数カラーコード
						await message.channel.send(embed=embed)
			else:
				embed = discord.Embed(title="ERROR", description="登録されていないカテゴリです。\nサーバー管理者に**" + settings.bot_prefix + 'blog-category-setup**を実行するようにお願いしてください', color=0xff0000)  # 16進数カラーコード
				await message.channel.send(embed=embed)
spinner = Halo(text='Loading Now',
			   spinner={
				   'interval': 300,
				   'frames': ['-', '+', 'o', '+', '-']
			   })
spinner.start()
client.run(settings.bot_token)
