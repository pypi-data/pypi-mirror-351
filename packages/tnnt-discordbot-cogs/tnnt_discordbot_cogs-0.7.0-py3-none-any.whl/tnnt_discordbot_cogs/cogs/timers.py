"""
All about the timers …
"""

# Standard Library
import datetime
import logging

# Third Party
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands
from structuretimers.models import Timer

# Django
from django.apps import apps

# Alliance Auth
from allianceauth.eveonline.templatetags.evelinks import dotlan_solar_system_url

# Alliance Auth Discord Bot
from aadiscordbot.app_settings import ADMIN_DISCORD_BOT_CHANNELS
from aadiscordbot.cogs.utils.decorators import message_in_channels

# Alliance Auth (External Libs)
from app_utils.urls import reverse_absolute

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)


def structuretimers_active():
    """
    Check if "structuretimers" is installed
    :return:
    :rtype:
    """

    return apps.is_installed("structuretimers")


def timezones_active():
    """
    Check if "timezones" is installed
    :return:
    :rtype:
    """

    return apps.is_installed("timezones")


def add_empty_line(embed: Embed) -> None:
    """
    Adding an empty line to the embed

    :param embed:
    :type embed:
    :return:
    :rtype:
    """

    embed.add_field(
        name="\u200b",
        value="\u200b",
        inline=False,
    )


class Timers(commands.Cog):
    """
    TimerBoard Stuffs!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @message_in_channels(ADMIN_DISCORD_BOT_CHANNELS)
    async def timer(self, ctx):
        """
        Gets the Next Timer!

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        embed = Embed(title="Next Timer")

        next_timer = Timer.objects.filter(
            is_opsec=False,
            visibility=Timer.VISIBILITY_UNRESTRICTED,
            date__gte=datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc),
        ).first()

        if next_timer is None:
            embed.description = "No upcoming timer"
        else:
            if next_timer.objective == Timer.OBJECTIVE_FRIENDLY:
                embed.colour = Color.blue()
            elif next_timer.objective == Timer.OBJECTIVE_HOSTILE:
                embed.colour = Color.red()
            elif next_timer.objective == Timer.OBJECTIVE_NEUTRAL:
                embed.colour = Color.light_gray()
            elif next_timer.objective == Timer.OBJECTIVE_UNDEFINED:
                embed.colour = Color.dark_gray()
            else:
                embed.colour = Color.from_rgb(r=255, g=255, b=255)

            user_has_profile = True

            if next_timer.user is not None:
                creator_name = next_timer.user.username

                try:
                    creator_profile = next_timer.user.profile
                except Exception:
                    user_has_profile = False

                if user_has_profile is True:
                    if creator_profile.main_character is not None:
                        creator_name = creator_profile.main_character.character_name

                embed.set_footer(text=f"Timer added by {creator_name}")

            embed.add_field(name="Structure:", value=next_timer.structure_type.name)

            solar_system_name = next_timer.eve_solar_system.name
            solar_system_link = dotlan_solar_system_url(next_timer.eve_solar_system)
            solar_system_md_link = f"[{solar_system_name}]({solar_system_link})"
            location_details = next_timer.location_details

            embed.add_field(
                name="Location:", value=f"{solar_system_md_link}\n{location_details}"
            )

            add_empty_line(embed=embed)

            timer_timestamp = str(int(next_timer.date.timestamp()))

            if timezones_active():
                timezones_url = reverse_absolute(
                    viewname="timezones:index",
                    args=[timer_timestamp],
                )
                timezones_md_link = f"[TZ Conversion]({timezones_url})"
                timer_eve_time = next_timer.date.strftime("%Y-%m-%d %H:%M")

                embed.add_field(
                    name="Eve Time:",
                    value=f"{timer_eve_time} ({timezones_md_link})",
                    inline=True,
                )
            else:
                embed.add_field(
                    name="Eve Time:",
                    value=next_timer.eve_time.strftime("%Y-%m-%d %H:%M"),
                    inline=True,
                )

            embed.add_field(
                name="Local Time:",
                value=f"<t:{timer_timestamp}:F>",
                inline=True,
            )

        return await ctx.send(embed=embed)


def setup(bot):
    """
    Set up the cog

    :param bot:
    :type bot:
    :return:
    :rtype:
    """

    if structuretimers_active():
        # Unload the Timers cog from `aadiscordbot`, so we can load our own.
        unload_cog(bot=bot, cog_name="Timers")

        # Add the Timers cog to the bot
        bot.add_cog(Timers(bot))
    else:
        logger.debug("Timerboard not installed")
