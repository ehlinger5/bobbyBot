"""
Created: 01/15/2022
Last Updated: 01/15/2022
@author: Josh Ehlinger (theEhlien)
"""

import os.path
import json
import logging
import discord
import nest_asyncio
import random

# This bot is only intended to be run on a single server at a time
####################
CONF_FILE_NAME = "bobbyBot.conf"
# CONF VALUES - Default values are replaced with conf file (CONF_FILE_NAME)
# Dictionary of configuration values
ACTIVE_CONF = {
    "LOGGING_LEVEL": logging.INFO,
    "LOGGING_FORMAT": '[%(levelname)s]: %(message)s',
    "DISCORD_KEY_FILE": ".discordKey",
    "BOT_NAME": "Bobby Bot",
    "BOT_PREFIX": "!bb",
    "MODERATOR_ROLE_NAME": "Moderator",
    "MODERATOR_ROLE_ID": 0, # this will be updated on load based on the value from the server
    "MEMBER_ROLE_NAME": "Member",
    "MEMBER_ROLE_ID": 0, # this will be updated on load based on the value from the server
    "PHRASES": ["Relateable","Unbelievable","Me too","Cry about it","pog","pogn't","poggers","It do be like that","I agree","Yeah, me too","You know what? Me too","No :heart:","Yeah, same","I'm gonna commit violence","No respect","Do you know who I am?","Get a load of this guy","Hey, how you doin'?","Do I know you?","Have we met?"]
}
####################

client = None

def main():
    global ACTIVE_CONF
    global client
    # Const for space char
    SPACE_CHAR = " "

    initialize()

    nest_asyncio.apply()

    #set bot client
    client = discord.Client()

    # log on event
    @client.event
    async def on_ready():
        logging.info('We have logged in as {0.user}'.format(client))
        for guild in client.guilds:
            # Check for the member role name value and assign the propper ID
            for role in guild.roles:
                if(str(role) == ACTIVE_CONF["MEMBER_ROLE_NAME"]):
                    # name exists - set roleID value
                    roleID = role.id
                    ACTIVE_CONF["MEMBER_ROLE_ID"] = roleID
            # Check for the moderator role name value and assign the propper ID
            for role in guild.roles:
                if(str(role) == ACTIVE_CONF["MODERATOR_ROLE_NAME"]):
                    # name exists - set roleID value
                    roleID = role.id
                    ACTIVE_CONF["MODERATOR_ROLE_ID"] = roleID
            updateConfFile()

    # reading message event
    @client.event
    async def on_message(message):
        # if message is authored by client, do nothing (return)
        if message.author == client.user:
            return
        
        # checks for messages starting with bot prefix (case sensitive)
        if message.content.startswith(ACTIVE_CONF["BOT_PREFIX"]):
            if message.content != None:
                messageNoCase = message.content.lower()
            else:
                messageNoCase = None

            ###################################################################################################################
            # Make check for 'killbot' command call
            ###################################################################################################################
            if messageNoCase == (ACTIVE_CONF["BOT_PREFIX"] + SPACE_CHAR + "killbot").lower():
                # do check for admin role (returns true if admin role)
                if message.author.guild_permissions.administrator:
                    logging.info(f'User {message.author} has issued the killbot command. The bot will be killed and will print some errors...')
                    await message.reply(f'{ACTIVE_CONF["BOT_NAME"]} Signing off. Hope to see you again soon!')
                    await client.close()
                else:
                    logging.warning(f'User {message.author} tried to use the killbot command without sufficient permissions')
                    await message.reply("This command can only be used by an administrator role")

            ###################################################################################################################
            # Make check for 'updateconf' command call
            ###################################################################################################################
            if messageNoCase == (ACTIVE_CONF["BOT_PREFIX"] + SPACE_CHAR + "updateconf").lower():
                # do check for admin role
                if message.author.guild_permissions.administrator:
                    updateConf()
                    await message.reply("Live configuration updated from local conf file")
                else:
                    logging.warning(f'User {message.author} tried to use the updateconf command without sufficient permissions')
                    await message.reply("This command can only be used by an administrator role")
            
            ###################################################################################################################
            # Make check for 'prefix' command call (this has no sanitization yet for values given)
            ###################################################################################################################
            if message.content != None and "prefix" in message.content:
                # do check for admin role
                if message.author.guild_permissions.administrator:
                    newPrefix = changeBotPrefix(message.content)
                    if newPrefix == False:
                        await message.reply("Something isn't right. Make sure your new prefix is included in the command and " + 
                        "that it is only one word (no whitespace)")
                        await message.reply(f'Usage: {ACTIVE_CONF["BOT_PREFIX"]} prefix [new-prefix]')
                    else:
                        await message.reply(f'{ACTIVE_CONF["BOT_NAME"]}\'s prefix has been changed to {newPrefix}')
                else:
                    logging.warning(f'User {message.author} tried to use the prefix command without sufficient permissions')
                    await message.reply("This command can only be used by an administrator role")
            
            ###################################################################################################################
            # Make check for 'memberrole' command call (this only has sanitization on @role calls -
            # although it will check if roles exist first)
            ###################################################################################################################
            if message.content != None and "memberrole" in message.content:
                # do check for admin role
                if message.author.guild_permissions.administrator:
                    newRole = changeMemberRole(message)
                    if newRole == False:
                        await message.reply("Something isn't right. Make sure the member role you specified exists on this server")
                        await message.reply(f'Usage: {ACTIVE_CONF["BOT_PREFIX"]} memberrole [@member-role/member-role]')
                    else:
                        await message.reply(f'{ACTIVE_CONF["BOT_NAME"]}\'s member role has been changed to {newRole}')
                else:
                    logging.warning(f'User {message.author} tried to use the memberrole command without sufficient permissions')
                    await message.reply("This command can only be used by an administrator role")
            
            ###################################################################################################################
            # Make check for 'moderatorrole' command call (this only has sanitization on @role calls -
            # although it will check if roles exist first)
            ###################################################################################################################
            if message.content != None and "moderatorrole" in message.content:
                # do check for admin role
                if message.author.guild_permissions.administrator:
                    newRole = changeModeratorRole(message)
                    if newRole == False:
                        await message.reply("Something isn't right. Make sure the moderator role you specified exists on this server")
                        await message.reply(f'Usage: {ACTIVE_CONF["BOT_PREFIX"]} moderatorrole [@moderator-role/moderator-role]')
                    else:
                        await message.reply(f'{ACTIVE_CONF["BOT_NAME"]}\'s moderator role has been changed to {newRole}')
                else:
                    logging.warning(f'User {message.author} tried to use the moderatorrole command without sufficient permissions')
                    await message.reply("This command can only be used by an administrator role")

            ###################################################################################################################
            # Make check for 'randomphrase' command call - will reply with error when list is empty
            ###################################################################################################################
            if messageNoCase == (ACTIVE_CONF["BOT_PREFIX"] + SPACE_CHAR + "randomphrase").lower():
                # do check for member role (if configured member role id is 0, assume that @everyone is alright)
                if (ACTIVE_CONF["MEMBER_ROLE_ID"] == 0 # id is 0 so @everyone can make this call
                    or message.author.guild_permissions.administrator # author is admin so they can make the call
                    or checkForUserRoles(message.author.roles, [int(ACTIVE_CONF["MODERATOR_ROLE_ID"]), int(ACTIVE_CONF["MEMBER_ROLE_ID"])]) # author has moderator or member role so they can make call
                ):
                    phrase = chooseRandomPhrase()
                    if phrase == False:
                        await message.reply("Something went wrong trying to pick a phrase. Make sure there are phrases available in the list first")
                    else:
                        await message.reply(phrase)
                else:
                    logging.warning(f'User {message.author} tried to use the randomphrase command without sufficient permissions')
                    await message.reply(f'This command can only be used by a user with the {ACTIVE_CONF["MEMBER_ROLE_NAME"]} role')

            ###################################################################################################################
            # Make check for 'randomphrase' command call - will reply with error when list is empty
            ###################################################################################################################
            if message.content != None and "addphrase" in message.content:
                # do check for moderator role
                canCall = False
                if ACTIVE_CONF["MODERATOR_ROLE_ID"] == 0: # mod id is 0 - if member id is also 0, assume @everyone is alright - user with member role can also make call
                    if ACTIVE_CONF["MEMBER_ROLE_ID"] == 0 or checkForUserRoles(message.author.roles, [int(ACTIVE_CONF["MEMBER_ROLE_ID"])]):
                        canCall = True
                elif checkForUserRoles(message.author.roles, [int(ACTIVE_CONF["MODERATOR_ROLE_ID"])]):
                    canCall = True
                if message.author.guild_permissions.administrator: # author is admin so they can make the call
                    canCall = True

                if canCall:
                    newPhrase = addPhrase(message)
                    if newPhrase == False:
                        await message.reply("Something isn't right. Check your command again")
                        await message.reply(f'Usage: {ACTIVE_CONF["BOT_PREFIX"]} addphrase [brand new phrase]')
                    elif newPhrase == True:
                        await message.reply(f'That phrase is already in the list of available Bobby phrases')
                    else:
                        await message.reply(f'"{newPhrase}" was added to the list of available Bobby phrases')
                else:
                    logging.warning(f'User {message.author} tried to use the addphrase command without sufficient permissions')
                    if ACTIVE_CONF["MODERATOR_ROLE_ID"] == 0:
                        await message.reply(f'This command can only be used by a user with the {ACTIVE_CONF["MEMBER_ROLE_NAME"]} role')
                    else:
                        await message.reply(f'This command can only be used by a user with the {ACTIVE_CONF["MODERATOR_ROLE_NAME"]} role')

            # Change bot name must be performed by admin roles
            # Adding a bobby message can be performed by moderator and admin roles

    # Add code to get key from file instead of plain text
    with open(ACTIVE_CONF["DISCORD_KEY_FILE"]) as keyFile:
        logging.info(f'Discord API key has been taken from the following file: {ACTIVE_CONF["DISCORD_KEY_FILE"]}\n')
        client.run(keyFile.read())

### This function handles initial operations such as setting up a logger
### and loading the configuration settings
def initialize():
    # scope global vars to be actually global
    global ACTIVE_CONF
    global CONF_FILE_NAME

    print('Initializing Bot...')

    # Load conf file
    loadConf(CONF_FILE_NAME)

    # Setup logger with basic config
    logging.basicConfig(level=ACTIVE_CONF["LOGGING_LEVEL"], format=ACTIVE_CONF["LOGGING_FORMAT"])
    print('Initialization Finished\n')

### This function handles loading a configuration file if one exists or
### generating one from default value if one does not exist
def loadConf(confFileName):
    global ACTIVE_CONF
    # Check for existence of file
    confExists = os.path.exists(confFileName)

    # If exists, load
    if confExists:
        with open(confFileName, "r") as confFile:
            data = json.load(confFile)
            print(f'Read in configuration file {confFileName}')
            confFile.close()
            
        # Load file values into active configuration
        ACTIVE_CONF = data
        print('Loaded configuration')

    # If does not exist, create default
    else:
        print(f'No configuration file ({confFileName}) was found. Generating default configuration...')
        with open(confFileName, "w") as confFile:
            json.dump(ACTIVE_CONF, confFile)
            confFile.close()

### This function will update the running configuration from a file
def updateConf():
    global ACTIVE_CONF
    global CONF_FILE_NAME
    # Update the variables with values from the configuration file
    logging.info(f'Updating variables from configuration file for {ACTIVE_CONF["BOT_NAME"]}')
    loadConf(CONF_FILE_NAME)

### This function will update the conf file from the running configuration
def updateConfFile():
    global CONF_FILE_NAME
    global ACTIVE_CONF
    with open(CONF_FILE_NAME, "w") as confFile:
        json.dump(ACTIVE_CONF, confFile)
        confFile.close()

### This function will check for matching role IDs from a list against the user's role list
### Returns True if any of the roles are found and False if none are found
def checkForUserRoles(userRoleList, roleIdsToBeFound):
    for serverRole in userRoleList:
        id = serverRole.id
        if id in roleIdsToBeFound:
            return True
    return False

### This function will change the prefix used in bot commands
def changeBotPrefix(fullMessage):
    global ACTIVE_CONF
    # Change the bot prefix conf value and update discord server side
    commandList = fullMessage.split()
    # A prefix cannot have whitespace. 
    if len(commandList) == 3:
        # This is the third item in the command ({prefix} {command} {expectedValue})
        prefix = commandList[2]
    else:
        return False
    logging.info(f'Changing {ACTIVE_CONF["BOT_NAME"]} prefix from {ACTIVE_CONF["BOT_PREFIX"]} to {prefix}')
    ACTIVE_CONF["BOT_PREFIX"] = prefix
    # Any changes made locally to conf variables must be pushed to the conf file so they are persistent on restart
    updateConfFile()
    return prefix

### This function will change the username of the bot
def changeBotName(name):
    global ACTIVE_CONF
    # Change the bot name conf value and update discord server side
    logging.info(f'Changing the bot\'s name from {ACTIVE_CONF["BOT_NAME"]} to {name}')

### This function will change the role used as the general "member" on the server
def changeMemberRole(message):
    global ACTIVE_CONF
    fullMessage = message.content
    # Change the bot member conf value and update discord server side
    commandList = fullMessage.split()
    # A role should either be preceded with an "@" character or be a string of text (possibly with whitespaces)
    if len(commandList) >= 3:
        atPos = fullMessage.find("@")
        roleID = -1
        # No @ symbol. Use the remainder of the command then
        if atPos == -1:
            # the substring used is the pos of the command + the length of the command + 1 which places the start
            # at the name of the role (taken to the end)
            roleName = fullMessage[(fullMessage.find(commandList[1]) + len(commandList[1]) + 1):]
            # do check for role name on server
            for role in message.guild.roles:
                if(str(role) == roleName):
                    # name exists - set roleID value
                    roleID = role.id
        # @ symbol was found. Use the <@&IDNUMBER> form to substring it and fail anything that fails this form
        else:
            # check if "<@&" and ">" exists and the closing ">" is the last character
            if "<@&" in fullMessage and ">" in fullMessage and (len(fullMessage) - 1 == fullMessage.find(">")):
                roleID = int(fullMessage[fullMessage.find("<@&")+3:fullMessage.find(">")])
                # we know the roleID is a good value but we need to grab the name from the server
                roleName = message.guild.get_role(roleID).name
        if roleID == -1:
            #Error: role could not be found
            return False
        logging.info(f'Changing member role name value from {ACTIVE_CONF["MEMBER_ROLE_NAME"]} to {roleName}')
        ACTIVE_CONF["MEMBER_ROLE_NAME"] = roleName
        logging.info(f'Changing member role id value from {ACTIVE_CONF["MEMBER_ROLE_ID"]} to {roleID}')
        ACTIVE_CONF["MEMBER_ROLE_ID"] = roleID
        updateConfFile()
        return roleName
    else:
        return False

### This function will change the role used as the "moderator" on the server
def changeModeratorRole(message):
    global ACTIVE_CONF
    fullMessage = message.content
    # Change the bot member conf value and update discord server side
    commandList = fullMessage.split()
    # A role should either be preceded with an "@" character or be a string of text (possibly with whitespaces)
    if len(commandList) >= 3:
        atPos = fullMessage.find("@")
        roleID = -1
        # No @ symbol. Use the remainder of the command then
        if atPos == -1:
            # the substring used is the pos of the command + the length of the command + 1 which places the start
            # at the name of the role (taken to the end)
            roleName = fullMessage[(fullMessage.find(commandList[1]) + len(commandList[1]) + 1):]
            # do check for role name on server
            for role in message.guild.roles:
                if(str(role) == roleName):
                    # name exists - set roleID value
                    roleID = role.id
        # @ symbol was found. Use the <@&IDNUMBER> form to substring it and fail anything that fails this form
        else:
            # check if "<@&" and ">" exists and the closing ">" is the last character
            if "<@&" in fullMessage and ">" in fullMessage and (len(fullMessage) - 1 == fullMessage.find(">")):
                roleID = int(fullMessage[fullMessage.find("<@&")+3:fullMessage.find(">")])
                # we know the roleID is a good value but we need to grab the name from the server
                roleName = message.guild.get_role(roleID).name
        if roleID == -1:
            #Error: role could not be found
            return False
        logging.info(f'Changing moderator role name value from {ACTIVE_CONF["MODERATOR_ROLE_NAME"]} to {roleName}')
        ACTIVE_CONF["MODERATOR_ROLE_NAME"] = roleName
        logging.info(f'Changing moderator role id value from {ACTIVE_CONF["MODERATOR_ROLE_ID"]} to {roleID}')
        ACTIVE_CONF["MODERATOR_ROLE_ID"] = roleID
        updateConfFile()
        return roleName
    else:
        return False

### This function will add a phrase to the list of available phrases
def addPhrase(message):
    global ACTIVE_CONF
    fullMessage = message.content
    # Change the bot phrases list conf value and update discord server side
    commandList = fullMessage.split()
    # A phrase should be some text following the prefix and command (possibly with whitespace)
    if len(commandList) >= 3:
        # the substring used is the pos of the command + the length of the command + 1 which places the start
        # at the beginning of the phrase (taken to the end)
        phrase = fullMessage[(fullMessage.find(commandList[1]) + len(commandList[1]) + 1):]
        # do check for phrase already in list
        if phrase in ACTIVE_CONF["PHRASES"]:
            # already in list
            logging.info(f'Given phrase is already in the list, doing nothing')
            return True
        else:
            logging.info(f'Adding passed in phrase to list of Bobby phrases')
            ACTIVE_CONF["PHRASES"].append(phrase)
            updateConfFile()
            return phrase
    else:
        return False # format of command is bad

### This function will choose a random phrase from the list of available phrases
def chooseRandomPhrase():
    global ACTIVE_CONF
    # check if phrase list is empty - return False if it is
    if ACTIVE_CONF["PHRASES"]:
        return random.choice(ACTIVE_CONF["PHRASES"])
    else:
        return False

### Handle main function def for standalone application
if __name__ == '__main__':
    main()