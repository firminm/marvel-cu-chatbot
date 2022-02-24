import discord, os, json, db_manager, format_docs

from discord.ext.commands.errors import MissingPermissions
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
    # try:
    return prefixes[message.guild.id]
    # except AttributeError:
    #     print('Startup Error')
    #     return prefixes[0]

bot = commands.Bot(command_prefix=(get_prefix))
bot.remove_command('help')  # Deletes default help command so I can "override" and make my own


@bot.event
async def on_guild_join(guild):
    prefixes[guild.id] = prefixes[0]    # Set to default prefix
    db_manager.add_guild(guild)
    print('Joined guild ', guild.name)



@bot.event
async def on_guild_remove(guild): #when the bot is removed from the guild
    del prefixes[guild.id]
    db_manager.remove_guild(guild)
    print('Removed from guild {0}, ID = {1}'.format(guild.name, guild.id))



@bot.event
async def on_ready():
    global prefixes
    prefixes = db_manager.establish_prefixes()

    # db_manager.command_line()

    
    print('Logged in as {0.user}'.format(bot))
    



"""  --------------------   Begin User Commands Tracking   --------------------  """


@bot.command(pass_context=True)
@has_permissions(administrator=True)        #ensure that only administrators can use this command
async def prefix(ctx, prefix):        #command: $prefix ...
    db_manager.change_prefix(ctx.guild, prefix)

    prefixes[ctx.guild.id] = prefix
    await ctx.send(f'Prefix changed to: {prefix}')  # Confirms the prefix it's been changed to
    name=f'{prefix}MCU Quotes'                      # Changes nickname to have prefix


''' Gets random quote from DB or specific character '''
@bot.command(pass_context=True)
async def quote(ctx, *args):  # *args is a list of arguments from user
    print('{0}:  {1}quote '.format(ctx.guild.id, prefixes[ctx.guild.id]) + ' '.join(args))

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


''' Provides information about a specified chharacter '''
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


''' 
    Displays Known Birthdays across MCU 
    Takes month as args
    Input:
      noArgs - displays today's birthday
      args  - displays that month's birthday
'''
@bot.command(pass_context=True)
async def bday(ctx, *args):
    print('{0}:  {1}bday '.format(ctx.guild.id, prefixes[ctx.guild.id]) + ' '.join(args))
    
    if len(args) == 0:  # No args -> return today's bdays
        bdays = db_manager.get_today_bday()
        bday_embed = format_docs.constr_bday_page(bdays)    # No-bday-today error checking done in method
    else:
        try:
            month_as_str = ' '.join(args)
            bdays = db_manager.get_bday(month_as_str)
            bday_embed = format_docs.constr_bday_page(bdays, month_as_str)
        except ValueError:
            await ctx.channel.send(text='An error occurred. Make sure that the day is formatted as **only a number**.\nExample: `{0}bday October 14th` will cause an error, instead use {0}bday October 14`'.format(prefixes[ctx.guild.id]))

    await ctx.channel.send(embed=bday_embed)


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
@bot.command(name="deaths", pass_context=True)
@has_permissions(manage_roles=True)
async def _deaths(ctx, *args):
    if len(args) == 0:  # return status of whether spoilers are on or not
        status = db_manager.get_deaths_status(ctx.guild)
        if status:
            await ctx.channel.send(embed=discord.Embed( title="deaths", description="**on**", color=0x2ecc71))
        else:
            await ctx.channel.send(embed=discord.Embed( title="deaths", description="**off**", color=0xe74c3c))
            # await ctx.channel.send('`deaths` is currently set to **off**')
    elif args[0].lower() == 'on':
        db_manager.set_deaths(ctx.guild, True)
        await ctx.channel.send('Death status enabled')

    elif args[0].lower() == 'off':
        db_manager.set_deaths(ctx.guild, False)
        await ctx.channel.send('Death status disabled')

    else:
        await ctx.channel.send('Invalid argument. Use `on` or `off`, or call without argument')

'''
    Error for deaths command, sends status of deaths
'''
@_deaths.error
async def kick_ereror(ctx, error):
    if isinstance(error, MissingPermissions):
        txt = "❌You do not have permission to use this command.\n`{0}deaths` is currenty set to ".format(prefixes[ctx.guild.id])
        
        status = db_manager.get_deaths_status(ctx.guild)
        if status:  # Rather than displaying a boolean
            txt += '**on**'
        else:
            txt += '**off**'
            
        await ctx.channel.send(text=txt)
    else:
        print('_kick: ', error)

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
    elif args[1].lower() == 'off':
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