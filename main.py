import discord
from discord.ext import commands
import json
import util
import asyncio



# Load configuration
config = json.load(open("config.json", "r"))


# Initialize the bot
bot = commands.Bot(
    command_prefix=util.get_prefix,
    help_command=None
)


binded_cache = []
banned_users_cache = []
banned_guilds_cache = []



# NOTE - Error handler, DO. NOT. REMOVE.
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            content=f"You are missing permissions to execute that command, <@!{ctx.author.id}>!",
            delete_after=10
        )
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            content=f"Invalid arguments, do `{util.get_prefix(bot, ctx)[0]}help` for more info, <@!{ctx.author.id}>!",
            delete_after=10
        )
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            content=f"That command is on cooldown for another **{round(error.retry_after, 1)}**s, <@!{ctx.author.id}>!",
            delete_after=10
        )
    elif isinstance(error, commands.NSFWChannelRequired):
        await ctx.send(
            content=f"This command can only be run in NSFW channels, <@!{ctx.author.id}>!",
            delete_after=10
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            content=f"Make sure you are putting in all required arguments, <@!{ctx.author.id}>!",
            delete_after=10
        )
    else:
        await ctx.send(
            content=f"Unknown error! Please report this to ItsIsaac#0001 or Laith#0617!:\n```{error}```"
        )
        print(error)
    



# Runs once the bot is fully ready
@bot.event
async def on_ready():
    # Create lists of the JSON guilds and bot guilds
    bot_guild_list = []
    for guild in bot.guilds:
        bot_guild_list.append(guild.id)

    json_guild_list = []
    for guild in util.guilds_json():
        json_guild_list.append(guild["guild-id"])

    # Remove guilds that the bot is not in anymore
    for guild in json_guild_list:
        if guild not in bot_guild_list:
            util.remove_guild(guild)

    # Add guilds that the bot is now in
    for guild in bot_guild_list:
        if guild not in json_guild_list:
            util.add_guild(guild)

    # Set the bot status and update the cache
    while True:
        for guild in util.guilds_json():
            if guild["binded-channel"] not in binded_cache:
                binded_cache.append(guild["binded-channel"])

        for user in util.banned_json()["users"]:
            if user not in banned_users_cache:
                banned_users_cache.append(user)

        for guild in util.banned_json()["guilds"]:
            if guild not in banned_guilds_cache:
                banned_guilds_cache.append(guild)    
    
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.streaming,
                name=f"{len(bot.guilds)} guilds! | ~help"
            )
        )
        await asyncio.sleep(10)


# Broadcast a message to all binded channels
async def broadcast(message):
    # Form the embed
    embed = util.fancy_embed(
        ctx=message,
        description=message.content
    )
    embed.set_author(
        name=message.author,
        icon_url=message.author.avatar_url
    )
    embed.set_footer(
        text=f"Sent from: {message.guild.name}",
        icon_url=message.guild.icon_url
    )
    # Send the message to every binded channel
    for channel in binded_cache:
        if channel == message.channel.id:
            continue

        if channel == None:
            continue
        
        channel = bot.get_channel(channel)
        if channel.id == message.channel.id:
            await message.channel.send(
                content="Sent!",
                delete_after=1
            )

        await channel.send(
            embed=embed
        )
    
    await log(message, message, 0)


# await log an event in the moderation channel
# event 0 - message sent | event 1 - message blocked 
# event 2 - bind | event 3 - unbind
# event 4 - set-colour
# event 5 - banned user | event 6 - unbanned user
async def log(ctx, info, event: int): 
    mod_channel = bot.get_channel(config["dev-guild"]["moderation-log"])
    # Message sent
    if event == 0:
        # Form the embed
        embed = util.fancy_embed(
            ctx=None,
            description=f"Message sent: {info}"
        )
        embed.colour(discord.Colour(3093151))
        embed.set_author(
            name=f"{ctx.author} | {ctx.author.id}",
            icon_url=ctx.author.avatar_url
        )
        embed.set_footer(
            text=f"{ctx.guild.name} | ({ctx.guild.id})",
            icon_url=ctx.guild.icon_url
        )
        # Send it
        await mod_channel.send(
            embed=embed
        )
    elif event == 1:
        # Form the embed
        embed = util.fancy_embed(
            ctx=None,
            description=f"Message blocked: {info}"
        )
        embed.colour(discord.Colour(16712763))
        embed.set_author(
            name=f"{ctx.author} | {ctx.author.id}",
            icon_url=ctx.author.avatar_url
        )
        embed.set_footer(
            text=f"{ctx.guild.name} | ({ctx.guild.id})",
            icon_url=ctx.guild.icon_url
        )
        # Send it
        await mod_channel.send(
            embed=embed
        )
    elif event == 2:
        # Form the embed
        embed = util.fancy_embed(
            ctx=None,
            description=f"Binded to `{info.name}` | {info.id}!"
        )
        embed.colour(discord.Colour(3093151))
        embed.set_author(
            name=f"{ctx.author} | {ctx.author.id}",
            icon_url=ctx.author.avatar_url
        )
        embed.set_footer(
            text=f"{ctx.guild.name} | ({ctx.guild.id})",
            icon_url=ctx.guild.icon_url
        )
        # Send it
        await mod_channel.send(
            embed=embed
        )
    elif event == 3:
        # Form the embed
        embed = util.fancy_embed(
            ctx=None,
            description=f"Unbound from `{info.name}` | {info.id}!"
        )
        embed.colour(discord.Colour(3093151))
        embed.set_author(
            name=f"{ctx.author} | {ctx.author.id}",
            icon_url=ctx.author.avatar_url
        )
        embed.set_footer(
            text=f"{ctx.guild.name} | ({ctx.guild.id})",
            icon_url=ctx.guild.icon_url
        )
        # Send it
        await mod_channel.send(
            embed=embed
        )
    elif event == 4:
        # Form the embed
        embed = util.fancy_embed(
            ctx=None,
            description=f"Set colour theme to `{info}`!"
        )
        embed.colour(discord.Colour(3093151))
        embed.set_author(
            name=f"{ctx.author} | {ctx.author.id}",
            icon_url=ctx.author.avatar_url
        )
        embed.set_footer(
            text=f"{ctx.guild.name} | ({ctx.guild.id})",
            icon_url=ctx.guild.icon_url
        )
        # Send it
        await mod_channel.send(
            embed=embed
        )
    elif event == 5:
        # Form the embed
        embed = util.fancy_embed(
            ctx=None,
            description=f"Banned {info}!"
        )
        embed.colour(discord.Colour(3093151))
        embed.set_author(
            name=f"{ctx.author} | {ctx.author.id}",
            icon_url=ctx.author.avatar_url
        )
        embed.set_footer(
            text="Ban event",
            icon_url=ctx.guild.icon_url
        )
        # Send it
        await mod_channel.send(
            embed=embed
        )
    elif event == 6:
        # Form the embed
        embed = util.fancy_embed(
            ctx=None,
            description=f"Unbanned {info}!"
        )
        embed.colour(discord.Colour(3093151))
        embed.set_author(
            name=f"{ctx.author} | {ctx.author.id}",
            icon_url=ctx.author.avatar_url
        )
        embed.set_footer(
            text="Ban event",
            icon_url=ctx.guild.icon_url
        )
        # Send it
        await mod_channel.send(
            embed=embed
        )



# When a message is sent
@bot.event
async def on_message(message):
    # If the message is sent by the bot
    if message.author == bot.user:
        return

    # If the message is in a binded channel
    if util.get_guild_attr(message.guild.id, "binded-channel"):
        # If the guild is banned
        if message.guild.id in banned_guilds_cache:
            return
        
        # If the user is banned
        if message.author.id in banned_users_cache:
            return

        # Check the message for filtered words
        if util.message_filtered(message):
            await message.channel.send(
                content=f"Your message has been blocked, <@!{message.author.id}>!",
                delete_after=10
            )
            await log(message, message, 1)
            return


        # Broadcast the message
        await broadcast(message)



    await bot.process_commands(message)



# When the bot is added to a guild
@bot.event
async def on_guild_join(guild):
    # Shouldn't happen, just incase!
    if util.guild_exists(guild):
        util.remove_guild(guild.id)
    
    # Add the guild to guilds.json
    util.add_guild(guild.id)

    # Look for a channel that the bot has perms in and send the welcome message
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            welcomePage = """
**Thanks for adding me! :smile:**
- My prefix is `{1}`.
- To get started, type `{1}setup` in a channel and follow the simple step by step guide!
- You can see a list of available commands by typing `{1}help`.
- This bot is still in early development so if you find any bugs, report them to Laith#0617 or ItsIsaac#0001!

*Note: If your server has an NSFW icon the server will get banned from global channels.*
            """.format(bot.user.name, bot.command_prefix[0])

            await channel.send(welcomePage)

        break


# When the bot is removed from a guild
@bot.event
async def on_guild_remove(guild):
    # Remove the guild from guilds.json
    util.remove_guild(guild.id)





# Bind command
@bot.command()
@commands.has_permissions(manage_guild=True)
async def bind(ctx, channel: discord.TextChannel = None):
    # If the channel is None then set it to ctx.channel
    if channel == None:
        channel = ctx.channel
    
    # If the bot is already binded to the channel
    if util.get_guild_attr(ctx.guild.id, "binded-channel") == channel.id:
        await ctx.send(
            content=f"The bot is already binded to that channel, <@!{ctx.author.id}>", 
            delete_after=10
        )
        return
    
    # Set the channel bind
    util.set_guild_attr(
        guild_id=ctx.guild.id,
        attr="binded-channel",
        value=channel.id
    )

    # Tell the user
    await ctx.send(
        embed=util.fancy_embed(
            ctx=ctx,
            title="Success!",
            description=f"Successfully binded to `{channel.name}`!"
        )
    )
    
    await log(
        ctx=ctx, 
        info=channel, 
        event=2
    )


# Help command
@bot.command()
async def help(ctx):
    # Help pages
    help_page = """
`{0}help` - General help page
`{0}setup` - How to setup the bot
`{0}bind [#channel]` - Bind the global chat to the current channel
`{0}unbind` - Unbind the global chat from the current channel
`{0}set-colour <hexadecimal>` - Set the global embed colour for this server
`{0}set-prefix` - Set a prefix for this guild

*Invite the bot [here](https://discord.com/oauth2/authorize?client_id=747929473495859241&scope=bot&permissions=537263168)*
*The bot can be found on top.gg [here](https://top.gg/bot/747929473495859241)!*
""".format(util.get_prefix(bot, ctx)[0])

    contributor_page = """
`Laith#0617`
<:Github:790615511829708840> Laith's [github](https://github.com/LaithDevelopment)
`ItsIsaac#0001`
<:Github:790615511829708840> Isaac's [github](https://github.com/1tsIsaac)
"""

    # Create the help embed
    embed = util.fancy_embed(
        ctx=ctx,
        title="GlobalMsg | Help",
        description="__Anything in <> is required__\n__Anything in [] is optional__\n"
    )
    # Credit
    embed.set_author(name="by Laith & ItsIsaac") # you can remove me if you want

    # Add the help field
    embed.add_field(name=":tools: Help", value=help_page, inline=False)

    # Add the contributors field
    embed.add_field(name=":robot: Contributors", value=contributor_page, inline=False)
    embed.set_footer(text="Report bugs to Laith#0617")
    await ctx.send(embed=embed)


# Setup command
@bot.command()
async def setup(ctx):
    # Form the setup embed
    embed = util.fancy_embed(
        ctx=ctx
    )
    embed.add_field(
        name=":hammer: Setup",
        value=f"Create a channel that will be dedicated for GlobalMsg, then use `{util.get_prefix(bot, ctx)[0]}bind` to bind the global chat to the channel",
        inline=False
    )
    # Send it
    await ctx.send(embed=embed)



# Unbind command
@bot.command()
@commands.has_permissions(manage_guild=True)
async def unbind(ctx):
    binded_channel_id = util.get_guild_attr(ctx.guild.id, "binded-channel")
    binded_channel = await bot.fetch_channel(binded_channel_id)
    # If the bot is not binded to a channel
    if binded_channel_id == None:
        await ctx.send(
            content=f"The bot is not binded to a channel, <@!{ctx.author.id}>", 
            delete_after=10
        )
        return
    # If the bot is binded to a channel that no longer exists
    if binded_channel == None:
        util.set_guild_attr(ctx.guild.id, "binded-channel", None)
        await ctx.send(
            content=f"The bot is not binded to a channel, <@!{ctx.author.id}>", 
            delete_after=10
        )
        return


    # If no errors are detected
    util.set_guild_attr(ctx.guild.id, "binded-channel", None)
    await ctx.send(
        embed=util.fancy_embed(
            ctx=ctx,
            title="Success!",
            description=f"Successfully unbinded from `{binded_channel.name}`!"
        )
    )
    await log(ctx, binded_channel, 3)
    return



# Set colour command
@bot.command(aliases=["set-colour"])
@commands.has_permissions(manage_guild=True)
async def set_colour(ctx, colour):
    # Do stuff to the colour >.>
    if not colour.startswith("0x"):
        if isinstance(colour, str):
            colour = f"0x{colour}"
    colour = int(colour, 0)
    # If the colour decimal is too large
    if colour > 16777215:
        await ctx.send(
            content=f"`{colour}` is higher than `16777215`. Try using hexadecimal!",
            delete_after=10
        )
        
        return
        
    # If the colour is unchanged
    if colour == util.get_guild_attr(ctx.guild.id, "theme"):
        await ctx.send(
            content=f"`{colour}` is already your colour theme, <@!{ctx.author.id}>!",
            delete_after=10
        )
        
        return
    
    # Change the colour
    util.set_guild_attr(
        guild_id=ctx.guild.id,
        attr="theme",
        value=colour
    )
    # Tell the user
    await ctx.send(
        embed=util.fancy_embed(
            ctx=ctx,
            title="Success!",
            description=f"Successfully changed the embed colour to `{colour}`!"
        )
    )

    await log(ctx, colour, 4)



# Set prefix command
@bot.command(aliases=["set-prefix"])
@commands.has_permissions(manage_guild=True)
async def set_prefix(ctx, prefix: str):
    # If the prefix is too long
    if len(prefix) > 5:
        await ctx.send(
            content=f"The prefix cannot be over 5 characters, <@!{ctx.author.id}>!",
            delete_after=10
        )
        return

    # If the prefix is the same
    if util.get_guild_attr(ctx.guild.id, "prefix") == prefix:
        await ctx.send(
            content=f"The prefix is already `{prefix}`, <@!{ctx.author.id}>!",
            delete_after=10
        )
        return

    # Change the prefix
    util.set_guild_attr(
        guild_id=ctx.guild.id,
        attr="prefix",
        value=prefix
    )
    # Tell the user
    await ctx.send(
        embed=util.fancy_embed(
            ctx=ctx,
            title="Success!",
            description=f"Successfully changed the prefix to `{prefix}`!"
        )
    )











# Run the bot
# If the bot is in debug mode
if config["debug?"]:
    bot.run(config["debug-token"])

# If the bot isn't in debug mode
elif not config["debug?"]:
    bot.run(config["release-token"])

# If 'debug?' is not a boolean
else:
    bot.run(config["debug-token"]) # Default to debug token
