"""VOLYA ranker bot."""

import logging
import os

from discord import Client, Intents, Embed
from helpers import (
    parseJSON,
    createFighterRankEmbed,
    getFighterNumber,
)

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
STAKE_STATS_CHANNEL_ID = os.getenv("STAKE_STATS_CHANNEL_ID")
ME_BOT_NAME = "VOLYA Ranker"
# ME_BOT_NAME = "2.5 Magic Eden Bot"

RANKS = parseJSON("volya_ranks.json")


class RankerBot(Client):
    """Ranker Bot class."""

    async def on_ready(self):
        """Make sure the bot is ready."""
        logging.debug(f"Logged on as {self.user}!")

        self._channel = self.get_channel(int(STAKE_STATS_CHANNEL_ID))
        if self._channel is None:
            logging.error(f"Channel {STAKE_STATS_CHANNEL_ID} not found.")
            return

        embed = Embed(
            title="Freedom Fighter #1534 [View details]",
            description="Desc",
            color=0x00FF00,
        )
        embed.add_field(
            name="Like header in HTML", value="Text of field  1", inline=False
        )
        embed.add_field(
            name="Like header in html", value="text of field 2", inline=False
        )
        await self._channel.send(embed=embed)

    async def on_message(self, message):
        """Display rank and tier when a ME sale or buy message is sent."""
        if (
            message.author.bot
            and message.author.name == ME_BOT_NAME
            and len(message.embeds) > 0
        ):
            fighter_number = getFighterNumber(message)

            # Post rank and tier embed.
            if fighter_number is not None:
                embed = await createFighterRankEmbed(fighter_number, RANKS)
                await self._channel.send(embed=embed)


if __name__ == "__main__":
    intents = Intents.default()
    intents.message_content = True

    client = RankerBot(intents=intents)
    client.run(BOT_TOKEN)
