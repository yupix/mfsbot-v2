#! /usr/bin/env python
# 本体
import discord
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
# 設定
import settings
import datetime
import json
client = discord.Client()  # インスタンス化


def check_json_file():
	if os.path.exists("./db/blocklist.json"):
		print(f'[main/INFO] blocklist.jsonチェックに成功')
	else:
		with open('./db/blocklist.json', mode='x') as f:
			f.write('{}')

@client.event
async def on_ready():
	await client.change_presence(activity=discord.Game(name="{0}" .format(settings.bot_status), type=1))
	spinner.stop()
	print('\r' + Color.BOLD + Color.GREEN + ja.startup_message +
		  '{0}!'.format(client.user) + Color.END)
	check_json_file()
	print (settings.bot_name + 'インフォメーション')
	print(' ・Discord.py Version:'+discord.__version__)

@client.event
async def on_member_join(member):
	with open('db/blocklist.json', "r") as blocklist_json_file:
		blocklist_json_data = json.load(blocklist_json_file)
	server_id = member.guild.id
	user_id = member.id
	print(user_id)
	check_blacklist = blocklist_json_data.get(f'{user_id}')
	if check_blacklist is not None:
		print('ブロックリストの人が来たよ')
	else:
		role = discord.utils.find(lambda r: r.name == f'{settings.bot_add_role}', member.guild.roles)
		await member.add_roles(role)

@client.event
async def on_message(message):
	print('Message from {0.author}: {0.content}'.format(message))
	# メッセージ送信者がBotだった場合は無視する
	if message.author.bot:
		return
	if message.content.startswith(settings.bot_prefix+'addblocklist '):
		if message.author.guild_permissions.administrator:
			with open('db/blocklist.json', "r") as blocklist_json_file:
				blocklist_json_data = json.load(blocklist_json_file)
			delcmd = message.content
			delcmd_ = delcmd.split()
			get_message_delcmd = (delcmd_[1])
			server_id = message.guild.id
			get_user_name = await client.fetch_user(get_message_delcmd)
			blocklist_json_data.setdefault(f'{get_message_delcmd}', get_message_delcmd)
			await message.channel.send('ブロックリストに登録しました')
			with open('db/blocklist.json', 'w') as f:
				json.dump(blocklist_json_data, f, indent=4, ensure_ascii=False)
		else:
			await message.channel.send('このコマンドには管理者権限が必要です')
	if message.content == settings.bot_prefix+'ping':
		await message.channel.send(f'ping: {round(client.latency * 1000)}ms ')
	if message.content == settings.bot_prefix+'neko':
		await message.channel.send('にゃーん')
	if message.content == settings.bot_prefix+'cleanup':
		if message.author.guild_permissions.administrator:
			await message.channel.purge()
			await message.channel.send('ログを削除しました(このメッセージは3秒後に自動で削除されます)')
			await asyncio.sleep(3)
			await message.channel.purge(limit=1)
		else:
			await message.channel.send('このコマンドには管理者権限が必要です')
	if message.content == settings.bot_prefix+'help':
		embed = discord.Embed(title="BOTヘルプ一覧", colour=discord.Colour(0x112f43), url="https://discordapp.com", description="```Prefix:{0}```".format(settings.bot_prefix))
		embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/424758866165891072/a0b5caf9c968acb6d1f6f9286baff558.webp?size=128")
		embed.set_author(name=settings.bot_name, url="https://discordapp.com", icon_url="https://cdn.discordapp.com/avatars/424758866165891072/a0b5caf9c968acb6d1f6f9286baff558.webp?size=128")
		embed.set_footer(text="©2020 Team Yupix", icon_url="https://cdn.discordapp.com/avatars/424758866165891072/a0b5caf9c968acb6d1f6f9286baff558.webp?size=128")
		embed.add_field(name=settings.bot_prefix+"help", value="ヘルプを表示")
		embed.add_field(name=settings.bot_prefix+"version", value="バージョンを表示")
		embed.add_field(name=settings.bot_prefix+"cleanup", value="チャンネルのテキストを50個削除")
		embed.add_field(name=settings.bot_prefix+"addblocklist ```USERID```", value="このBOTが参加しているサーバー内でのブロックリストにユーザーを追加します", inline=True)
		embed.add_field(name="ComingSoon...", value="none", inline=True)
		await message.channel.send(embed=embed)
	if message.content == settings.bot_prefix+'version':
		await message.channel.send('この' + settings.bot_name + 'は現在**' + settings.bot_version + '**で稼働中です')

spinner = Halo(text='Loading Now',
	spinner={
		'interval': 300,
		'frames': ['-', '+', 'o', '+', '-']
	})
spinner.start()
client.run(settings.bot_token)
