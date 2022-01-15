"""
Created: 01/15/2022
Last Updated: 01/15/2022
@author: Josh Ehlinger (Ehlien)
"""

import logging
import discord
import nest_asyncio

####################
# CONF VALUES - Default values are replaced with conf file (bobbyBot.conf)
LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '[%(levelname)s]: %(message)s'
DISCORD_KEY_FILE = ".discordKey"
BOT_NAME = "Bobby Bot"
BOT_PREFIX = "!b"
####################

def main():
    initialize()

    nest_asyncio.apply()

    #set bot client
    client = discord.Client()

    # log on event
    @client.event
    async def on_ready():
        logging.debug('We have logged in as {0.user}'.format(client))

    # reading message event
    @client.event
    async def on_message(message):
        # if message is authored by client, do nothing (return)
        if message.author == client.user:
            return
        
        # checks for messages starting with bot prefix
        if message.content.startswith(BOT_PREFIX):
            # Replace the following with actual code...
            await message.channel.send("Found Prefix")
            # updating conf from file command must be performed by admin roles
            # Make checks for supported commands and then make those calls
            # Change bot name and change bot prefix must be performed by admin roles
            # Sending a bobby message can be performed by anyone
            # Adding a bobby message can be performed by moderator and admin roles

    # Add code to get key from file instead of plain text
    client.run('KEY_GOES_HERE')

def initialize():
    logging.debug('Initializing Bot...')

    # Load conf file
    loadConf("bobbyBot.conf")

    # Setup logger with basic config
    logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)

def loadConf(confFileName):
    # Check for existence of file

    # If exists, load

    # If does not exist, create default

    logging.debug(f'Loading Configuration File: {confFileName}')

def updateConf():
    # Update the variables with values from the configuration file
    logging.info(f'Updating variables from configuration file for {BOT_NAME}')

def changeBotPrefix(prefix):
    # Change the bot prefix conf value
    logging.info(f'Changing {BOT_NAME} prefix to: {BOT_PREFIX}')

def changeBotName(name):
    # Change the bot name conf value
    logging.info(f'Changing the bot\'s name to {BOT_NAME}')
    

# Handle main function def for standalone application
if __name__ == '__main__':
    main()