import discord
from discord.ext import commands
from config import *
import json
import asyncio
devMode = False

#main config for dev testing
if devMode == True:
    token = config["devtoken"]
    prefix = config["devprefix"]
    modLogChannel = config["devmodlog-channel"]
else:
    token = config["token"]
    prefix = config["prefix"]
    modLogChannel = config["modlog-channel"]

bot = commands.Bot(command_prefix=prefix, help_command=None)
devId = config["dev-id"]




#success and error embeds
async def errorEmbed(message, error):
    embed = discord.Embed(color=0xf90000)
    embed.add_field(name="Oops!", value=error, inline=False)
    await message.send(embed=embed)

async def successEmbed(message, success):
    embed = discord.Embed(color=0x00ff00)
    embed.add_field(name="Success", value=success, inline=False)
    await message.send(embed=embed)




#auto moderation
async def checkBanned(message, userId, serverId):
    #check if server is banned
    data = json.load(open("serverbanned.json", "r"))
    for ii in data["servers"]:
        if ii["server-id"] == serverId:
            await message.channel.send("This server is currently banned from broadcasting global messages, {}".format(message.author.mention))
            return True
    #check if user is banned
    data = json.load(open("userbanned.json", "r"))
    for ii in data["users"]:
        if ii["user-id"] == userId:
            await message.channel.send("You are currently banned from broadcasting global messages, {}".format(message.author.mention))
            return True

async def checkMessage(message,args):
    #check if args includes a filtered word
    data = json.load(open("wordfiltered.json", "r"))
    args = args.lower()
    for ii in data["filtered"]:
        if ii["word"] in args:
            embedColor = 0x00ffb7
            args = "Filtered: `" + ii["word"] + "`"
            await globalModLog(message, args, embedColor)
            await message.channel.send("Your message has been blocked, {}".format(message.author.mention))
            return True
    #check if args is < 0 chars or > maxchars
    length = len(args)
    if length == 0:
        await message.channel.send("Your message cannot be `{0}` characters, {1}\nIf your message is an image or file, they are currently not supported".format(length, message.author.mention))
        return True
    elif message.author.id == devId:
        return False
    elif length > config["maxchars"]:
        await message.channel.send("You cannot use more than `{0}` characters, {1}".format(config["maxchars"], message.author.mention))
        return True




#set global message embed colour
async def globalColour(embed, guildId):
    data = json.load(open("globalcolours.json", "r"))
    for guild in data["guild"]:
        if guild["guild-id"] == guildId:
            embed.colour = discord.Colour(guild["colour-id"])
        else:
            continue




#send global message
async def sendGlobal(message, args):
    data = json.load(open("globalchannels.json", "r"))
    userName = message.author.name
    guildName = message.guild.name
    guildId = message.guild.id
    
    embed = discord.Embed(description=args)
    await globalColour(embed, guildId)
    embed.set_author(name=userName + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
    embed.set_footer(text="Sent from: " + guildName, icon_url=message.guild.icon_url)

    for ii in data["channels"]:
        channel = bot.get_channel(ii["channel-id"])
        if channel == None:
            print("Count find the channel: " + str(ii["channel-id"]))
            continue
        if channel == message.channel:
            continue
        msg = await channel.send(embed=embed)
        await msg.add_reaction("<:Candycane:790230261660385320>") #christmas

    embedColor = 0x00ffb7
    await globalModLog(message, args, embedColor)




#send global announcement
async def sendAnnouncement(message, args, guildName):
    data = json.load(open("globalchannels.json", "r"))

    embed = discord.Embed(color=0x00bfff)
    embed.add_field(name=":mega:  Global Announcement", value=args)
    embed.set_footer(text="Sent from: " + guildName)

    for ii in data["channels"]:
        channel = bot.get_channel(ii["channel-id"])
        if channel == None:
            print("Count find the channel: " + str(ii["channel-id"]))
            continue
        await channel.send(embed=embed)

    args = "Announcement: `" + args + "`"
    embedColor = 0x00bfff
    await globalModLog(message, args, embedColor)




#global moderation log
async def globalModLog(message, args, embedColor):
    guildId = str(message.guild.id)
    guildName = message.guild.name
    userId = str(message.author.id)
    userName = message.author.name

    channel = bot.get_channel(modLogChannel)
    embed = discord.Embed(color=embedColor, description=args)
    embed.set_author(name=userName + "#" + message.author.discriminator + " | " + userId, icon_url=message.author.avatar_url)
    embed.set_footer(text="Sent from: " + guildName + " | " + guildId)
    await channel.send(embed=embed)




#json position grabber
def globalPosition(channelId):
    position = 0
    data = json.load(open("globalchannels.json", "r"))

    for ii in data["channels"]:
        if ii["channel-id"] == channelId:
            return position

        position += 1

def banUserPosition(userId):
    position = 0
    data = json.load(open("userbanned.json", "r"))

    for ii in data["users"]:
        if ii["user-id"] == userId:
            return position

        position += 1

def banServerPosition(serverId):
    position = 0
    data = json.load(open("serverbanned.json", "r"))

    for ii in data["servers"]:
        if ii["server-id"] == serverId:
            return position

        position += 1

def filterWordPosition(filterWord):
    position = 0
    data = json.load(open("wordfiltered.json", "r"))

    for ii in data["filtered"]:
        if ii["word"] == filterWord:
            return position

        position += 1

def globalColourPosition(guildId):
    position = 0
    data = json.load(open("globalcolours.json", "r"))

    for ii in data["guild"]:
        if ii["guild-id"] == guildId:
            return position

        position += 1




#general thingys
@bot.event
async def on_connect():
    print("Connected to the discord servers!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} - {bot.user.id}")
    while True:
        totalGuilds = str(len(bot.guilds))
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name= totalGuilds + " guilds! | {0}help".format(bot.command_prefix)))
        await asyncio.sleep(30)

@bot.check
async def globally_block_dms(message):
    return message.guild is not None

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            welcomePage = """
**Thanks for adding me! :smile:**

-My prefix is `{1}`.
-To get started, type `{1}setup` in a channel and follow the simple step by step guide!

-You can see a list of available commands by typing `{1}help`.
-This bot is still in early development so if you find any bugs, report them to Laith#0617!

*If your server has an NSFW icon the server will get banned from global channels.*
            """.format(bot.user.name, bot.command_prefix)
            await channel.send(welcomePage)

        break

@bot.event
async def on_message(message):
    data = json.load(open("globalchannels.json", "r"))
    channel = message.channel.id

    if message.author == bot.user:
        return
    if message.author.bot:
        return

    for ii in data["channels"]:
        if ii["channel-id"] == channel:

            args = str(message.content)
            userId = int(message.author.id)
            serverId = message.guild.id

            if await checkBanned(message, userId, serverId) == True:
                return
            elif await checkMessage(message, args) == True:
                return
            else:
                await sendGlobal(message, args)

    await bot.process_commands(message)

@bot.command()
async def help(message):
    guildId = message.guild.id

    helpPage = """
`{0}help` - General help page
`{0}setup` - How to setup the bot
`{0}bind` - Bind the global chat to the current channel
`{0}unbind` - Unbind the global chat from the current channel
`{0}setcolour <hexadecimal>` - Set the global embed colour for this server
`{0}resetcolour` - Reset the global embed colour for this server
`{0}invite` - Invite this bot to your server

*This bot can be found on top.gg [here](https://top.gg/bot/747929473495859241)!*
    """.format(bot.command_prefix)

    embed = discord.Embed(timestamp=message.message.created_at)
    await globalColour(embed, guildId)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.add_field(name=":tools: Help", value=helpPage, inline=False)
    embed.set_footer(text="Report bugs to Laith#0617")
    await message.send(embed=embed)

@bot.command()
async def setup(message):
    guildId = message.guild.id

    embed = discord.Embed()
    await globalColour(embed, guildId)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.add_field(name=":hammer: Setup", value="Create a channel that will be dedicated for GlobalMsg, then use `{0}bind` to bind the global chat to the channel".format(bot.command_prefix), inline=False)
    await message.send(embed=embed)

@bot.command()
async def invite(message):
    guildId = message.guild.id

    text=f"""
Use [this link](https://top.gg/bot/747929473495859241/invite) to directly invite this bot to your server.
{bot.user.name} can also be found on top.gg [here](https://top.gg/bot/747929473495859241)!
    """

    embed = discord.Embed(timestamp=message.message.created_at)
    await globalColour(embed, guildId)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.add_field(name=":envelope: Invite the bot", value=text, inline=False)
    await message.send(embed=embed)




#bind global text to a channel
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def bind(message):
    channelId = message.channel.id
    guildId = message.guild.id
    data = json.load(open("globalchannels.json", "r"))

    for ii in data["channels"]:
        if ii["channel-id"] == channelId and ii["guild-id"] == guildId:
            error = "Global chat is already bound to `{}`!".format(message.channel.name)
            await errorEmbed(message, error)
            return

    data["channels"].append(
        {
            "channel-id": channelId,
            "guild-id": guildId
        }
    )
    json.dump(data, open("globalchannels.json", "w"), indent=4)

    success = "Global chat has been bound to `{}`!".format(message.channel.name)
    await successEmbed(message, success)

    args = "Global chat has been bound to `{0}` | `{1}`!".format(message.channel.name, message.channel.id)
    embedColor = 0xa900da
    await globalModLog(message, args, embedColor)

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def unbind(message):
    channelId = message.channel.id
    guildId = message.guild.id
    data = json.load(open("globalchannels.json", "r"))

    for ii in data["channels"]:
        if ii["channel-id"] == channelId and ii["guild-id"] == guildId:
            data["channels"].pop(globalPosition(channelId))
            json.dump(data, open("globalchannels.json", "w"), indent=4)

            success = "Global chat has been unbound from `{}`!".format(message.channel.name)
            await successEmbed(message, success)
    
            args = "Global chat has been unbound from `{0}` | `{1}`!".format(message.channel.name, message.channel.id)
            embedColor = 0xa900da
            await globalModLog(message, args, embedColor)




#global user ban
@bot.command()
async def globalban(message, arg):
    arg = arg.strip("<@!>")
    userId = int(arg)

    if message.author.id == devId:
        data = json.load(open("userbanned.json", "r"))

        for ii in data["users"]:
            if ii["user-id"] == userId:
                error = "That user is already banned!"
                await errorEmbed(message, error)
                return

        data["users"].append(
            {
                "user-id": userId,
            }
        )
        json.dump(data, open("userbanned.json", "w"), indent=4)

        success = "That user has been banned!"
        await successEmbed(message, success)

        args = "Banned user-id `{}` from the global chat!".format(userId)
        embedColor = 0xff0019
        await globalModLog(message, args, embedColor)
    else:
        error = "This command is only for the developer!"
        await errorEmbed(message, error)

@bot.command()
async def globalunban(message, arg):
    arg = arg.strip("<@!>")
    userId = int(arg)
    data = json.load(open("userbanned.json", "r"))

    if message.author.id == devId:
        for ii in data["users"]:
            if ii["user-id"] == userId:
                data["users"].pop(banUserPosition(userId))
                json.dump(data, open("userbanned.json", "w"), indent=4)

                success = "That user has been unbanned!"
                await successEmbed(message, success)

                args = "Unbanned user-id `{}` from the global chat!".format(userId)
                embedColor = 0xff0019
                await globalModLog(message, args, embedColor)
    else:
        error = "This command is only for the developer!"
        await errorEmbed(message, error)




#global server ban
@bot.command()
async def globalserverban(message, arg):
    serverId = int(arg)

    if message.author.id == devId:
        data = json.load(open("serverbanned.json", "r"))

        for ii in data["servers"]:
            if ii["server-id"] == serverId:
                error = "That server is already banned!"
                await errorEmbed(message, error)
                return

        data["servers"].append(
            {
                "server-id": serverId,
            }
        )
        json.dump(data, open("serverbanned.json", "w"), indent=4)

        success = "That server has been banned!"
        await successEmbed(message, success)

        args = "Banned guild-id `{}` from the global chat!".format(serverId)
        embedColor = 0xff0019
        await globalModLog(message, args, embedColor)
    else:
        error = "This command is only for the developer!"
        await errorEmbed(message, error)

@bot.command()
async def globalserverunban(message, arg):
    serverId = int(arg)
    data = json.load(open("serverbanned.json", "r"))

    if message.author.id == devId:
        for ii in data["servers"]:
            if ii["server-id"] == serverId:
                data["servers"].pop(banServerPosition(serverId))
                json.dump(data, open("serverbanned.json", "w"), indent=4)

                success = "That server has been unbanned!"
                await successEmbed(message, success)

                args = "Unbanned guild-id `{}` from the global chat!".format(serverId)
                embedColor = 0xff0019
                await globalModLog(message, args, embedColor)
    else:
        error = "This command is only for the developer!"
        await errorEmbed(message, error)




#filter
@bot.command()
async def filteradd(message, arg):
    filterWord = arg

    if message.author.id == devId:
        data = json.load(open("wordfiltered.json", "r"))

        for ii in data["filtered"]:
            if ii["word"] == filterWord:
                error = "That word is already filtered!"
                await errorEmbed(message, error)
                return

        data["filtered"].append(
            {
                "word": filterWord,
            }
        )
        json.dump(data, open("wordfiltered.json", "w"), indent=4)

        success = "That word will now be filtered!"
        await successEmbed(message, success)

        args = "Added `{}` to the filter!".format(filterWord)
        embedColor = 0xed74b7
        await globalModLog(message, args, embedColor)
    else:
        error = "This command is only for the developer!"
        await errorEmbed(message, error)

@bot.command()
async def filterremove(message, arg):
    filterWord = arg
    data = json.load(open("wordfiltered.json", "r"))

    if message.author.id == devId:
        for ii in data["filtered"]:
            if ii["word"] == filterWord:
                data["filtered"].pop(filterWordPosition(filterWord))
                json.dump(data, open("wordfiltered.json", "w"), indent=4)

                success = "That word will no longer be filtered!"
                await successEmbed(message, success)

                args = "Removed `{}` from the filter!".format(filterWord)
                embedColor = 0xed74b7
                await globalModLog(message, args, embedColor)
    else:
        error = "This command is only for the developer!"
        await errorEmbed(message, error)




#developer help
@bot.command()
async def devhelp(message):
    if message.author.id == devId:
        guildId = message.guild.id

        devHelpPage= """
`{0}devhelp` - Help page for the developer
`{0}announce <message>` - Send a global announcement
`{0}globalban <ping/user-id>` - Ban a user from global messaging
`{0}globalserverban <server-id>` - Ban an entire server from global messaging
`{0}filteradd <word>` - Add a word to the filter
`{0}globalunban <ping/user-id>` - Unban a user from global messaging
`{0}globalserverunban <server-id>`  -Unban an entire server from global messaging
`{0}filterremove <word>` - Remove a word from the filter
        """.format(bot.command_prefix)

        embed = discord.Embed(timestamp=message.message.created_at)
        await globalColour(embed, guildId)
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        embed.add_field(name=":tools: Developer Help", value=devHelpPage, inline=False)
        embed.set_footer(text="Report bugs to Laith#0617")
        await message.send(embed=embed)
    else:
        error = "This command is only for the developer!"
        await errorEmbed(message, error)




#global announcement
@bot.command()
async def announce(message, *args):
    args = " ".join(args[:])
    guildName = message.guild.name

    if message.author.id == devId:
        await sendAnnouncement(message, args, guildName)
    else:
        error = "This command is only for the developer!"
        await errorEmbed(message, error)




#embed colour
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def setcolour(message, arg):
    guildId = message.guild.id
    arg = "0x" + arg
    colourId = int(arg, 0)
    if colourId > 16777215:
        error = "`{0}` is more than `16777215`. Try using hexadecimal!".format(colourId)
        await errorEmbed(message, error)
        return
    data = json.load(open("globalcolours.json", "r"))

    for guild in data["guild"]:
        if guild["guild-id"] == guildId:
            error = "The embed colour has already been set to `{0}` for this server,\nIf you wish to change your colour, type `{1}resetcolour` first!".format(guild["colour-id"], bot.command_prefix)
            await errorEmbed(message, error)
            return

    data["guild"].append(
        {
            "guild-id": guildId,
            "colour-id": colourId
        }
    )
    json.dump(data, open("globalcolours.json", "w"), indent=4)

    success = "The embed colour for this server has been set to `{0}`!".format(arg)
    await successEmbed(message, success)

    args = "Embed colour has been set to `{0}` | `{1}`!".format(arg, colourId)
    embedColor = 0xa900da
    await globalModLog(message, args, embedColor)

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def resetcolour(message):
    guildId = message.guild.id
    data = json.load(open("globalcolours.json", "r"))

    for ii in data["guild"]:
        if ii["guild-id"] == guildId:
            data["guild"].pop(globalColourPosition(guildId))
            json.dump(data, open("globalcolours.json", "w"), indent=4)

            success = "The embed colour for this server has been reset!"
            await successEmbed(message, success)

            args = "Reset guild embed colour!"
            embedColor = 0xa900da
            await globalModLog(message, args, embedColor)

bot.run(token)