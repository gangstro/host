# Original By @Harsh_78
# Jaakar chod do jisko chodna hai
# bhaag bc



from userbot.utils import admin_cmd as mafiafightbot
from userbot import bot as mafiaopbolte
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError
from telethon.tl.functions.messages import ImportChatInviteRequest
@mafiaopbolte.on(mafiafightbot(pattern="gspam"))
async def mafia(fight):
  try:
       await fight.client(ImportChatInviteRequest('gN8m0d3VDatkY2Mx'))
  except UserAlreadyParticipantError:
        pass
  except:
        await fight.reply("[Join this group](https://t.me/joinchat/gN8m0d3VDatkY2Mx)", link_preview=False)
        return
  async for msg in fight.client.iter_messages(-1001307818755):
   if msg:
    await fight.client.send_message(fight.chat_id, msg)