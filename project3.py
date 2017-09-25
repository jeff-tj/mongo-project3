
# coding: utf-8

# In[1]:

#_author_jeffrey_t
#clean the OSM data for Sydney Metro Area:
#https://mapzen.com/data/metro-extracts/your-extracts/c98c29b17741
#Mirrored on Google Drive: https://drive.google.com/file/d/0B65XFpo9P0K3NW52RGdidzU3eEU/view?usp=sharing

#import required libraries
import xml.etree.cElementTree as ET
from bs4 import BeautifulSoup
import os
import re
from collections import defaultdict
import pprint
import codecs
import json

#some global refs
osm_test_file = 'sydney_australia.osm'

#setup print pretty
pp = pprint.PrettyPrinter()


# In[2]:

#print some basic stats about our file
def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    from: http://stackoverflow.com/questions/2104080/how-to-check-file-size-in-python
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

file_info = os.stat(osm_test_file)
print convert_bytes(file_info.st_size)

def count_tags(filename):
    # YOUR CODE HERE
    p_evt = ('start',)
    tags = {}
    for _, elem in ET.iterparse(filename, events=p_evt):
        my_tag = elem.tag
        if my_tag in tags:
            tags[my_tag] += 1
        else:
            tags[my_tag] = 1
    return tags

print count_tags(osm_test_file)


# In[3]:

#module to audit street names
st_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
st_types = set() #defaultdict(set) ???

def is_st_name(elem):
    return (elem.attrib["k"].rstrip() == "addr:street")

def audit_st_type(street_types, street_name):
    m = st_type_re.search(street_name)
    if m:
        this_st_type = m.group()
        st_types.add(this_st_type)

def list_st_types(filename):
    p_evt = ("start",)
    n = 0
    for _, elem in ET.iterparse(filename, events=p_evt):
        if elem.tag == "way" or elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_st_name(tag):
                    audit_st_type(st_types, tag.attrib['v'])

list_st_types(osm_test_file)
print st_types

#We can see that there are a few inconsistencies in naming which we should clean


# In[4]:

# audit postcodes - a field not covered in the case study
postcode_re = re.compile(r'^\d{4}$')
postcode_flds = set()
postcode_bad = set()

# according to the osm documentation, there are a few postcode fields:
# addr:postcode, boundary=postal_code

def is_postcode(elem):
    return (elem.attrib['k'].rstrip() == 'addr:postcode')

def audit_postcode_fld(elem):
    if elem.attrib['k'].find('code') != -1:
        postcode_flds.add(elem.attrib['k'])

postcode_types = defaultdict(set)
def audit_postcodes(filename):
    p_evt = ('start',)
    n = 0
    for _, elem in ET.iterparse(filename, events=p_evt):
        for tag in elem.iter('tag'):
            if is_postcode(tag):
                pc = postcode_re.search(tag.attrib['v'])
                if not pc:
                    postcode_types[tag.attrib['k']].add(tag.attrib['v'])
            else:
                if tag.attrib['k'].find('code') != -1:
                    postcode_types[tag.attrib['k']].add(tag.attrib['v'])

audit_postcodes(osm_test_file)
pprint.pprint(dict(postcode_types))

# In[5]:

def compare_postcodes(filename):
    p_evt = ('start',)
    n = 0
    test_flds = set(['addr:postcode', 'postal_code'])
    for _, elem in ET.iterparse(filename, events=p_evt):
        #setup test variables for each tag
        addr_postcode = False
        postal_code = False
        postcodes = {}
        for tag in elem.iter('tag'):
            tag_k = tag.attrib['k'].rstrip()
            if tag_k == 'addr:postcode':
                addr_postcode = True
                postcodes['addr:postcode'] = tag.attrib['v']
            elif tag_k == 'postal_code':
                postal_code = True
                postcodes['postalcode'] = tag.attrib['v']
        if (addr_postcode and postal_code):
            print postcodes

compare_postcodes(osm_test_file)

# In[6]:

# testing tag types
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
lower_two_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def test_tag_type(elem):
    tag_type = elem.attrib['k']
    if lower.match(tag_type) != None:
        keys['lower'] += 1
    elif lower_colon.match(tag_type) != None:
        keys['lower_colon'] += 1
    elif lower_two_colon.match(tag_type) != None:
        keys['lower_two_colon'] += 1
        two_colon_set.add(tag_type)
    elif problemchars.match(tag_type) != None:
        keys['problemchars'] += 1
    else:
        keys['other'] += 1
        others_set.add(tag_type)

keys = {
        'lower': 0,
        'lower_colon': 0,
        'lower_two_colon': 0,
        'problemchars': 0,
        'other': 0
        }
two_colon_set = set()
others_set = set()

def test_tag_types(filename):
    p_evt = ('start',)
    n = 0
    test_flds = set(['addr:postcode', 'postal_code'])
    for _, elem in ET.iterparse(filename, events=p_evt):
        if 'k'  in elem.attrib:
            test_tag_type(elem)

test_tag_types(osm_test_file)
print keys
print two_colon_set
print others_set

# In[7]:

# Printing out problem postcode elements
# We know from above that postcodes are stored in two fields 
postcode_tags = ["addr:postcode", "postal_code"]


def examine_postcodes(filename, test_flds):
    p_evt = ("start",)
    for _, elem in ET.iterparse(filename, events=p_evt):
        print_elem = False
        for tag in elem.iter("tag"):
            if tag.attrib["k"] in test_flds:
                # If in fields test value
                pc_value = tag.attrib["v"]
                if not postcode_re.search(pc_value):
                    # Also exclude where starts with state and ends with 4 digits
                    if not ((pc_value[:3] == "NSW") and (postcode_re.search(pc_value[-4:]) is not None)):
                        print_elem = True
        if print_elem:
            #print BeautifulSoup(elem.iter("tag"), "xml").prettify()
            for tag in elem.iter("tag"):
                print ET.tostring(tag)
            print "---"

examine_postcodes(osm_test_file, postcode_tags)

# In[8]:

# Set of good names:
valid_st_types = set(["Way",
                     "Highway",
                     "Road",
                     "Lane",
                     "Drive",
                     "Place",
                     "Circuit",
                     "Square",
                     "Parade",
                     "Point",
                     "Esplanade",
                     "Boulevard",
                     "Street",
                     "Crescent",
                     "Broadway",
                     "Avenue",
                     "Freeway"])

# Dictionary to unify abbreviations - also unify spelling
abbr_dict = {"Rd": "Road",
            "St": "Street",
            "St.": "Street",
            "street": "Street",
            "Ave": "Avenue",
            "Boulevarde": "Boulevard"}

# Print out things that don't conform
def examine_street(filename):
    p_evt = ("start",)
    # Create a set of good street names and solved problems
    solved_set = valid_st_types
    solved_set.update(set(abbr_dict.keys()))
    
    for _, elem in ET.iterparse(filename, events=p_evt):
        print_elem = False
        for tag in elem.iter("tag"):
            if elem.tag == "way" or elem.tag == "node":
                if tag.attrib["k"] == "addr:street":
                    # If in fields test value
                    st_value = tag.attrib["v"]
                    m = st_type_re.search(st_value)
                    st_end = m.group()
                    if not st_end in solved_set:
                        #print tag.attrib["v"]
                        print_elem = True
        if print_elem:
            for tag in elem.iter("tag"):
                print ET.tostring(tag)
            print "---"

examine_street(osm_test_file)

# In[9]:

def get_postcode(pc_value):
    if postcode_re.search(pc_value) != None:
        # Postcode has no error
        return pc_value
    elif (pc_value[:3] == "NSW" and postcode_re.search(pc_value[-4:]) != None):
        # Errors of the style "NSW 2133"
        return pc_value[-4:]
    else:
        # Manual fix
        fix_dict = {"210": "2010",
                   "1465;2033": "2033",
                   "200": "2000"}
        return fix_dict[pc_value]

# Updated street lists
valid_st_types = set(["Way",
                     "Highway",
                     "Road",
                     "Lane",
                     "Drive",
                     "Place",
                     "Circuit",
                     "Square",
                     "Parade",
                     "Point",
                     "Esplanade",
                     "Boulevard",
                     "Street",
                     "Crescent",
                     "Broadway",
                     "Avenue",
                     "Freeway",
                     "Promanade",
                     "Plaza",
                     "Arcade",
                     "Terrace",
                     "South",
                     "North",
                     "Gardens"])
abbr_dict = {"Rd": "Road",
            "St": "Street",
            "St.": "Street",
            "street": "Street",
            "Ave": "Avenue",
            "Boulevarde": "Boulevard"
            }
    
def get_street(street_val):
    st_search = st_type_re.search(street_val)
    if st_search != None:
        st_type = st_search.group()
        if st_type in valid_st_types:
            return street_val
        elif st_type in abbr_dict.keys():
            end_st = st_search.start()
            return street_val[:end_st] + abbr_dict[st_type]
        elif street_val.startswith("70A Campbell Parade"):
            return "Campbell Parade"
        elif street_val.startswith("Playfair St"):
            return "Playfair Street"
        else:
            # Manually correct street values
            manual_fix = {"Wolli": "Wolli Street",
                         "Wollit": "Wolli Street",
                         "Berith": "Berith Street",
                         "Edward": "Edward Street",
                         "King Street Offramp": "King Street",
                         "Sydney Fish Market": "Pyrmont Bridge Road",
                         "Androtis": "Pyrmonth Bridge Road",
                         "Addison road, nr East street, marrickville": "Addison Road",
                         "Holt Street (enter via Gladstone Street)": "Holt Street",
                         "Pacific Highway underpass": "Pacific Highway",
                         "Leichhardt": "Norton Street",
                         "City": "City", # We leave as is without enough info to change
                         "The Wharf, Cowper Wharf Road, Woolloomooloo, Sydney": "Cowper Wharf Street",
                         #"70A Campbell Parade, Bondi Beach NSW 2026&#28595;&#27954;": "Campbell Parade",
                         #"Playfair St &amp; Argyle Street, The Rocks NSW 2000&#28595;&#27954;": "Playfair Street",
                         "Jones": "Jones Street",
                         "Fitzroy": "Fitzroy Street"}
            return manual_fix[street_val]
    else:
        return None

# In[10]:

def copy_dict(keys, source_dict, dest_dict):
    for key in keys:
        if key in source_dict:
            dest_dict[key] = source_dict[key]

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node['type'] = element.tag
        e_att = element.attrib
        copy_dict(['id', 'visible'], e_att, node)
        created_ls = ['version', 'changeset', 'timestamp', 'user', 'uid']
        created_tmp = {}
        copy_dict(created_ls, e_att, created_tmp)
        node['created'] =  created_tmp
        node['pos'] = []
        for coord in ['lat', 'lon']:
            if coord in e_att:
                node['pos'].append(float(e_att[coord]))
        addr_dict = {}
        for sub in element:
            if 'k' in sub.attrib:    
                sub_att = sub.attrib
                sub_tag = sub.attrib['k']
                if problemchars.search(sub_tag) == None:
                    if sub_tag.startswith('addr:housenumber'):
                        addr_dict['housenumber'] = sub_att['v']
                    elif sub_tag.rstrip() == 'addr:street':
                        addr_dict['street'] = get_street(sub_att['v'])
                    elif sub_tag.rstrip() in postcode_tags:
                        addr_dict['postcode'] = get_postcode(sub_att['v'])
                    elif sub_tag.rstrip() == 'addr:suburb':
                        addr_dict['suburb'] = sub_att['v']
                    elif not sub_tag.startswith('addr:'):
                        if sub_tag.count(':') == 0:
                            node[sub_tag] = sub_att['v']
                        if sub_tag.count(':') == 1:
                            sub_node_dict = {}
                            sub_node_loc = sub_tag.find(':')
                            sub_node_dict_name = sub_tag[:sub_node_loc]
                            sub_node_fld = sub_tag[(sub_node_loc + 1):]
                            sub_node_dict[sub_node_fld] = sub_att['v']
                            node[sub_node_dict_name] = sub_node_dict
        if addr_dict != {}:
            node['address'] = addr_dict
        if element.tag == 'way':
            node_refs = []
            for sub in element:
                if 'ref' in sub.attrib:
                    node_refs.append(sub.attrib['ref'])
            node['node_refs'] = node_refs
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

json_data = process_map("sydney_australia.osm", False)


# In[11]:

# Load data into a mongo database
from pymongo import MongoClient

client = MongoClient()
db = client.mymaps

num_entries = db.mymaps.find().count()
print "Entries before load: ", num_entries

for entry in json_data:
    db.mymaps.insert(entry)

num_entries = db.mymaps.find().count()
print "Entries after load: ", num_entries


# In[12]:

json_info = os.stat("sydney_australia.osm.json")

print "json size: ", convert_bytes(json_info.st_size)
print "Node count: ", db.mymaps.find({"type": "node"}).count()
print "Way count: ", db.mymaps.find({"type": "way"}).count()


# In[13]:

# Number of unique users
print "Number of unique users: ", len(db.mymaps.distinct("created.user"))


# In[14]:

# Top 5 users
top_users = db.mymaps.aggregate([{"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
                                 {"$project": {"_id": "$_id",
                                               "count": "$count",
                                               "percent": {"$divide": ["$count", num_entries]}}},
                                 {"$sort": {"count": -1}},
                                 {"$limit": 5}])

pp.pprint(list(top_users))

# In[15]:

# Users with only 1 post
single_post = db.mymaps.aggregate([{"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
                                   {"$match": {"count": 1}}])
len(list(single_post))


# In[16]:

# Top 10 amenities
top_amenities = db.mymaps.aggregate([{"$match": {"amenity": {"$exists": 1}}},
                                     {"$group": {"_id": "$amenity", "count": {"$sum": 1}}},
                                     {"$sort": {"count": -1}},
                                     {"$limit": 10}])
pp.pprint(list(top_amenities))


# In[17]:

# Top 10 cuisines
top_cuisines = db.mymaps.aggregate([{"$match": {"cuisine": {"$exists": 1}}},
                                    {"$group": {"_id": "$cuisine", "count": {"$sum": 1}}},
                                    {"$sort": {"count": -1}},
                                    {"$limit": 10}])
pp.pprint(list(top_cuisines))


# In[18]:

# Best postcodes to dine in - we find the postcodes with the most restaurants
# Top 10 amenities
top_eatpc = db.mymaps.aggregate([{"$match": {"amenity": "restaurant", "address.postcode": {"$exists": 1}}},
                                 {"$group": {"_id": "$address.postcode", "count": {"$sum": 1}}},
                                 {"$sort": {"count": -1}},
                                 {"$limit": 10}])
pp.pprint(list(top_eatpc))

# In[19]:

# Most popular amenities in 2050
top_local = db.mymaps.aggregate([{"$match": {"address.postcode": "2050", "amenity": {"$exists": 1}}},
                                 {"$group": {"_id": "$amenity", "count": {"$sum": 1}}},
                                 {"$sort": {"count": -1}}])

pp.pprint(list(top_local))

# In[20]:

# Entry has a postcode
print "Number entries with a postcode: ", db.mymaps.find({"address.postcode": {"$exists": 1}}).count()
# Entry has an address
print "Number of entries with a suburb: ", db.mymaps.find({"address.suburb": {"$exists": 1}}).count()
# Entry has both
both = db.mymaps.find({"$and": [{"address.postcode": {"$exists": 1}}, 
                                {"address.suburb": {"$exists": 1}}]}
                     ).count()
print "Number of entries with both postcode and suburbs: ", both

# Look at these entries
pc_suburb = db.mymaps.aggregate([{"$match": {"address.postcode": {"$exists": 1}, "address.suburb": {"$exists": 1}}},
                                 {"$group": {"_id": "$address.postcode", 
                                             "suburbs": {"$addToSet": "$address.suburb"}}}])
print ""
print "List of postcodes and suburbs"
pp.pprint(list(pc_suburb))
