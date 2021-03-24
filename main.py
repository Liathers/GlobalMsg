import discord
from discord.ext import commands
import json
from config import *

if config["debugMode"]:
    token = config["debugToken"]
    prefix = config["debugPrefix"]
    modLogChannel = config["debugModlog-channel"]
else:
    token = config["token"]
    prefix = config["prefix"]
    modLogChannel = config["modlog-channel"]

devId = config["dev-id"]
client = commands.Bot(command_prefix=prefix, help_command=None)


async def successEmbed(message, successArgs):
    embed = discord.Embed(color=0x00ff00)
    embed.add_field(name="Success", value=successArgs, inline=False)
    await message.channel.send(embed=embed)


async def errorEmbed(message, errorArgs):
    embed = discord.Embed(color=0xf90000)
    embed.add_field(name="Oops!", value=errorArgs, inline=False)
    await message.channel.send(embed=embed)


async def sysErrorEmbed(message, errorArgs):
    embed = discord.Embed(color=0xf90000)
    embed.add_field(name="Oops, unknown error!", value=errorArgs, inline=False)
    embed.set_footer(text="Please report this to Laith#0617!")
    await message.send(embed=embed)


async def loadDatabase():
    global data
    data = json.load(open("./database/database.json", "r"))


async def appendDatabase(data):
    json.dump(data, open("./database/database.json", "w"), indent=4)


async def checkDatabaseEntry(message, guildId, channelId):
    global embedColour
    global prefix
    await loadDatabase()
    for ii in data["guilds"]:
        if ii["channel-id"] == channelId:
            errorArgs = f"Global chat is already bound to `{message.channel.name}`!"
            await errorEmbed(message, errorArgs)
            return False
        elif ii["guild-id"] == guildId:
            embedColour = ii["embed-colour"]
            prefix = ii["prefix"]
            guildBanned = ii["guild-banned"]
            await deleteDatabaseEntry(guildId)
            await addDatabaseEntry(channelId, guildId, embedColour, prefix, guildBanned)
            successArgs = f"Global chat has been bound to `{message.channel.name}`!"
            await successEmbed(message, successArgs)
            logArgs = f"Global chat bound to `{message.channel.name}`"
            await sendModerationLog(message, logArgs)
            return False


async def deleteDatabaseEntry(guildId):
    await loadDatabase()
    for ii in data["guilds"]:
        if ii["guild-id"] == guildId:
            data["guilds"].pop(getDatabaseEntryPosition(guildId))
            await appendDatabase(data)


async def addDatabaseEntry(channelId, guildId, embedColour, prefix, guildBanned):
    await loadDatabase()
    data["guilds"].append(
        {
            "channel-id": channelId,
            "guild-id": guildId,
            "embed-colour": embedColour,
            "prefix": prefix,
            "guild-banned": guildBanned
        }
    )
    await appendDatabase(data)


def getDatabaseEntryPosition(guildId):
    position = 0
    data = json.load(open("./database/database.json", "r"))

    for ii in data["guilds"]:
        if ii["guild-id"] == guildId:
            return position

        position += 1


def getDatabaseUserEntryPosition(userId):
    position = 0
    data = json.load(open("./database/database.json", "r"))

    for ii in data["users"]:
        if ii["user-id"] == userId:
            return position

        position += 1


def getDatabaseWordEntryPosition(filterWord):
    position = 0
    data = json.load(open("./database/database.json", "r"))

    for ii in data["profanities"]:
        if ii["word"] == filterWord:
            return position

        position += 1


async def getDatabaseEmbedColour(embed, guildId):
    await loadDatabase()
    for ii in data["guilds"]:
        if ii["guild-id"] == guildId:
            embed.colour = discord.Colour(ii["embed-colour"])
        else:
            continue


async def moderateGlobalMessage(message, args):
    await loadDatabase()
    userName = message.author.name
    userId = message.author.id
    guildId = message.guild.id
    length = len(args)
    for ii in data["users"]:
        if userId == ii["user-id"]:
            await message.channel.send(
                f"You are currently banned from broadcasting global messages, {message.author.mention}")
            return True
    for ii in data["guilds"]:
        if guildId == ii["guild-id"] and ii["guild-banned"] == True:
            await message.channel.send(
                f"This server is currently banned from broadcasting global messages, {message.author.mention}")
            return True
    for ii in data["profanities"]:
        if ii["word"] in userName.lower():
            await message.channel.send(f"Your username has been blocked, {message.author.mention}")
            logArgs = f"Filtered username: `{userName}`"
            await sendModerationLog(message, logArgs)
            return True
        if ii["word"] in args.lower():
            await message.channel.send(f"Your message has been blocked, {message.author.mention}")
            logArgs = f"Filtered message: `{args}`"
            await sendModerationLog(message, logArgs)
            return True
    if length == 0:
        await message.channel.send(
            f"Your message cannot be `{length}` characters, {message.author.mention}\nIf your message is an image or file, they are currently not supported")
        return True
    elif length > config["maxchars"] and userId != devId:
        await message.channel.send(
            "You cannot use more than `{0}` characters, {1}".format(config["maxchars"], message.author.mention))
        return True


async def sendGlobalMessage(message, args):
    await loadDatabase()
    userName = message.author.name
    guildName = message.guild.name
    guildId = message.guild.id

    embed = discord.Embed(description=args)
    await getDatabaseEmbedColour(embed, guildId)
    embed.set_author(name=userName + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
    embed.set_footer(text="Sent from: " + guildName, icon_url=message.guild.icon_url)

    logArgs = f"User said: {args}"
    await sendModerationLog(message, logArgs)

    for ii in data["guilds"]:
        channel = client.get_channel(ii["channel-id"])
        if channel == None:
            print("Count find the channel: " + str(ii["channel-id"]) + " for guild: " + str(ii["guild-id"]))
            continue
        elif channel == message.channel:
            continue
        else:
            try: await channel.send(embed=embed)
            except: pass


async def sendModerationLog(message, logArgs):
    guildId = message.guild.id
    channel = client.get_channel(modLogChannel)

    embed = discord.Embed(title="Moderation Log")
    await getDatabaseEmbedColour(embed, guildId)
    embed.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
    embed.add_field(name="Info",value=">User name: `" + message.author.name + "#" + message.author.discriminator + "`\n >User id: `" + str(message.author.id) + "`\n>\n>Guild name: `" + message.guild.name + "`\n>Guild id: `" + str(message.guild.id) + "`", inline=False)
    embed.add_field(name="Action", value=logArgs, inline=False)
    embed.set_footer(text=client.user.name, icon_url=client.user.avatar_url)
    await channel.send(embed=embed)


@client.event
async def on_connect():
    print("Connected to the discord servers!")


@client.event
async def on_ready():
    print(f"Logged in as {client.user.name} - {client.user.id}")
    while True:
        totalGuilds = str(len(client.guilds))
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=totalGuilds + " servers! | {0}help".format(client.command_prefix)))


@client.check
async def globally_block_dms(message):
    return message.guild is not None


@client.event
async def on_command_error(message, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        errorArgs = "That command wasn't found!"
        await errorEmbed(message, errorArgs)
        return
    elif isinstance(error, commands.MissingAnyRole):
        errorArgs = "You do not have the required permissions to perform this command!"
        await errorEmbed(message, errorArgs)
        return
    else:
        errorArgs = str(error)
        await sysErrorEmbed(message, errorArgs)
        return


@client.event
async def on_message(message):
    await loadDatabase()
    channelId = message.channel.id
    args = str(message.content)

    if message.author.bot:
        return
    if message.author == client.user:
        return

    await client.process_commands(message)

    for ii in data["guilds"]:
        if ii["channel-id"] == channelId:
            if await moderateGlobalMessage(message, args) != True:
                await sendGlobalMessage(message, args)


@client.command()
async def help(message):
    guildId = message.guild.id
    helpPage = """
`{0}help` - General help page
`{0}setup` - How to setup the bot
`{0}bind` - Bind the global chat to the current channel
`{0}unbind` - Unbind the global chat from the current channel
`{0}setcolour <hexadecimal>` - Set the global embed colour for this server
`{0}invite` - Invite this bot to your server

*This bot can be found on top.gg [here](https://top.gg/bot/747929473495859241)!*
    """.format(client.command_prefix)
    contributorPage = """
`Laith#0617`
<:Github:790615511829708840> Laith's [github](https://github.com/LaithDevelopment)

`ItsIsaac#0001`
<:Github:790615511829708840> Isaac's [github](https://github.com/1tsIsaac)
"""
    embed = discord.Embed(timestamp=message.message.created_at)
    await getDatabaseEmbedColour(embed, guildId)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.add_field(name=":tools: Help", value=helpPage, inline=False)
    embed.add_field(name="Contributors:", value=contributorPage, inline=False)
    embed.set_footer(text="Report bugs to Laith#0617")
    await message.send(embed=embed)


@client.command()
async def devhelp(message):
    if message.author.id == devId:
        guildId = message.guild.id

        devHelpPage = """
`{0}devhelp` - Help page for the developer
`{0}announce <message>` - Send a global announcement
`{0}globalban <ping/user-id>` - Ban a user from global messaging
`{0}globalserverban <server-id>` - Ban an entire server from global messaging
`{0}filteradd <word>` - Add a word to the filter
`{0}globalunban <ping/user-id>` - Unban a user from global messaging
`{0}globalserverunban <server-id>`  -Unban an entire server from global messaging
`{0}filterremove <word>` - Remove a word from the filter
        """.format(client.command_prefix)

        embed = discord.Embed(timestamp=message.message.created_at)
        await getDatabaseEmbedColour(embed, guildId)
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        embed.add_field(name=":tools: Developer Help", value=devHelpPage, inline=False)
        await message.send(embed=embed)
    else:
        error = "This command is only for the developer!"
        await errorEmbed(message, error)


@client.command()
async def invite(message):
    guildId = message.guild.id

    text = f"""
Use [this link](https://top.gg/bot/747929473495859241/invite) to directly invite this bot to your server.
{client.user.name} can also be found on top.gg [here](https://top.gg/bot/747929473495859241)!
    """

    embed = discord.Embed(timestamp=message.message.created_at)
    await getDatabaseEmbedColour(embed, guildId)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.add_field(name=":envelope: Invite the bot", value=text, inline=False)
    await message.send(embed=embed)


@client.command()
async def setup(message):
    guildId = message.guild.id

    embed = discord.Embed()
    await getDatabaseEmbedColour(embed, guildId)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.add_field(name=":hammer: Setup",
                    value=f"Create a channel that will be dedicated for GlobalMsg, then use `{client.command_prefix}bind` to bind the global chat to the channel",
                    inline=False)
    await message.send(embed=embed)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def bind(message):
    channelId = message.channel.id
    guildId = message.guild.id
    embedColour = 0
    prefix = "~"
    guildBanned = False

    if await checkDatabaseEntry(message, guildId, channelId) != False:
        await addDatabaseEntry(channelId, guildId, embedColour, prefix, guildBanned)
        successArgs = f"Global chat has been bound to `{message.channel.name}`!"
        await successEmbed(message, successArgs)

        logArgs = f"Global chat bound to `{message.channel.name}`"
        await sendModerationLog(message, logArgs)


@client.command(bass_context=True)
@commands.has_permissions(administrator=True)
async def unbind(message):
    guildId = message.guild.id
    await loadDatabase()
    for ii in data["guilds"]:
        if ii["guild-id"] == guildId:
            channelId = 0
            guildId = ii["guild-id"]
            embedColour = ii["embed-colour"]
            prefix = ii["prefix"]
            guildBanned = ii["guild-banned"]
            await deleteDatabaseEntry(guildId)
            await addDatabaseEntry(channelId, guildId, embedColour, prefix, guildBanned)
            successArgs = f"Global chat has been unbound from `{message.channel.name}`!"
            await successEmbed(message, successArgs)

            logArgs = f"Global chat unbound from `{message.channel.name}`"
            await sendModerationLog(message, logArgs)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def setcolour(message, arg):
    guildId = message.guild.id
    arg = "0x" + arg
    colourId = int(arg, 0)
    if colourId > 16777215:
        errorArgs = f"`{colourId}` is more than `16777215`. Try using hexadecimal!"
        await errorEmbed(message, errorArgs)
        return
    await loadDatabase()
    for ii in data["guilds"]:
        if ii["guild-id"] == guildId:
            channelId = ii["channel-id"]
            guildId = ii["guild-id"]
            embedColour = colourId
            prefix = ii["prefix"]
            guildBanned = ii["guild-banned"]
            await deleteDatabaseEntry(guildId)
            await addDatabaseEntry(channelId, guildId, embedColour, prefix, guildBanned)
            successArgs = f"The embed colour for this server has been set to `{arg}`!"
            await successEmbed(message, successArgs)

            logArgs = f"Embed colour for server set to `{arg}`!"
            await sendModerationLog(message, logArgs)


@client.command()
async def globalserverban(message, arg):
    guildId = int(arg)
    if message.author.id == devId:
        await loadDatabase()

        for ii in data["guilds"]:
            if ii["guild-id"] == guildId and ii["guild-banned"] == True:
                error = "That guild is already banned!"
                await errorEmbed(message, error)
                return

        for ii in data["guilds"]:
            if ii["guild-id"] == guildId:
                channelId = ii["channel-id"]
                guildId = ii["guild-id"]
                embedColour = ii["embed-colour"]
                prefix = ii["prefix"]
                guildBanned = True
                await deleteDatabaseEntry(guildId)
                await addDatabaseEntry(channelId, guildId, embedColour, prefix, guildBanned)
                successArgs = f"Banned guild-id `{guildId}` from the global chat!"
                await successEmbed(message, successArgs)

                logArgs = f"Banned guild-id `{guildId}` from global chat"
                await sendModerationLog(message, logArgs)
    else:
        errorArgs = "This command is only for the developer!"
        await errorEmbed(message, errorArgs)


@client.command()
async def globalserverunban(message, arg):
    guildId = int(arg)
    if message.author.id == devId:
        await loadDatabase()
        for ii in data["guilds"]:
            if ii["guild-id"] == guildId and ii["guild-banned"] == True:
                channelId = ii["channel-id"]
                guildId = ii["guild-id"]
                embedColour = ii["embed-colour"]
                prefix = ii["prefix"]
                guildBanned = False
                await deleteDatabaseEntry(guildId)
                await addDatabaseEntry(channelId, guildId, embedColour, prefix, guildBanned)
                successArgs = f"Unbanned guild-id `{guildId}` from the global chat!"
                await successEmbed(message, successArgs)

                logArgs = f"Unbanned guild-id `{guildId}` from global chat"
                await sendModerationLog(message, logArgs)
            elif ii["guild-id"] == guildId and ii["guild-banned"] == False:
                errorArgs = f"Cannot unban, guild `{guildId}` is not banned!"
                await errorEmbed(message, errorArgs)
    else:
        errorArgs = "This command is only for the developer!"
        await errorEmbed(message, errorArgs)


@client.command()
async def globalban(message, arg):
    await loadDatabase()
    userId = int(arg)
    if message.author.id == devId:
        for ii in data["users"]:
            if ii["user-id"] == userId:
                error = "That user is already banned!"
                await errorEmbed(message, error)
                return

        data["users"].append(
            {
                "user-id": userId,
                "reason": "null",
                "banned": True
            }
        )
        await appendDatabase(data)
        successArgs = f"Banned user-id `{userId}` from the global chat!"
        await successEmbed(message, successArgs)

        logArgs = f"Banned user-id `{userId}` from global chat"
        await sendModerationLog(message, logArgs)
    else:
        errorArgs = "This command is only for the developer!"
        await errorEmbed(message, errorArgs)


@client.command()
async def globalunban(message, arg):
    await loadDatabase()
    userId = int(arg)
    if message.author.id == devId:
        await loadDatabase()
        for ii in data["users"]:
            if ii["user-id"] == userId and ii["banned"] == True:
                data["users"].pop(getDatabaseUserEntryPosition(userId))
                await appendDatabase(data)
                successArgs = f"Unbanned user-id `{userId}` from the global chat!"
                await successEmbed(message, successArgs)

                logArgs = f"Unbanned user-id `{userId}` from global chat"
                await sendModerationLog(message, logArgs)
    else:
        errorArgs = "This command is only for the developer!"
        await errorEmbed(message, errorArgs)


@client.command()
async def filteradd(message, arg):
    await loadDatabase()
    filterWord = arg
    if message.author.id == devId:
        for ii in data["profanities"]:
            if ii["word"] == filterWord:
                errorArgs = f"`{filterWord}` is already being filtered!"
                await errorEmbed(message, errorArgs)
                return

        data["profanities"].append(
            {
                "word": filterWord,
                "filtered": True
            }
        )
        await appendDatabase(data)
        successArgs = f"`{filterWord}` will now be filtered from the global chat!"
        await successEmbed(message, successArgs)

        logArgs = f"Added `{filterWord}` to global filter"
        await sendModerationLog(message, logArgs)
    else:
        errorArgs = "This command is only for the developer!"
        await errorEmbed(message, errorArgs)


@client.command()
async def filterremove(message, arg):
    await loadDatabase()
    filterWord = arg
    if message.author.id == devId:
        await loadDatabase()
        for ii in data["profanities"]:
            if ii["word"] == filterWord and ii["filtered"] == True:
                data["profanities"].pop(getDatabaseWordEntryPosition(filterWord))
                await appendDatabase(data)
                successArgs = f"`{filterWord}` will no longer be filtered from the global chat!"
                await successEmbed(message, successArgs)

                logArgs = f"Removed `{filterWord}` from global filter"
                await sendModerationLog(message, logArgs)
    else:
        errorArgs = "This command is only for the developer!"
        await errorEmbed(message, errorArgs)


@client.command()
async def announce(message, *args):
    await loadDatabase()
    args = " ".join(args[:])
    guildName = message.guild.name

    if message.author.id == devId:
        embed = discord.Embed(color=0x00bfff)
        embed.add_field(name=":mega:  Global Announcement", value=args)
        embed.set_footer(text="Sent from: " + guildName)

        for ii in data["guilds"]:
            channel = client.get_channel(ii["channel-id"])
            if channel == None:
                print("Count find the channel: " + str(ii["channel-id"]) + " for guild: " + str(ii["guild-id"]))
                continue
            elif channel == message.channel:
                continue
            else:
                await channel.send(embed=embed)
            logArgs = f"Announced: {args}"
            await sendModerationLog(message, logArgs)
    else:
        errorArgs = "This command is only for the developer!"
        await errorEmbed(message, errorArgs)


client.run(token)
