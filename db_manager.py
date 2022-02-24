from discord.ext.commands.help import HelpCommand
import pymongo, os
from dotenv import load_dotenv
from bson.son import SON
from datetime import datetime

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
    
    QUOTES.update_many({'realName': None, 'sameName': False}, {'$set': {'sameName': True}})

    # QUOTES.update_many({'suffix': {'$exists': False}}, {'$set': {'suffix': None}})
    # QUOTES.update_many({'name': {'$regex': "/\Ravager T'Challa"}}, {'$set': {'suffix': "W/I? Ravager T'Challa"}})
    # cursor = CHARS.find({'birthday': {'$regex': ']$'}})
    # for doc in cursor:
    #     temp = doc['birthday'][:-3]
    #     # print(temp)
    #     CHARS.update_one({'_id': doc['_id']}, {'$set': {'birthday': temp}})


    

    # QUOTES.update_many({'suffix': {'$exists': False}}, {'$set': {'suffix': None}})
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
    
    # account for spoilers
    if GUILDS.find_one({'_id': guild.id})['deaths'] == False:
        item['status'] = None
    return item


'''
    Retrieves document containing information about a character

    TODO: add about bot (no args call)
        - optimize search
        - IMPROVE SUFFIX HANDLING
'''
def get_about(guild, args):
    # Begin by attempting to search for an exact match
    doc = CHARS.find_one({'name': args, 'suffix': None})
    if doc is None:
        doc = CHARS.find_one({'realName': args, 'suffix': None})

    # Check for a character whose name starts with arg
    if doc is None:
        doc = CHARS.find_one({'$or': [{'name': {'$regex': '^'+args, '$options': 'i'}, 'suffix': None}, {'realName': {'$regex': '^'+args, '$options': 'i'}, 'suffix': None}]})

    # Last resort check, finds FIRST character where the args string is contained
    # Begin by checking for characters with no suffix to avoid accessing an alt-character
    if doc is None:
        doc = CHARS.find_one({'$or': [{'name': {'$regex': args, '$options': 'i'}, 'suffix': None}, {'realName': {'$regex': args, '$options': 'i'}, 'suffix': None}]})

    if doc is None: # Wildcard search, can really be anything
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
        'Setup': [],
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

''' Returns list of characters with today's birthday'''
def get_today_bday():
    x = datetime.now()
    date_as_str = "^" + x.strftime("%B") + ' ' + str(x.day)         # (Month day) '^' added for regex matching
    print(date_as_str)
    bdays = CHARS.find({'birthday': {'$regex': date_as_str}})
    
    bdays = list(bdays)
    if len(bdays) == 0:
        return None
    
    return bdays

''' 
    Returns list of characters born in a specific month
    Input: month = args from ($bday *args) in main
      Searches for birthdays fields that begin with *args
'''
def get_bday(month):
    bdays = bdays = CHARS.find({'birthday': {'$regex': '^'+month, '$options': 'i'}})
    
    bdays = list(bdays)
    if len(bdays) == 0:
        return None

    # Sort by date:
    bdays.sort(key=lambda x: int(x['birthday'][-4:]))
    return bdays



"""  --------------------   Functions Relating to Guilds   --------------------  """

''' Changes a guild's prefix '''
def change_prefix(guild, prefix):
    GUILDS.update_one({'_id': guild.id}, {'$set': {'prefix': prefix}})


''' Takes boolean on, sets death status to on/off'''
def set_deaths(guild, status):
    GUILDS.update_one({'_id': guild.id}, {'$set': {'deaths': status}})

''' Returns the status of death spoilers'''
def get_deaths_status(guild):
    return GUILDS.find_one({'_id': guild.id})['deaths']



"""  --------------------   Startup & Automatic Commands   --------------------  """

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


''' Called when a new guild is joined, sets default values '''
def add_guild(guild):
    default = GUILDS.find_one({"_id": 0})   # guild which holds all default values

    GUILDS.insert_one({
        "_id": guild.id, 
        "name": guild.name,
        "members": guild.member_count,
        "perms": default['perms'],
        "deaths": default['deaths'],
        "repeats": default['repeats'],
        "prefix": default['prefix'],
        "used_quotes": []
        })
    GUILDS.update_one({'_id': 0}, {'$inc': {'servers': 1, 'members': guild.member_count}})


def remove_guild(guild):
    negated = GUILDS.find_one({'_id': guild.id})['members']
    GUILDS.update_one({'_id': 0}, {'$inc': {'members': -negated, 'servers': -1}})

    GUILDS.delete_one({'_id': guild.id})