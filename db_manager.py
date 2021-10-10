from discord.ext.commands.help import HelpCommand
import pymongo, os
from dotenv import load_dotenv
from bson.son import SON

"""
    Handles all calls to the mcuQuotes database
    used by main.py and guild_handling.py

"""


load_dotenv() 
DB_CLIENT   = os.getenv('DB_CLIENT')
db_client   = pymongo.MongoClient(DB_CLIENT)
DB          = db_client['mcuQuotes']
GUILDS      = DB['guilds']
QUOTES      = DB['quotes']
CHARS       = DB['characters']
HELP        = DB['command-info']



"""  --------------------   Functions used by main.py   --------------------  """
''' Used for quick db modifying'''
def command_line():
    QUOTES.update_many({'suffix': {'$exists': False}}, {'$set': {'suffix': None}})
    # cursor = QUOTES.find({'charPage': {'$regex': ' '}})
    # for doc in cursor:
    #     s = doc['charPage'].replace(' ', '_')
    #     QUOTES.update_one({'_id': doc['_id']}, {'$set': {'charPage': s}})
    #     print(doc['charPage'])
    # QUOTES.update_many({'name':'Phil Coulson', 'suffix': 'Chronicom LMD'}, {'$set': {'charPage': 'https://marvelcinematicuniverse.fandom.com/wiki/Phil_Coulson/Chronicom_LMD'}})

def get_quote(guild, args=None):
    if args is None:
        items = QUOTES.aggregate([{ "$sample": {"size": 1}}])
    else:
        items = QUOTES.aggregate([
            { "$match": { '$or': [{'name': {'$regex': args, '$options': 'i'}}, {'realName': {'$regex': args, '$options': 'i'}}]}},
            { "$sample": {"size": 1} }
        ])

    item = list(items)
    if len(item) == 0:
        return None
    
    item = item[0]
    GUILDS.update_one({'_id': guild.id}, {'$push': {'used_quotes': item['_id']}})
    
    return item


'''
    Retrieves document containing information about a character

    TODO: add about bot (no args call)
        - Potentially add a more efficient search method using regex substring functionality
        - Ability to exclude spoiler info
'''
def get_about(guild, args):
    # Begin by attempting to search for an exact match
    doc = CHARS.find_one({'name': args})
    if doc is None:
        doc = CHARS.find_one({'realName': args})

    # Last resort check, finds FIRST character that matches simplified criteria (WARNING: a search for xxx can fetch xxx-XX instead)
    if doc is None:
        doc = CHARS.find_one({'$or': [{'name': {'$regex': args, '$options': 'i'}}, {'realName': {'$regex': args, '$options': 'i'}}]})
    
    return doc


'''
    Called by no args help command in main.py
    Returns list of commands
'''
def get_help_dict():
    help_dict = {       # Alternative to dictionary is a help obj, but I feel like it works well enough without OOP
        'Quotes': [], 
        'Info': [],
        'Setup': []
    }  
    cursor = HELP.find()
    for item in cursor:
        help_dict[item['group']].append(item['command'])

    return help_dict


'''
    Called by help command with argument in main.py
    Returns the document (dict)
'''
def get_help_page(cmd):
    try:
        doc = HELP.find_one({'command': {'$regex': cmd, '$options': 'i'}})
        return doc
    except KeyError:
        return None



"""  --------------------   Functions Relating to Guilds   --------------------  """

'''
    Called on startup by guild_handling.py's establish_dicts()
    Returns a tupple containing prefixes in [0] and permissions in [1]
'''
def establish_guild_info():
    prefixes    = {}
    permissions = {}
    guilds = GUILDS.find()
    for guild in guilds:
        prefixes[guild['_id']]    = guild['prefix']
        permissions[guild['_id']] = guild['perms']
    return (prefixes, permissions)


def establish_prefixes():
    prefixes = {}
    guilds = GUILDS.find()
    for guild in guilds:
        prefixes[guild['_id']]  = guild['prefix']

    return prefixes


''' Changes a guild's prefix '''
def change_prefix(guild_id, prefix):
    GUILDS.update_one({'_id': guild_id}, {'$set': {'prefix': prefix}})