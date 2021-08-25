import discord, os, json, db_manager, format_docs
from discord.ext import commands
from discord.ext.commands.core import has_permissions
from dotenv import load_dotenv
"""
    Main function, deals with commands made by users and makes calles to db_manager and format_docs

    TODO:
      - Add ability to toggle spoiler info in "about" command (death & status)
      - Add birthday command [finds next/current birthday, or takes argument to find birthdays on that day]
"""

load_dotenv()
TOKEN = os.getenv('TOKEN')
# client = discord.Client() # old way

def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]

bot = commands.Bot(command_prefix=(get_prefix))


@bot.event
async def on_guild_join(guild):
    print('Joined guild ', guild.name)
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)             #load the json file
    prefixes[str(guild.id)] = '$'           #default prefix
    
    with open('prefixes.json', 'w') as f:   #write in the prefix.json "message.guild.id": "$"
        json.dump(prefixes, f, indent=4)    #the indent is to make everything look a bit neater

@bot.event
async def on_guild_remove(guild): #when the bot is removed from the guild
    with open('prefixes.json', 'r') as f: #read the file
        prefixes = json.load(f)
    prefixes.pop(str(guild.id)) #find the guild.id that bot was removed from

    with open('prefixes.json', 'w') as f: #deletes the guild.id as well as its prefix
        json.dump(prefixes, f, indent=4)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))


@bot.command(pass_context=True)
@has_permissions(administrator=True)        #ensure that only administrators can use this command
async def changeprefix(ctx, prefix):        #command: $changeprefix ...
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:   #writes the new prefix into the .json
        json.dump(prefixes, f, indent=4)

    await ctx.send(f'Prefix changed to: {prefix}')  #confirms the prefix it's been changed to
    name=f'{prefix}MCU Quotes'              #changes nickname to have prefix in it


""" -------------------- Begin Custom commands Tracking -------------------- """

''' Gets random quote from DB or specific character '''
@bot.command(pass_context=True)
async def quote(ctx, *args):  # *args is a list of arguments from user
    if len(args) == 0:
        quote_doc = db_manager.get_quote(ctx.guild)
    else:
        arg = ' '.join(args)    # *args comes in as list, get_quote() processes args from string
        # print('arg = {0}, type(arg) = {1}'.format(arg, type(arg)))
        quote_doc   = db_manager.get_quote(ctx.guild, arg)

    if quote_doc is None:
        await ctx.channel.send('Could not find character', arg)
    else:
        quote_embed = format_docs.constr_quote(quote_doc)
        await ctx.channel.send(embed=quote_embed)


@bot.command(pass_context=True)
async def about(ctx, *args):
    if len(args) == 0:  # Send information about the bot
        await ctx.channel.send('No arg about command still under construction')
    else:
        arg = ' '.join(args)
        doc = db_manager.get_about(ctx.guild, arg)
    
    if doc is None:
        await ctx.channel.send('Could not find character', arg)
    else:
        abt_embed = format_docs.constr_about(doc)
        await ctx.channel.send(embed=abt_embed)


''' 
    Help command
    No arg  - retreives list of commands
    Arg     - retreives command specified's help page
'''
@bot.command(pass_context=True)
async def help(ctx, *args):
    if len(args) == 0:  # Send list of commands
        pass
    else:               # Send information about command
        pass


''' Adds movie/tv show to list of media to pull quotes from '''
@bot.command(pass_context=True)
async def add(ctx, *args):
    pass


''' Removes movie/tv show from list of media to pull quotes from '''
@bot.command(pass_context=True)
async def remove(ctx, *args):
    pass


''' 
    Check or change whether death/status is shown on about page
    Off by default
    TODO: Lock behind permissions
'''
@bot.command(pass_context=True)
async def deaths(ctx, *args):
    if len(args) == 0:  # return status of whether spoilers are on or not
        pass
    elif args[1].lower() == 'on':
        pass
    elif args[1].lower() == 'off':
        pass
    else:
        await ctx.channel.send('Invalid argument. Use `on` or `off`, or call without argument')


''' 
    Enables/Disables repeated quotes 
    Default = disabled
    TODO: Lock behind permissions
'''
@bot.command(pass_context=True)
async def repeat(ctx, *args):
    if len(args) == 0:  # Return status of whether repeats are on or off
        pass
    elif args[1].lower() == 'on':
        pass
    elif args[1].lower() == 'on':
        pass
    else:
        await ctx.channel.send('Invalid argument. Use `on` or `off`, or call without argument')



'''
    Change permissions for certain commands
    Commands affected: add, remove, deaths, perms
'''
@bot.command(pass_context=True)
async def perms(ctx, *args):
    # Check if args[2] is a valid role
    # if valid_role(role):
        # await ctx.channel.send('Invalid Role')

    if len(args) == 0:  # Return permission settings
        pass
    elif args[1].lower() == 'reset':
        pass
    elif args[1].lower() == 'set':
        if args[2].lower() == 'media':
            pass
        elif args[2].lower() == 'deaths':
            pass
        elif args[2].lower() == 'perms':
            pass
        else:
            await ctx.channel.send('Unrecognized command argument \"{0}\"'.format(args[2]))
    else:  
        await ctx.channel.send('Invaled argument. Use `set`, `reset`, or call without argument')





bot.run(TOKEN)