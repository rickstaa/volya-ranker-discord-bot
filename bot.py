"""VOLYA ranker bot."""

import logging
import os

import discord
from discord import Intents, app_commands, Client
from helpers import (
    parse_JSON,
    create_fighter_rank_embed,
    get_fighter_number,
    create_help_embed,
)

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ME_BOT_NAME = "2.5 Magic Eden Bot"

RANKS = parse_JSON("volya_ranks.json")


class RankerBot(Client):
    """Ranker Bot class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.synced = False

    async def on_ready(self):
        """Make sure the bot is ready."""
        logging.debug("Logging in.")
        await self.wait_until_ready()
        logging.debug("Syncing slash commands.")
        if not self.synced:
            await tree.sync(guild=discord.Object(id=947791831582793748))
            self.synced = True
            logging.debug("Slash commands synced.")
        logging.debug(f"Logged on as {self.user}!")

    async def on_message(self, message):
        """Display rank and tier when a ME sale or buy message is sent."""
        if (
            message.author.bot
            and message.author.name.lower() == ME_BOT_NAME.lower()
            and len(message.embeds) > 0
        ):
            fighter_number = get_fighter_number(message)
            channel = message.channel

            # Post rank and tier embed.
            if fighter_number is not None:
                embed = await create_fighter_rank_embed(fighter_number, RANKS)
                await channel.send(embed=embed)


if __name__ == "__main__":
    intents = Intents.default()
    intents.message_content = True

    # Create bot.
    client = RankerBot(intents=intents)
    tree = app_commands.CommandTree(client)

    # Add help command.
    @tree.command(
        name="help",
        description="Get information about our Ranker bot.",
        guild=discord.Object(id=947791831582793748),
    )
    async def help(
        interaction: discord.Interaction,
    ):
        await interaction.response.send_message(embed=await create_help_embed())

    # Add rank command.
    @tree.command(
        name="rank",
        description="Check the rank and rarity tier of your Freedom Fighter.",
        guild=discord.Object(id=947791831582793748),
    )
    async def rank(
        interaction: discord.Interaction,
        tokenid: app_commands.Range[int, 1, 5000],
    ):
        await interaction.response.send_message(
            embed=await create_fighter_rank_embed(tokenid, RANKS)
        )

    client.run(BOT_TOKEN)
