import discord

"""
    Used by main.py
    Handles supplemental functions for main.py, mostly formats documents returned from db_manager so they are visually appealing to end-user
"""

COLOR = 0x893a94            # global holding embed color



def constr_quote(quote_doc):
    if quote_doc['name'] != quote_doc['realName']:  # TODO: replace this with <if !sameName> once DB has been formatted properly
        name = quote_doc['name'] + ' (' + quote_doc['realName'] + ')'
    else:
        name = quote_doc['name']
    

    embed_var = discord.Embed(title=name, description=quote_doc['quote'], color = COLOR)


    source = '['+quote_doc['sourceTitle']+']('+quote_doc['source']+')'
    embed_var.add_field(name='Context', value=quote_doc['name']+ ' ' +quote_doc['context'] + '\n(' + source + ')')

    if quote_doc['characterPage'] is not None:
        embed_var.add_field(name='Character Page', value='['+quote_doc['name']+' ]('+quote_doc['characterPage']+')', inline=True)
    

    if quote_doc['thumbnail'] is not None:
        embed_var.set_thumbnail(url=quote_doc['thumbnail'])

    return embed_var


''' TODO: add ability to disable spiler information (deathday and status) '''
def constr_about(doc):
    if doc['name'] != doc['realName']:          # TODO: replace this with <if !sameName> once DB has functionality
        name = doc['name'] + ' (' + doc['realName'] + ')'
    else:
        name = doc['name']
    embed_var = discord.Embed(title=name, description='\u2008')     # TODO: replace description with about once DB has that

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
    if doc['death'] is not None:
        if doc['deathInfo'] is not None:
            embed_var.add_field(name='Death', value=doc['death'] + '\n' + doc['deathInfo'] , inline=True)
        else:
            embed_var.add_field(name='Death', value=doc['death'], inline=True)
    if doc['status'] is not None:
        embed_var.add_field(name='Status', value=doc['status'], inline=True)

    if doc['thumbnail'] is not None:
        embed_var.set_thumbnail(url=doc['thumbnail'])
    
    embed_var.add_field(name=str(doc['references']) + ' Quotes', value=str(doc['percent']) + ' \u0025 of all quotes stored', inline=False)
    return embed_var
