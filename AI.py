import discord
from discord import Intents
import random
import os
import json
import youtube_dl
from discord import utils, Activity, ActivityType, Client, Embed, Colour
import PIL

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from io import BytesIO
from discord.errors import Forbidden
from typing import Optional
import asyncio
import urllib.parse, urllib.request, re
import sqlite3
from random import choice
from discord.voice_client import VoiceClient
from discord.ext import commands, tasks
from itertools import cycle
from discord import Member as DiscordMember
from discord import guild
import datetime

from aiohttp import request
from discord.ext.commands import (CommandNotFound,BadArgument,MissingRequiredArgument,CommandOnCooldown)
from discord.errors import HTTPException, Forbidden

IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


# os.chdir(r'\\pythonbot')
youtube_dl.utils.bug_reports_message = lambda: ''
# Guild = object()
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

def get_prefix(client,message):
    with open('genAI.json', 'r') as f:
        prefixesAI = json.load(f)

    return prefixesAI[str(message.guild.id)]

queue = []
intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = get_prefix, intents= intents)
status = cycle(['GTA V', 'Intelligent Assistance'])

@client.event
async def on_guild_join(guild):
    with open('genAI.json', 'r') as f:
        prefixesAI = json.load(f)

    prefixesAI[str(guild.id)] = '-'

    with open('genAI.json', 'w') as f:
        json.dump(prefixesAI,f, indent=4)

@client.event
async def on_guild_remove(guild):
    with open('genAI.json', 'r') as f:
        prefixesAI = json.load(f)

    prefixesAI.pop(str(guild.id))

    with open('genAI.json', 'w') as f:
        json.dump(prefixesAI,f, indent=4)

@client.command()
@commands.has_permissions(manage_messages=True)
async def changeprefix(ctx,prefix):
    with open('genAI.json', 'r') as f:
        prefixesAI = json.load(f)

    prefixesAI[str(ctx.guild.id)] = prefix

    with open('genAI.json', 'w') as f:
        json.dump(prefixesAI,f, indent=4)

    await ctx.sent(f'Prefix changed to: {prefix}')


class BotData:
    def __init__(self):
        self.welcome_channel = None
        self.goodbye_channel = None

botdata = BotData()

@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready.')

@client.event
async def on_member_remove(member):
    if botdata.goodbye_channel != None:
        await botdata.goodbye_channel.send(f'Goodbye {member.mention}')
    else:
        print('Goodbye channel was not set.')

@client.command()
async def set_goodbye_channel(ctx,channel_name= None):
    if channel_name != None:
        for channel in ctx.guild.channels:
            if channel.name == channel_name:
                botdata.goodbye_channel = channel
                await ctx.channel.send(f'Goodbye channel has been set to: {channel_name}')
                await channel.send('This is the new goodbye channel!')
    else:
        await ctx.channel.send("you didn't include the name of a welcome channel.")

@client.command(pass_context=True)
async def h(ctx):
    embed = discord.Embed(
        Colour= discord.Colour.purple(),
        title= 'A.I profile',
        description= 'Artificial intelligence Bot'
    )
    embed.set_author(name='A.I', icon_url='https://cdn.discordapp.com/attachments/779982015398936589/781646622873747487/AI.jpg')
    embed.set_image(url='https://cdn.discordapp.com/attachments/779982015398936589/781646622873747487/AI.jpg')
    embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/779982015398936589/781646622873747487/AI.jpg')
    embed.add_field(name='Age', value='1 year old')
    embed.add_field(name='gender', value='unknown')
    embed.add_field(name='prefix', value="'-'")
    embed.add_field(name='youtube', value='this command use to search video from youtube')
    embed.add_field(name='join', value='this command ask A.I join voice channel')
    embed.add_field(name='pause', value='this command pause the song')
    embed.add_field(name='resume', value='this command resume the song')
    embed.add_field(name='play', value='this command play the song')
    embed.add_field(name='view', value='this command shows the queue')
    embed.add_field(name='8ball', value='this command ask and answer random questions')
    embed.add_field(name='queue', value='this command adds a song to the queue')
    embed.add_field(name='remove', value='This command removes an item from the list')
    embed.set_footer(text='A.I developed by Raymoon')

    await ctx.send(embed=embed)

@client.command()
async def set_all(ctx):
    await ctx.invoke(client.get_command("set_goodbye_channel"),channel_name='general')
    # await set_goodbye_channel(ctx,channel_name='general')

@client.command(aliases=['8ball','test'])
async def _8ball(ctx, *, question):
    responses = ['It is certain.',
                 'It is decidedly so.',
                 'Without a doubt',
                 'Yes - definitely.',
                 'You may reply on it.',
                 'As I see it, yes',
                 'Most likely',
                 'Outlook good.',
                 'Yes.',
                 'Signs point to yes.',
                 'Reply hazy, try again.',
                 'Ask again later.',
                 'Better not tell you now.'
                 ]
    await ctx.send(f'Question: {question}\n Answer: {random.choice(responses)}')

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)

@clear.error
async def clear_error(ctx, error):
    if isinstance(error,commands.MissingRequiredArgument):
        await ctx.send('Please specific an amount of messages to delete.')

@client.command()
@commands.has_permissions(manage_messages=True)
async def kick(ctx, member : discord.Member,*, reason= None):
    await member.kick(reason=reason)

@client.command()
@commands.has_permissions(manage_messages=True)
async def ban(ctx, member : discord.Member,*, reason= None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')

@client.command()
@commands.has_permissions(manage_messages=True)
async def unban(ctx,*, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

@client.command()
@commands.has_permissions(manage_messages=True)
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
@commands.has_permissions(manage_messages=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

@client.command()
@commands.has_permissions(manage_messages=True)
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

@tasks.loop(minutes=60)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

@client.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):
        await ctx.send('Invalid command used.')

def is_it_me(ctx):
    return ctx.author.id == 544680324018339881 or ctx.author.id == 718225724594585682
@client.command()
@commands.check(is_it_me)
async def check(ctx):
    await ctx.send(f'Hi I am {ctx.author}')

@client.command(name='queue', help='This command adds a song to the queue')
async def queue_(ctx, url):
    global queue

    queue.append(url)
    player = await YTDLSource.from_url(queue[-1], loop=client.loop)
    await ctx.send(f'`{player.title}` added to queue!')

@client.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()


@client.command(pass_context=True)
async def leave(ctx):
    if ctx.message.author.voice:
        server = ctx.message.guild.voice_client
    await server.disconnect()


@client.command(name='play', help='This command plays songs')
async def play(ctx):
    global queue

    server = ctx.message.guild
    voice_channel = server.voice_client
    if queue is not None:
        async with ctx.typing():
            player = await YTDLSource.from_url(queue[0], loop=client.loop)
            voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('**Now playing:** {}'.format(player.title))
        del(queue[0])


@client.command(name='remove', help='This command removes an item from the list')
async def remove(ctx, number):
    global queue

    try:
        del(queue[int(number)])
        await ctx.send(f'Your queue is now `{queue}!`')

    except:
        await ctx.send('Your queue is either **empty** or the index is **out of range**')

@client.command(pass_context = True)
async def pause(ctx):
    server = ctx.message.guild
    voice_channel =server.voice_client
    voice_channel.pause()
    await ctx.send('The song has been paused!')

@client.command(pass_context = True)
async def resume(ctx):
    server = ctx.message.guild
    voice_channel =server.voice_client
    voice_channel.resume()
    await ctx.send('The song has been resumed!')

@client.command(pass_context = True)
async def stop(ctx):
    server = ctx.message.guild
    voice_channel =server.voice_client
    voice_channel.stop()
    await ctx.send('The song has been stopped!')




@client.command(name='view', help='This command shows the queue')
async def view(ctx):
    queuelist = []
    z = 1
    for x in queue:
        player = await YTDLSource.from_url(x, loop=client.loop)
        queuelist.append(player.title)
    await ctx.send(f'Your queue have {len(queuelist)} songs now :')
    for y in queuelist:
        await ctx.send(f' `{z}.{y}!`')
        z += 1

@client.command()
async def youtube(ctx, *, search):
    query_string = urllib.parse.urlencode({
        'search_query' : search
    })
    htm_content = urllib.request.urlopen(
        'https://www.youtube.com/results?search_query=' + query_string
    )
    search_results = re.findall(r'watch\?v=(\S{11})',htm_content.read().decode())
    await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])






@client.command(name="userinfo")
async def user_info(Ctx, Target:Optional[DiscordMember]):
    """Displays user info. If no member is given, it defaults to the command invoker."""
    if Target is None:
        Target = Ctx.author

    header = f"User information - {Target.display_name}\n\n"
    rows = {
        "Account name"     : Target.name,
        "Disciminiator"    : Target.discriminator,
        "ID"               : Target.id,
        "Is bot"           : "Yes" if Target.bot else "No",
        "Top role"         : Target.top_role,
        "Nº of roles"      : len(Target.roles),
        "Current status"   : str(Target.status).title(),
        "Current activity" : f"{str(Target.activity.type).title().split('.')[1]} {Target.activity.name}" if Target.activity is not None else "None",
        "Created at"       : Target.created_at.strftime("%d/%m/%Y %H:%M:%S"),
        "Joined at"        : Target.joined_at.strftime("%d/%m/%Y %H:%M:%S"),
    }
    table = header + "\n".join([f"{key}{' '*(max([len(key) for key in rows.keys()])+2-len(key))}{value}" for key, value in rows.items()])
    await Ctx.send(f"```{table}```{Target.avatar_url}")
    return

@client.command(name="slap")
async def slap_member(Ctx, Target:DiscordMember):
    """Slaps a member."""
    # await Ctx.send(f"**{Ctx.author.display_name}** just slapped {Target.mention} silly!")
    rlist = ['https://media.giphy.com/media/k1uYB5LvlBZqU/giphy.gif','https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif','https://media.giphy.com/media/a7HKjDb3UJ0kM/giphy.gif']
    embed = discord.Embed(colour=0x95efcc,title=f"**{Ctx.author.display_name}** just slapped {Target.name} silly!:clap: :clap: ")
    embed.set_image(url=random.choice(rlist))
    await Ctx.send(embed=embed)

@client.command(alaises=['t','o'])
async def to(ctx):
    await ctx.send(f'channel id: {ctx.guild.id}, member name: {ctx.guild.get_member(291801254747701249)}\n'
                   f'owner_id: {ctx.guild.owner_id}, total member: {ctx.guild._member_count}\n'
                   f'server name: {ctx.guild.name}, {ctx.guild._members}' )

@client.command(name='cn',pass_context=True)
async def change_nick(ctx,Target:DiscordMember,nick):
    old = Target.display_name
    await Target.edit(nick=nick)
    embed = Embed(Colour=0x95efcc , title=f'{old.title()} nickname has changed to {Target.display_name} :partying_face: :partying_face:  ',description=f'Discriminator: {Target.discriminator}\n'
                                                                                                                                                      f'Id           : {Target.id}'  )
    embed.set_thumbnail(url=f'{Target.avatar_url}')
    embed.set_footer(text=f'{Target.guild}',icon_url=f'{Target.guild.icon_url}')
    embed.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=embed)

@client.command()
async def wanted(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author
    wanted = Image.open('wanted.jpg')

    asset = user.avatar_url_as(size = 128)
    data = BytesIO(await asset.read())
    pfp = Image.open(data)

    pfp = pfp.resize((280,350))

    wanted.paste(pfp,(217,297))

    wanted.save('profile.jpg')

    await ctx.send(file =discord.File("profile.jpg"))

@client.command(name='f')
async def fight(ctx, user1: discord.Member = None, user2: discord.Member = None, *,bet):
    """fight with people f user1 user2."""
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    loser = user2
    


    if str(user1) == None or str(user2) == None:
        user = ctx.author

        user2 = ctx.guild.get_member(721904320320241715)
        bet = 10
        await ctx.send(f'default beting amount {bet} coins:coin: :coin: !!!')


    if user1 == user2:

        if user1 == ctx.author:
            await ctx.send(f'You can not fight with yourself !!!')
            pass
            return
        else:
            await ctx.send(f'You can not let people fight with themself !!!')
            pass
            return

    elif int(bet) < 0:
        await ctx.send(f'Betting amount can not less than zero !!!')
        pass
        return

    elif user1 != ctx.author and  user2 != ctx.author:

        await ctx.send(f'You can not let others people fight with each others !!!')
        pass
        return

    elif int(users[str(user1.id)]['wallet']) < int(bet):

        await ctx.send(f'{user1.display_name} does not have enough money to bet!!!')
        pass
        return

    elif int(users[str(user2.id)]['wallet']) < int(bet):

        await ctx.send(f'{user2.display_name} does not have enough money to bet!!!')
        pass
        return




    flist = ['fight.jpg', 'fight1.jpg']
    r = random.choice(flist)


    fight = Image.open(str(r))

    asset = user1.avatar_url_as(size = 128)
    asset2 = user2.avatar_url_as (size = 128)
    data = BytesIO(await asset.read())
    data2 = BytesIO(await asset2.read())
    pfp2 = Image.open(data2)
    pfp = Image.open(data)
    draw = ImageDraw.Draw(fight)
    user_name = user1.name.title()
    user2_name = user2.name.title()
    player = [user_name, user2_name]


    if r == 'fight.jpg':
        pfp = pfp.resize((200,200))
        pfp2 = pfp2.resize((200,200))
        fight.paste(pfp,(81,223))
        fight.paste(pfp2,(703,223))
        font = ImageFont.truetype('impact.ttf', 45)

        draw.text((100,440), str(user_name),(251, 232, 255), font=font)
        draw.text((730,440), str(user2_name),(251, 232, 255), font=font)
    elif r == 'fight1.jpg':
        pfp = pfp.resize((295,239))
        pfp2 = pfp2.resize((295,239))
        fight.paste(pfp,(93,205))
        fight.paste(pfp2,(616,205))


        font = ImageFont.truetype('impact.ttf', 45)

        draw.text((150,585), user_name,(251, 232, 255), font=font)
        draw.text((670,585), user2_name,(251, 232, 255), font=font)


    fight.save('fighting.jpg')

    await ctx.send(file =discord.File("fighting.jpg"))
    apikey = "IXK108TOSY48"
    lmt = 50

    search_term = "anime fight"
    y = "https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, apikey, lmt)
    # get the top 8 GIFs for the search term
    async with request('GET',y,headers={}) as resp:
        if resp.status == 200:
            data = await resp.json()
            d= data.get('results')
            giflist = []
            giflist2 = []
            for x in range(len(d)):
                t = d[x]
                c= t.get('media')
                giflist.append(c)

            for y in giflist:
                giflist2.append(y[0].get('mediumgif').get('url'))

            op = random.randint(0,len(giflist2)-1)

            img_url =giflist2[op]
            # print(img_url)
        else:
            img_url = None


    async with request('GET',img_url,headers={}) as resp:
        if resp.status == 200:
            embed = discord.Embed(title='Fighting :crossed_swords: :crossed_swords: :crossed_swords: ')
            embed.set_image(url=img_url)

            await ctx.send(embed=embed)
        else:
            ctx.send('No API found')
    await asyncio.sleep(5)
    winner = random.choice(player)
    await ctx.send(f'{winner} Won and received {bet} coins:coin::coin::moneybag::money_mouth:  !!'
                   f'{user2.name.title()} lose {bet}:money_with_wings: :money_with_wings: ')

    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author


    if winner == ctx.author.name.title():
        users[str(user1.id)]['wallet'] += int(bet)
        users[str(user2.id)]['wallet'] -= int(bet)
    else:
        users[str(user1.id)]['wallet'] -= int(bet)
        users[str(user2.id)]['wallet'] += int(bet)

    with open('mainbank.json','w') as f:
        json.dump(users,f)

@client.command(name='bl')
async def balance(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()
    user = ctx.author
    wallet_amt = users[str(user.id)]['wallet']
    bank_amt = users[str(user.id)]['bank']
    em = discord.Embed(title=f"{ctx.author.name.title()}'s balance", color = discord.Colour.blurple())
    em.add_field(name= 'Wallet balance', value = wallet_amt)
    em.add_field(name= 'Bank balance', value = bank_amt)
    await ctx.send(embed=em)

@client.command()
@commands.cooldown(3, 30, commands.BucketType.user)                                
async def beg(ctx):
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    earnings = random.randrange(101)
    await ctx.send(f'Someone gave you {earnings} coins!!')

    users[str(user.id)]['wallet'] += earnings

    with open('mainbank.json','w') as f:
        json.dump(users,f)



async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]['wallet'] = 0
        users[str(user.id)]['bank'] = 0

    with open('mainbank.json','w') as f:
        json.dump(users,f)
    return True

async def get_bank_data():
    with open('mainbank.json','r') as f:
        users = json.load(f)
    return users

@client.event
async def on_command_error(ctx, exc):
    if any([isinstance(exc, error)for error in IGNORE_EXCEPTIONS]):
        pass

    elif isinstance(exc, MissingRequiredArgument):
        await ctx.send(" One or more required arguments are missing.")

    elif isinstance(exc, CommandOnCooldown):
        await ctx.send(f'That command is on cooldown. Try again in {exc.retry_after:,.2f} secs.')


@client.command(name='g')
async def give_money(ctx, member: DiscordMember, coins):
    '''Give coins to other user'''
    await open_account(ctx.author)
    users = await get_bank_data()
    user = ctx.author
    if int(coins)<0:
        await ctx.send(f'The amount can not less than zero!!')
        return
    elif int(users[str(user.id)]['wallet']) < int(coins):
        await ctx.send(f'You do not have enough money in your wallet')
        return


    await ctx.send(f'{user.name} successful gave  {coins} :coin::moneybag: to {member.display_name} :handshake::gift_heart:  !!')

    users[str(user.id)]['wallet'] -= int(coins)
    users[str(member.id)]['wallet'] += int(coins)

    with open('mainbank.json','w') as f:
        json.dump(users,f)






client.run('NzIxOTA0MzIwMzIwMjQxNzE1.XubTyg.VxjCavsNueBonohM435SioOrzws')
