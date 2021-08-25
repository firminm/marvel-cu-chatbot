import pymongo, os
from dotenv import load_dotenv
from bson.son import SON

load_dotenv()
DB_CLIENT   = os.getenv('DB_CLIENT')
db_client   = pymongo.MongoClient(DB_CLIENT)
DB          = db_client['marvelQuotes']
GUILDS      = DB['mcu_guilds']
QUOTES      = DB['all_mcu_quotes']
CHARS       = DB['mcu_characters']


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