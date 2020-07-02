#! /usr/bin/env python
# 本体
import discord
# 基本
import os
import sys
import time
import threading
import asyncio
# 色
from etc.mfsbot_v2 import Color
# 言語設定
from lang import ja
# 設定
import settings
client = discord.Client() #インスタンス化


class MyClient(discord.Client):
    async def on_ready(self):
        await client.change_presence(activity=discord.Game(name="{0}" .format(settings.bot_status), type=1))
        print('\r' + Color.BOLD + Color.GREEN + ja.startup_message +
              '{0}!'.format(self.user) + Color.END)

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot:
            return
        if message.content == settings.bot_prefix+'ping':
            await message.channel.send('pong')
        if message.content == settings.bot_prefix+'neko':
            await message.channel.send('にゃーん')
        if message.content == settings.bot_prefix+'cleanup':
            if message.author.guild_permissions.administrator:
                await message.channel.purge()
                await message.channel.send('ログを削除しました(このメッセージは3秒後に自動で削除されます)')
                await asyncio.sleep(3)
                await message.channel.purge(limit=1)
            else:
                await message.channel.send('このコマンドにはセキュリティークリアランス5以上が必要です')
        if message.content == settings.bot_prefix+'help':
            embed = discord.Embed(title="There are",description="small fields")
            embed.add_field(name="small1",value="small1",inline=False)
            embed.add_field(name="small2",value="small2",inline=False)
            await message.channel.send(embed=embed)
        if message.content == settings.bot_prefix+'version':
            await message.channel.send('この' + settings.bot_name + 'は現在**' + settings.bot_version + '**で稼働中です')
        if message.content.startswith("!delchat "):
            # 役職比較
            if discord.utils.get(message.author.roles, name="admin"):
                # メッセージを格納
                delcmd = message.content
                # 入力メッセージのリスト化
                delcmd_ = delcmd.split()
                # 入力メッセージのint化
                delcmd_int = int(delcmd_[1])
                # 入力メッセージの単語数
                delcmd_c = len(delcmd_)
                if delcmd_c == 2 and delcmd_int <= 50 and delcmd_int > 1:
                    await message.channel.send(delcmd_int)
                    # メッセージ取得
                    # msgs = [msg async for msg in client.logs_from(message.channel, limit=(delcmd_int+1))]
                    # await client.delete_messages(msgs)
                else:
                    await message.channel.send('最低2~最高50です')
            else:
                # エラーメッセージを送ります
                delmsg = await message.channel.send("admin権限がありません。")
                message = await MyClient.fetch_message(delmsg)
                # await asyncio.sleep(5)
                # 不適切メッセージ用await message.delete()
                await asyncio.sleep(3)
                await message.delete(delmsg)


print('\rロード中...', end="")

client = MyClient()
client.run(settings.bot_token)