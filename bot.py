"""VOLYA ranker bot."""

import logging
import os
from discord.ext import commands

from discord import Intents
from helpers import (
    parseJSON,
    createFighterRankEmbed,
    getFighterNumber,
    createInfoEmbed,
)

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ME_BOT_NAME = "2.5 Magic Eden Bot"

RANKS = parseJSON("volya_ranks.json")


class RankerBot(commands.Bot):
    """Ranker Bot class."""

    async def on_ready(self):
        """Make sure the bot is ready."""
        logging.debug(f"Logged on as {self.user}!")

    async def on_message(self, message):
        """Display rank and tier when a ME sale or buy message is sent."""
        if (
            message.author.bot
            and message.author.name.lower() == ME_BOT_NAME.lower()
            and len(message.embeds) > 0
        ):
            fighter_number = getFighterNumber(message)
            channel = message.channel

            # Post rank and tier embed.
            if fighter_number is not None:
                embed = await createFighterRankEmbed(fighter_number, RANKS)
                await channel.send(embed=embed)

        # Make sure commands are processed
        await self.process_commands(message)


def parseRankerCommandArgs(message, command_prefix, command):
    """Parse ranker command arguments.

    Args:
        message (str): Message content.
        command_prefix (str): Command prefix.
        command (str): Command name.

    Returns:
        int: freedom fighter number. Returns None if command could not be parsed.
    
    Throws:
        ValueError: If arguments are invalid.
    """    
    args = message.replace(command_prefix + command, "").split(" ")
    args = [arg for arg in args if arg]
    args = [arg.strip() for arg in args]

    # Check if args are valid.
    if len(args) != 1:
        raise ValueError("Please specify a single fighter number and try again.・🤖")
    if not args[0].isdigit():
        raise ValueError("Please specify a integer and try again.・🤖")
    if int(args[0]) <= 0:
        raise ValueError("Fighter number has to be between 1 and 5000.・😅")
    if int(args[0]) > 5000:
        raise ValueError("Fighter number has to be between 1 and 5000.・😅")
    return int(args[0])


if __name__ == "__main__":
    intents = Intents.default()
    intents.message_content = True

    client = RankerBot(intents=intents, command_prefix="!")

    # Add commands.
    @client.command()
    async def volyaRank(ctx):
        try:
            args = parseRankerCommandArgs(
                ctx.message.content, ctx.clean_prefix, ctx.invoked_with
            )
        except Exception as e:
            await ctx.message.channel.send(embed=createInfoEmbed(e.args[0]))
            return

        # Create and send rank embed.
        embed = await createFighterRankEmbed(args, RANKS)
        await ctx.message.channel.send(embed=embed)

    client.run(BOT_TOKEN)
