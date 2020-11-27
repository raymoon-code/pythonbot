import discord
from discord.ext import commands


class Func(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def func(self, ctx):
        await ctx.send('test')

def setup(client):
    client.add_cog(Func(client))