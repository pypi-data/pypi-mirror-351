"""
"Auth" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

# Standard Library
import logging

# Third Party
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands

# Django
from django.conf import settings

# Alliance Auth
from allianceauth.eveonline.evelinks.eveimageserver import (
    alliance_logo_url,
    corporation_logo_url,
)
from allianceauth.services.modules.discord.models import DiscordUser

# Alliance Auth Discord Bot
from aadiscordbot.app_settings import get_site_url
from aadiscordbot.cogs.utils.decorators import sender_is_admin

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)


class Auth(commands.Cog):
    """
    A Collection of Authentication Tools for Alliance Auth
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def auth(self, ctx):
        """
        Returns a link to TN-NT Auth
        Used by many other Bots and is a common command that users will attempt to run.

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.trigger_typing()

        auth_url = get_site_url()
        embed = Embed(title="Terra Nanotech Auth")

        try:
            if settings.TNNT_TEMPLATE_ENTITY_ID == 1:
                aa_icon = f"{auth_url}/static/allianceauth/icons/allianceauth.png"
                embed.set_thumbnail(url=aa_icon)
            else:
                if settings.TNNT_TEMPLATE_ENTITY_TYPE == "alliance":
                    embed.set_thumbnail(
                        url=alliance_logo_url(
                            alliance_id=settings.TNNT_TEMPLATE_ENTITY_ID, size=256
                        )
                    )
                elif settings.TNNT_TEMPLATE_ENTITY_TYPE == "corporation":
                    embed.set_thumbnail(
                        url=corporation_logo_url(
                            corporation_id=settings.TNNT_TEMPLATE_ENTITY_ID, size=256
                        )
                    )
        except AttributeError:
            pass

        embed.colour = Color.blue()

        embed.description = (
            "All authentication functions for this Discord "
            "server are handled through our Auth system."
        )

        embed.add_field(name="Auth Link", value=auth_url, inline=False)

        return await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    @sender_is_admin()
    async def orphans(self, ctx):
        """
        Returns a list of users on this server, who are unknown to TN-NT Auth

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.trigger_typing()
        await ctx.send("Searching for Orphaned Discord Users")
        await ctx.trigger_typing()

        payload = "The following Users cannot be located in Alliance Auth\n"

        member_list = ctx.message.guild.members

        for member in member_list:
            discord_member_id = member.id
            discord_member_is_bot = member.bot

            try:
                discord_member_exists = DiscordUser.objects.get(uid=discord_member_id)
            except DiscordUser.DoesNotExist as exception:
                logger.error(msg=exception)
                discord_member_exists = False

            if discord_member_exists is not False:
                # Nothing to do, the user exists. Move on with ur life dude.
                pass

            elif discord_member_is_bot is True:
                # Let's also ignore bots here
                pass
            else:
                # Dump the payload if it gets too big
                if len(payload) > 1000:
                    try:
                        await ctx.send(payload)

                        payload = (
                            "The following Users cannot be located in Alliance Auth\n"
                        )
                    except Exception as exc:
                        logger.error(msg=exc)

                # keep building the payload
                payload = payload + member.mention + "\n"

        try:
            await ctx.send(payload)
        except Exception as exc:
            logger.error(msg=exc)
            # await ctx.send(payload[0:1999])
            # await ctx.send("Maximum Discord message length reached")


def setup(bot):
    """
    Set up the cog

    :param bot:
    :type bot:
    :return:
    :rtype:
    """

    # Unload the Auth cog from `aadiscordbot`, so we can load our own.
    unload_cog(bot=bot, cog_name="Auth")

    # Add the Auth cog to the bot
    bot.add_cog(Auth(bot))
