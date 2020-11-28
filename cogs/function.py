import discord
from discord.ext import commands
from random import choice, randint
from typing import Optional
from discord import Member as DiscordMember
from aiohttp import request
from discord import Member, Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown


class Func(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def func(self, ctx):
        await ctx.send('test')
    
    @command(name="fact")
    @cooldown(3, 60, BucketType.guild)
    async def animal_fact(self, ctx, animal: str):
        if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala"):
            fact_url = f"https://some-random-api.ml/facts/{animal}"
            image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

            async with request("GET", image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]

                else:
                    image_link = None

            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(title=f"{animal.title()} fact",
                                  description=data["fact"],
                                  colour=ctx.author.colour)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)

                else:
                    await ctx.send(f"API returned a {response.status} status.")

        else:
            await ctx.send("No facts are available for that animal.")

    @command(name="d")
    @cooldown(3, 60, BucketType.guild)
    async def do_act(self, ctx, animu:str, Target:DiscordMember):
        """Action available 'pat','wink','hug'."""
        if(animu:=animu.lower()) in ("wink", 'pat', 'hug'):

            img_url = f"https://some-random-api.ml/animu/{animu}"

            async with request('GET',img_url,headers={}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    img_link = data['link']
                else:
                    img_link = None
            async with request('GET',img_url,headers={}) as resp:
                if resp.status == 200:

                    embed = Embed(title=f'**{ctx.author.display_name.title()}** just {animu.title()} {Target.name.upper()}  :laughing: :laughing: :laughing: !!!',
                                  colour=ctx.author.colour)
                    if img_link is not None:
                        embed.set_image(url=img_link)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f'API returned a {resp.status} status')
        else:
            await ctx.send('No features are available for that action. ')

def setup(client):
    client.add_cog(Func(client))
    print("Function is loaded")
