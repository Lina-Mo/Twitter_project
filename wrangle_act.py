#!/usr/bin/env python
# coding: utf-8

# # Twitter Data Wrangle and Analyze Project

# ## Table of Contents
# - [Project Details](#details)
# - [Gathering Data](#gathering)
# - [Assessing Data](#assessing)
# - [Cleaning Data](#cleaning)
# - [Data Analysis](#analysing)

# <a id='details'></a>
# ## Project Details

# In this project I will wrangle and analyze the tweet archive of Twitter user @dog_rates, also image prediction file and additional data via Twitter API.
#     The goal is wrangle Twitter data to create interesting and trustworthy analyses and visualizations.

# **Tasks of this are as follows:**
# 
# - Data wrangling, which consists of:
#     - Gathering data
#     - Assessing data
#     - Cleaning data
# - Storing, analyzing, and visualizing your wrangled data
# - Reporting on
#     - 1) your data wrangling efforts and 
#     - 2) your data analyses and visualizations

# First we need to import tweepy package and libraries we need in this project.

# In[1]:


# Instal tweepy for gathering data via Twitter API
conda install -c conda-forge tweepy


# In[2]:


# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import tweepy
import re
import os
import json
import time
import warnings
import tweepy
from IPython.display import Image
import seaborn as sns; sns.set()
from tweepy import OAuthHandler
from timeit import default_timer as timer
from datetime import datetime as dt
get_ipython().run_line_magic('matplotlib', 'inline')


# <a id='gathering'></a>
# ## Gathering Data

# ### WeRageDogs Twitter Archive

# In[3]:


archive = pd.read_csv('twitter-archive-enhanced.csv')


# ### Image predictions

# In[4]:


#Downloading URL programatically 
url = "https://d17h27t6h515a5.cloudfront.net/topher/2017/August/599fd2ad_image-predictions/image-predictions.tsv"
response = requests.get(url)

with open('image-predictions.tsv', mode ='wb') as file:
    file.write(response.content)

#Reading TSV file
image_prediction = pd.read_csv('image-predictions.tsv', sep='\t' )


# ### Twitter API and JSON

# In[5]:


#import tweepy
from tweepy import OAuthHandler
import json
from timeit import default_timer as timer

# Query Twitter API for each tweet in the Twitter archive and save JSON in a text file
# These are hidden to comply with Twitter's API terms and conditions
consumer_key = ''
consumer_secret = ''
access_token = ''
access_secret = '' 
 


auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


# In[6]:


tweet_ids = archive.tweet_id.values
len(tweet_ids)


# In[7]:


# Query Twitter's API for JSON data for each tweet ID in the Twitter archive
count = 0
fails_dict = {}
start = timer()
# Save each tweet's returned JSON as a new line in a .txt file
with open('tweet_json.txt', 'w') as outfile:
    # This loop will likely take 20-30 minutes to run because of Twitter's rate limit
    for tweet_id in tweet_ids:
        count += 1
        print(str(count) + ": " + str(tweet_id))
        try:
            tweet = api.get_status(tweet_id, tweet_mode='extended')
            print("Success")
            json.dump(tweet._json, outfile)
            outfile.write('\n')
        except tweepy.TweepError as e:
            print("Fail")
            fails_dict[tweet_id] = e
            pass
end = timer()
print(end - start)
print(fails_dict)


# In[8]:


# saving required info to the dataframe
tweet_json = pd.DataFrame(columns=['tweet_id', 'retweet_count', 'favorite_count'])

with open('tweet_json.txt') as f:
    for line in f:
        status = json.loads(line)
        tweet_id = status['id_str']
        retweet_count = status['retweet_count']
        favorite_count = status['favorite_count']
        tweet_json = tweet_json.append(pd.DataFrame([[tweet_id, retweet_count, favorite_count]], 
                                       columns = ['tweet_id', 'retweet_count', 'favorite_count']))
tweet_json = tweet_json.reset_index(drop = True)
tweet_json.sample(10)


# <a id='assessing'></a>
# ## Assessing Data

# After gathering data, we are going to start with visual assessment and then use to programmatic assessment to identify data quality and tidiness issues.

# ### Visual assessment

# In[9]:


# Display the Twitter archive table
archive


# `archive` (Twitter archive) columns:
# 
# - **tweet_id**: the unique identifier for each tweet
# - **in_reply_to_status_id**: if the represented Tweet is a reply, this field will contain the integer representation of the original Tweet’s ID
# - **in_reply_to_user_id**: if the represented Tweet is a reply, this field will contain the integer representation of the original Tweet’s author ID
# - **timestamp**: time when this Tweet was created
# - **source**: utility used to post the Tweet, as an HTML-formatted string. e.g. Twitter for Android, Twitter for iPhone, Twitter Web Client
# - **text**: actual UTF-8 text of the status update
# - **retweeted_status_id**: if the represented Tweet is a retweet, this field will contain the integer representation of the original Tweet’s ID
# - **retweeted_status_user_id**: if the represented Tweet is a retweet, this field will contain the integer representation of the original Tweet’s author ID
# - **retweeted_status_timestamp**: time of retweet
# - **expanded_urls**: tweet URL
# - **rating_numerator**: numerator of the rating of a dog. Note: ratings almost always greater than 10
# - **rating_denominator**: denominator of the rating of a dog. Note: ratings almost always have a denominator of 10
# - **name**: name of the dog
# - **doggo**: one of the 4 dog "stage"
# - **floofer**: one of the 4 dog "stage"
# - **pupper**: one of the 4 dog "stage"
# - **puppo**: one of the 4 dog "stage"

# In[10]:


# Display the tweet image predictions table
image_prediction


# `image_prediction` (tweet image predictions) columns:
# 
# - **tweet_id**: the unique identifier for each tweet and it is the last part of the tweet URL after "status/"
# - **jpg_url**: image URL
# - **img_num**: image number
# - **p1**: algorithm's 1 prediction for the image in the tweet
# - **p1_conf**: how confident the algorithm is in its 1 prediction
# - **p1_dog**: whether or not the 1 prediction is a breed of dog
# - **p2**: algorithm's 2 prediction for the image in the tweet
# - **p2_conf**: how confident the algorithm is in its 2 prediction
# - **p2_dog**: whether or not the 2 prediction is a breed of dog
# - **p3**: algorithm's 3 prediction for the image in the tweet
# - **p3_conf**: how confident the algorithm is in its 3 prediction
# - **p3_dog**: whether or not the 3 prediction is a breed of dog

# In[11]:


# Display the weet status table
tweet_json


# `tweet_json` (tweet status) columns:
# 
# - **tweet_id**: the unique identifier for each tweet
# - **retweet_count**: number of times this Tweet has been retweeted
# - **favorite_count**: indicates approximately how many times this Tweet has been liked by Twitter users
# - **display_text_range**: an array of two unicode code point indices, identifying the inclusive start and exclusive end of the displayable content of the Tweet
# 

# ### Programmatic assessment

# In[12]:


archive.info()


# In[13]:


archive.describe()


# In[14]:


# Checking if dataframe have duplicated rows
archive.duplicated().sum()


# In[15]:


# Checking null values of the dataframe
archive.isnull().sum()


# In[16]:


# Checking retweet's total
len(archive[archive.retweeted_status_id.isnull() == False])


# In[17]:


# Review the dog names by sorthing by descending 
archive.name.value_counts().sort_index(ascending=False)


# In[18]:


# Checking if are both dog stages provided
len(archive[(archive.doggo != 'None') & (archive.floofer != 'None')])


# In[19]:


# Checking if are both dog stages provided
len(archive[(archive.doggo != 'None') & (archive.pupper != 'None')])


# In[20]:


# Checking if are both dog stages provided
len(archive[(archive.doggo != 'None') & (archive.puppo != 'None')])


# In[21]:


image_prediction.info()


# In[22]:


image_prediction.describe()


# In[23]:


# Checking if dataframe have duplicated rows
image_prediction.duplicated().sum()


# In[24]:


# Checking null values of the dataframe
image_prediction.isnull().sum()


# In[25]:


# Review the values of prediction 1
image_prediction['p1'].value_counts()


# In[26]:


# Review the values of prediction 2
image_prediction['p2'].value_counts()


# In[27]:


# Review the values of prediction 3
image_prediction['p3'].value_counts()


# In[28]:


tweet_json.info()


# In[29]:


tweet_json.describe()


# In[30]:


# Checking if dataframe have duplicated rows
tweet_json.tweet_id.duplicated().sum()


# In[31]:


# Checking null values of the dataframe
tweet_json.isnull().sum()


# In[32]:


# Review the retweet_count by sorthing by ascending 
tweet_json.sort_values(['retweet_count'], ascending=False)


# In[33]:


# Review the favorite_count by sorthing by ascending 
tweet_json.sort_values(['favorite_count'], ascending=False)


# In[34]:


# Detecting same colums in all dataframes
all_columns = pd.Series(list(archive) + list(image_prediction) + list(tweet_json))
all_columns[all_columns.duplicated()]


# ###### The following issues were found:

# #### Quality issues and solutions 
# ##### `Twitter archive` 
# - Dataset contains retweets entries and reply tweets entries columns.
#     - [1. Remove retweets and reply tweets entries](#retweets)
# - Timestamp column is 'object' data type not datetime.
#     - [2. Convert timestamp column data type from 'object'  to 'datetime64'](#datatime)
# - Dog name column contains not the dog names.
#     - [3. Eliminate not the dog names in the name column](#dogname)
# - The sources names in Twitter archive  are not clear.
#     - [4. Make a source name clear](#source)
# - Source column have ‘object’ data type instead of category.
#     - [5. Convert source column data type to category](#category)
# 
# ##### `Tweet image predictions` 
# - Prediction contains not the dog breed.
#     - [6. Eliminate not dog breed predictions](#bread)
# - Predictions have underscores instead of spaces.
#     - [7. Replace "_" from predictions](#predictions)
# 
# ##### `Twitter API` 
# - Tweet id column data type is an object not the sting.
#     - [8. Convert tweet_id column data type to sting](#datatype)
# 
# #### Tidiness
# - Column’s names p1, p2 and p3 in Tweet image prediction dataset don’t identify the columns content.
#     - [9. Change `image prediction` table 'p1', 'p2' and 'p3' columns names](#names)
# - The Twitter archive, Tweet image predictions and Twitter API datasets should be merged into a single one.
#     - [10. Merging `archive`, `imagine prediction` and `tweets` tables in one dataframe](#merging)
# - Dog stages have four separated columns and repeated stages.
#     - [11. Combine four columns in one dog_stage column](#dog_stage)
# 

# <a id='cleaning'></a>
# ## Cleaning Data

# In[35]:


#Copy dataframes Copies of the original pieces of data are made prior to cleaning.
archive_clean = archive.copy()
image_clean = image_prediction.copy()
tweets_clean = tweet_json.copy()


# ### Quality Issues

# ### `Archive_clean`

# <a id='retweets'></a>
# ##### 1. Remove retweets and reply tweets entries

# In[36]:


# detect the retweets count
archive_clean.retweeted_status_user_id.value_counts().sum()


# In[37]:


# detect the replies count
archive_clean.in_reply_to_status_id.value_counts().sum()


# #### Code

# In[38]:


# Remove retweets rows (count of 181)
archive_clean = archive_clean[archive_clean.retweeted_status_id.isna()]


# In[39]:


# droping retweet and reply tweets columns 
archive_clean = archive_clean.drop(['retweeted_status_id', 'retweeted_status_user_id', 'retweeted_status_timestamp'], axis = 1)


# In[40]:


# Remove reply columns
archive_clean.drop(['in_reply_to_status_id', 'in_reply_to_user_id'], axis=1, inplace = True)


# #### Test

# In[41]:


archive_clean.info()


# <a id='datatime'></a>
# ##### 2. Convert timestamp column data type from 'object'  to 'datetime64'

# #### Define
# 
# - Timestamp: Convert type from object to datetime.

# #### Code

# In[42]:


archive_clean.timestamp = pd.to_datetime(archive_clean.timestamp)


# #### Test

# In[43]:


archive_clean.info()


# <a id='dogname'></a>
# ##### 3. Eliminate not the dog names in the name column

# #### Define
# 
# - Name: Found and replace faulty dogs names

# #### Code

# In[44]:


# Sort non-names by detecting the lowercase words in the column name
archive_clean[archive_clean.name.str.islower() == True]['name'].unique()


# In[45]:


# Create the list of the detected non-name
not_names = ['such', 'a', 'quite', 'not', 'one', 'incredibly', 'very', 'my',
       'his', 'an', 'actually', 'just', 'getting', 'mad', 'this',
       'unacceptable', 'all', 'old', 'infuriating', 'the', 'by',
       'officially', 'life', 'light', 'space']


# In[46]:


# Replace the non-names to "None"
for n in not_names:
    archive_clean.name.replace(n, 'None', inplace = True)


# #### Test

# In[47]:


archive_clean.name.value_counts()


# In[48]:


archive_clean.name.unique()


# <a id='source'></a>
# ##### 4. Make a source name clear

# #### Define
# 
# - Source: Change source column values to more visible and clean

# #### Code

# In[101]:


# Mapping from full source name to specifing source name
df_merged.source = df_merged.source.replace('<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>', 'Twitter for iPhone')
df_merged.source = df_merged.source.replace('<a href="http://vine.co" rel="nofollow">Vine - Make a Scene</a>', 'Vine - Make a Scene')
df_merged.source = df_merged.source.replace('<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>', 'Twitter Web Client')
df_merged.source = df_merged.source.replace('<a href="https://about.twitter.com/products/tweetdeck" rel="nofollow">TweetDeck</a>', 'TweetDeck')


# #### Test

# In[102]:


# Review new source values
df_merged.source.value_counts()


# <a id='category'></a>
# ##### 5. Convert  source column data type to category

# #### Define
# 
# - Source: change source column datatype to category

# #### Code

# In[76]:


# Convert it into category type. 
archive_clean.source = archive_clean.source.astype('category')


# #### Test

# In[77]:


# Check if source datatype
archive_clean.info()


# ### `Image_prediction`

# <a id='bread'></a>
# ##### 6. Eliminate not dog breed predictions

# #### Define
# 
# - p1, p2, p3: Eliminate not the dog breed from p1, p2, p3 and delete p1_conf, p1_dog, p2_conf, p2_dog, p3_conf, p3_dog.

# In[78]:


image_prediction.sample(5)


# #### Code

# In[79]:


# Request the list of the dog prediction when p1_dog is False
not_image_dog = image_clean[image_clean['p1_dog'] == False]
not_image_dog.p1.unique()


# In[80]:


# Create the list of the detected not the dog breed
not_dog_breeds = ['box turtle', 'shopping cart', 'hen', 'desktop computer',
       'three-toed sloth', 'ox', 'guinea pig', 'coho', 'llama',
       'seat belt', 'snail', 'triceratops', 'swab', 'hay', 'hyena',
       'jigsaw puzzle', 'vacuum', 'teddy', 'porcupine', 'goose', 'hare',
       'electric fan', 'web site', 'ibex', 'fire engine', 'lorikeet',
       'toyshop', 'common iguana', 'frilled lizard', 'leatherback turtle',
       'hamster', 'Angora', 'Arctic fox', 'trombone', 'canoe',
       'king penguin', 'shopping basket', 'bearskin', 'bustard',
       'crash helmet', 'ski mask', 'shower curtain', 'jellyfish',
       'doormat', 'Arabian camel', 'lynx', 'hog', 'comic book', 'minivan',
       'seashore', 'cuirass', 'candle', 'weasel', 'Christmas stocking',
       'washbasin', 'car mirror', 'piggy bank', 'pot', 'boathouse',
       'mud turtle', 'platypus', 'ping-pong ball', 'sea urchin',
       'bow tie', 'window shade', "jack-o'-lantern", 'sorrel', 'peacock',
       'axolotl', 'wool', 'banana', 'wood rabbit', 'dhole', 'lacewing',
       'dingo', 'brown bear', 'scorpion', 'flamingo', 'microphone',
       'pitcher', 'African hunting dog', 'refrigerator', 'picket fence',
       'tub', 'zebra', 'hermit crab', 'swing', 'park bench',
       'feather boa', 'Loafer', 'stone wall', 'ice bear', 'prayer rug',
       'chimpanzee', 'china cabinet', 'bee eater', 'tennis ball',
       'carton', 'killer whale', 'ostrich', 'terrapin', 'Siamese cat',
       'gondola', 'microwave', 'starfish', 'sandbar', 'tusker',
       'motor scooter', 'ram', 'leaf beetle', 'wombat', 'water bottle',
       'suit', 'toilet seat', 'robin', 'slug', 'toilet tissue',
       'acorn squash', 'soccer ball', 'African crocodile', 'tick',
       'ocarina', 'street sign', 'bow', 'stove', 'paper towel', 'upright',
       'dough', 'bath towel', 'walking stick', 'bubble', 'book jacket',
       'rain barrel', 'black-footed ferret', 'guenon', 'water buffalo',
       'patio', 'cowboy hat', 'dogsled', 'maze', 'harp', 'panpipe',
       'cash machine', 'mailbox', 'wallaby', 'earthstar', 'pillow',
       'space heater', 'carousel', 'birdhouse', 'snorkel', 'bald eagle',
       'koala', 'cheetah', 'minibus', 'clog', 'dishwasher', 'white wolf',
       'sliding door', 'damselfly', 'cheeseburger', 'fiddler crab',
       'bannister', 'crane', 'snowmobile', 'badger', 'bighorn', 'geyser',
       'barrow', 'bison', 'ice lolly', 'sea lion', 'dining table',
       'beaver', 'grey fox', 'mousetrap', 'hippopotamus', 'hummingbird',
       'tailed frog', 'otter', 'Egyptian cat', 'four-poster', 'wild boar',
       'bathtub', 'agama', 'muzzle', 'hotdog', 'bib', 'espresso',
       'timber wolf', 'meerkat', 'nail', 'hammer', 'home theater', 'alp',
       'bonnet', 'handkerchief', 'hand blower', 'polecat', 'lakeside',
       'studio couch', 'cup', 'cliff', 'lawn mower', 'balloon',
       'sunglasses', 'rapeseed', 'traffic light', 'coil', 'binoculars',
       'paddle', 'tiger shark', 'sulphur-crested cockatoo',
       'American black bear', 'rotisserie', 'conch', 'skunk', 'bookshop',
       'radio telescope', 'cougar', 'African grey', 'coral reef', 'lion',
       'maillot', 'Madagascar cat', 'tabby', 'giant panda',
       'long-horned beetle', 'sundial', 'padlock', 'pool table', 'quilt',
       'beach wagon', 'remote control', 'bakery', 'pedestal', 'gas pump',
       'bookcase', 'shield', 'loupe', 'restaurant', 'prison',
       'school bus', 'cowboy boot', 'jersey', 'wooden spoon', 'leopard',
       'mortarboard', 'teapot', 'military uniform', 'washer',
       'coffee mug', 'fountain', 'pencil box', 'barbell', 'grille',
       'revolver', 'envelope', 'syringe', 'marmot', 'pole', 'laptop',
       'basketball', 'tricycle', 'convertible', 'limousine', 'orange']


# In[81]:


# Replace the not dog breed predictions by empty cell
for m in not_dog_breeds:
    image_clean.p1.replace(m, '', inplace = True)


# In[82]:


# Request the list of the dog prediction when p2_dog is False
not_image_dog = image_clean[image_clean['p2_dog'] == False]
not_image_dog.p2.unique()


# In[83]:


# Create the list of the detected not the dog breed
not_dog_breeds2 = ['mud turtle', 'shopping basket', 'cock', 'desk', 'otter', 'skunk',
       'barracouta', 'chain saw', 'slug', 'teddy', 'armadillo',
       'African hunting dog', 'doormat', 'swab', 'bath towel', 'drake',
       'ice bear', 'Christmas stocking', 'dhole', 'spotlight',
       'dishwasher', 'bighorn', 'tow truck', 'hummingbird', 'prayer rug',
       'frilled lizard', 'ox', 'hog', 'guinea pig', 'hen', 'wallaby',
       'cowboy boot', 'cornet', 'minivan', 'paddle', 'hamper', 'bow',
       'pelican', 'toaster', 'llama', 'knee pad', 'pillow', 'coral reef',
       'bison', 'waffle iron', 'tabby', 'bib', 'police van',
       'breastplate', 'pickup', 'lampshade', 'Siamese cat',
       'studio couch', 'toilet seat', 'hamster', 'seat belt', 'koala',
       'hair spray', 'tray', 'birdhouse', 'terrapin',
       'spotted salamander', 'tennis ball', 'porcupine', 'cardigan',
       'corn', 'European gallinule', 'indri', 'tailed frog',
       'beach wagon', 'siamang', 'orange', 'home theater', 'hare',
       'American black bear', 'sulphur butterfly', 'tarantula',
       'Persian cat', 'coral fungus', 'accordion', 'wood rabbit',
       'sunglasses', 'plow', 'rain barrel', 'bathtub', 'tiger', 'snail',
       'tick', 'water bottle', 'wig', 'platypus', 'ram', 'gorilla',
       'entertainment center', 'toucan', 'mask', 'shopping cart', 'crate',
       'grey whale', 'badger', 'Arabian camel', 'cockroach', 'lifeboat',
       'rotisserie', 'goldfish', 'stingray', 'warthog', 'bobsled',
       'rhinoceros beetle', 'beaver', 'brown bear', 'weasel', 'quill',
       'Arctic fox', 'ashcan', 'bow tie', 'bearskin', 'ice lolly',
       'American alligator', 'mosquito net', 'sea lion', 'nail',
       'black-footed ferret', 'promontory', 'sarong', 'space heater',
       'mailbox', 'bakery', 'sandal', 'leafhopper', 'barrel',
       'water buffalo', 'polecat', 'macaque', 'folding chair',
       'trench coat', 'Angora', 'junco', 'crib', 'snowmobile',
       'streetcar', 'window screen', 'bannister', 'hair slide', 'meerkat',
       'cannon', 'jaguar', 'hay', 'apron', 'cloak', 'radiator', 'muzzle',
       'feather boa', 'rifle', 'chimpanzee', 'loggerhead', 'torch',
       'spindle', 'triceratops', 'stove', 'dingo', 'oscilloscope',
       'common newt', 'hotdog', 'medicine chest', 'quail', 'horse cart',
       'four-poster', 'pier', 'red fox', 'assault rifle', 'mashed potato',
       'moped', 'hyena', 'seashore', 'tub', 'sports car', 'swing', 'mink',
       'neck brace', 'grey fox', 'mongoose', 'fur coat', 'spatula',
       'paper towel', 'shoji', 'toyshop', 'banded gecko', 'peacock',
       'crossword puzzle', 'tree frog', 'wombat', 'turnstile',
       'sleeping bag', 'quilt', 'Gila monster', 'giant panda',
       'handkerchief', 'sombrero', 'Indian elephant', 'coffee mug',
       'gibbon', 'carton', 'screw', 'minibus', 'hatchet', 'window shade',
       'lawn mower', 'washbasin', 'sock', 'prison', 'patio',
       'china cabinet', 'chain mail', 'breakwater', 'computer keyboard',
       'goose', 'lakeside', 'solar dish', 'table lamp', 'Windsor tie',
       'punching bag', 'comic book', 'sunglass', 'great white shark',
       'timber wolf', 'fountain', 'dugong', 'marmot', 'barbershop',
       'shovel', 'lesser panda', 'monitor', 'crutch', 'cash machine',
       'printer', 'volcano', 'wallet', 'laptop', 'bathing cap',
       'confectionery', 'dam', 'killer whale', 'canoe', 'Madagascar cat',
       'jean', 'boathouse', 'cliff', 'maillot', 'iPod',
       'hand-held computer', 'black widow', 'necklace', 'dining table',
       'binoculars', 'cradle', 'sea urchin', 'cougar', 'basketball',
       'lighter', 'saltshaker', 'harvester', 'television', 'envelope',
       'house finch', 'web site', 'palace', 'shower curtain', 'cab',
       'snorkel', 'jigsaw puzzle', 'sweatshirt', 'white wolf',
       'sliding door', 'academic gown', 'cowboy hat', 'can opener', 'cup',
       'rule', 'soccer ball', 'bucket', 'racket', 'menu', 'purse',
       'dumbbell', 'projectile', 'dock', 'oxygen mask', 'sandbar',
       'umbrella', 'shower cap', 'bagel']


# In[84]:


# Replace the not dog breed predictions by empty cell
for l in not_dog_breeds2:
    image_clean.p2.replace(l, '', inplace = True)


# In[85]:


# Request the list of the dog prediction when p3_dog is False
not_image_dog = image_clean[image_clean['p3_dog'] == False]
not_image_dog.p3.unique()


# In[86]:


# Create the list of the detected not the dog breed
not_dog_breeds3 = ['terrapin', 'fur coat', 'partridge', 'bookcase', 'great grey owl',
       'hamster', 'gar', 'dingo', 'power drill', 'acorn', 'teddy',
       'common iguana', 'wig', 'water buffalo', 'coyote', 'seat belt',
       'space heater', 'toilet tissue', 'Christmas stocking', 'badger',
       'hen', 'weasel', 'ski mask', 'lampshade', 'oscilloscope', 'ram',
       'jeep', 'ice bear', 'African grey', 'doormat', 'African chameleon',
       'muzzle', 'triceratops', 'Band Aid', 'wood rabbit', 'white wolf',
       'giant panda', 'French horn', 'bassinet', 'panpipe', 'crane',
       'mouse', 'titi', 'Angora', 'sandbar', 'balance beam',
       'black-footed ferret', 'bathtub', 'goldfish', 'llama', 'koala',
       'pillow', 'jersey', 'minibus', 'bulletproof vest', 'beach wagon',
       'plunger', 'paper towel', 'wing', 'bolete', 'ashcan', 'box turtle',
       'guinea pig', 'bison', 'racket', 'cardoon', 'window screen',
       'agama', 'common newt', 'car wheel', 'gorilla', 'bagel',
       'Egyptian cat', 'television', 'brown bear', 'leafhopper', 'menu',
       'wolf spider', 'bathing cap', 'stinkhorn', 'drumstick', 'mask',
       'shower curtain', 'plastic bag', 'swimming trunks',
       'prairie chicken', 'red wolf', 'snail', 'gibbon', 'black swan',
       'beacon', 'wool', 'cowboy boot', 'poncho', 'swing', 'Arctic fox',
       'bib', 'steam locomotive', 'fountain', 'chickadee', 'abaya',
       'bubble', 'chimpanzee', 'hammerhead', 'Siamese cat',
       'sea cucumber', 'seashore', 'nipple', 'moped', 'Arabian camel',
       'crayfish', 'wallaby', 'toilet seat', 'pajama', 'shovel', 'bucket',
       'Windsor tie', 'quill', 'Persian cat', 'European fire salamander',
       'three-toed sloth', 'swab', 'echidna', 'tennis ball', 'coral reef',
       'mink', 'screw', 'wreck', 'kimono', 'joystick', 'microwave',
       'loggerhead', 'French loaf', 'purse', 'greenhouse', 'broccoli',
       'shopping basket', 'macaque', 'squirrel monkey', 'green lizard',
       'parallel bars', 'cloak', 'chest', 'sundial', 'mosquito net',
       'bath towel', 'cuirass', 'zebra', 'lumbermill', 'wallet',
       'feather boa', 'electric fan', 'hippopotamus', 'ox', 'quilt',
       'assault rifle', 'axolotl', 'pot', 'toyshop', 'pizza',
       'scuba diver', 'beaver', 'cliff', 'loupe', 'wild boar', 'jaguar',
       'hog', 'polecat', 'lion', 'hand-held computer', 'washbasin',
       'whiptail', 'rock crab', 'hare', 'shoji', 'sombrero', 'bell cote',
       'rifle', 'goose', 'pickup', 'sunglasses', 'limousine', 'bow tie',
       'pretzel', 'marmot', 'ice lolly', 'vacuum', 'prison', 'shower cap',
       'sliding door', 'dugong', 'eel', 'binder', 'bullfrog',
       'soap dispenser', 'sea lion', 'carton', 'brass', 'mitten',
       'golfcart', 'cougar', 'warthog', 'umbrella', 'neck brace', 'cup',
       'book jacket', 'padlock', 'cab', 'chime', 'viaduct',
       'American black bear', 'tub', 'hand blower', 'king penguin',
       'rotisserie', 'bannister', 'passenger car', 'mongoose', 'dhole',
       'consomme', 'valley', 'park bench', 'mushroom', 'barrow',
       'parachute', 'desktop computer', 'snorkel', 'wok', 'space shuttle',
       'rain barrel', 'ballplayer', 'mountain tent', 'oxcart', 'buckeye',
       'sunglass', 'croquet ball', 'refrigerator', 'snow leopard',
       'tripod', 'rapeseed', 'tiger cat', 'notebook', 'maraca',
       'pool table', 'lakeside', 'theater curtain', 'pier', 'cheetah',
       'mousetrap', 'pop bottle', 'soccer ball', 'wombat',
       'rhinoceros beetle', 'paddlewheel', 'paintbrush', 'maze',
       'hatchet', 'chain', 'jigsaw puzzle', 'switch', 'barbell',
       'convertible', 'entertainment center', 'file', 'guillotine',
       'nail', 'bow', 'grocery store', 'boathouse', 'conch', 'grey fox',
       'shopping cart', 'meerkat', 'grand piano', 'envelope', 'screen',
       'coffeepot', 'printer', 'otter', 'restaurant', 'bonnet',
       'crossword puzzle', 'go-kart', 'orangutan', 'canoe',
       'barber chair', 'traffic light', 'ibex', 'can opener',
       'Indian elephant', 'spatula', 'banana']


# In[87]:


# Replace the not dog breed predictions by empty cell
for k in not_dog_breeds3:
    image_clean.p3.replace(k, '', inplace = True)


# In[88]:


# Drop columns
image_clean = image_clean.drop(['p1_conf', 'p1_dog', 'p2_conf', 'p2_dog', 'p3_conf', 'p3_dog'], axis=1)


# #### Test

# In[89]:


# Review the revised image_clean dataframe
image_clean.info()


# In[90]:


# Review revised dataframe
image_clean.head()


# >First I filtered predictions by False on p1_dog, p2_dog and p3_dog which showed that prediction is not dog breed. After I created the list of the not dog breeds and replaced with empty cells used replace function.

# <a id='predictions'></a>
# ##### 7. Replace "_" from predictions

# #### Define
# 
# - p1, p2, p3: replace _ from all preciction columns

# #### Code

# In[91]:


# Remove _ from the predictions
image_clean.p1= image_clean.p1.str.replace('_',' ')
image_clean.p2= image_clean.p2.str.replace('_',' ')
image_clean.p3= image_clean.p3.str.replace('_',' ')


# #### Test

# In[92]:


# Review revised columns
image_clean.head()


# ### `Tweet clean`

# In[93]:


tweets_clean.head()


# In[94]:


tweets_clean.info()


# <a id='datatype'></a>
# ##### 8. Convert tweet_id column data type to sting 

# #### Define
# 
# tweet_id: change data type from object to sting

# #### Code

# In[95]:


# Change the datatype
tweets_clean['tweet_id'] = tweets_clean['tweet_id'].astype('int64')


# #### Test

# In[96]:


# Cheking if datatype changed
tweets_clean.info()


# ## Tidiness Issues

# <a id='names'></a>
# ##### 9. Change `image prediction` table 'p1', 'p2' and 'p3' columns names

# #### Define
# - p1, p2, p3: change column names

# #### Code

# In[97]:


# Rename the columns
image_clean = image_clean.rename({'p1': '1st_prediction', 'p2': '2nd_prediction', 'p3': '3rd_prediction'}, axis=1)


# #### Test 

# In[98]:


# Review changes
image_clean.head()


# ### Merging the dataframes

# <a id='merging'></a>
# ##### 10. Merging `archive`, `imagine prediction` and `tweets` tables in one dataframe

# #### Define
# 
# Merge the 3 datasets (archive_clean, image_clean amd tweets_clean)

# #### Code

# In[99]:


# Merge archive_clean with image_clean
df_merged1 = pd.merge(archive_clean, image_clean, how = 'inner', on = ['tweet_id']).copy()

# Merge df_merged1 with tweets_clean
df_merged = pd.merge(df_merged1, tweets_clean, how = 'inner', on = ['tweet_id']).copy()


# #### Test

# In[100]:


# Review merged dataframe
df_merged.info()


# <a id='dog_stage'></a>
# ##### 11. Combine four columns in one dog_stage column

# #### Define
# 
# - Stages of dog: Create the "dog_stage" column by extracting stages from text columns and create "stage" columns by  combining columns "doggo", "floofer", "pupper" and "puppo". After comparing and cleaning the columns get one column with the dog stage

# #### Code

# In[49]:


# Extract the "doggo", "floofer", "pupper" and "puppo" from text column.
archive_clean['dog_stage'] = archive_clean['text'].str.extract('(puppo|pupper|floofer|doggo)')


# In[50]:


# Combine the "doggo", "floofer", "pupper" and "puppo" columns to one stage column.
archive_clean['stage'] = (archive_clean['doggo'] + archive_clean['floofer'] + archive_clean['pupper'] + archive_clean['puppo'])


# In[51]:


# Review new colums created
archive_clean[['dog_stage', 'stage', 'doggo', 'floofer', 'pupper', 'puppo']]


# In[52]:


# Droping "doggo", "floofer", "pupper" and "puppo" columns
archive_clean = archive_clean.drop(['doggo', 'floofer', 'pupper', 'puppo'], axis=1)


# In[53]:


# Review stage column values
archive_clean.stage.value_counts()


# In[54]:


# Changing values to correct ones
archive_clean['stage'].replace('NoneNoneNoneNone', 'None', inplace=True)
archive_clean['stage'].replace('NoneNonepupperNone', 'pupper', inplace=True)
archive_clean['stage'].replace('doggoNoneNoneNone', 'doggo', inplace=True)
archive_clean['stage'].replace('NoneNoneNonepuppo', 'puppo', inplace=True)
archive_clean['stage'].replace('doggoNonepupperNone', 'doggo/pupper', inplace=True)
archive_clean['stage'].replace('NoneflooferNoneNone', 'floofer', inplace=True)
archive_clean['stage'].replace('doggoflooferNoneNone', 'doggo/floofer', inplace=True)
archive_clean['stage'].replace('doggoNoneNonepuppo', 'doggo/puppo', inplace=True)


# In[55]:


# Cheking the new values
archive_clean.stage.value_counts()


# In[56]:


# Review dog_stage column values
archive_clean.dog_stage.value_counts()


# In[57]:


# Replace empty value in "stage_dog" to None
archive_clean['dog_stage'].replace(np.nan, 'None', inplace=True )


# In[58]:


# Compare "dog_stage" and "stage" columns
non_maching_stage = archive_clean[archive_clean['stage'] != archive_clean['dog_stage']]


# In[59]:


# Review non macthing rows
pd.set_option('max_colwidth', None)
pd.set_option('max_rows', None)
non_maching_stage[['tweet_id','text','dog_stage','stage']]


# In[60]:


# Replace "stage" column "None" values with "dog_stage" value
archive_clean['stage'].replace('None', non_maching_stage['dog_stage'], inplace=True )


# In[61]:


# Also, replacing "dog_stage" column "None" values with "stage" value
archive_clean['dog_stage'].replace('None', non_maching_stage['stage'], inplace=True )


# In[62]:


non_maching_stage2 = archive_clean[archive_clean['stage'] != archive_clean['dog_stage']]
pd.set_option('max_colwidth', None)
pd.set_option('max_rows', None)
non_maching_stage2[['tweet_id','text','dog_stage','stage']]


# In[63]:


# Change 'dog_stage' of line 172 from 'puppo' to 'doggo'
archive_clean.loc[172, 'dog_stage'] = 'doggo'


# In[64]:


# Replace 'stage' of 200 line to 'doggo'
archive_clean['stage'].replace('doggo/floofer', 'doggo', inplace=True )


# In[65]:


# Change 'stage' of line 191 from 'doggo/puppo' to 'puppo'
archive_clean.loc[191, 'stage'] = 'puppo'


# In[66]:


# Change 'stage' of line 460 from 'doggo/pupper' to 'doggo'
archive_clean.loc[460, 'stage'] = 'doggo'


# In[67]:


# Change 'stage' and 'dog_stage' of line 575 from 'doggo/pupper' to 'pupper'
archive_clean.loc[575, 'stage'] = 'pupper'
archive_clean.loc[575, 'dog_stage'] = 'pupper'


# In[68]:


# Change 'stage' of line 956 from 'doggo/pupper' to 'doggo'
archive_clean.loc[956, 'stage'] = 'doggo'


# In[69]:


# Change 'dog_stage' of line 531,565,889,1063 and 1113 change to 'doggo/pupper'
archive_clean.loc[531, 'dog_stage'] = 'doggo/pupper'
archive_clean.loc[565, 'dog_stage'] = 'doggo/pupper'
archive_clean.loc[889, 'dog_stage'] = 'doggo/pupper'
archive_clean.loc[1063, 'dog_stage'] = 'doggo/pupper'
archive_clean.loc[1113, 'dog_stage'] = 'doggo/pupper'


# In[70]:


# Review the image of tweet id 785639753186217984
Image(url = 'https://pbs.twimg.com/media/CucnLmcXEAAxVwC?format=jpg&name=900x900')


# > From the picture we can see that the tweet are not related to the dog rating.

# In[71]:


# delete the row 705 as it is not the dog image
archive_clean = archive_clean[~archive_clean['tweet_id'].isin(['785639753186217984'])]
archive_clean = pd.DataFrame(archive_clean)


# #### Test

# In[72]:


# Runing again the not macthing "dog_stage" and "stage" columns for check
non_maching_stage3 = archive_clean[archive_clean['stage'] != archive_clean['dog_stage']]
pd.set_option('max_colwidth', None)
pd.set_option('max_rows', None)
non_maching_stage3[['tweet_id','text','dog_stage','stage']]


# In[73]:


# Drop "stage" column as it is the same as "dog_stage"
archive_clean = archive_clean.drop(['stage'], axis=1)


# In[74]:


# Review unique values of "dog_stage"
archive_clean['dog_stage'].unique()


# In[75]:


# Review info
archive_clean.info()


# ### Store New Dataframe

# In[103]:


#Save the gathered, assessed, and cleaned master dataset to a CSV file.
# save the wrangled dataframe to a csv file.
df_merged.to_csv('twitter_archive_master.csv', encoding = 'utf-8')

# making copy of the dataframe as well
df_merged_clean = df_merged.copy()


# <a id='analysing'></a>
# ## Data Analysis

# ##### Analysis questions
# - [1.1 Which are the most popular dog stages by count and most favorite?](#dogstagess)
# - [1.2 Which are the most popular tweet sources by retweets?](#sourceretweets)
# - [1.3 Which are the most predicted dog breed of the tweets?](#predicted)
# - [1.4 Which are the most likeable predicted dog breeds ?](#likeable)

# In[104]:


# #Explore new dataset
pd.set_option('max_rows', None)
df_merged_clean.describe()


# <a id='dogstagess'></a>
# ###  **1.1 Which are the most popular dog stages by count and most favorite?**

# In[105]:


# Receiving the tweet count of each dog state
dog_stage_proc = df_merged_clean[df_merged_clean['dog_stage'] != 'None']['dog_stage'].value_counts()
dog_stage_proc


# In[106]:


# Creating the new dataframe with number of tweets, total likes and average likes 
top_stages = df_merged_clean.groupby('dog_stage').favorite_count.agg(['count', 'sum'])
top_stages['average'] = top_stages['sum'] / top_stages['count']
df_stages = top_stages.sort_values(by=['sum'], ascending=False).head(7)

#convert dictionary to a dataframe
df = pd.DataFrame(df_stages)
df.index.name = 'Dog Stages'
df.reset_index(inplace=True)
df.rename(columns={'count': 'Number of tweets', 'sum': 'Total likes received', 'average': 'Average likes'}, inplace=True)
df_new = df.loc[df['Dog Stages'] != 'None']
df_new_stages = pd.DataFrame(df_new)
df_new_stages


# In[107]:


# Create pie plot
df_new_stages.groupby(['Dog Stages']).sum().plot(kind='pie', y='Number of tweets', explode = (0, 0.1, 0, 0, 0), shadow = True, startangle=50,
figsize=(7,7), autopct='%1.1f%%')

#set pie title
plt.title("Proportion of Dog Stages by Counting Tweets\n", fontsize = 16)
plt.show()


# > As you can see in this pie bar visualization on the left the 67.4 % of tweets containing a "pupper” stage. The "Doggo" stage was the next most frequent stage at 21.1%. "Floofer" , "puppo" and combined dog stage “doggo/pupper”  all of them leading to a combined 11.6% of the total stages. So, when the stages are provided, the most popular dog stage is “pupper”.

# In[108]:


# Create pie plot
df_new_stages.groupby(['Dog Stages']).sum().plot(kind='pie', y='Average likes', shadow = True, startangle=80,
figsize=(12,7), autopct='%1.1f%%', explode = (0, 0, 0, 0, 0.1))

#set pie title
plt.title("Proportion of the Dog Stages by Average Likes\n", fontsize = 16)
plt.show()


# > As you can see in this pie bar visualization on the left,  the most likeable dog stage is “puppo” with 29.6 % of average likes per tweet. The "Doggo" stage was the next most likeable stage with 23.6% and “Doggo/pupper” combined stages followed with 21.9%. "Floofer" and "puppo" together have a total 24.9% proportion. 

# <a id='sourceretweets'></a>
# ###  **1.2 Which are the most popular tweet sources by retweets?**

# In[109]:


# Receiving tweet count of all sources
df_merged_clean['source'].value_counts()


# In[110]:


#Creating new dataset for sources with number of tweets, total retweet received and Average retweet
tweet_sources = df_merged_clean.groupby('source').retweet_count.agg(['count', 'sum'])
tweet_sources['average'] = tweet_sources['sum'] / tweet_sources['count']
df_tweet_sources = tweet_sources.sort_values(by=['sum'], ascending=False).head(10)

#convert dictionary to a dataframe
df_tweet_sources = pd.DataFrame(df_tweet_sources)
df_tweet_sources.index.name = 'Tweet Source'
df_tweet_sources.reset_index(inplace=True)
df_tweet_sources.rename(columns={'count': 'Number of tweets', 'sum': 'Total retweet received', 'average': 'Average retweet by tweet'}, inplace=True)
df_tweet_sources.head(3)


# > The created table shows that Twitter for iPhone source is the most popular tweet source with the 1948 number of tweets and has the highest average retweet count with 2399.93.  The "Twitter Web Client" source has 28 numbers of tweets and the “TweetDeck” source has 10 number of tweets. 

# <a id='predicted'></a>
# ###  **1.3 Which are most predicted dog breed of the tweets?**

# In[111]:


# Create predictions 1 table with counts and average sums
top_breed_p1 = df_merged_clean.groupby('1st_prediction').favorite_count.agg(['count', 'sum'])
top_breed_p1 = pd.DataFrame(top_breed_p1)
top_breed_p1 = top_breed_p1.sort_values(by=['count'], ascending=False)
top_breed_p1.index.name = 'Prediction'
top_breed_p1.head()


# In[112]:


# Create predictions 2 table with counts and average sums
top_breed_p2 = df_merged_clean.groupby('2nd_prediction').favorite_count.agg(['count', 'sum'])
top_breed_p2 = pd.DataFrame(top_breed_p1)
top_breed_p2 = top_breed_p1.sort_values(by=['count'], ascending=False)
top_breed_p2.index.name = 'Prediction'
top_breed_p2


# In[113]:


# Create predictions 3 table with counts and average sums
top_breed_p3 = df_merged_clean.groupby('3rd_prediction').favorite_count.agg(['count', 'sum'])
top_breed_p3 = pd.DataFrame(top_breed_p1)
top_breed_p3 = top_breed_p1.sort_values(by=['count'], ascending=False)
top_breed_p3.index.name = 'Prediction'
top_breed_p3.reset_index(inplace=True)
top_breed_p3


# In[114]:


# merge top_breed_p1 with top_breed_p2
df_merged_p = pd.merge(top_breed_p1, top_breed_p2, how = 'inner', on = ['Prediction']).copy()

# merge df_merged_p with top_breed_p3
df_merged_pp = pd.merge(df_merged_p, top_breed_p3, how = 'inner', on = ['Prediction']).copy()

# drop repeated the columns
df_merged_pp.drop(['count_x', 'sum_x', 'count_y', 'sum_y'], axis=1, inplace = True)
df_merged_pp.head()


# In[115]:


# Create new prediction dataframe except empty cells and add total likes received, average likes per tweet columns
df_merged_pp = df_merged_pp.loc[df_merged_pp['Prediction'] != '']
df_merged_pp['Average likes per tweet'] = df_merged_pp['sum'] / df_merged_pp['count']
df_merged_pp.rename(columns={'count': 'Number of tweets', 'sum': 'Total likes received'}, inplace=True)
df_merged_pp = df_merged_pp.sort_values(by=['Number of tweets'], ascending=False).head(10)
df_merged_m = pd.DataFrame(df_merged_pp)


# In[116]:


# Review new dataframe
df_merged_m.head(10)


# > After combining three image predictions in one column the count value, the total likes count and the average likes per tweet value was calculated.

# In[117]:


# Set the size
plt.figure(figsize=[20,10])
sns.set(style="white", rc={"lines.linewidth": 3})

# Use bar plot to display Dog breeds by tweet count of occurance
bar_plot_count = sns.barplot(data=df_merged_m.sort_values(by='Number of tweets', ascending=False), x='Prediction', y='Number of tweets', palette='pastel')
for p in bar_plot_count.patches:
    bar_plot_count.annotate(format(p.get_height(),',.0f'), (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 10), textcoords = 'offset points')

#set title and axis labels
plt.xlabel('Dog breed predictions', fontsize = 16)
plt.ylabel('Tweet count', fontsize = 16)
plt.title('Top 10 Most Popular Dog Breed Prediction by Tweet Count', fontsize = 16)
plt.show()


# > From the bar plot we can see that Golden retriever dog breed prediction is most popular in the dataset and has appeared 139 times. Second place taken by Labrador retriever appeared 93 times. After two retrievers breeds follow Pembroke (88), Chihuahua (79),  Pug (54) and others.

# <a id='likeable'></a>
# ###  **1.4 Which are the most likeable predicted dog breeds ?**

# In[118]:


# Set the size
plt.figure(figsize=[20,10])
sns.set(style="white", rc={"lines.linewidth": 3})

# Use bar plot to display Dog breeds by average likes per tweet
bar_plot_likes = sns.barplot(data=df_merged_m.sort_values(by='Average likes per tweet', ascending=False), x='Prediction', y='Average likes per tweet', palette='colorblind')
for r in bar_plot_likes.patches:
    bar_plot_likes.annotate(format(r.get_height(),',.2f'), (r.get_x() + r.get_width() / 2., r.get_height()), ha = 'center', va = 'center', xytext = (0, 10), textcoords = 'offset points')

#set title and axis labels
plt.xlabel('Dog breed predictions', fontsize = 16)
plt.ylabel('Average likes', fontsize = 16)
plt.title('Top 10 Most Likeble Dog breeds by Average Likes per Tweet', fontsize = 16)
plt.show()


# > The bar plot above shows that the Samoyed dogs images received more likes (12,058.64 avg. likes) than the rest of the dog breeds based on average likes by count of tweets. Second and third places taken by Golden and Labrador retriever with 11,136 and 10,460 average likes.  After them follow Pembroke, Chow, Chihuahua, Malamute  and others.
# 

# ### Sources

# - Python for Data Analysis - Wes McKinney - 2012;
# - Jupyter Notebooks https://jupyter.org/
# - Pandas Documentation https://pandas.pydata.org/
# - Kaggle guide https://www.kaggle.com/learn/pandas 
# - And below links:
#     - Pandas DataFrame Plot - Pie Chart:https://kontext.tech/column/code-snippets/402/pandas-dataframe-plot-pie-chart
#     - How to add percentages on top of bars in seaborn?: https://stackoverflow.com/questions/31749448/how-to-add-percentages-on-top-of-bars-in-seaborn
#     - General principles for using color in plots: https://seaborn.pydata.org/tutorial/color_palettes.html
