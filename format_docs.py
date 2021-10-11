from discord import Embed
from datetime import datetime

"""
    Used by user commands in main.py
      - Formats raw documents from database to be sent to end-user
      - Error checks documents
"""


COLOR = 0x893a94            # global holding embed color



def constr_quote(quote_doc):
    # if quote_doc['name'] != quote_doc['realName']:  # : replace this with <if !sameName> once DB has been formatted properly
    if quote_doc["sameName"] == False:
        name = quote_doc['name'] + ' (' + quote_doc['realName'] + ')'
    elif quote_doc["suffix"] is not None:
        name = quote_doc['name'] + ' (' + quote_doc['suffix'] + ')'
    else:
        name = quote_doc['name']
    

    embed_var = Embed(title=name, description=quote_doc['quote'], color = COLOR)


    source = '['+quote_doc['sourceTitle']+']('+quote_doc['source']+')'      # guaranteed to exist
    if quote_doc['context'] is not None:
        source = quote_doc['name'] +' '+ quote_doc['context'] + '\n' + source    # Adds context (i.e. "Iron Man to Spider-Man") before linking source
    embed_var.add_field(name='Source', value=source) 

    if quote_doc['charPage'] is not None:
        embed_var.add_field(name='Character Page', value='['+quote_doc['name']+']('+quote_doc['charPage']+')', inline=True)
    

    if quote_doc['thumbnail'] is not None:
        embed_var.set_thumbnail(url=quote_doc['thumbnail'])

    return embed_var


''' TODO: add ability to disable spiler information (deathday and status) '''
def constr_about(doc):
    if doc['name'] != doc['realName']:          # TODO: replace this with <if !sameName> once DB has functionality
        name = doc['name'] + ' (' + doc['realName'] + ')'
    else:
        name = doc['name']
    embed_var = Embed(title=name, description='\u2008', color=COLOR)     # TODO: replace description with about once DB has that

    if doc['species'] is not None and doc['citizenship'] is not None:
        embed_var.add_field(name='Species/Citizenship', value=doc['species']+'/'+doc['citizenship'], inline=False)
    elif doc['species'] is not None:
        embed_var.add_field(name='Species', value=doc['species'], inline=False)
    elif doc['citizenship'] is not None:
        embed_var.add_field(name='Citizenship', value=doc['citizenship'], inline=False)
    
    # if doc['birthday'] is not None and doc['death'] is not None:
    #     embed_var.add_field(name='Lived', value=doc['birthday'] + ' \u2014 ' + doc['death'])
    # elif doc['birthday'] is not None:
    #     embed_var.add_field(name='Lived', value=doc['birthday'])
    # elif doc['death'] is not None:
    #     embed_var.add_field(name='Lived', value=doc['death'])
    if doc['birthday'] is not None:
        embed_var.add_field(name='Birthday', value=doc['birthday'], inline=True)
    # if doc['death'] is not None:  As of now this field is always none
        # if doc['deathInfo'] is not None:
            # embed_var.add_field(name='Death', value=doc['death'] + '\n' + doc['deathInfo'] , inline=True)
        # else:
            # embed_var.add_field(name='Death', value=doc['death'], inline=True)
    if doc['status'] is not None:   # Set to None when deaths are set to off
        embed_var.add_field(name='Status', value=doc['status'], inline=True)

    if doc['thumbnail'] is not None:
        embed_var.set_thumbnail(url=doc['thumbnail'])
    
    embed_var.add_field(name=str(doc['references']) + ' Quotes', value=str(doc['percent']) + ' \u0025 of all quotes\n\n[Wiki]('+doc['charPage']+')', inline=False)
    return embed_var


''' 
    Creates embed for no-args help cmd 
    Parameters: 
      - h_dict = dictionary containing list of commands and category
      - prefix = server prefix (used to set footer)
'''
def constr_help_list(h_dict, prefix):
    desc = "I'm a bot that generates quotes from the Marvel Cinematic Universe\nType `{0}help <command>` for more information about that command".format(prefix)
    embed_var = Embed(title='MCU Quotes Bot', description=desc, color=COLOR)
    for group in h_dict:    # iterate through keys of dict, recall values are an array
        if len(h_dict[group]) == 1:
            val = '`' + h_dict[group][0] + '`'
        elif len(h_dict[group]) == 0:
            continue
        else:
            val = '`, `'.join(h_dict[group])
        embed_var.add_field(name=group, value=val, inline=False)

    # embed_var.set_footer(text='Prefix: {0}'.format(prefix))
    return embed_var


''' 
    Creates embed for help <command> call 
    Takes doc as retreived from database (dict)
'''
def constr_help_page(doc, prefix):
    if doc is None:
        return None
    
    embed_var = Embed(title=doc['command'], description=doc['details'], color=COLOR)
    embed_var.add_field(name='Use', value='`' + prefix + doc['use'], inline=False)
    embed_var.add_field(name='Group', value=doc['group'], inline=True)

    examples = '`' + '\n`'.join(doc['examples'])
    embed_var.add_field(name='Examples', value=examples, inline=False)
    return embed_var
    

''' 
    Constructs page of today's birthdays
    Input: list of character docs +(optnl) month being checked
'''
def constr_bday_page(bdays, month=None):
    x = datetime.now()
    # date_as_words = x.strftime("%B") + ' ' + str(x.day)+ ", " + str(x.year)
    if month is None:   # if checking today's date
        date_of  = str(x.month) + '/' + str(x.day)
        heading = "Today's Birthdays ({0})".format(date_of)
    else:               # if checking a specific date
        date_of  = month 
        heading = month[0].upper() + month[1:].lower() +' Birthdays'
    
    if bdays is None:
        return Embed(title="No {0} Birthdays".format(date_of), description='\u2008', color=COLOR)

    embed_var = Embed(title=heading, description='\u2008', color=COLOR)
    embed_var.set_footer(text=str(len(bdays)) + ' Total')

    for doc in bdays:
        if doc['sameName']:
            name_val = doc['name']
        else:
            name_val = doc['name']+' ('+doc['realName']+')'
        
        embed_var.add_field(name=name_val, value=doc['birthday'])
    
    return embed_var
