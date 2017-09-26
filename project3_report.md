## Sydney OpenStreetMap Data Wrangling Project
### Jeffrey Tjeuw
### Contents
1. [Introduction](#introduction)
2. [Problems Encountered in OSM Data](#problems)
    * [Street name endings problems](#streetnameprob)
    * [Postcode problems](#postcodeprob)
3. [Auditing the Data](#audit)
    * [Postcodes](#postcodeaudit)
    * [Street name endings](#streetnameaudit)
4. [Overview of the Data](#overview)
5. [Improvements](#improvements)
6. [Conclusion](#conclusion)

### 1. Introduction <a name="introduction"></a>
The data we used was a custom data set centered on Sydney metropolitan area.

>Link: https://mapzen.com/data/metro-extracts/your-extracts/c98c29b17741  
>Mirrored on Google Drive: https://drive.google.com/file/d/0B65XFpo9P0K3NW52RGdidzU3eEU/view?usp=sharing

The original Sydney area dataset on OSM, included an extremely large areas of Sydney, including many places that I had not heard of before.Therefore, I selected a smaller area, however this allowed me to go through it in more detail, often case-by-case decisions.

This document only provides a concise summary of the problems encountered and the steps taken to resolve them. Please see the iPython notebook and printout (project3.ipynb, project3.html) for more detail.

Quick overview of the data, such as size and the number of each type of tag present:
>OSM size: 65.9 MB  
>{'node': 282039, 'nd': 359303, 'bounds': 1, 'member': 25166, 'tag': 241467, 'osm': 1, 'way': 49541, 'relation': 2094}

### 2. Problems Encountered in the OSM Data <a name="problems"></a>
We initially look for some common problems in the data, such as inconsistency in street name endings and postcodes.

#### Street name endings <a name="streetnameprob"></a>
To look at street name endings we use regex to extract the ending in the "addr:street" field and compile a set of endings in our data. We can see the results below:
>set(['City', 'Boulevard', 'Sydney', 'Arcade', 'Wollit', u'2026\u6fb3\u6d32', 'St.', 'street', 'Rd', 'Edward', 'Way', 'Promanade', 'Highway', 'underpass', 'Fitzroy', 'marrickville', u'2000\u6fb3\u6d32', 'Street)', 'South', 'Terrace', 'Jones', 'Lane', 'Offramp', 'Plaza', 'Drive', 'St', 'Freeway', 'Place', 'Circuit', 'Ave', 'North', 'Gardens', 'Road', 'Wolli', 'Square', 'Parade', 'Point', 'Leichhardt', 'Esplanade', 'Boulevarde', 'Androtis', 'Street', 'Crescent', 'Broadway', 'Berith', 'Avenue', 'Market'])

Here we can see that most streets end with the unabbreviated street endings but there are the common problems of inconsistent abbreviations as well as other errors. In our audit we will print out these problems and examine them in detail

#### Postcodes <a name="postcodeprob"></a>
We also create a regex query for four integers, and create a set of entries in the "addr:postcode" field that do not conform to this. We also search other tags that contain "code", in case postcodes have been stored in other tags. We truncate the output below:
>{'addr:postcode': set(['200',
>                       '210',
>                       'NSW 1460',
>                       ...
>                       'NSW 2037']),
> 'is_in:country_code': set(['AU']),
> 'is_in:state_code': set(['NSW']),
> 'postal_code': set(['1465;2033',
>                     '2000',
>                     ...
>                     '2231']),
> 'source:addr:postcode': set(['knowledge']),
> 'source:postal_code': set(['Wikipedia',
>                            'knowledge',
>                            'local_knowledge',
>                            'wikipedia'])}

In Australia all postcodes are 4 integers, so can see that the "addr:postcode" has two errors where there are data entry mistakes (only 3 characters) and also inconsistent formatting where "NSW" has been appended to the front. Of the other fields containing code, only "postal_code" contains postcodes. These are mostly correct, apart from the first entry: "1465:2033".

### 3. Auditing the data <a name="audit"></a>
We know take a slightly deeper look at some of the problems in our data, namely we will print out a some of the problem elements in our data.

#### Postcodes <a name=postcodeaudit></a>
The first issue will look at are the postcodes which have problems other than being append with the state prefix - i.e. if "NSW 2000" we know that the problem is fairly simple - namely we will strip out the prefix.
However we will look at the following issues identified above:
* 3 digit poscodes
* '1465;2033' case
We manually print out these problems:

```
<tag k="name" v="Big Boy Thai" />
<tag k="amenity" v="restaurant" />
<tag k="cuisine" v="thai" />
<tag k="addr:city" v="Darlinghurst" />
<tag k="addr:street" v="Stanley Street" />
<tag k="addr:postcode" v="210" />
<tag k="addr:housenumber" v="82" />
---
<tag k="addr:postcode" v="210" />
---
<tag k="name" v="Kensington POSTshop" />
<tag k="amenity" v="post_office" />
<tag k="building" v="yes" />
<tag k="addr:street" v="Anzac Parade" />
<tag k="postal_code" v="1465;2033" />
<tag k="addr:housenumber" v="168,170" />
---
<tag k="postal_code" v="1465;2033" />
---
<tag k="name" v="Queen Victoria Building" />
<tag k="shop" v="mall" />
<tag k="name:ko" v="&#53304; &#48709;&#53664;&#47532;&#50500; &#48716;&#46377;" />
<tag k="name:zh" v="&#32500;&#22810;&#21033;&#20122;&#22899;&#29579;&#22823;&#21414;" />
<tag k="tourism" v="attraction" />
<tag k="building" v="retail" />
<tag k="wikidata" v="Q54518" />
<tag k="wikipedia" v="en:Queen Victoria Building" />
<tag k="wheelchair" v="yes" />
<tag k="addr:street" v="George Street" />
<tag k="addr:postcode" v="200 />
<tag k="building:levels" v="4" />
<tag k="addr:housenumber" v="455" />
---
<tag k="addr:postcode" v="200" />
---
```
Here we can see the non-obvious errors are a small enough sample for us to correct manually. And we can explain them:
* The first error is a mistake - the postcode for Darlinghurst is 2010 - not 210
* The second one is a post office - 2033 is the postcode for the suburb, while 1465 is the postcode for PO Boxes located there. Since we are interested in the location and suburb, we will amend this to 2033
* The last one is also another mistake, the Queen Victoria Building is a popular building located in Sydney - which has postcode 2000 These should be relatively simple fixes but which will need to account for in our fix postcode function.

#### Street name endings <a name="streetnameaudit"></a>
From above we have collected all the endings in "addr:street" field. Of the ones that are not good street names, we can form them into two groups:
* Abbreviations - these we will form a dictionary to correct
* Miscellaneous unrecognised forms - we will print these out to get a better handle on these issues

We manually check the miscellaneous entries and resolve them the following way:
* Offramp is further information, so should not be in street names - we remove this.
* "Sydney Fish Market" is a venue and not a street name - we will amend these to "Pyrmont Bridge Road". "Androtis" likewise is the name of a business in the Fish Market. We will similarly amend.
* "marrickville" is the suburb - we weill remove this to leave only the street name. We should also add this field in under suburb as well.
* "Street)" ending likewise additional information that should be removed.
* "The Promenade", "Elizabeth Plaza", "Tramway Arcade", "Magdalene Terrace" are valid street names.
* "Underpass" additional information that is not part of the street name.
* "Berith", "Edward" and "Wolli" are missing "Street". These are all in the suburb of Kingsgrove and so must be the format of the contributor of that area. "Wollit" is probably a typo for "Wolli as well.
* Bardsley Gardens and Roslyn Gardens are valid street names - in fact I have learnt something new here in that Gardens is a valid street ending.
* "Leichhardt" lists as the street address to a Commonwealth Bank. While there is a "Leichhardt Street" - there is no Bank @ no 18, however there is one on 18 Norton Street. We make this correction as well.
* Fitroy is a data entry problem - the proper name is "Fitzroy Street", an easy correction.
* The entry with "City" does not have enough information for us to rectify. It would probably be best to leave as is or remove this entry.
* "The Wharf, Cowper Wharf Road, Woolloomooloo, Sydney" - is incorrect and so we just take the street name.
* Similarly we can also do the same to the two entry ending in a string of numbers and dashes.
* The entry "Jones" is for a now defunct company "Team Bondi" which used to be on "Jones Street". While we could remove this entry, this would be inconsistent as the database may also contain other defunct companies - it would be better to audit this at that time. So here we settle for correcting the street name.
* The last one is slightly tricky - the official street name does turn out to be "Alfred Street South". We so the entry is correctly entered. If we were taking statistics on street types and that was important, we may consider changing it to "Alfred (South) Street" or something similar. However I have decided to leave it be as it stands. As is "Ocean Street North".

### 4. Overview of the data <a name=overview></a>
We print off some basic stats about our json file:
* Number of documents:
```
num_entries = db.mymaps.find().count()
print "Entries after load: ", num_entries
```
> Entries after load:  331580

* File size and tag count:

```
json_info = os.stat("sydney_australia.osm.json")
print "json size: ", convert_bytes(json_info.st_size)
print "Node count: ", db.mymaps.find({"type": "node"}).count()
print "Way count: ", db.mymaps.find({"type": "way"}).count()
```
>json size:  72.2 MB  
>Node count:  282012    
>Way count:  49535

* Number of unique users:
```
print "Number of unique users: ", len(db.mymaps.distinct("created.user"))
```
Number of unique users:  1231

* Top 5 users:

```
top_users = db.mymaps.aggregate([{"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
                                 {"$project": {"_id": "$_id",
                                               "count": "$count",
                                               "percent": {"$divide": ["$count", num_entries]}}},
                                 {"$sort": {"count": -1}},
                                 {"$limit": 5}])

pp.pprint(list(top_users))
```
>[{u'_id': u'aharvey', u'count': 21450, u'percent': 0.06469027082453707},  
> {u'_id': u'inas', u'count': 18083, u'percent': 0.054535858616321854},  
> {u'_id': u'samuelrussell', u'count': 16322, u'percent': 0.04922492309548224},  
> {u'_id': u'Ebenezer', u'count': 13689, u'percent': 0.04128415465347729},  
> {u'_id': u'TheSwavu', u'count': 13442, u'percent': 0.04053923638337656}]

Unlike other data sets in the course example, this dataset does not appear to heavily automised (i.e. with data scraping an bots). In fact, the user IDs appear mostly human and the percentage contributions of the top 5 are relatively low (in the example project, the top user had contributed 52.92%). So the database seems to mostly have been contributed to by humans. This has both positives (it shows an active community and we are likely to have interesting additions), but at the same time opens up data entry issues and inconsistencies (seen above).

* User with only one post:
```
single_post = db.mymaps.aggregate([{"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
                                   {"$match": {"count": 1}}])
len(list(single_post))
```
> 293

* Top 10 amenities:
```
top_amenities = db.mymaps.aggregate([{"$match": {"amenity": {"$exists": 1}}},
                                     {"$group": {"_id": "$amenity", "count": {"$sum": 1}}},
                                     {"$sort": {"count": -1}},
                                     {"$limit": 10}])
pp.pprint(list(top_amenities))
```
>[{u'_id': u'parking', u'count': 737},  
> {u'_id': u'restaurant', u'count': 645},  
> {u'_id': u'cafe', u'count': 565},  
> {u'_id': u'bench', u'count': 540},  
> {u'_id': u'drinking_water', u'count': 407},  
> ...

* Top 10 cuisines:
```
top_cuisines = db.mymaps.aggregate([{"$match": {"cuisine": {"$exists": 1}}},
                                    {"$group": {"_id": "$cuisine", "count": {"$sum": 1}}},
                                    {"$sort": {"count": -1}},
                                    {"$limit": 10}])
pp.pprint(list(top_cuisines))
```
>[{u'_id': u'coffee_shop', u'count': 82},  
> {u'_id': u'burger', u'count': 53},  
> {u'_id': u'pizza', u'count': 45},  
> {u'_id': u'thai', u'count': 44},  
> {u'_id': u'italian', u'count': 38},  
> ...

* Best postcodes to dine in (we find the postcodes with the most restaurants):
```
top_eatpc = db.mymaps.aggregate([{"$match": {"amenity": "restaurant", "address.postcode": {"$exists": 1}}},
                                 {"$group": {"_id": "$address.postcode", "count": {"$sum": 1}}},
                                 {"$sort": {"count": -1}},
                                 {"$limit": 10}])
pp.pprint(list(top_eatpc))
```
>[{u'_id': u'2000', u'count': 23},  
> {u'_id': u'2010', u'count': 14},  
> {u'_id': u'2060', u'count': 14},  
> {u'_id': u'2011', u'count': 11},  
> {u'_id': u'2049', u'count': 11},   
> ...

The results of the last two queries are as expected - Australians like to pride themselves on "coffee-culture" and so the abundance of coffee shops would be expected. We see that there is good evidence of the multicultural society we live in as well with a good assortment of restaurants.

Likewise the most popular eating spots are 2000 (Sydney CBD), 2010 (Surry Hills) which are well known. However 2060 (North Sydney) was also a little unexpected, but that could be due to the fact that I do not regularly go there. Interesting my current suburb 2050 made the top 10 list.

Lastly I would like to see the most popular amenities in my local area.

* Top amenities in my local area (postcode 2050):
```
top_local = db.mymaps.aggregate([{"$match": {"address.postcode": "2050", "amenity": {"$exists": 1}}},
                                 {"$group": {"_id": "$amenity", "count": {"$sum": 1}}},
                                 {"$sort": {"count": -1}}])
pp.pprint(list(top_local))
```
>[{u'_id': u'restaurant', u'count': 6},  
> {u'_id': u'cafe', u'count': 5},  
> {u'_id': u'pub', u'count': 3},  
> {u'_id': u'post_box', u'count': 2},  
> {u'_id': u'brothel', u'count': 1},  
> ...

### 5. Improvements <a name=improvements></a>
One of the issues that we encountered in data cleaning part of the project was that there were many inconsistent ways for users to list addresses. Some were well formatted with separate street, name, suburb, etc. However as we saw above sometimes there were streetnames which contained suburb, postcode information etc.

We can see that not all entries with suburbs have postcodes and vice versa.

```
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
```

>Number entries with a postcode:  3788  
>Number of entries with a suburb:  465  
>Number of entries with both postcode and suburbs:  433  
>
>List of postcodes and suburbs  
>[{u'_id': u'2016', u'suburbs': [u'Redfern']},  
> {u'_id': u'2037', u'suburbs': [u'Glebe']},  
> {u'_id': u'2040', u'suburbs': [u'Leichhardt']},  
> {u'_id': u'2027', u'suburbs': [u'Edgecliff']},  
> {u'_id': u'2089', u'suburbs': [u'Neutral Bay']},  
> {u'_id': u'2062', u'suburbs': [u'Cammeray']},  
> {u'_id': u'2060', u'suburbs': [u'North Sydney']},  
> {u'_id': u'2011', u'suburbs': [u'Kings Cross']},  
> {u'_id': u'2044', u'suburbs': [u'Tempe']},  
> {u'_id': u'2134', u'suburbs': [u'Burwood']},  
> {u'_id': u'2131', u'suburbs': [u'Ashfield']},  
> {u'_id': u'2133', u'suburbs': [u'Croydon Park']},  
> {u'_id': u'2048', u'suburbs': [u'Stanmore']},  
> {u'_id': u'2065', u'suburbs': [u'St Leonards', u'Crows Nest']},  
> ...

So here we can try and improve the data and make it more complete by using our entries in the database with both to go back and fill in the ones with missing data. Our process would involve:
* Using the entries with both postcode and suburbs to generate a list of both suburbs and postcodes
* Use this list to then update the entries with missing values

However, we can see that there may be a few issues here highlighted by our invetigative query:
* The list where we have both values is not comprehensive - in fact it is centered around the inner city
* The mapping is not 1:1 - we can see for 2065 we have 2 suburbs. And indeed we can see we would have the same problem the other way - i.e. Chippendale appears twice for 2000 and 2008. So using our current list we could only feasibly fill in a few.
    * However this could be recitified via a comprehensive data, for example the Auspost sells comprehensive postal code data which we would expect to be clean which we could use to improve our own database: https://auspost.com.au/business/marketing-and-communications/access-data-and-insights/address-data/postcode-data

However after some brief Googling, it also appears that mongo may also have a limitation that would prevent us from using one entry to update a different entry:
* "Bad news is that AFAIK you can't do it with a single update() call - mongo doesn't support referring to current object in update." https://stackoverflow.com/questions/2606657/update-field-with-another-fields-value-in-the-document
* "You cannot refer to the document itself in an update (yet)." https://stackoverflow.com/questions/3974985/update-mongodb-field-using-value-of-another-field?rq=1
Therefore this would need to be accomplomplished via python perhaps in the data cleaning phase.

### 6. Conclusion <a name="conclusion"></a>

Overall we can see that the custom area I selected for metropolitan Syney (mainly because of the better knowledge I have of the area rather than taking a whole state area) is in relatively good shape. The initial scan of problem tags appeared to be minimal.

However there did appear to some data entry issues, mainly inconsistency and data entry errors, in that data. This is what would be expected from a dataset which had been entered by humans. The steps I outlined above highlight rudimentary attempts to clean and standardise the data.

We also see when we run database queries that the map details are incomplete. If we wanted, we could cross reference it with a commercial database to improve it.
