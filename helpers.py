"""Contains helper functions for the ranker bot."""

import json
import re
from discord import Embed, Color
import logging

TIER_EMOJIS = {
    "myth": (
        "<:mythic1:1063075588002304041><:mythic2:1063075586433630271>"
        "<:mythic3:1063075585166950420><:mythic4:1063075582943965244>"
    ),
    "legendary": (
        "<:legendary1:1063075603449925712><:legendary2:1063075602187440259>"
        "<:legendary3:1063075591542292561><:legendary4:1063075589763891234>"
    ),
    "epic": (
        "<:epic1:1063075611377156246><:epic2:1063075609741373472>"
        "<:epic3:1063075607711330314><:epic4:1063075605886795877>"
    ),
    "rare": (
        "<:rare1:1063071963238629437><:rare2:1063072369859633232>"
        "<:rare3:1063072387538624572><:rare4:1063072404026433566>"
    ),
    "uncommon": (
        "<:uncommon1:1063073463516004352><:uncommon2:1063073478250606623>"
        "<:uncommon3:1063073517605748807><:uncommon4:1063073535934865429>"
    ),
    "common": (
        "<:common1:1063074109124247603><:common2:1063074112009936936>"
        "<:common3:1063074114149044344><:common4:1063074174295363675>"
    ),
}

TIER_COLORS = {
    "myth": "#9f0d19",
    "legendary": "#b35a00",
    "epic": "#6f01b4",
    "rare": "#007db3",
    "uncommon": "#189e66",
    "common": "#4e5558",
}


def parseJSON(file):
    """Parse JSON data.

    Args:
        file (str): JSON file.

    Returns:
        dict: Python dictionary.
    """
    data = json.load(open(file, "r"))
    parsed_data = {
        re.search(r"(?<=Freedom Fighter #)(\d+)", data[i]["name"]).group(): data[i]
        for i in range(0, len(data), 1)
    }
    return parsed_data


def getTierColor(tier):
    """Get tier color.

    Args:
        tier (str): Rarity tier.

    Returns:
        str: Tier color.

    Raises:
        Exception: Tier not found.
    """
    try:
        return TIER_COLORS[tier.lower()]
    except KeyError:
        raise Exception(f"Tier {tier} not found.")


def getTierEmoji(tier):
    """Get tier emoji string.

    Args:
        tier (str): Rarity tier.

    Returns:
        str: Trier emoji string.

    Raises:
        Exception: Tier not found.
    """
    try:
        return TIER_EMOJIS[tier.lower()]
    except KeyError:
        raise Exception(f"Tier {tier} not found.")


def getFighterNumber(magiceden_message):
    """Get fighter number from ME message.

    Args:
        magiceden_message (str): ME message.

    Returns:
        int: Fighter number.
    """
    solrarity_embed_title = magiceden_message.embeds[0].title
    fighter_number = re.search(r"(?<=Freedom Fighter #)(\d+)", solrarity_embed_title)
    if fighter_number is None:
        logging.warning("Fighter number not found.")
        return
    else:
        fighter_number = fighter_number.group()
    return int(fighter_number)


def getFighterRank(rank_dict, fighter_number):
    """Get fighter rank.

    Args:
        rank_dict (dict): Rank dictionary.
        fighter_number (int): Fighter number.

    Returns:
        dict: Fighter rank dictionary. None if not found.
    """
    try:
        return rank_dict[str(fighter_number)]
    except KeyError:
        return None


def createRankEmbed(fighter_rank, fighter_tier):
    """Create not found embed.

    Args:
        fighter_number (int): Fighter rank.
        fighter_number (str): Fighter tier.

    Returns:
        discord.Embed: Embed object.
    """
    return Embed(
        title=(f"🏆・Rank: {fighter_rank} ・ " "{}".format(getTierEmoji(fighter_tier))),
        color=Color.from_str(getTierColor(fighter_tier)),
    )


def createInfoEmbed(text):
    """Create info embed.

    Args:
        text (string): Info text.

    Returns:
        discord.Embed: Embed object.
    """
    return Embed(title=(f":information_source:・{text}"))


def createNotFoundEmbed(fighter_number):
    """Create not found embed.

    Args:
        fighter_number (int): Fighter number.

    Returns:
        discord.Embed: Embed object.
    """
    return createInfoEmbed(
        f"Rank of Freedom Fighter `{fighter_number}` could not be found.・🤔"
    )


async def createFighterRankEmbed(fighter_number, ranks_dict):
    """Create fighter rank embed message.

    Args:
        fighter_number (int): Fighter number.
        ranks_dict (dict): Rank dictionary.

    Returns:
        discord.Embed: Discord embed message.
    """
    fighter_rank = getFighterRank(ranks_dict, fighter_number)
    if fighter_rank is None:  # If not found.
        logging.warning(f"Rank of Fighter `{fighter_number}` not found.")
        return createNotFoundEmbed(fighter_number)
    return createRankEmbed(fighter_rank["rank"], fighter_rank["tier"])
