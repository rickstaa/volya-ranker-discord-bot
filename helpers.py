"""Contains helper functions for the ranker bot."""

import json
import re
from discord import Embed, Color, Object, utils
import logging
from math import floor

TIER_EMOJIS = {
    "mythic": (
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
    "mythic": "#9f0d19",
    "legendary": "#b35a00",
    "epic": "#6f01b4",
    "rare": "#007db3",
    "uncommon": "#189e66",
    "common": "#4e5558",
}

TIER_SNIPER_ROLES = {
    "mythic": "1063954538521952257",
    "legendary": "1063954755442982943",
    "epic": "1063954819896836166",
    "rare": "1063954910544150639",
    "uncommon": "1063954980421255300",
    "common": "1063955086776217690",
}

TIER_STAKING_REWARDS = {
    "mythic": 3.3,
    "legendary": 2.75,
    "epic": 2.2,
    "rare": 1.65,
    "uncommon": 1.10,
    "common": 0.55,
}


def get_volya_ranks():
    """Get VOLYA ranks from Solrarity JSON file and correct them for missing 1/1s.

    Returns:
        dict: Corrected VOLYA ranks.
    """

    # Get SolRanker NFT ranks.
    solrarity_ranks = load_JSON("./assets/volya_solrarity_ranks.json")

    # Get incorrectly ranked NFTs.
    rank_corrections = load_JSON("./assets/rank_corrections.json")

    # Remove incorrectly ranked NFTs.
    for fighter_number in rank_corrections:
        del solrarity_ranks[fighter_number]

    # Prepend correct ranks.
    volya_ranks = {**rank_corrections, **solrarity_ranks}

    # Update ranks and tiers.
    # NOTE: Percentages taken from solrarity discord FAQ channel.
    for idx, (fighter, _) in enumerate(volya_ranks.items()):
        rank = idx + 1
        volya_ranks[fighter]["rank"] = rank
        if rank <= floor(0.01 * len(volya_ranks)):
            volya_ranks[fighter]["tier"] = "Mythic"
        elif rank <= floor(0.05 * len(volya_ranks)):
            volya_ranks[fighter]["tier"] = "Legendary"
        elif rank <= floor(0.15 * len(volya_ranks)):
            volya_ranks[fighter]["tier"] = "Epic"
        elif rank <= floor(0.35 * len(volya_ranks)):
            volya_ranks[fighter]["tier"] = "Rare"
        elif rank <= floor(0.6 * len(volya_ranks)):
            volya_ranks[fighter]["tier"] = "Uncommon"
        else:
            volya_ranks[fighter]["tier"] = "Common"

    # Save corrected ranks.
    save_JSON(volya_ranks, "./assets/volya_solrarity_ranks_corrected.json")

    return volya_ranks


def load_JSON(file):
    """Load JSON data and return as VOLYA fighter ranking object.

    Args:
        file (str): JSON file.

    Returns:
        dict: VOLYA fighter ranking object.
    """
    data = json.load(open(file, "r"))
    parsed_data = {
        re.search(r"(?<=Freedom Fighter #)(\d+)", data[i]["name"]).group(): data[i]
        for i in range(0, len(data), 1)
    }
    return parsed_data


def save_JSON(data, file):
    """Save VOLYA fighter ranking object as Solrarity ranking data struct.

    Args:
        data (dict): Python dictionary.
        file (str): JSON file.
    """
    solrarity_data = [fighter for _, fighter in data.items()]
    with open(file, "w") as outfile:
        json.dump(solrarity_data, outfile)


def get_tier_color(tier):
    """Get rarity tier color.

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


def get_tier_emoji(tier):
    """Get rarity tier emoji string.

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


def get_fighter_number(magiceden_message):
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


def get_fighter_rank(rank_dict, fighter_number):
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


def get_role_mention(role_id):
    """Get role mention string.

    Args:
        role (str): Role id.

    Returns:
        string: Role mention string.
    """
    try:
        return "<@&{}>".format(role_id)
    except KeyError:
        return None


def get_tier_sniper_role_mention(tier):
    """Get tier sniper role mention string.

    Args:
        tier (str): Rarity tier.

    Returns:
        string: Sniper mention role string.
    """
    try:
        return get_role_mention(TIER_SNIPER_ROLES[tier.lower()])
    except KeyError:
        return None


def create_info_embed(text):
    """Create info embed.

    Args:
        text (string): Info text.

    Returns:
        discord.Embed: Embed object.
    """
    return Embed(title="📢・Info", description=text, color=Color.from_str("#00b3ff"))


def create_not_found_embed(fighter_number):
    """Create fighter not found embed object.

    Args:
        fighter_number (int): Fighter number.

    Returns:
        discord.Embed: Fighter not found embed object.
    """
    return create_info_embed(
        f"Rank of Freedom Fighter `{fighter_number}` could not be found.・🤔"
    )


def create_rank_embed(fighter_number, fighter_rank, fighter_tier):
    """Create rank embed.

    Args:
        fighter_number (int): Fighter number.
        fighter_rank (str): Fighter rank.
        fighter_tier (str): Fighter tier.

    Returns:
        discord.Embed: Rank embed object.
    """
    rank_embed = Embed(
        title=(
            "🏆・[#{}]・Rank: {}・Stake reward: `{}`/day ・ {}".format(
                fighter_number,
                fighter_rank,
                TIER_STAKING_REWARDS[fighter_tier.lower()],
                get_tier_emoji(fighter_tier),
            )
        ),
        color=Color.from_str(get_tier_color(fighter_tier)),
    )
    return rank_embed


def create_fighter_rank_embed(fighter_number, ranks_dict):
    """Create fighter rank embed message.

    Args:
        fighter_number (int): Fighter number.
        ranks_dict (dict): Rank dictionary.

    Returns:
        tuple (discord.Embed, dict): Fighter rank embed message and fighter rank
            dictionary.
    """
    fighter_rank = get_fighter_rank(ranks_dict, fighter_number)
    if fighter_rank is None:  # If not found.
        logging.warning(f"Rank of Fighter `{fighter_number}` not found.")
        return create_not_found_embed(fighter_number)
    return (
        create_rank_embed(fighter_number, fighter_rank["rank"], fighter_rank["tier"]),
        fighter_rank,
    )


def create_sniper_action_embed(tier, action):
    """Create sniper action embed.

    Args:
        tier (string): Fighter tier.
        action (int): Role action. Options are 'enable' or 'disable' (i.e. 1 or 0).

    Returns:
        discord.Embed: Sniper discord embed message.
    """
    return Embed(
        title=":eyes:・`{}` fighter sniper `{}`.".format(
            tier.capitalize(), "enabled" if action else "disabled"
        ),
        color=Color.from_str(get_tier_color(tier)),
    )


def create_sniper_role_present_embed(tier, present):
    """Create sniper role present embed.

    Args:
        tier (string): Fighter tier.
        present (bool): Whether the sniper role is present.

    Returns:
        discord.Embed: Sniper role (not) present embed.
    """
    return Embed(
        title=":eyes:・`{}` fighter sniper role {} present.".format(
            tier.capitalize(), "already" if present else "not"
        ),
        color=Color.from_str(get_tier_color(tier)),
    )


def contains_role(interaction, role_id):
    """Check if user has a role.

    Args:
        interaction (discord.Interaction): Discord interaction object.
        role_id (int): Role ID.

    Returns:
        bool: Whether the user has the role.
    """
    return utils.get(interaction.guild.roles, id=role_id) in interaction.user.roles


def get_sniper_roles(interaction):
    """Get sniper roles.

    Args:
        interaction (discord.Interaction): Discord interaction object.

    Returns:
        list: List of sniper roles.
    """
    sniper_roles = []
    for role_id in TIER_SNIPER_ROLES.values():
        if contains_role(interaction, int(role_id)):
            sniper_roles.append(role_id)
    return sniper_roles


async def change_sniper_role(interaction, tier, action):
    """Add or remove tier sniper role.

    Args:
        interaction (discord.Interaction): Discord interaction object.
        tier (str): Sniper role tier.
        action (int): Action to perform on the role. 1 = add, 0 = remove.
    """
    if action == 1:
        if not contains_role(interaction, TIER_SNIPER_ROLES[tier]):
            await interaction.user.add_roles(Object(id=TIER_SNIPER_ROLES[tier]))
            await interaction.response.send_message(
                embed=create_sniper_action_embed(tier=tier, action=action),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                embed=create_sniper_role_present_embed(tier=tier, present=True),
                ephemeral=True,
            )
    else:
        if contains_role(interaction, TIER_SNIPER_ROLES[tier]):
            await interaction.user.remove_roles(Object(id=TIER_SNIPER_ROLES[tier]))
            await interaction.response.send_message(
                embed=create_sniper_action_embed(tier=tier, action=action),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                embed=create_sniper_role_present_embed(tier=tier, present=False),
                ephemeral=True,
            )


def create_help_embed():
    """Create help embed.

    Returns:
        discord.Embed: Help embed.
    """
    return Embed(
        title=":question:・Help",
        description=(
            "A simple bot that can be used to check the rank, rarity tier and staking "
            "reward of your VOLYA Freedom Fighter. 🤖💎"
            "\n\n"
            "It uses the rarity calculation provided by "
            "https://solrarity.app/dashboard but is adjusted so that the rarity tier "
            "of the `1/1` is shown correctly."
            "\n\n"
            "If you have any suggestions or experience problems, feel free to drop "
            "them in the <#1003297324187013141> channel! 🔥"
            "\n\n"
            "**Commands**\n"
            "> ⦁ `/rank <fighter_number>`: Get the rank of a fighter.\n"
            "> ⦁ `/sniper <tier> <enable/disable>`: Enable/disable tier sniper role. "
            "If enabled, you will be mentioned when a specified tier fighter is "
            "listed.\n"
            "> ⦁ `/config`: Get current bot configuration (i.e. active sniper roles).\n"
        ),
    )


def create_config_embed(interaction):
    """_summary_

    Args:
        interaction (discord.Interaction): Discord interaction object.

    Returns:
        discord.Embed: Configuration embed.
    """
    active_roles = [
        get_role_mention(role_id) for role_id in get_sniper_roles(interaction)
    ]
    return Embed(
        title=":wrench:・Config",
        description=(
            "Current config:\n"
            "> ⦁ Active sniper roles: {}\n".format(", ".join(active_roles))
        ),
    )
