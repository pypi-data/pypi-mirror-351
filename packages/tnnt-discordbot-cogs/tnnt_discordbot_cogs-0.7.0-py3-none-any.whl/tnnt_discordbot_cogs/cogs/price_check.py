"""
Market Price Checks cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

# Standard Library
import locale
import logging
from collections.abc import Coroutine

# Third Party
import requests
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands

# Alliance Auth Discord Bot
from aadiscordbot import app_settings

# Alliance Auth (External Libs)
from eveuniverse.models import EveEntity

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)


class PriceCheck(commands.Cog):
    """
    Price checks on Jita, Amarr, Rens, Hek and Dodixie markets
    """

    imageserver_url = "https://images.evetech.net"

    def __init__(self, bot):
        self.bot = bot

    @classmethod
    def _build_market_price_embed(
        cls, embed: Embed, market: dict, item_name: str, eve_type_id: str
    ) -> None:
        """
        Build the price embed for the selected market

        :param embed:
        :type embed:
        :param market:
        :type market:
        :param item_name:
        :type item_name:
        :param eve_type_id:
        :type eve_type_id:
        :return:
        :rtype:
        """

        market_system_name = market["name"]
        market_system_id = market["system_id"]
        url = "https://market.fuzzwork.co.uk/aggregates/"
        url_params = {"system": market_system_id, "types": eve_type_id}
        market_data = requests.get(url=url, params=url_params, timeout=5.00)

        embed.add_field(
            name=market_system_name,
            value=f"Prices for {item_name} on the {market_system_name} Market.",
            inline=False,
        )

        if market_data.status_code == 200:
            market_json = market_data.json()

            sell_min = market_json[eve_type_id]["sell"]["min"]
            sell_order_count = int(market_json[eve_type_id]["sell"]["orderCount"])
            buy_max = market_json[eve_type_id]["buy"]["max"]
            buy_order_count = int(market_json[eve_type_id]["buy"]["orderCount"])
            thumbnail_url = f"{cls.imageserver_url}/types/{eve_type_id}/icon?size=64"

            # Set the Embed thumbnail
            embed.set_thumbnail(url=thumbnail_url)

            locale.setlocale(category=locale.LC_ALL, locale="")

            # Sell order price
            market_min_sell_order_price = locale.format_string(
                f="%.2f", val=float(sell_min), grouping=True
            )

            sell_orders_string = f"{sell_order_count} Orders"
            if sell_order_count == 0:
                market_min_sell_order_price = "No sell orders found"
                sell_orders_string = "No Orders"

            if 0 < sell_order_count < 2:
                sell_orders_string = f"{sell_order_count} Order"

            embed.add_field(
                name=f"Sell Order Price ({sell_orders_string})",
                value=f"{market_min_sell_order_price} ISK",
                inline=True,
            )

            # Buy order price
            market_max_buy_order_price = locale.format_string(
                f="%.2f", val=float(buy_max), grouping=True
            )

            buy_orders_string = f"{buy_order_count} Orders"
            if buy_order_count == 0:
                market_max_buy_order_price = "No buy orders found"
                buy_orders_string = "No Orders"

            if 0 < buy_order_count < 2:
                buy_orders_string = f"{buy_order_count} Order"

            embed.add_field(
                name=f"Buy Order Price ({buy_orders_string})",
                value=f"{market_max_buy_order_price} ISK",
                inline=True,
            )
        else:
            embed.add_field(
                name="API Error",
                value=(
                    f"Could not not fetch the price for the {market_system_name} market."
                ),
                inline=False,
            )

    # @commands.command(pass_context=True)
    @commands.slash_command(name="price", guild_ids=app_settings.get_all_servers())
    async def price(self, ctx, item_name: str):
        """
        Check an item price on all major market hubs

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self.price_check(
                markets=[
                    {"name": "Jita", "system_id": 30000142},
                    {"name": "Amarr", "system_id": 30002187},
                    {"name": "Rens", "system_id": 60004588},
                    {"name": "Hek", "system_id": 60005686},
                    {"name": "Dodixie", "system_id": 30002659},
                ],
                item_name=item_name,
            ),
            ephemeral=True,
        )

    @commands.slash_command(name="jita", guild_ids=app_settings.get_all_servers())
    async def jita(self, ctx, item_name: str):
        """
        Check an item price on Jita market

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self.price_check(
                markets=[{"name": "Jita", "system_id": 30000142}], item_name=item_name
            ),
            ephemeral=True,
        )

    @commands.slash_command(name="amarr", guild_ids=app_settings.get_all_servers())
    async def amarr(self, ctx, item_name: str):
        """
        Check an item price on Amarr market

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self.price_check(
                markets=[{"name": "Amarr", "system_id": 60008494}], item_name=item_name
            ),
            ephemeral=True,
        )

    @commands.slash_command(name="rens", guild_ids=app_settings.get_all_servers())
    async def rens(self, ctx, item_name: str):
        """
        Check an item price on Rens market

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self.price_check(
                markets=[{"name": "Rens", "system_id": 60004588}], item_name=item_name
            ),
            ephemeral=True,
        )

    @commands.slash_command(name="hek", guild_ids=app_settings.get_all_servers())
    async def hek(self, ctx, item_name: str):
        """
        Check an item price on Hek market

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self.price_check(
                markets=[{"name": "Hek", "system_id": 60005686}], item_name=item_name
            ),
            ephemeral=True,
        )

    @commands.slash_command(name="dodixie", guild_ids=app_settings.get_all_servers())
    async def dodixie(self, ctx, item_name: str):
        """
        Check an item price on Dodixie market

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self.price_check(
                markets=[{"name": "Dodixie", "system_id": 30002659}],
                item_name=item_name,
            ),
            ephemeral=True,
        )

    @classmethod
    def price_check(cls, markets, item_name: str = None) -> Coroutine:
        """
        Do the price checks and post to Discord

        :param ctx:
        :type ctx:
        :param markets:
        :type markets:
        :param item_name:
        :type item_name:
        :return:
        :rtype:
        """

        if item_name != "":
            try:
                eve_type = (
                    EveEntity.objects.fetch_by_names_esi([item_name])
                    .filter(category=EveEntity.CATEGORY_INVENTORY_TYPE)
                    .values_list("id", flat=True)
                )

                eve_type_id = str(eve_type[0])
            except (EveEntity.DoesNotExist, IndexError):
                embed = Embed(
                    title=f"Price Lookup for {item_name}",
                    color=Color.orange(),
                )

                embed.add_field(
                    name="Error",
                    value=(
                        f"{item_name} could not be found. "
                        "Are you sure you spelled it correctly?"
                    ),
                    inline=False,
                )
            else:
                embed = Embed(
                    title=f"Price Lookup for {item_name}",
                    color=Color.green(),
                )

                for market in markets:
                    cls._build_market_price_embed(
                        embed=embed,
                        market=market,
                        item_name=item_name,
                        eve_type_id=eve_type_id,
                    )
        else:
            embed = Embed(
                title="Price Lookup",
                color=Color.red(),
            )

            embed.add_field(
                name="Error",
                value=(
                    "You forget to enter an item you want to lookup the price for ..."
                ),
                inline=False,
            )

        return embed


def setup(bot) -> None:
    """
    Set up the cog

    :param bot:
    :type bot:
    :return:
    :rtype:
    """

    # Unload the PriceCheck cog from `aadiscordbot`, so we can load our own.
    unload_cog(bot=bot, cog_name="PriceCheck")

    # Add the PriceCheck cog to the bot
    bot.add_cog(PriceCheck(bot))
