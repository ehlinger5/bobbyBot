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
    "PHRASES": ["Relateable","Unbelievable","Me too","Cry about it"]
}
####################

def main():
    initialize()

    nest_asyncio.apply()

    #set bot client
    client = discord.Client()

    # log on event
    @client.event
    async def on_ready():
        logging.info('We have logged in as {0.user}'.format(client))

    # reading message event
    @client.event
    async def on_message(message):
        # if message is authored by client, do nothing (return)
        if message.author == client.user:
            return
        
        # checks for messages starting with bot prefix
        if message.content.startswith(ACTIVE_CONF["BOT_PREFIX"]):
            # Replace the following with actual code...
            await message.channel.send("Found Prefix")
            # updating conf from file command must be performed by admin roles
            # Make checks for supported commands and then make those calls
            # Change bot name and change bot prefix must be performed by admin roles
            # Sending a bobby message can be performed by anyone
            # Adding a bobby message can be performed by moderator and admin roles

    # Add code to get key from file instead of plain text
    with open(ACTIVE_CONF["DISCORD_KEY_FILE"]) as keyFile:
        logging.info(f'Discord API key has been taken from the following file: {ACTIVE_CONF["DISCORD_KEY_FILE"]}\n')
        client.run(keyFile.read())

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

def loadConf(confFileName):
    global ACTIVE_CONF
    # Check for existence of file
    confExists = os.path.exists(confFileName)

    # If exists, load
    if confExists:
        with open(confFileName, "r") as confFile:
            data = json.load(confFile)
            print(f'Read in configuration file {confFileName}')
            
        # Load file values into active configuration
        ACTIVE_CONF = data
        print('Loaded configuration')

    # If does not exist, create default
    else:
        print(f'No configuration file ({confFileName}) was found. Generating default configuration...')
        with open(confFileName, "w") as confFile:
            json.dump(ACTIVE_CONF, confFile)

def updateConf():
    global CONF_FILE_NAME
    # Update the variables with values from the configuration file
    logging.info(f'Updating variables from configuration file for {ACTIVE_CONF["BOT_NAME"]}')
    loadConf(CONF_FILE_NAME)

def changeBotPrefix(prefix):
    # Change the bot prefix conf value
    logging.info(f'Changing {ACTIVE_CONF["BOT_NAME"]} prefix from {ACTIVE_CONF["BOT_PREFIX"]} to {prefix}')

def changeBotName(name):
    # Change the bot name conf value
    logging.info(f'Changing the bot\'s name from {ACTIVE_CONF["BOT_NAME"]} to {name}')
    

# Handle main function def for standalone application
if __name__ == '__main__':
    main()