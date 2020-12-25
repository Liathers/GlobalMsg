import json
import discord
import datetime


# Load configuration
config = json.load(open("config.json", "r"))


# Errors
class WordAlreadyInFilterError(Exception):
    pass

class WordNotInFilterError(Exception):
    pass

class UserAlreadyBannedError(Exception):
    pass

class UserNotBannedError(Exception):
    pass

class GuildAlreadyBannedError(Exception):
    pass

class GuildNotBannedError(Exception):
    pass




# Fancies / auto-formats up embeds
def fancy_embed(ctx, **kwargs):
    embed = discord.Embed(
        **kwargs,
        colour=discord.Colour(get_guild_attr(ctx.guild.id, "theme")),
        timestamp=datetime.datetime.now()
    )
    

    return embed
    


# Used in the initialization of the bot, don't remove
def get_prefix(bot, message):
    return [get_guild_attr(
        guild_id=message.guild.id,
        attr="prefix"
    ), f"<@!{bot.user.id}> "]


# Adds a guild to guilds.json
def add_guild(guild_id: int):
    data = guilds_json()

    # Append the guild
    data.append({
        "guild-id": guild_id,
        "binded-channel": None,
        "theme": 0,
        "prefix": config["default-prefix"]
    })
    # Write the guild
    json.dump(
        obj=data,
        fp=open("database/guilds.json", "w"),
        indent=4
    )



# Removes a guild from guilds.json
def remove_guild(guild_id: int):
    data = guilds_json()

    # Remove the guild
    pos = 0
    for guild in data:
        if guild["guild-id"] == guild_id:
            # Remove the guild
            data.pop(pos)
            # Write
            json.dump(
                obj=data,
                fp=open("database/guilds.json", "w"),
                indent=4
            )
            return

        pos += 1



# Returns True if a guild is in guilds.json, False otherwise
def guild_exists(guild_id: int):
    data = guilds_json()

    # Look for the guild
    for guild in data:
        if guild["guild-id"] == guild_id:
            return True

    return False




# Fetches an attribute of a guild
def get_guild_attr(guild_id: int, attr: str):
    data = guilds_json()
    for guild in data:
        if guild["guild-id"] == guild_id:
            return guild[attr]


    # If the guild does not exist, add it
    add_guild(guild_id)
    return get_guild_attr(guild_id, attr)


# Sets an attribute of a guild and writes
def set_guild_attr(guild_id: int, attr: str, value: any):
    data = guilds_json()
    for guild in data:
        if guild["guild-id"] == guild_id:
            # Set the attribute
            guild[attr] = value
            # Write
            json.dump(
                obj=data,
                fp=open("database/guilds.json", "w"),
                indent=4
            )
            return


    # If the guild does not exist, add it
    data.append({
        "guild-id": guild_id,
        "binded-channel": None,
        "theme": 0,
        "prefix": config["default-prefix"]
    })
    # Write the guild
    json.dump(
        obj=data,
        fp=open("database/guilds.json", "w"),
        indent=4
    )
    return set_guild_attr(guild_id, attr, value)


# Adds a word to the filter
def add_to_filter(word: str):
    data = filter_json()

    # If the word is already being filtered, raise:
    if word in data:
        raise WordAlreadyInFilterError(f"The word {word} is already in the filter!")

    # Add the word to the filter
    data.append(word)
    # Write
    json.dump(
        obj=data,
        fp=open("database/filter.json", "w"),
        indent=4
    )


# Returns True if the word is in the filter, False otherwise
def message_filtered(message: str):
    message = message.content.lower()
    for word in filter_json():
        if message.find(word) == -1:
            return True
    
    return False


# Removes a word from the filter
def remove_from_filter(word: str):
    data = filter_json()
    pos = 0
    for filtered in data:
        if filtered == word:
            # Remove the word from the filter
            data.pop(pos)
            # Write and exit
            json.dump(
                obj=data,
                fp=open("database/filter.json", "w"),
                indent=4
            )
            return

        pos += 1
    
    # If the loop completes and the word is not in the filter, raise:
    raise WordNotInFilterError(f"The word '{word}' is not in the filter!")



# Adds a user to banned.json (users list)
def ban_user(user_id: int):
    data = banned_json()
    
    # If the user is already banned, raise:
    if user_id in data["users"]:
        raise UserAlreadyBannedError(f"The user {user_id} is already banned!")

    # Add the user to the banlist
    data["users"].append(user_id)
    # Write
    json.dump(
        obj=data,
        fp=open("database/banned.json", "w"),
        indent=4
    )


# Removes a user from banned.json (users list)
def unban_user(user_id: int):
    data = banned_json()

    # If the user is not banned, raise:
    if user_id not in data["users"]:
        raise UserNotBannedError(f"The user {user_id} is not banned!")

    # Remove the user from the banlist
    data["users"].remove(user_id)
    # Write
    json.dump(
        obj=data,
        fp=open("database/banned.json", "w"),
        indent=4
    )



# Adds a guild to banned.json (guild list)
def ban_guild(guild_id: int):
    data = banned_json()
    
    # If the guild is already banned, raise:
    if guild_id in data["guilds"]:
        raise GuildAlreadyBannedError(f"The guild {guild_id} is already banned!")

    # Add the guild to the banlist
    data["guilds"].append(guild_id)
    # Write
    json.dump(
        obj=data,
        fp=open("database/banned.json", "w"),
        indent=4
    )


# Removes a guild from banned.json (guilds list)
def unban_guild(guild_id: int):
    data = banned_json()

    # If the guild is not banned, raise:
    if guild_id not in data["guilds"]:
        raise GuildNotBannedError(f"The guild {guild_id} is not banned!")

    # Remove the guild from the banlist
    data["guilds"].remove(guild_id)
    # Write
    json.dump(
        obj=data,
        fp=open("database/banned.json", "w"),
        indent=4
    )




# Return loaded guilds.json
def guilds_json():
    return json.load(
        fp=open("database/guilds.json", "r")
    )

# Return loaded filter.json
def filter_json():
    return json.load(
        fp=open("database/filter.json", "r")
    )

# Return loaded banned.json
def banned_json():
    return json.load(
        fp=open("database/banned.json", "r")
    )
