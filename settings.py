import os

bot_version = "1.0.0" # Botバージョン
bot_name = "mfsbot-v2" # Bot名
bot_token = os.environ["DISCORD_BOT_TOKEN"]
bot_prefix = "tx!" # Botのコマンドの先頭部分につく
bot_add_role = "❖MEMBER❖" # 参加したユーザーに自動で付与する権限の名前
bot_status = "テスト稼働中" #Botのステータス（〇〇をプレイ中）の部分