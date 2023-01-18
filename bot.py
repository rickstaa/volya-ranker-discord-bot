"""VOLYA ranker bot."""

import logging
import os

import discord
from discord import Intents, app_commands, Client, Interaction
from helpers import (
    create_fighter_rank_embed,
    change_sniper_role,
    get_fighter_number,
    create_help_embed,
    get_volya_ranks,
    get_tier_sniper_role_mention,
    create_config_embed,
)

GUILD_ID = "947791831582793748"
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ME_BOT_NAME = "2.5 Magic Eden Bot"

RANKS = get_volya_ranks()


class RankerBot(Client):
    """Ranker Bot class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.synced = False

    async def on_ready(self):
        """Make sure the bot is ready."""
        logging.debug("Logging in.")
        await self.wait_until_ready()

        # Sync commands to guild.
        logging.debug("Syncing slash commands.")
        if not self.synced:
            await tree.sync(guild=discord.Object(id=GUILD_ID))
            self.synced = True
            logging.debug("Slash commands synced.")
        logging.debug(f"Logged on as {self.user}!")

    async def on_message(self, message):
        """Display rank, tier and staking rate when a ME sale or buy message is sent."""
        if (
            message.author.bot
            and message.author.name.lower() == ME_BOT_NAME.lower()
            and len(message.embeds) > 0
        ):
            fighter_number = get_fighter_number(message)
            channel = message.channel

            # Check if the message is a sale or listing message.
            try:
                message.embeds[0].description.lower()
            except AttributeError:
                return  # Not a sale or buy message.

            # Add mention if the message is a listing message.
            mention = (
                True if "listed" in message.embeds[0].description.lower() else False
            )

            # Post rank, tier and staking rate embed.
            if fighter_number is not None:
                embed, rank_dict = create_fighter_rank_embed(
                    fighter_number, RANKS
                )
                await channel.send(
                    # NOTE: Add mention before embed since you cannot ping inside embed.
                    get_tier_sniper_role_mention(rank_dict["tier"]) if mention else "",
                    embed=embed,
                )


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
        guild=discord.Object(id=GUILD_ID),
    )
    async def help(
        interaction: Interaction,
    ):
        await interaction.response.send_message(
            embed=create_help_embed(), ephemeral=True
        )

    # Add rank command.
    @tree.command(
        name="rank",
        description="Check the rank and rarity tier of your Freedom Fighter.",
        guild=discord.Object(id=GUILD_ID),
    )
    async def rank(
        interaction: Interaction,
        tokenid: app_commands.Range[int, 1, 5000],
    ):
        embed, _ = create_fighter_rank_embed(tokenid, RANKS)
        await interaction.response.send_message(embed=embed)

    # Add sniper role enable command.
    @app_commands.choices(
        tier=[
            app_commands.Choice(name="Mythic", value="mythic"),
            app_commands.Choice(name="Legendary", value="legendary"),
            app_commands.Choice(name="Epic", value="epic"),
            app_commands.Choice(name="Rare", value="rare"),
            app_commands.Choice(name="Uncommon", value="uncommon"),
            app_commands.Choice(name="Common", value="common"),
        ],
        action=[
            app_commands.Choice(name="Enable", value=1),
            app_commands.Choice(name="Disable", value=0),
        ],
    )
    @tree.command(
        name="sniper",
        description="Enable/disable sniper mentions for a given rarity tier.",
        guild=discord.Object(id=GUILD_ID),
    )
    async def sniper(
        interaction: Interaction,
        tier: str,
        action: int,
    ):
        await change_sniper_role(interaction, tier, action)

    # Add config command.
    @tree.command(
        name="config",
        description="Shows the current bot configuration.",
        guild=discord.Object(id=GUILD_ID),
    )
    async def config(
        interaction: Interaction,
    ):
        await interaction.response.send_message(
            embed=create_config_embed(interaction), ephemeral=True
        )

    client.run(BOT_TOKEN)
