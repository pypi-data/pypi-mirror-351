"""
RecruitMe Cog
"""

# Standard Library
import logging
from enum import Enum

# Third Party
import discord
from discord.embeds import Embed
from discord.ext import commands

# Django
from django.conf import settings
from django.utils import timezone

# Alliance Auth Discord Bot
from aadiscordbot import app_settings
from aadiscordbot.utils import auth

# Alliance Auth (External Libs)
from app_utils.urls import reverse_absolute

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)

APPLICANT_ROLE_NAME = "TN-NT Applicant"
AUDIT_SYSTEM_NAME = "Character Audit"
AUDIT_SYSTEM_URL = reverse_absolute(viewname="corptools:react")
AUDIT_SYSTEM = f"[{AUDIT_SYSTEM_NAME}]({AUDIT_SYSTEM_URL})"
GROUPS_PAGE_URL = reverse_absolute(viewname="groupmanagement:groups")


class BotResponse(str, Enum):
    """
    Bot responses for the RecruitMe cog
    """

    NOT_IN_APPLICATION_GROUP = (
        f"**You are not in the `{APPLICANT_ROLE_NAME}` group.**\n\n"
        f"Please open the [groups page]({GROUPS_PAGE_URL}) and "
        f"join the `{APPLICANT_ROLE_NAME}` group first …"
    )
    MEMBER_NOT_IN_APPLICATION_GROUP = (
        "**{MEMBER} is not in the "
        f"`{APPLICANT_ROLE_NAME}` group.**\n\n"
        "Please let them know to open the "
        f"[groups page]({GROUPS_PAGE_URL}) and join the "
        f"`{APPLICANT_ROLE_NAME}` group first …"
    )
    NOT_A_RECRUITER = (
        "You are not a recruiter for Terra Nanotech and "
        "cannot use this command on this user …"
    )
    PRIVATE_THREAD_GUIDE_TITLE = "Private Thread Guide"
    PRIVATE_THREAD_GUIDE_BODY = (
        "To add a person to this thread simply `@ping` them. "
        "This works with `@groups` as well to bulk add people to the channel. "
        "Use wisely, abuse will not be tolerated."
    )
    RECRUITMENT_THREAD_TITLE = "{MAIN_CHARACTER} | Recruitment | {DATE}"
    RECRUITMENT_THREAD_BODY = (
        "Dragging in: <@&{LEADERSHIP_ROLE_ID}> and <@&{RECRUITER_ROLE_ID}> …\n\n"
        "Hello <@{MEMBER_ID}>, and welcome! :wave:\n\n"
        f"Feel free to ask questions and please ensure **all** your characters are added to {AUDIT_SYSTEM}.\n"
        "And of course, tell us a bit about yourself!\n\n"
        "Someone from the recruitment team will get in touch with you soon!"
    )
    RECRUITMENT_THREAD_CREATED = "Recruitment thread created!"


class RecruitMe(commands.Cog):
    """
    Thread Tools for recruiting!
    """

    def __init__(self, bot):
        """
        Initialize the RecruitMe cog

        :param bot: The bot instance
        :type bot: discord.ext.commands.Bot
        """

        self.bot = bot

    async def open_ticket(self, ctx: discord.Interaction, member: discord.Member):
        """
        Open a recruitment ticket

        :param ctx: The context of the command
        :type ctx: discord.Interaction
        :param member: The member requesting a recruiter
        :type member: discord.Member
        :return: None
        :rtype: None
        """

        auth_user = auth.get_auth_user(user=member, guild=ctx.guild)
        main_character = auth_user.profile.main_character

        ch = ctx.guild.get_channel(settings.TNNT_DISCORDBOT_COGS_RECRUITING_CHANNEL)
        th = await ch.create_thread(
            name=BotResponse.RECRUITMENT_THREAD_TITLE.value.format(
                MAIN_CHARACTER=main_character,
                DATE=timezone.now().strftime("%Y-%m-%d %H:%M"),
            ),
            auto_archive_duration=10080,
            type=discord.ChannelType.private_thread,
            reason=None,
        )
        msg = BotResponse.RECRUITMENT_THREAD_BODY.value.format(
            LEADERSHIP_ROLE_ID=settings.TNNT_DISCORDBOT_COGS_LEADERSHIP_ROLE_ID,
            RECRUITER_ROLE_ID=settings.TNNT_DISCORDBOT_COGS_RECRUITER_ROLE_ID,
            MEMBER_ID=member.id,
        )
        embd = Embed(
            title=BotResponse.PRIVATE_THREAD_GUIDE_TITLE.value,
            description=BotResponse.PRIVATE_THREAD_GUIDE_BODY.value,
        )

        await th.send(content=msg, embed=embd)
        await ctx.response.send_message(
            content=BotResponse.RECRUITMENT_THREAD_CREATED.value,
            view=None,
            ephemeral=True,
        )

    @commands.slash_command(name="recruit_me", guild_ids=app_settings.get_all_servers())
    async def slash_recruit_me(self, ctx):
        """
        Get hold of a recruiter

        :param ctx: The context of the command
        :type ctx: discord.Interaction
        :return: None
        :rtype: None
        """

        if settings.TNNT_DISCORDBOT_COGS_APPLICANT_ROLE_ID not in [
            role.id for role in ctx.user.roles
        ]:
            return await ctx.respond(
                BotResponse.NOT_IN_APPLICATION_GROUP.value, ephemeral=True
            )

        await self.open_ticket(ctx=ctx, member=ctx.user)

    @commands.message_command(
        name="Create Recruitment Thread", guild_ids=app_settings.get_all_servers()
    )
    async def reverse_recruit_msg_context(self, ctx, message):
        """
        Help a new guy get a recruiter

        :param ctx: The context of the command
        :type ctx: discord.Interaction
        :param message: The message that triggered the command
        :type message: discord.Message
        :return: None
        :rtype: None
        """

        # Check if the user is a recruiter and if the user is different from the target user
        if settings.TNNT_DISCORDBOT_COGS_RECRUITER_ROLE_ID not in [
            role.id for role in ctx.user.roles
        ] and int(ctx.user.id) != int(message.author.id):
            return await ctx.respond(BotResponse.NOT_A_RECRUITER.value, ephemeral=True)

        # Check if the target user is in the Applicants group
        if settings.TNNT_DISCORDBOT_COGS_APPLICANT_ROLE_ID not in [
            role.id for role in message.author.roles
        ]:
            return await ctx.respond(
                BotResponse.MEMBER_NOT_IN_APPLICATION_GROUP.value.format(
                    MEMBER=message.author.mention,
                ),
                ephemeral=True,
            )

        await self.open_ticket(ctx=ctx, member=message.author)

    @commands.user_command(
        name="Recruit Member", guild_ids=app_settings.get_all_servers()
    )
    async def reverse_recruit_user_context(self, ctx, user):
        """
        Help a new guy get a recruiter

        :param ctx: The context of the command
        :type ctx: discord.Interaction
        :param user: The user that triggered the command
        :type user: discord.User
        :return: None
        :rtype: None
        """

        # Check if the user is a recruiter and if the user is different from the target user
        if settings.TNNT_DISCORDBOT_COGS_RECRUITER_ROLE_ID not in [
            role.id for role in ctx.user.roles
        ] and int(ctx.user.id) != int(user.id):
            return await ctx.respond(BotResponse.NOT_A_RECRUITER.value, ephemeral=True)

        # Check if the target user is in the Applicants group
        if settings.TNNT_DISCORDBOT_COGS_APPLICANT_ROLE_ID not in [
            role.id for role in user.roles
        ]:
            return await ctx.respond(
                BotResponse.MEMBER_NOT_IN_APPLICATION_GROUP.value.format(
                    MEMBER=user.mention
                ),
                ephemeral=True,
            )

        await self.open_ticket(ctx=ctx, member=user)


def setup(bot):
    """
    Set up the RecruitMe cog

    :param bot:
    :type bot:
    :return:
    :rtype:
    """
    # Unload the RecruitMe cog from `aadiscordbot`, so we can load our own.
    unload_cog(bot=bot, cog_name="RecruitMe")

    # Add the RecruitMe cog to the bot
    bot.add_cog(RecruitMe(bot))
