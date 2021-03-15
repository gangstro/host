# MAFIABOT FIGHT BOT

# ADMIN

from asyncio import sleep

from telethon import functions
from telethon.errors import (
    BadRequestError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
)
from telethon.errors.rpcerrorlist import UserAdminInvalidError, UserIdInvalidError
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    ChatAdminRights,
    ChatBannedRights,
    MessageEntityMentionName,
    MessageMediaPhoto,
)

from userbot import *
from userbot.plugins.sql_helper.mute_sql import is_muted, mute, unmute
from userbot.utils import *

# =================== CONSTANT ===================

PP_TOO_SMOL = "`The image is too small`"
PP_ERROR = "`Failure while processing the image`"
NO_ADMIN = "`I am not an admin! Chutiya sala`"
NO_PERM = "`I don't have sufficient permissions! Sed -_-`"
CHAT_PP_CHANGED = "`Chat Picture Changed Successfully`"
INVALID_MEDIA = "`Invalid media Extension`"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

# ================================================


@bot.on(admin_cmd("setgpic$"))
@bot.on(sudo_cmd(pattern="setgpic$", allow_sudo=True))
@errors_handler
async def set_group_photo(gpic):
    if not gpic.is_group:
        await edit_or_reply(gpic, "`I don't think this is a group.`")
        return
    replymsg = await gpic.get_reply_message()
    chat = await gpic.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    photo = None
    if not admin and not creator:
        await edit_or_reply(gpic, NO_ADMIN)
        return
    if replymsg and replymsg.media:
        if isinstance(replymsg.media, MessageMediaPhoto):
            photo = await gpic.client.download_media(message=replymsg.photo)
        elif "image" in replymsg.media.document.mime_type.split("/"):
            photo = await gpic.client.download_file(replymsg.media.document)
        else:
            await edit_or_reply(gpic, INVALID_MEDIA)
    kraken = None
    if photo:
        try:
            await gpic.client(
                EditPhotoRequest(gpic.chat_id, await gpic.client.upload_file(photo))
            )
            await edit_or_reply(gpic, CHAT_PP_CHANGED)
            kraken = True
        except PhotoCropSizeSmallError:
            await edit_or_reply(gpic, PP_TOO_SMOL)
        except ImageProcessFailedError:
            await edit_or_reply(gpic, PP_ERROR)
        except Exception as e:
            await edit_or_reply(gpic, f"**Error : **`{str(e)}`")
        if BOTLOG and kraken:
            await gpic.client.send_message(
                BOTLOG_CHATID,
                "#GROUPPIC\n"
                f"Group profile pic changed "
                f"CHAT: {gpic.chat.title}(`{gpic.chat_id}`)",
            )


@bot.on(admin_cmd("promote(?: |$)(.*)"))
@bot.on(sudo_cmd(pattern="promote(?: |$)(.*)", allow_sudo=True))
@errors_handler
async def promote(promt):
    chat = await promt.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(promt, NO_ADMIN)
        return
    new_rights = ChatAdminRights(
        add_admins=False,
        invite_users=True,
        change_info=False,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
    )
    mafiaevent = await edit_or_reply(promt, "`Promoting...`")
    user, rank = await get_user_from_event(promt)
    if not rank:
        rank = "FIGHTER"
    if not user:
        return
    try:
        await promt.client(EditAdminRequest(promt.chat_id, user.id, new_rights, rank))
        await mafiaevent.edit("`Promoted Successfully!` Promoted By [𝕄𝔸𝔽𝕀𝔸 𝕌𝕊𝔼ℝ𝔹𝕆𝕋](https://t.me/MAFIA_USERBOT)")
    except BadRequestError:
        await mafiaevent.edit(NO_PERM)
        return
    if BOTLOG:
        await promt.client.send_message(
            BOTLOG_CHATID,
            "#PROMOTE\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {promt.chat.title}(`{promt.chat_id}`)",
        )


@bot.on(admin_cmd("demote(?: |$)(.*)"))
@bot.on(sudo_cmd(pattern="demote(?: |$)(.*)", allow_sudo=True))
@errors_handler
async def demote(dmod):
    chat = await dmod.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(dmod, NO_ADMIN)
        return
    mafiaevent = await edit_or_reply(dmod, "`Demoting...`")
    rank = "admeme"
    user = await get_user_from_event(dmod)
    user = user[0]
    if not user:
        return
    newrights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    try:
        await dmod.client(EditAdminRequest(dmod.chat_id, user.id, newrights, rank))
    except BadRequestError:
        await mafiaevent.edit(NO_PERM)
        return
    await mafiaevent.edit("`Demoted retard Successfully!` Promoted By [𝕄𝔸𝔽𝕀𝔸 𝕌𝕊𝔼ℝ𝔹𝕆𝕋](https://t.me/MAFIA_USERBOT)")
    if BOTLOG:
        await dmod.client.send_message(
            BOTLOG_CHATID,
            "#DEMOTE\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {dmod.chat.title}(`{dmod.chat_id}`)",
        )


@bot.on(admin_cmd("ban(?: |$)(.*)"))
@bot.on(sudo_cmd(pattern="ban(?: |$)(.*)", allow_sudo=True))
@errors_handler
async def ban(bon):
    chat = await bon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(bon, NO_ADMIN)
        return
    user, reason = await get_user_from_event(bon)
    if not user:
        return
    mafiaevent = await edit_or_reply(bon, "`Banning this retard`")
    try:
        await bon.client(EditBannedRequest(bon.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        await mafiaevent.edit(NO_PERM)
        return
    try:
        reply = await bon.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        await mafiaevent.edit("`I ain't got msg deleting right. But still Banned!`")
        return
    if reason:
        await mafiaevent.edit(f"`{str(user.id)}` is banned !!\nReason: {reason}")
    else:
        await mafiaevent.edit(f"{str(user.id)} is banned😏 !!")
    if BOTLOG:
        await bon.client.send_message(
            BOTLOG_CHATID,
            "#BAN\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {bon.chat.title}(`{bon.chat_id}`)",
        )


@bot.on(admin_cmd("unban(?: |$)(.*)"))
@bot.on(sudo_cmd(pattern="unban(?: |$)(.*)", allow_sudo=True))
@errors_handler
async def nothanos(unbon):
    chat = await unbon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(unbon, NO_ADMIN)
        return
    mafiaevent = await edit_or_reply(unbon, "`Unbanning...`")
    user = await get_user_from_event(unbon)
    user = user[0]
    if not user:
        return
    try:
        await unbon.client(EditBannedRequest(unbon.chat_id, user.id, UNBAN_RIGHTS))
        await mafiaevent.edit("```Unbanned Successfully. Granting another chance🚶.```")
        if BOTLOG:
            await unbon.client.send_message(
                BOTLOG_CHATID,
                "#UNBAN\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {unbon.chat.title}(`{unbon.chat_id}`)",
            )
    except UserIdInvalidError:
        await mafiaevent.edit("`Uh oh my unban logic broke!`")


@command(incoming=True)
async def watcher(event):
    if is_muted(event.sender_id, event.chat_id):
        try:
            await event.delete()
        except Exception as e:
            LOGS.info(str(e))


@bot.on(admin_cmd("mute(?: |$)(.*)"))
@bot.on(sudo_cmd(pattern="mute(?: |$)(.*)", allow_sudo=True))
async def startmute(event):
    if event.is_private:
        await event.edit("Unexpected issues or ugly errors may occur!")
        await sleep(3)
        await event.get_reply_message()
        userid = event.chat_id
        replied_user = await event.client(GetFullUserRequest(userid))
        chat_id = event.chat_id
        if is_muted(userid, chat_id):
            return await event.edit("This user is already muted🤣🤣🤣")
        try:
            mute(userid, chat_id)
        except Exception as e:
            await event.edit("Error occured!\nError is " + str(e))
        else:
            await event.edit("Chup reh lawde.\n**｀-´)⊃━☆ﾟ.*･｡ﾟ **")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#PM_MUTE\n"
                f"USER: [{replied_user.user.first_name}](tg://user?id={userid})\n"
                f"CHAT: {event.chat.title}(`{event.chat_id}`)",
            )
    else:
        chat = await event.get_chat()
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == bot.uid:
            return await edit_or_reply(event, "Sorry, I can't mute myself")
        if is_muted(user.id, event.chat_id):
            return await edit_or_reply(
                event, "This user is already muted in this chat😏🚶"
            )
        try:
            admin = chat.admin_rights
            creator = chat.creator
            if not admin and not creator:
                await edit_or_reply(
                    event, "`You can't mute a person without admin rights` ಥ﹏ಥ  "
                )
                return
            result = await event.client(
                functions.channels.GetParticipantRequest(
                    channel=event.chat_id, user_id=user.id
                )
            )
            try:
                if result.participant.banned_rights.send_messages:
                    return await edit_or_reply(
                        event,
                        "This user is already muted in this chat 😏🚶",
                    )
            except:
                pass
            await event.client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
        except UserAdminInvalidError:
            if "admin_rights" in vars(chat) and vars(chat)["admin_rights"] is not None:
                if chat.admin_rights.delete_messages is not True:
                    return await edit_or_reply(
                        event,
                        "`You can't mute a person if you dont have delete messages permission. ಥ﹏ಥ`",
                    )
            elif "creator" not in vars(chat):
                return await edit_or_reply(
                    event, "`You can't mute a person without admin rights.` ಥ﹏ಥ  "
                )
            try:
                mute(user.id, event.chat_id)
            except Exception as e:
                return await edit_or_reply(event, "Error occured!\nError is " + str(e))
        except Exception as e:
            return await edit_or_reply(event, f"**Error : **`{str(e)}`")
        if reason:
            await edit_or_reply(
                event,
                f"{user.first_name} is muted in {event.chat.title}\n"
                f"`Reason:`{reason}",
            )
        else:
            await edit_or_reply(
                event, f"{user.first_name} is muted in {event.chat.title}"
            )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#MUTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {event.chat.title}(`{event.chat_id}`)",
            )


@bot.on(admin_cmd("unmute(?: |$)(.*)"))
@bot.on(sudo_cmd(pattern="unmute(?: |$)(.*)", allow_sudo=True))
async def endmute(event):
    if event.is_private:
        await event.edit("Unexpected issues or ugly errors may occur!")
        await sleep(3)
        userid = event.chat_id
        replied_user = await event.client(GetFullUserRequest(userid))
        chat_id = event.chat_id
        if not is_muted(userid, chat_id):
            return await event.edit(
                "__This user is not muted in this chat__\n（ ^_^）o自自o（^_^ ）"
            )
        try:
            unmute(userid, chat_id)
        except Exception as e:
            await event.edit("Error occured!\nError is " + str(e))
        else:
            await event.edit("Abb bol gendu\n乁( ◔ ౪◔)「    ┑(￣Д ￣)┍")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#UNMUTE\n"
                f"USER: [{replied_user.user.first_name}](tg://user?id={userid})\n"
                f"CHAT: {event.chat.title}(`{event.chat_id}`)",
            )
    else:
        user = await get_user_from_event(event)
        user = user[0]
        if not user:
            return
        try:
            if is_muted(user.id, event.chat_id):
                unmute(user.id, event.chat_id)
            else:
                result = await event.client(
                    functions.channels.GetParticipantRequest(
                        channel=event.chat_id, user_id=user.id
                    )
                )
                try:
                    if result.participant.banned_rights.send_messages:
                        await event.client(
                            EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS)
                        )
                except:
                    return await edit_or_reply(
                        event,
                        "This user can already speak freely in this chat😪",
                    )
        except Exception as e:
            return await edit_or_reply(event, f"**Error : **`{str(e)}`")
        await edit_or_reply(event, "Abb bol gendu\n乁( ◔ ౪◔)「    ┑(￣Д ￣)┍")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#UNMUTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {event.chat.title}(`{event.chat_id}`)",
            )


@bot.on(admin_cmd("pin($| (.*))"))
@bot.on(sudo_cmd(pattern="pin($| (.*))", allow_sudo=True))
@errors_handler
async def pin(msg):
    chat = await msg.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(msg, NO_ADMIN)
        return
    to_pin = msg.reply_to_msg_id
    if not to_pin:
        await edit_or_reply(msg, "`Reply to a message to pin it.`")
        return
    options = msg.pattern_match.group(1)
    is_silent = True
    if options.lower() == "loud":
        is_silent = False
    try:
        await msg.client(UpdatePinnedMessageRequest(msg.to_id, to_pin, is_silent))
    except BadRequestError:
        await edit_or_reply(msg, NO_PERM)
        return
    hmm = await edit_or_reply(msg, "`Pinned Successfully!`")
    user = await get_user_from_id(msg.sender_id, msg)
    if BOTLOG:
        await msg.client.send_message(
            BOTLOG_CHATID,
            "#PIN\n"
            f"ADMIN: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {msg.chat.title}(`{msg.chat_id}`)\n"
            f"LOUD: {not is_silent}",
        )
    await sleep(3)
    try:
        await hmm.delete()
    except:
        pass


@bot.on(admin_cmd("kick(?: |$)(.*)"))
@bot.on(sudo_cmd(pattern="kick(?: |$)(.*)", allow_sudo=True))
@errors_handler
async def kick(usr):
    chat = await usr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(usr, NO_ADMIN)
        return
    user, reason = await get_user_from_event(usr)
    if not user:
        await edit_or_reply(usr, "`Couldn't fetch user.`")
        return
    mafiaevent = await edit_or_reply(usr, "`Kicking...`")
    try:
        await usr.client.kick_participant(usr.chat_id, user.id)
        await sleep(0.5)
    except Exception as e:
        await mafiaevent.edit(NO_PERM + f"\n{str(e)}")
        return
    if reason:
        await mafiaevent.edit(
            f"`Kicked` [{user.first_name}](tg://user?id={user.id})`!`\nReason: {reason}"
        )
    else:
        await mafiaevent.edit(f"`Kicked` [{user.first_name}](tg://user?id={user.id})`!`")
    if BOTLOG:
        await usr.client.send_message(
            BOTLOG_CHATID,
            "#KICK\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {usr.chat.title}(`{usr.chat_id}`)\n",
        )


@bot.on(admin_cmd("undlt$"))
@bot.on(sudo_cmd(pattern="undlt$", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    c = await event.get_chat()
    if c.admin_rights or c.creator:
        a = await event.client.get_admin_log(
            event.chat_id, limit=5, edit=False, delete=True
        )
        deleted_msg = "Deleted message in this group:"
        for i in a:
            deleted_msg += "\n👉`{}`".format(i.old.message)
        await edit_or_reply(event, deleted_msg)
    else:
        await edit_or_reply(
            event, "`You need administrative permissions in order to do this command`"
        )
        await sleep(3)
        try:
            await event.delete()
        except:
            pass


async def get_user_from_event(event):
    args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.sender_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]
        if user.isnumeric():
            user = int(user)
        if not user:
            await event.edit("`Pass the user's username, id or reply!`")
            return
        if event.message.entities:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError):
            await event.edit("Could not fetch info of that user.")
            return None
    return user_obj, extra


async def get_user_from_id(user, event):
    if isinstance(user, str):
        user = int(user)
    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None
    return user_obj
    

# ALIVE

import asyncio
import random
from telethon import events
from userbot.utils import admin_cmd
from userbot import ALIVE_NAME, mafiaversion
from userbot.utils import admin_cmd, sudo_cmd
from telethon.tl.types import ChannelParticipantsAdmins

# 🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔
DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else "𝕄𝔸𝔽𝕀𝔸 𝕌𝕊𝔼ℝ𝔹𝕆𝕋"

# Thanks to Sipak bro and Raganork.. 
# animation Idea by @NOOB_GUY_OP (Sipakisking)
# Made by @ROMANTIC_KILLER...and thanks to @Crackexy for the logos...
# Kang with credits else gay...
# alive.py for ÂÝŮ$HópBØȚ

ludosudo = Config.SUDO_USERS

if ludosudo:
    sudou = "True"
else:
    sudou = "False"

mafia = bot.uid

edit_time = 10
""" =======================CONSTANTS====================== """
file1 = "https://telegra.ph/file/502d3b7372c1c395bba5a.mp4"
file2 = "https://telegra.ph/file/d938d8f4ecaf2d6e70d31.mp4"
file3 = "https://telegra.ph/file/52e33f519c5b932082298.mp4"
file4 = "https://telegra.ph/file/cfd9a3fa2c8a7aba0d5ab.jpg"
""" =======================CONSTANTS====================== """
pm_caption = "__**🔥🔥𝕄𝔸𝔽𝕀𝔸 𝕌𝕊𝔼ℝ𝔹𝕆𝕋 𝕀𝕊 𝔸𝕃𝕀𝕍𝔼🔥🔥**__\n\n"

pm_caption += (
    f"                 👑𝕄𝔸𝕊𝕋𝔼ℝ👑\n**  『😈[{DEFAULTUSER}](tg://user?id={mafia})😈』**\n\n"
)

pm_caption += "🛡️TELETHON🛡️ : `1.15.0` \n\n"

pm_caption += f"😈𝕄𝔸𝔽𝕀𝔸 𝕌𝕊𝔼ℝ𝔹𝕆𝕋😈 : `{mafiaversion}`\n\n"

pm_caption += f"😱Sudo😱            : `{sudou}`\n\n"

pm_caption += "😇CHANNEL😇️   : [ᴊᴏɪɴ](https://t.me/MAFIA_USERBOT)\n\n"

pm_caption += "😎CREATOR😎    : [Himanshu](https://t.me/H1M4N5HU0P)\n\n"

pm_caption += "🤩SUPPORTER🤩    :[HellBoy](https://t.me/kraken_the_badass)\n\n"

pm_caption += "      [🔥REPO🔥](https://github.com/H1M4N5HU0P/MAFIA-USERBOT) 🔹 [📜License📜](https://github.com/H1M4N5HU0P/MAFIA-USERBOT/blob/main/LICENSE)"

# @command(outgoing=True, pattern="^.alive$")
@bot.on(admin_cmd(outgoing=True, pattern="alive$"))
@bot.on(sudo_cmd(pattern="alive$", allow_sudo=True))
async def amireallyalive(alive):
    await alive.get_chat()   
    
    on = await borg.send_file(alive.chat_id, file=file1,caption=pm_caption)

    await asyncio.sleep(edit_time)
    ok = await borg.edit_message(alive.chat_id, on, file=file2) 

    await asyncio.sleep(edit_time)
    ok2 = await borg.edit_message(alive.chat_id, ok, file=file3)

    await asyncio.sleep(edit_time)
    ok3 = await borg.edit_message(alive.chat_id, ok2, file=file1)
    
    await asyncio.sleep(edit_time)
    ok4 = await borg.edit_message(alive.chat_id, ok3, file=file3)
    
    await asyncio.sleep(edit_time)
    ok5 = await borg.edit_message(alive.chat_id, ok4, file=file2)
    
    await asyncio.sleep(edit_time)
    ok6 = await borg.edit_message(alive.chat_id, ok5, file=file4)
    
    await asyncio.sleep(edit_time)
    ok7 = await borg.edit_message(alive.chat_id, ok6, file=file1)

    """ For .alive command, check if the bot is running.  """
    await borg.send_file(alive.chat_id, PM_IMG, caption=pm_caption)
    await alive.delete()


# GSPAM

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
    
    
# HEROKU

import asyncio
import math
import os

import heroku3
import requests

from userbot import CMD_HELP
from userbot.Config import Config
from userbot.utils import admin_cmd

# =================

Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
Heroku = heroku3.from_key(Var.HEROKU_API_KEY)
heroku_api = "https://api.heroku.com"
HEROKU_APP_NAME = Config.HEROKU_APP_NAME
HEROKU_API_KEY = Config.HEROKU_API_KEY

Heroku = heroku3.from_key(Var.HEROKU_API_KEY)
heroku_api = "https://api.heroku.com"


@borg.on(
    admin_cmd(pattern="(set|get|del) var(?: |$)(.*)(?: |$)([\s\S]*)", outgoing=True)
)
async def variable(var):
    """
    Manage most of ConfigVars setting, set new var, get current var,
    or delete var...
    """
    if Var.HEROKU_APP_NAME is not None:
        app = Heroku.app(Var.HEROKU_APP_NAME)
    else:
        return await var.edit("`[HEROKU]:" "\nPlease setup your` **HEROKU_APP_NAME**")
    exe = var.pattern_match.group(1)
    heroku_var = app.config()
    if exe == "get":
        await var.edit("`Getting information...`")
        await asyncio.sleep(1.5)
        try:
            variable = var.pattern_match.group(2).split()[0]
            if variable in heroku_var:
                return await var.edit(
                    "**ConfigVars**:" f"\n\n`{variable} = {heroku_var[variable]}`\n"
                )
            else:
                return await var.edit(
                    "**ConfigVars**:" f"\n\n`Error:\n-> {variable} don't exists`"
                )
        except IndexError:
            configs = prettyjson(heroku_var.to_dict(), indent=2)
            with open("configs.json", "w") as fp:
                fp.write(configs)
            with open("configs.json", "r") as fp:
                result = fp.read()
                if len(result) >= 4096:
                    await var.client.send_file(
                        var.chat_id,
                        "configs.json",
                        reply_to=var.id,
                        caption="`Output too large, sending it as a file`",
                    )
                else:
                    await var.edit(
                        "`[HEROKU]` ConfigVars:\n\n"
                        "================================"
                        f"\n```{result}```\n"
                        "================================"
                    )
            os.remove("configs.json")
            return
    elif exe == "set":
        await var.edit("`Setting information...weit ser`")
        variable = var.pattern_match.group(2)
        if not variable:
            return await var.edit(">`.set var <ConfigVars-name> <value>`")
        value = var.pattern_match.group(3)
        if not value:
            variable = variable.split()[0]
            try:
                value = var.pattern_match.group(2).split()[1]
            except IndexError:
                return await var.edit(">`.set var <ConfigVars-name> <value>`")
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await var.edit(
                f"**{variable}**  `successfully changed to`  ->  **{value}**"
            )
        else:
            await var.edit(
                f"**{variable}**  `successfully added with value`  ->  **{value}**"
            )
        heroku_var[variable] = value
    elif exe == "del":
        await var.edit("`Getting information to deleting variable...`")
        try:
            variable = var.pattern_match.group(2).split()[0]
        except IndexError:
            return await var.edit("`Please specify ConfigVars you want to delete`")
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await var.edit(f"**{variable}**  `successfully deleted`")
            del heroku_var[variable]
        else:
            return await var.edit(f"**{variable}**  `is not exists`")


@borg.on(admin_cmd(pattern="usage(?: |$)", outgoing=True))
async def dyno_usage(dyno):
    """
    Get your account Dyno Usage
    """
    await dyno.edit("`Processing...`")
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    user_id = Heroku.account().id
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {Var.HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + user_id + "/actions/get-quota"
    r = requests.get(heroku_api + path, headers=headers)
    if r.status_code != 200:
        return await dyno.edit(
            "`Error: something bad happened`\n\n" f">.`{r.reason}`\n"
        )
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]

    """ - Used - """
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)

    """ - Current - """
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)

    await asyncio.sleep(1.5)

    return await dyno.edit(
        "**Dyno Usage**:\n\n"
        f" -> `Dyno usage for`  **{Var.HEROKU_APP_NAME}**:\n"
        f"     •  `{AppHours}`**h**  `{AppMinutes}`**m**  "
        f"**|**  [`{AppPercentage}`**%**]"
        "\n\n"
        " -> `Dyno hours quota remaining this month`:\n"
        f"     •  `{hours}`**h**  `{minutes}`**m**  "
        f"**|**  [`{percentage}`**%**]"
    )


@borg.on(admin_cmd(pattern="logs$", outgoing=True))
async def _(dyno):
    try:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        app = Heroku.app(HEROKU_APP_NAME)
    except:
        return await dyno.reply(
            " Please make sure your Heroku API Key, Your App name are configured correctly in the heroku"
        )
    await dyno.edit("Getting Logs....")
    with open("logs.txt", "w") as log:
        log.write(app.get_log())
    await dyno.edit("Got the logs wait a sec")
    await dyno.client.send_file(
        dyno.chat_id,
        "logs.txt",
        reply_to=dyno.id,
        caption="Mafia Userbot logs of 100+ lines",
    )

    await asyncio.sleep(5)
    await dyno.delete()
    return os.remove("logs.txt")


def prettyjson(obj, indent=2, maxlinelength=80):
    """Renders JSON content with indentation and line splits/concatenations to fit maxlinelength.
    Only dicts, lists and basic types are supported"""

    items, _ = getsubitems(
        obj,
        itemkey="",
        islast=True,
        maxlinelength=maxlinelength - indent,
        indent=indent,
    )
    return indentitems(items, indent, level=0)


# INVITE

from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    ChannelPublicGroupNaError,
)
from telethon.tl import functions
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest

from userbot import CMD_HELP
from userbot.utils import admin_cmd, edit_or_reply, sudo_cmd


async def get_chatinfo(event):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await event.reply("`Invalid channel/group`")
            return None
        except ChannelPrivateError:
            await event.reply(
                "`This is a private channel/group or I am banned from there`"
            )
            return None
        except ChannelPublicGroupNaError:
            await event.reply("`Channel or supergroup doesn't exist`")
            return None
        except (TypeError, ValueError):
            await event.reply("`Invalid channel/group`")
            return None
    return chat_info


def user_full_name(user):
    names = [user.first_name, user.last_name]
    names = [i for i in list(names) if i]
    full_name = " ".join(names)
    return full_name


@bot.on(admin_cmd(pattern="inviteall ?(.*)"))
@bot.on(sudo_cmd(pattern="inviteall ?(.*)", allow_sudo=True))
async def get_users(event):
    sender = await event.get_sender()
    me = await event.client.get_me()
    if not sender.id == me.id:
        hell = await event.reply("`processing...`")
    else:
        hell = await event.edit("`processing...`")
    kraken = await get_chatinfo(event)
    chat = await event.get_chat()
    if event.is_private:
        return await hell.edit("`Sorry, Can add users here`")
    s = 0
    f = 0
    error = "None"

    await hell.edit("**TerminalStatus**\n\n`Collecting Users.......`")
    async for user in event.client.iter_participants(kraken.full_chat.id):
        try:
            if error.startswith("Too"):
                return await hell.edit(
                    f"**Terminal Finished With Error**\n(`May Got Limit Error from telethon Please try agin Later`)\n**Error** : \n`{error}`\n\n• Invited `{s}` people \n• Failed to Invite `{f}` people"
                )
            await event.client(
                functions.channels.InviteToChannelRequest(channel=chat, users=[user.id])
            )
            s = s + 1
            await hell.edit(
                f"**Terminal Running...**\n\n• Invited `{s}` people \n• Failed to Invite `{f}` people\n\n**× LastError:** `{error}`"
            )
        except Exception as e:
            error = str(e)
            f = f + 1
    return await hell.edit(
        f"**Terminal Finished** \n\n• Successfully Invited `{s}` people \n• failed to invite `{f}` people"
    )


@bot.on(admin_cmd(pattern="add ?(.*)"))
@bot.on(sudo_cmd(pattern="add ?(.*)", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    to_add_users = event.pattern_match.group(1)
    if event.is_private:
        await edit_or_reply(event, "`.add` users to a chat, not to a Private Message")
    else:
        logger.info(to_add_users)
        if not event.is_channel and event.is_group:
            # https://lonamiwebs.github.io/Telethon/methods/messages/add_chat_user.html
            for user_id in to_add_users.split(" "):
                try:
                    await borg(
                        functions.messages.AddChatUserRequest(
                            chat_id=event.chat_id, user_id=user_id, fwd_limit=1000000
                        )
                    )
                except Exception as e:
                    await event.reply(str(e))
            await edit_or_reply(event, "Invited Successfully")
        else:
            # https://lonamiwebs.github.io/Telethon/methods/channels/invite_to_channel.html
            for user_id in to_add_users.split(" "):
                try:
                    await borg(
                        functions.channels.InviteToChannelRequest(
                            channel=event.chat_id, users=[user_id]
                        )
                    )
                except Exception as e:
                    await event.reply(str(e))
            await edit_or_reply(event, "Added user to the chat....")


# MAFIA

import time

from userbot import ALIVE_NAME, StartTime, mafiaversion
from userbot.utils import admin_cmd, edit_or_reply, sudo_cmd


async def reply_id(event):
    reply_to_id = None
    if event.sender_id in Config.SUDO_USERS:
        reply_to_id = event.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    return reply_to_id


DEFAULTUSER = ALIVE_NAME or "Mafia User"
MAFIA_IMG = https://telegra.ph/file/502d3b7372c1c395bba5a.mp4
CUSTOM_ALIVE_TEXT = Config.ALIVE_MSG or "𝕃𝕖𝕘𝕖𝕟𝕕𝕒𝕣𝕪_𝔸𝔽_𝕄𝕒𝕗𝕚𝕒_𝕌𝕤𝕖𝕣𝕓𝕠𝕥"

USERID = bot.uid

mention = f"[{DEFAULTUSER}](tg://user?id={USERID})"


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


uptime = get_readable_time((time.time() - StartTime))


@bot.on(admin_cmd(outgoing=True, pattern="mafia$"))
@bot.on(sudo_cmd(pattern="mafia$", allow_sudo=True))
async def amireallyalive(alive):
    if alive.fwd_from:
        return
    reply_to_id = await reply_id(alive)

    if MAFIA_IMG:
        mafia_caption = f"**{CUSTOM_ALIVE_TEXT}**\n\n"
        mafia_caption += f"≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈\n"
        mafia_caption += f"__**𝔹𝕆𝕋 𝕊𝕋𝔸𝕋𝕌𝕊**__\n\n"
        mafia_caption += f"**★ 𝕋𝕖𝕝𝕖𝕥𝕙𝕠𝕟 𝕧𝕖𝕣𝕤𝕚𝕠𝕟 :** `1.15.0`\n"
        mafia_caption += f"**★ 𝕄𝔸𝔽𝕀𝔸 𝕌𝕊𝔼ℝ𝔹𝕆𝕋 :**`{mafiaversion}`\n"
        mafia_caption += f"**★ 𝕌𝕡𝕥𝕚𝕞𝕖 :** `{uptime}\n`"
        mafia_caption += f"**★ 𝕄𝕒𝕤𝕥𝕖𝕣 :** {mention}\n"
        await alive.client.send_file(
            alive.chat_id, MAFIA_IMG, caption=mafia_caption, reply_to=reply_to_id
        )
        await alive.delete()
    else:
        await edit_or_reply(
            alive,
            f"**{CUSTOM_ALIVE_TEXT}**\n\n"
            f"≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈ \n"
            f"__**𝔹𝕆𝕋 𝕊𝕋𝔸𝕋𝕌𝕊**__\n\n"
            f"**★ 𝕋𝕖𝕝𝕖𝕥𝕙𝕠𝕟 𝕧𝕖𝕣𝕤𝕚𝕠𝕟 :** `1.15.0`\n"
            f"**★ 𝕄𝔸𝔽𝕀𝔸 𝕌𝕊𝔼ℝ𝔹𝕆𝕋 :** `{mafiaversion}`\n"
            f"**★ 𝕌𝕡𝕥𝕚𝕞𝕖 :** `{uptime}\n`"
            f"**★ 𝕄𝕒𝕤𝕥𝕖𝕣 :** {mention}\n",
        )


# PING

import asyncio
from datetime import datetime

from .. import ALIVE_NAME, CMD_HELP
from ..utils import admin_cmd, edit_or_reply, sudo_cmd

DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else "Mafia User"
kraken = borg.uid


@bot.on(admin_cmd(pattern=f"hbping$", outgoing=True))
@bot.on(sudo_cmd(pattern=f"hbping$", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    start = datetime.now()
    animation_interval = 0.2
    animation_ttl = range(0, 26)
    await event.edit("ping....")
    animation_chars = [
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ ",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ ",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛⬛‎📶‎📶‎📶‎📶‎📶⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛⬛‎📶‎📶‎📶‎📶‎📶⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛⬛‎📶‎📶‎📶‎📶‎📶⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛⬛‎📶‎📶‎📶‎📶‎📶⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛‎📶⬛⬛⬛‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛⬛‎📶‎📶‎📶‎📶‎📶⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛‎📶⬛⬛⬛‎📶⬛ \n⬛⬛‎📶‎📶⬛⬛‎📶⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛⬛‎📶‎📶‎📶‎📶‎📶⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛‎📶⬛⬛⬛‎📶⬛ \n⬛⬛‎📶‎📶⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛⬛‎📶‎📶‎📶‎📶‎📶⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛‎📶⬛⬛⬛‎📶⬛ \n⬛⬛‎📶‎📶⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛‎📶‎📶‎📶‎📶‎📶⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛⬛‎📶‎📶‎📶‎📶‎📶⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛‎📶⬛⬛⬛‎📶⬛ \n⬛⬛‎📶‎📶⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛",
        "⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛‎📶⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛‎📶‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛‎📶⬛⬛⬛ \n⬛⬛⬛⬛‎📶⬛⬛⬛⬛ \n⬛‎📶‎📶‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛⬛‎📶‎📶‎📶‎📶‎📶⬛⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛⬛⬛⬛⬛‎📶⬛ \n⬛‎📶⬛‎📶⬛⬛⬛‎📶⬛ \n⬛⬛‎📶‎📶⬛⬛‎📶⬛⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n⬛‎📶⬛‎📶‎📶‎📶‎📶‎📶⬛ \n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n \n My 🇵 🇮 🇳 🇬  Is : Calculating...",
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await event.edit(animation_chars[i % 26])
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await event.edit(
        "‎‎‎‎‎‎‎‎‎⬛⬛⬛⬛⬛⬛⬛⬛⬛\n⬛📶📶📶📶📶📶📶⬛\n⬛⬛⬛⬛📶⬛⬛📶⬛\n⬛⬛⬛⬛📶⬛⬛📶⬛\n⬛⬛⬛⬛📶⬛⬛📶⬛\n⬛⬛⬛⬛⬛📶📶⬛⬛\n⬛⬛⬛⬛⬛⬛⬛⬛⬛\n⬛⬛📶📶📶📶📶⬛⬛\n⬛📶⬛⬛⬛⬛⬛📶⬛\n⬛📶⬛⬛⬛⬛⬛📶⬛\n⬛📶⬛⬛⬛⬛⬛📶⬛\n⬛⬛📶📶📶📶📶⬛⬛\n⬛⬛⬛⬛⬛⬛⬛⬛⬛\n⬛📶📶📶📶📶📶📶⬛\n⬛⬛⬛⬛⬛⬛📶⬛⬛\n⬛⬛⬛⬛⬛📶⬛⬛⬛\n⬛⬛⬛⬛📶⬛⬛⬛⬛\n⬛📶📶📶📶📶📶📶⬛\n⬛⬛⬛⬛⬛⬛⬛⬛⬛\n⬛⬛📶📶📶📶📶⬛⬛\n⬛📶⬛⬛⬛⬛⬛📶⬛\n⬛📶⬛⬛⬛⬛⬛📶⬛\n⬛📶⬛📶⬛⬛⬛📶⬛\n⬛⬛📶📶⬛⬛📶⬛⬛\n⬛⬛⬛⬛⬛⬛⬛⬛⬛\n⬛📶⬛📶📶📶📶📶⬛\n⬛⬛⬛⬛⬛⬛⬛⬛⬛ \n‎‎‎‎‎‎‎‎‎ \n \n My 🇵 🇮 🇳 🇬  Is : {} ms".format(
            ms
        )
    )


@bot.on(admin_cmd(pattern="ping$"))
@bot.on(sudo_cmd(pattern=f"ping$", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    start = datetime.now()
    event = await edit_or_reply(event, "__**(❛ ᑭσɳց ❜!__**")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await event.edit(
        f"__**꧁ Pong! ꧂__**\n\n   ⚘ {ms}\n   ⚘ __**My**__ __**Master**__ [{DEFAULTUSER}](tg://user?id={kraken})"
    )


# SPAM

import asyncio
import base64
import os

from telethon import functions, types
from telethon.tl.functions.messages import ImportChatInviteRequest as Get

from userbot.utils import admin_cmd, sudo_cmd, edit_or_reply
from userbot.cmdhelp import CmdHelp


@bot.on(admin_cmd(pattern="spam (.*)"))
@bot.on(sudo_cmd(pattern="spam (.*)", allow_sudo=True))
async def spammer(e):
    if not e.text[0].isalpha() and e.text[0] not in ("/", "#", "@", "!"):
        message = e.text
        counter = int(message[6:8])
        spam_message = str(e.text[8:])
        await asyncio.wait([e.respond(spam_message) for i in range(counter)])
        await e.delete()
        if LOGGER:
            await e.client.send_message(
                LOGGER_GROUP, "#SPAM \n\n" "Spam was executed successfully"
            )


@bot.on(admin_cmd(pattern="bigspam"))
@bot.on(sudo_cmd(pattern="bigspam", allow_sudo=True))
async def bigspam(mafia):
    if not mafia.text[0].isalpha() and mafia.text[0] not in ("/", "#", "@", "!"):
        mafia_msg = mafia.text
        mafiabot_count = int(mafia_msg[9:13])
        mafia_spam = str(mafia.text[13:])
        for i in range(1, mafiabot_count):
            await mafia.respond(mafia_spam)
        await mafia.delete()
        if LOGGER:
            await mafia.client.send_message(
                LOGGER_GROUP, "#BIGSPAM \n\n" "Bigspam was executed successfully"
            )


@bot.on(admin_cmd("dspam (.*)"))
@bot.on(sudo_cmd(pattern="dspam (.*)", allow_sudo=True))
async def spammer(e):
    if e.fwd_from:
        return
    input_str = "".join(e.text.split(maxsplit=1)[1:])
    spamDelay = float(input_str.split(" ", 2)[0])
    counter = int(input_str.split(" ", 2)[1])
    spam_message = str(input_str.split(" ", 2)[2])
    await e.delete()
    for _ in range(counter):
        await e.respond(spam_message)
        await asyncio.sleep(spamDelay)


#@register(outgoing=True, pattern="^.mspam (.*)")
@bot.on(admin_cmd(pattern="mspam (.*)"))
@bot.on(sudo_cmd(pattern="mspam (.*)", allow_sudo=True))
async def tiny_pic_spam(e):

    sender = await e.get_sender()
    me = await e.client.get_me()

    if not sender.id == me.id and not FULL_SUDO:

        return await e.reply("`Sorry sudo users cant access this command..`")

    try:

        await e.delete()

    except:

        pass

    try:

        counter = int(e.pattern_match.group(1).split(" ", 1)[0])

        reply_message = await e.get_reply_message()

        if (
            not reply_message
            or not e.reply_to_msg_id
            or not reply_message.media
            or not reply_message.media
        ):

            return await e.edit("```Reply to a pic/sticker/gif/video message```")

        message = reply_message.media

        for i in range(1, counter):

            await e.client.send_file(e.chat_id, message)

    except:

        return await e.reply(
            f"**Error**\nUsage `!mspam <count> reply to a sticker/gif/photo/video`"
        )
        
        
# POWER TOOLS

import os
import sys

from uniborg.util import admin_cmd


@borg.on(admin_cmd(pattern="restart"))
async def _(event):
    if event.fwd_from:
        return
    # await asyncio.sleep(2)
    # await event.edit("Restarting [██░] ...\n`.ping` me or `.helpme` to check if I am online")
    # await asyncio.sleep(2)
    # await event.edit("Restarting [███]...\n`.ping` me or `.helpme` to check if I am online")
    # await asyncio.sleep(2)
    await event.edit("Restarted. `.ping` me or `.helpme` to check if I am online")
    await borg.disconnect()
    # https://archive.is/im3rt
    os.execl(sys.executable, sys.executable, *sys.argv)
    # You probably don't need it but whatever
    quit()


@borg.on(admin_cmd(pattern="shutdown"))
async def _(event):
    if event.fwd_from:
        return
    await event.edit("Turning off ...Manually turn me on later")
    await borg.disconnect()


#HELP 

import random, re
from uniborg.util import admin_cmd
import asyncio
from telethon import events

@borg.on(admin_cmd(pattern="help ?(.*)"))
async def _(event):
     if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        await event.edit("🔥🔥FIGHT BOT COMMANDS🔥🔥\n\n\n\n#ADMIN COMMANDS\n\nsetgpic\npromote\ndemote\nban\nunban\nmute\nunmute\nkick\npin\ncpin\nundlt\n\n\n#ALIVE COMMANDS\n\nalive\nmafia\n\n\n#GSPAM COMMANDS\n\ngspam\n\n\n#HEROKU COMMANDS\n\nset/get/del var\nusage\nlogs\n\n\n#INVITE COMMANDS\n\nadd\ninviteall\n\n\n#PING COMMANDS\n\nhbping\nping\n\n\n#POWER TOOL COMMANDS\n\nrestart\nshutdown\n\n\n#QBOT COMMANDS\n\nqbot\n\n\n#SPAM COMMANDS\n\nspam\nbigspam\ndspam\nmspam")
        
        
# FIGHT K LIYE KAAFIII HAII BAHENCHOD

# MAFIA FIGHT BOT