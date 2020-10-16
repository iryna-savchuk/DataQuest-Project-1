#!/usr/bin/env python
# coding: utf-8

# # Project 1: Profitable App Profiles for the App Store and Google Play Markets
# 
# The aim in this project is to find mobile app profiles that are profitable for the App Store and Google Play markets.  Only apps that are free to download and install are considered in this project, hence the main source of revenue consists of in-app ads. This means that the revenue for any given app is mostly influenced by the number of users that use our app. 
# 
# Our goal for this project is to analyze data to understand what kinds of apps are likely to attract more users.

# ## Opening and exploring the data.

# We will consider 2 datasets:
# * A data set containing data about approximately 10,000 Android apps from Google Play; the data was collected in August 2018. You can download the data set directly from [this link](https://dq-content.s3.amazonaws.com/350/googleplaystore.csv).
# * A data set containing data about approximately 7,000 iOS apps from the App Store; the data was collected in July 2017. You can download the data set directly from [this link](https://dq-content.s3.amazonaws.com/350/AppleStore.csv).

# In[1]:


from csv import reader

### The Google Play data set ###
opened_file = open('googleplaystore.csv', encoding="utf8")
read_file = reader(opened_file)
android = list(read_file)
android_header = android[0]
android = android[1:]

### The App Store data set ###
opened_file = open('AppleStore.csv', encoding="utf8")
read_file = reader(opened_file)
ios = list(read_file)
ios_header = ios[0]
ios = ios[1:]


# To make it easier to explore the two data sets, we'll first write a function named explore_data() that we can use repeatedly to explore rows in a more readable way. 

# In[2]:


### The functiona to explore Data ###
def explore_data(dataset, start, end, rows_and_columns=False):
    dataset_slice = dataset[start:end]    
    for row in dataset_slice:
        print(row)
        print('\n') # adds a empty line after each row

    if rows_and_columns:
        print('Number of rows:', len(dataset))
        print('Number of columns:', len(dataset[0]))


# In[3]:


### Exploring Android Data ###
print(android_header)
print('\n')
explore_data(android, 0, 3, rows_and_columns=True)


# In[4]:


### Exploring App Store Data ###
print(ios_header)
print('\n')
explore_data(ios, 0, 3, rows_and_columns=True)


# ## Data Cleaning.

# Before beginning our analysis, we need to make sure the data we analyze is accurate, otherwise the results of our analysis will be wrong. This means that we need to:
# 
# * Detect inaccurate data, and correct or remove it.
# * Detect duplicate data, and remove the duplicates.
# 
# ### Removing incorrect row.
# The Google Play data set has a dedicated [discussion section](https://www.kaggle.com/lava18/google-play-store-apps/discussion), and we can see that [one of the discussions](https://www.kaggle.com/lava18/google-play-store-apps/discussion/66015) describes an error for a certain row. Let's examine this raw: 

# In[5]:


explore_data(android, 10472, 10473)


# In[6]:


del android[10472]


# In[7]:


explore_data(android, 0, 0, rows_and_columns=True)


# ### Getting rid of duplicate rows.
# 
# If you explore the Google Play data set long enough or look at the [discussions](https://www.kaggle.com/lava18/google-play-store-apps/discussion) section, you'll notice some apps have duplicate entries. For instance, Instagram has four entries:

# In[8]:


for app in android:
    name = app[0]
    if name == "Instagram":
        print(app)


# Let's count the total number of duplicates:

# In[9]:


duplicate_apps = [] #list for storing the names of duplicate apps
unique_apps = [] #list for storing the names of unique apps

for app in android: #looping through the Google Play data set
    name = app[0]
    if name in unique_apps:
        duplicate_apps.append(name)
    else: 
        unique_apps.append(name)
        
print('Number of duplicate apps: ', len(duplicate_apps))
print('\n')
print('Examples of duplicate apps: ', duplicate_apps[:10])
print('\n')
print('Expected length: ', len(android) - len(duplicate_apps))


# We don't want to count certain apps more than once when we analyze data, so we need to remove the duplicate entries and keep only one entry per app. One thing we could do is remove the duplicate rows randomly, but we could probably find a better way.
# 
# If you examine the rows we printed for the Instagram app, the main difference happens on the fourth position of each row, which corresponds to the number of reviews. The different numbers show the data was collected at different times.
# 
# We can use this information to build a criterion for removing the duplicates. The higher the number of reviews, the more recent the data should be. Rather than removing duplicates randomly, we'll only keep the row with the highest number of reviews and remove the other entries for any given app.
# 
# To remove the duplicates, we will:
# * Create a dictionary, where each dictionary key is a unique app name and the corresponding dictionary value is the highest number of reviews of that app.
# * Use the information stored in the dictionary and create a new data set, which will have only one entry per app (and for each app, we'll only select the entry with the highest number of reviews).

# In[10]:


reviews_max = {}

for app in android: #looping through the Google Play data set
    name = app[0]
    n_reviews = float(app[3])
    if (name in reviews_max) and (reviews_max[name] < n_reviews):
        reviews_max[name] = n_reviews
    if name not in reviews_max:
        reviews_max[name] = n_reviews
        
print('Length of the obtained dictionary', len(reviews_max))
print('Record for Instagram app', reviews_max["Instagram"])


# In[11]:


android_clean = [] # list to store our new cleaned data set
already_added = [] # list to just store app names

for app in android: #looping through the Google Play data set
    name = app[0]
    n_reviews = float(app[3])
    if (n_reviews==reviews_max[name]) and (name not in already_added):
        android_clean.append(app)
        already_added.append(name)
        
# exploring the result
explore_data(android_clean, 0, 2, rows_and_columns=True)


# ### Removing non-English apps.
# Each character we use in a string has a corresponding number associated with it. We can get the corresponding number of each character using the ord() built-in function.
# 
# The numbers corresponding to the characters we commonly use in an English text are all in the range 0 to 127, according to the ASCII (American Standard Code for Information Interchange) system. Based on this number range, we can build a function that detects whether a character belongs to the set of common English characters or not. 

# In[12]:


# Function to check whether the string input is in English
def is_english(input_str):
    for character in input_str:
        if ord(character)>127:
            return False
    return True

print('Instagram >> ', is_english('Instagram'))
print('爱奇艺PPS -《欢乐颂2》电视剧热播 >> ', is_english('爱奇艺PPS -《欢乐颂2》电视剧热播'))
print('Docs To Go™ Free Office Suite >> ', is_english('Docs To Go™ Free Office Suite'))
print('Instachat 😜 >> ', is_english('Instachat 😜'))


# As can be seen above, emojis and characters like ™ fall outside the ASCII range and have corresponding numbers over 127. If we're going to use the function we've created, we'll lose useful data since many English apps will be incorrectly labeled as non-English. 
# 
# To minimize the impact of data loss, we'll only remove an app if its name has more than three characters with corresponding numbers falling outside the ASCII range.

# In[13]:


# Updated Function 
# to check whether the string input is in English

def is_english(input_str):
    non_english = 0
    
    for character in input_str:
        if ord(character)>127:
            non_english += 1
            
    if non_english>3:
        return False
    else:
        return True

print('Instagram >> ', is_english('Instagram'))
print('爱奇艺PPS -《欢乐颂2》电视剧热播 >> ', is_english('爱奇艺PPS -《欢乐颂2》电视剧热播'))
print('Docs To Go™ Free Office Suite >> ', is_english('Docs To Go™ Free Office Suite'))
print('Instachat 😜 >> ', is_english('Instachat 😜'))


# In[14]:


# Filtering out non-English apps from Google Play dataset
android_eng = [] # list to store our new cleaned data set

for app in android_clean:  
    name = app[0]
    if is_english(name):
        android_eng.append(app)
        
# exploring the result
explore_data(android_eng, 0, 0, rows_and_columns=True)


# In[15]:


# Filtering out non-English apps from App Store dataset
ios_eng = [] # list to store our new cleaned data set

for app in ios:  
    name = app[1]
    if is_english(name):
        ios_eng.append(app)
        
# exploring the result
explore_data(ios_eng, 0, 0, rows_and_columns=True)


# Thus, as we can see, that we're left with 9614 Android apps and 6183 iOS apps.

# ## Isolating the Free Apps

# As we mentioned in the introduction, we only build apps that are free to download and install, and our main source of revenue consists of in-app ads. 
# 
# Our data sets contain both free and non-free apps; we'll need to isolate only the free apps for our analysis.

# In[16]:


android_final = []
ios_final = []

# Isolating free Android apps 
for app in android_eng:  
    price = app[7]
    if price=='0':
        android_final.append(app)
        
# Isolating free IOS apps 
for app in ios_eng:  
    price = app[4]
    if price=='0.0':
        ios_final.append(app) 
        
# exploring the results
print('Free Android apps:')
explore_data(android_final, 0, 0, rows_and_columns=True)
print('\n')
print('Free IOS apps:')
explore_data(ios_final, 0, 0, rows_and_columns=True)


# ## Identifiying Most Common Apps by Genre

# As we mentioned in the introduction, our aim is to determine the kinds of apps that are likely to attract more users because our revenue is highly influenced by the number of people using our apps.
# 
# Let's begin the analysis by getting a sense of what are the most common genres for each market. For this, we'll need to build frequency tables for a few columns in our data sets.

# In[17]:


def freq_table(dataset, index): 
    
    frequencies = {}
    total = 0
    
    for row in dataset:
        total += 1
        val = row[index]
        if val in frequencies:
            frequencies[val] += 1
        else:
            frequencies[val] = 1
            
    table_percentages = {}
    
    for key in frequencies:
        percentage = (frequencies[key] / total) * 100
        table_percentages[key] = percentage 
    
    return table_percentages

def display_table(dataset, index):
    table = freq_table(dataset, index)
    table_display = []
    for key in table:
        key_val_as_tuple = (table[key], key)
        table_display.append(key_val_as_tuple)

    table_sorted = sorted(table_display, reverse = True)
    for entry in table_sorted:
        print(entry[1], ':', entry[0])


# We start by examining the frequency table for the prime_genre column of the App Store data set.

# In[18]:


# Displaying genre percenetage frequency table 
# for IOS data set
# by prime_genre column
display_table(ios_final, 11)


# We can see that among the free English apps, more than a half (58.16%) are games. Entertainment apps are close to 8%, followed by photo and video apps, which are close to 5%. Only 3.66% of the apps are designed for education, followed by social networking apps which amount for 3.29% of the apps in our data set.
# 
# Let's continue by examining the Genres and Category columns of the Google Play data set (two columns which seem to be related).

# In[19]:


# Displaying genre percenetage frequency table 
# for Android data set
# by Category column
display_table(android_final, 1)


# The landscape seems significantly different on Google Play: there are not that many apps designed for fun, and it seems that a good number of apps are designed for practical purposes (family, tools, business, lifestyle, productivity, etc.).
# 
# Let's have a look at frequency percentages for one more column in Android Data set:

# In[20]:


# Displaying genre percenetage frequency table 
# for Android data set
# by Genres column
display_table(android_final, 9)


# 
# The difference between the Genres and the Category columns is not crystal clear, but one thing we can notice is that the Genres column is much more granular (it has more categories). We're only looking for the bigger picture at the moment, so we'll only work with the Category column moving forward.
# 
# Up to this point, we found that the App Store is dominated by apps designed for fun, while Google Play shows a more balanced landscape of both practical and for-fun apps. Now we'd like to get an idea about the kind of apps that have most users.

# ## Identifying the Most Popular Apps by Genre on the App Store.

# One way to find out what genres are the most popular (have the most users) is to calculate the average number of installs for each app genre. 
# 
# For the Google Play data set, we can find this information in the Installs column, but this information is missing for the App Store data set. As a workaround, we'll take the total number of user ratings as a proxy, which we can find in the rating_count_tot app.
# 
# 
# Below, we calculate the average number of user ratings per app genre on the App Store:

# In[21]:


genres_ios = freq_table(ios_final, 11)

for genre in genres_ios:
    total = 0
    len_genre = 0
    
    for app in ios_final:
        genre_app = app[11]
        if genre_app == genre:            
            n_ratings = float(app[5])
            total += n_ratings
            len_genre += 1
            
    avg_n_ratings = total / len_genre
    print(genre, ':', avg_n_ratings)


# On average, navigation apps have the highest number of user reviews, after those go Reference, Social Networking and Weather.

# In[22]:


for app in ios_final:
    if app[-5] == 'Navigation':
        print(app[1], ':', app[5]) # print name and number of ratings


# In[23]:


for app in ios_final:
    if app[-5] == 'Reference':
        print(app[1], ':', app[5]) # print name and number of ratings


# In[24]:


for app in ios_final:
    if app[-5] == 'Social Networking':
        print(app[1], ':', app[5]) # print name and number of ratings


# In[25]:


for app in ios_final:
    if app[-5] == 'Weather':
        print(app[1], ':', app[5]) # print name and number of ratings


# One thing we could do is take another popular book and turn it into an app where we could add different features besides the raw version of the book. This might include daily quotes from the book, an audio version of the book, quizzes about the book, etc. On top of that, we could also embed a dictionary within the app, so users don't need to exit our app to look up words in an external app.
# 
# This idea seems to fit well with the fact that the App Store is dominated by for-fun apps. This suggests the market might be a bit saturated with for-fun apps, which means a practical app might have more of a chance to stand out among the huge number of apps on the App Store.

# ## Identifying the Most Popular Apps by Genre on the Google Play.

# We have data about the number of installs for the Google Play market, so we should be able to get a clearer picture about genre popularity. However, the install numbers don't seem precise enough — we can see that most values are open-ended (100+, 1,000+, 5,000+, etc.):

# In[26]:


display_table(android_final, 5) # the Installs column


# One problem with this data is that is not precise. For instance, we don't know whether an app with 100,000+ installs has 100,000 installs, 200,000, or 350,000. However, we don't need very precise data for our purposes — we only want to get an idea which app genres attract the most users, and we don't need perfect precision with respect to the number of users.
# 
# We're going to leave the numbers as they are, which means that we'll consider that an app with 100,000+ installs has 100,000 installs, and an app with 1,000,000+ installs has 1,000,000 installs, and so on.
# 
# To perform computations, however, we'll need to convert each install number to float — this means that we need to remove the commas and the plus characters, otherwise the conversion will fail and raise an error. We'll do this directly in the loop below, where we also compute the average number of installs for each genre (category).

# In[27]:


categories_android = freq_table(android_final, 1)

for category in categories_android:
    total = 0
    len_category = 0
    for app in android_final:
        category_app = app[1]
        if category_app == category:            
            n_installs = app[5]
            n_installs = n_installs.replace(',', '')
            n_installs = n_installs.replace('+', '')
            total += float(n_installs)
            len_category += 1
    avg_n_installs = total / len_category
    print(category, ':', avg_n_installs)


# From the results above, it can be ssen that, on average, communication apps have the most installs: 38,456,119. Let's have more details regarding this:

# In[28]:


for app in android_final:
    if app[1] == 'COMMUNICATION' and (app[5] == '1,000,000,000+'
                                      or app[5] == '500,000,000+'
                                      or app[5] == '100,000,000+'):
        print(app[0], ':', app[5])


# This number is heavily skewed up by a few apps that have over one billion installs (WhatsApp, Facebook Messenger, Skype, Google Chrome, Gmail, and Hangouts), and a few others with over 100 and 500 million installs.
# 
# If we removed all the communication apps that have over 100 million installs, the average would be reduced roughly ten times:

# In[29]:


under_100_m = []

for app in android_final:
    n_installs = app[5]
    n_installs = n_installs.replace(',', '')
    n_installs = n_installs.replace('+', '')
    if (app[1] == 'COMMUNICATION') and (float(n_installs) < 100000000):
        under_100_m.append(float(n_installs))
        
sum(under_100_m) / len(under_100_m)


# We see the same pattern for the video players category, which is the runner-up with 24,727,872 installs. The market is dominated by apps like Youtube, Google Play Movies & TV, or MX Player. The pattern is repeated for social apps (where we have giants like Facebook, Instagram, Google+, etc.), photography apps (Google Photos and other popular photo editors), or productivity apps (Microsoft Word, Dropbox, Google Calendar, Evernote, etc.).
# 
# Again, the main concern is that these app genres might seem more popular than they really are. Moreover, these niches seem to be dominated by a few giants who are hard to compete against.
# 
# The game genre seems pretty popular, but previously we found out this part of the market seems a bit saturated, so we'd like to come up with a different app recommendation if possible.
# 
# The books and reference genre looks fairly popular as well, with an average number of installs of 8,767,811. It's interesting to explore this in more depth, since we found this genre has some potential to work well on the App Store, and our aim is to recommend an app genre that shows potential for being profitable on both the App Store and Google Play.
# 
# Let's take a look at some of the apps from this genre and their number of installs:

# In[30]:


for app in android_final:
    if app[1] == 'BOOKS_AND_REFERENCE':
        print(app[0], ':', app[5])


# The book and reference genre includes a variety of apps: software for processing and reading ebooks, various collections of libraries, dictionaries, tutorials on programming or languages, etc. It seems there's still a small number of extremely popular apps that skew the average:

# In[31]:


for app in android_final:
    if app[1] == 'BOOKS_AND_REFERENCE' and (app[5] == '1,000,000,000+'
                                            or app[5] == '500,000,000+'
                                            or app[5] == '100,000,000+'):
        print(app[0], ':', app[5])


# However, it looks like there are only a few very popular apps, so this market still shows potential. Let's try to get some app ideas based on the kind of apps that are somewhere in the middle in terms of popularity (between 1,000,000 and 100,000,000 downloads):

# In[32]:


for app in android_final:
    if app[1] == 'BOOKS_AND_REFERENCE' and (app[5] == '1,000,000+'
                                            or app[5] == '5,000,000+'
                                            or app[5] == '10,000,000+'
                                            or app[5] == '50,000,000+'):
        print(app[0], ':', app[5])


# 
# This niche seems to be dominated by software for processing and reading ebooks, as well as various collections of libraries and dictionaries, so it's probably not a good idea to build similar apps since there'll be some significant competition.
# 
# We also notice there are quite a few apps built around the book Quran, which suggests that building an app around a popular book can be profitable. It seems that taking a popular book (perhaps a more recent book) and turning it into an app could be profitable for both the Google Play and the App Store markets.
# 
# However, it looks like the market is already full of libraries, so we need to add some special features besides the raw version of the book. This might include daily quotes from the book, an audio version of the book, quizzes on the book, a forum where people can discuss the book, etc.

# ## Conclusions.
# 
# In this project, we analyzed data about the App Store and Google Play mobile apps with the goal of recommending an app profile that can be profitable for both markets.
# 
# We concluded that taking a popular book (perhaps a more recent book) and turning it into an app could be profitable for both the Google Play and the App Store markets. The markets are already full of libraries, so we need to add some special features besides the raw version of the book. This might include daily quotes from the book, an audio version of the book, quizzes on the book, a forum where people can discuss the book, etc.
