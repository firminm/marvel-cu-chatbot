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
prefixes = {}   # Dictionary that stores server prefixes, default prefix stored at key [0]

load_dotenv()
TOKEN = os.getenv('TOKEN')
# client = discord.Client() # old way

def get_prefix(bot, message):
    return prefixes[message.guild.id]
    # with open('prefixes.json', 'r') as f:
        # prefixes = json.load(f)
    # return prefixes[str(message.guild.id)]

bot = commands.Bot(command_prefix=(get_prefix))
bot.remove_command('help')  # Deletes default help command so I can "override" and make my own


@bot.event
async def on_guild_join(guild):
    print('Joined guild ', guild.name)
    prefixes[guild.id] = prefixes[0]    # Set to default prefix


@bot.event
async def on_guild_remove(guild): #when the bot is removed from the guild
    print('Removed from guild {0}, ID = {1}'.format(guild.name, guild.id))
    del prefixes[guild.id]
    db_manager.remove_guild(guild.id)


@bot.event
async def on_ready():
    global prefixes
    prefixes = db_manager.establish_prefixes()
    print('Logged in as {0.user}'.format(bot))
    
    db_manager.command_line()



"""  --------------------   Begin User Commands Tracking   --------------------  """


@bot.command(pass_context=True)
@has_permissions(administrator=True)        #ensure that only administrators can use this command
async def changeprefix(ctx, prefix):        #command: $changeprefix ...
    db_manager.change_prefix(ctx.guild.id, prefix)

    prefixes[ctx.guild.id] = prefix
    await ctx.send(f'Prefix changed to: {prefix}')  # Confirms the prefix it's been changed to
    name=f'{prefix}MCU Quotes'                      # Changes nickname to have prefix


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
        await ctx.channel.send('Could not find character' + ' \"'+arg+'\"')
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
        help_doc = db_manager.get_help_dict()
        help_embed = format_docs.constr_help_list(help_doc, prefixes[ctx.guild.id])
    else:               # Send information about command
        help_doc = db_manager.get_help_page(args[0])
        help_embed = format_docs.constr_help_page(help_doc, prefixes[ctx.guild.id])
    
    if help_embed is not None:
        await ctx.channel.send(embed=help_embed)
    elif len(args) > 0:
        await ctx.channel.send('Character {0} not found'.format(args[1]))
    else:
        await ctx.channel.send('An Error has occurred')


''' Adds movie/tv show to list of media to pull quotes from '''
@bot.command(pass_context=True)
async def add(ctx, *args):
    pass


''' Removes movie/tv show from list of media to pull quotes from '''
@bot.command(pass_context=True)
async def remove(ctx, *args):
    pass


'''
    Lists characters
    No-args: sends full list of characters with a reaction for next
    Args: sends the list of characters that '^args'
'''
@bot.command(pass_context=True)
async def characters(ctx, *args):
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