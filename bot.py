import discord
from discord.ext import commands
from pcpartpicker import API
import os


BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

BOT_PREFIX = "!"


try:
    pcp_api = API()
except Exception as e:
    print(f"failed to initialize pcpartpicker api: {e}")
    print("the library may be outdated or pcpartpicker.com might be blocking requests.")
    pcp_api = None


intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

@bot.event
async def on_ready():
    """Event handler for when the bot logs in."""
    print(f'logged in as {bot.user.name}')
    print(f'bot id: {bot.user.id}')
    print('bot is ready to receive commands.')
    print('='*30)

@bot.command(name='price', help='calculates the total price of pc parts. separate parts with a comma (,)')
async def price(ctx, *, parts_query: str = None):
    """
    Calculates the total price for a list of PC parts.
    Parts should be provided as a single string, separated by commas.
    """
    if pcp_api is None:
        await ctx.send("api down. no bot")
        return

    if not parts_query:
        await ctx.send(f"**usage:** `{BOT_PREFIX}price part1, part2, part3`\n**example:** `{BOT_PREFIX}price ryzen 5 5600x, rtx 3060`")
        return

    part_names = [part.strip() for part in parts_query.split(',')]

    total_price = 0.0
    found_parts = []
    not_found_parts = []
    
    processing_message = await ctx.send(f"searching for {len(part_names)} part(s)")

    for name in part_names:
        if not name:
            continue
            
        try:

            search_results = pcp_api.part_search(name)
            
            if search_results:
                part = search_results[0]
                
                if part.price:
                    total_price += part.price
                    found_parts.append(f"• **{part.name}**: ${part.price:.2f}")
                else:
                    not_found_parts.append(f"• **{part.name}**: (price not available)")
            else:
                not_found_parts.append(f"• **{name}**: (part not found)")
        except Exception as e:
            # handle errors
            print(f"error searching for part '{name}': {e}")
            not_found_parts.append(f"• **{name}**: (error during search)")


    embed = discord.Embed(
        title="PC parts price",
        description="here are the results of your query.",
        color=discord.Color.blue()
    )

    if found_parts:
        embed.add_field(
            name="valid parts",
            value="\n".join(found_parts),
            inline=False
        )
    
    if not_found_parts:
        embed.add_field(
            name="not found or missing price",
            value="\n".join(not_found_parts),
            inline=False
        )

    embed.add_field(
        name="total price",
        value=f"**${total_price:.2f}**",
        inline=False
    )
    
    embed.set_footer(text="prices and parts sourced from pcpartpicker.com no guarantees")

    await processing_message.delete()
    await ctx.send(embed=embed)

def run_bot():
    """Runs the bot, with error handling for the token."""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("="*50)
        print("missing bot token go get one")

        print("="*50)
        return

    try:
        print("starting bot...")
        bot.run(BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("="*50)
        print("invalid token")

        print("="*50)
    except Exception as e:
        print(f"error e: {e}")

if __name__ == "__main__":
    run_bot()
