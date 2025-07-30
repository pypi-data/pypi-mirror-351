"""
"Members" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

# Standard Library
import logging

# Third Party
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands

# Django
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# Alliance Auth
from allianceauth.eveonline.evelinks import evewho
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth Discord Bot
from aadiscordbot.app_settings import (
    ADMIN_DISCORD_BOT_CHANNELS,
    DISCORD_BOT_MEMBER_ALLIANCES,
    aastatistics_active,
)
from aadiscordbot.cogs.utils.decorators import message_in_channels, sender_has_any_perm

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)


class Members(commands.Cog):
    """
    All about users!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @sender_has_any_perm(
        ["corputils.view_alliance_corpstats", "corpstats.view_alliance_corpstats"]
    )
    @message_in_channels(ADMIN_DISCORD_BOT_CHANNELS)
    async def lookup(self, ctx):
        """
        Gets Auth data about a character
        Input: An Eve Character Name

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        input_name = ctx.message.content[8:]
        embed = Embed(title=f"Character Lookup {input_name}")

        try:
            char = EveCharacter.objects.get(character_name=input_name)

            try:
                main = char.character_ownership.user.profile.main_character
                state = char.character_ownership.user.profile.state.name
                groups = char.character_ownership.user.groups.all().values_list(
                    "name", flat=True
                )

                try:
                    discord_string = f"<@{char.character_ownership.user.discord.uid}>"
                except Exception as e:
                    logger.error(msg=e)
                    discord_string = "unknown"

                if aastatistics_active():
                    alt_characters = (
                        char.character_ownership.user.character_ownerships.all()
                        .select_related("character", "character_stats")
                        .values_list(
                            "character__character_name",
                            "character__corporation_ticker",
                            "character__character_id",
                            "character__corporation_id",
                            "character__character_stats__zk_12m",
                            "character__character_stats__zk_3m",
                        )
                    )
                    zk12 = 0
                    zk3 = 0
                else:
                    alt_characters = (
                        char.character_ownership.user.character_ownerships.all()
                        .select_related("character")
                        .values_list(
                            "character__character_name",
                            "character__corporation_ticker",
                            "character__character_id",
                            "character__corporation_id",
                        )
                    )
                    zk12 = "Not Installed"
                    zk3 = "Not Installed"

                if aastatistics_active():
                    for alt_character in alt_characters:
                        if alt_character[4]:
                            zk12 += alt_character[4]
                            zk3 += alt_character[5]

                embed.colour = Color.blue()

                if main is None:
                    embed.description = (
                        f"**{char}** is not associated with any Auth account …"
                    )
                else:
                    embed.description = (
                        f"**{char}** is linked to **{main} "
                        f"[{main.corporation_ticker}]** (State: {state})"
                    )

                alt_list = []
                for alt_character in alt_characters:
                    alt_list.append(
                        f"[{alt_character[0]}](https://evewho.com/character/{alt_character[2]}) "  # pylint: disable=line-too-long
                        f"[[{alt_character[1]}](https://evewho.com/corporation/{alt_character[3]})]"  # pylint: disable=line-too-long
                    )

                for idx, names in enumerate(
                    [alt_list[i : i + 6] for i in range(0, len(alt_list), 6)]
                ):
                    if idx < 6:
                        embed.add_field(
                            name=f"Linked Characters {idx + 1}",
                            value="\n".join(names),
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name=(
                                f"Linked Characters {idx} "
                                "**(Discord Limited There are More)**"
                            ),
                            value="\n".join(names),
                            inline=False,
                        )
                        break

                if len(groups) > 0:
                    embed.add_field(
                        name="Groups", value=", ".join(groups), inline=False
                    )

                if aastatistics_active():
                    embed.add_field(name="12m Kills", value=zk12, inline=True)
                    embed.add_field(name="3m Kills", value=zk3, inline=True)

                embed.add_field(name="Discord Link", value=discord_string, inline=False)

                return await ctx.send(embed=embed)
            except ObjectDoesNotExist:
                users = char.ownership_records.values("user")
                users = User.objects.filter(id__in=users)
                characters = EveCharacter.objects.filter(
                    ownership_records__user__in=users
                ).distinct()
                embed = Embed(title="Character Lookup")
                embed.colour = Color.blue()

                embed.description = (
                    f"**{char}** is unlinked, searching for any "
                    "characters linked to known users"
                )
                user_names = [f"{user.username}" for user in users]
                embed.add_field(
                    name="Old Users", value="\n".join(user_names), inline=False
                )

                alt_list = []
                for character in characters:
                    alt_list.append(
                        f"[{character.character_name}](https://evewho.com/character/{character.character_id}) "  # pylint: disable=line-too-long
                        f"[[{character.corporation_ticker}](https://evewho.com/corporation/{character.corporation_id})]"  # pylint: disable=line-too-long
                    )

                for idx, names in enumerate(
                    [alt_list[i : i + 6] for i in range(0, len(alt_list), 6)]
                ):
                    if idx < 6:
                        embed.add_field(
                            name=f"Found Characters {idx + 1}",
                            value="\n".join(names),
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name=(
                                f"Found Characters {idx} "
                                "**(Discord Limited There are More)**"
                            ),
                            value="\n".join(names),
                            inline=False,
                        )
                        break

                return await ctx.send(embed=embed)
        except EveCharacter.DoesNotExist:
            embed.colour = Color.red()

            embed.description = (
                f"Character **{input_name}** does not exist in our Auth system"
            )

            return await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    @sender_has_any_perm(
        ["corputils.view_alliance_corpstats", "corpstats.view_alliance_corpstats"]
    )
    @message_in_channels(ADMIN_DISCORD_BOT_CHANNELS)
    async def altcorp(self, ctx):
        """
        Gets Auth data about an altcorp
        Input: An Eve Corporation Name

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        input_name = ctx.message.content[9:]
        chars = EveCharacter.objects.filter(corporation_name=input_name)
        own_ids = [DISCORD_BOT_MEMBER_ALLIANCES]
        alts_in_corp = []

        for char in chars:
            if char.alliance_id not in own_ids:
                alts_in_corp.append(char)

        mains = {}

        for alt_char in alts_in_corp:
            try:
                main = alt_char.character_ownership.user.profile.main_character

                if main.character_id not in mains:
                    mains[main.character_id] = [main, 0]

                mains[main.character_id][1] += 1
                # alt_corp_id = a.corporation_id
            except Exception as e:
                logger.error(msg=e)

        output = []
        base_string = "[{}]({}) [[{}]({})] has {} alt{}"

        for _, main_char in mains.items():
            output.append(
                base_string.format(
                    main_char[0],
                    evewho.character_url(main_char[0].character_id),
                    main_char[0].corporation_ticker,
                    evewho.corporation_url(main_char[0].corporation_id),
                    main_char[1],
                    "s" if main_char[1] > 1 else "",
                )
            )

        for strings in [output[i : i + 10] for i in range(0, len(output), 10)]:
            embed = Embed(title=input_name)
            embed.colour = Color.blue()
            embed.description = "\n".join(strings)

            await ctx.send(embed=embed)


def setup(bot):
    """
    Set up the cog

    :param bot:
    :type bot:
    :return:
    :rtype:
    """

    # Unload the Members cog from `aadiscordbot`, so we can load our own.
    unload_cog(bot=bot, cog_name="Members")

    # Add the Members cog to the bot
    bot.add_cog(Members(bot))
