#!/usr/bin/env python
# coding: utf-8

# ### Importing Libraries

# In[438]:


import pandas as pd
import numpy as np
from itertools import combinations, chain
from prettytable import PrettyTable


# ### Asking user to enter minimum support and minimum confidence in percentage

# In[439]:


min_support = int(input("Please Enter Minimum Support in %: "))
min_confidence = int(input("Please Enter Minimum Confidence in %: "))


# ### Menu for user to select a databse
# 

# In[440]:


menu = {}
menu["1"] = "Amazon"
menu["2"] = "Best Buy"
menu["3"] = "Nike"
menu["4"] = "K-mart"
menu["5"] = "Custom"
 
options=menu.keys()
while True:  
    for entry in options: 
        print(entry, menu[entry])
    selected_option=input("What Database you want select?[1-5] ") 
    if selected_option=="1": 
        dataset="amazon.csv" 
        transactions="amazon_transactions.csv"
        print("Amazon's Dataset is selected.")
        break
    elif selected_option=="2":
        dataset="best_buy.csv" 
        transactions="best_buy_transactions.csv"
        print("Best Buy's Dataset is selected.")
        break
    elif selected_option=="3":
        dataset="nike.csv" 
        transactions="nike_transactions.csv"
        print("Nike's Dataset is selected.")
        break
    elif selected_option=="4":
        dataset="kmart.csv" 
        transactions="kmart_transactions.csv"
        print("K-mart's Dataset is selected.")
        break
    elif selected_option=="5":
        dataset="custom_database.csv" 
        transactions="custom_transactions.csv"
        print("Custom Dataset is selected.")
        break
    
    elif selected_option !="":
      selected_option = input("\n Not Valid Choice Try again") 


# ### Reading CSV file and printing its data in table form using pandas based on user's selcted databas

# In[441]:


#table for items
data_items = pd.read_csv(dataset,names=["item#", "items"]) #source:https://www.w3schools.com/python/pandas/pandas_csv.asp
items=[] #list of items
for item in data_items["items"]:
    items.append(item)  
#print(items)


# In[442]:


#table of transactions
transaction_items = pd.read_csv(transactions,names=["Transaction ID","Transaction"])
#transaction_items.head(20)
print(transaction_items)

# ### creating list of transactions from the database

# In[443]:


records = [] #list of transactions with list of items in each transactions
for  trans in transaction_items["Transaction"]:
    transactions =  trans.split(", ")
    records.append(transactions)
#print((records))


# ### Creating initial C1 

# In[444]:


C={} #candidates for frequent items
L = {} # frequent items
itemset_size=1 #iteset with one items
non_frequent_items= {itemset_size: []} # item that not frequent items 
C.update({itemset_size: [ [f] for f in items]}) 
# source1:https://www.geeksforgeeks.org/python-ways-to-create-a-dictionary-of-lists/
#source2: https://www.geeksforgeeks.org/python-dictionary-update-method/
#print(C)


# ### Defining functions

# In[449]:


"""
This function takes two argument one is 'itemset' which is the set of items with
different number of items in it.
Another argument is 'record' which is the list of transactions
This function count the frequency itemset in all transactions
for e.g. if an item pen occurs 10 times in list of all transction then it will return 10.
e.g.2 if items: pen and notebook occurs 3 time together in list of all transaction it will return 3.
"""
def count_occurances(itemset,records):
    count = 0
    for i in range(len(records)):
        if set(itemset).issubset(set(records[i])): #if an item or an itemset is subset of a transaction 
                                                   #(pen is subset of [pen,notebook, milk]) it increments the counter
            count+=1
          
    return count

"""
This function sorts and joins two set of itemset list of items based on 
number of items in a itemset.

For example if a list og item [pen,notebook, milk] and item set should have 2 item
then it will return
[pen, notebook] for first iteration
[pen,notebook] for second iteration
[notebook, milk] for thir iteraton in the join_two_itemsets function

for the same lsit of items if item set should have 3 items the it will return
then it will return [pen,notebook, milk] in the join_two_itemsets function


"""
def join_two_itemsets(it1,it2,items):
    it1.sort(key=lambda x: items.index(x)) 
    #source: https://www.geeksforgeeks.org/python-sort-list-of-list-by-specified-index/
    it2.sort(key=lambda x: items.index(x))
    for i in range(len(it1)-1):
        if it1[i] != it2[i]: #if itemset in it1 and it2 are different then return empty list 
            return []
    if items.index(it1[-1])< items.index(it2[-1]): 
        return it1 + [it2[-1]]#joining two item sets
    return []

"""
This function takes two arguments first is 'set_of_itemsets' which is the set of itemsets
having different number of items in each set of items.

Second argument is 'items' which is the list of items in the database
This finction will return the list of list of item list based on number of items in the item set
from list of items.

For example if the the list of item is [pen,notebook, milk, cookie] and item set should have 2 items
then it will return
[[pen,notebook],[pen,milk],[pen,cookie],[notenook,milk],[notebook,cookie],[milk,cookie]]

For the same list of items if the itemset should have 3 items then it will return
[[pen,notebook,milk],[pen,notebook,cookie],[notebook,mil,cookie]]

It will only return if lenght of the list is greater than 0.
"""
def join_set_itemsets(set_of_itemsets,items):
    C=[]
    for i in range(len(set_of_itemsets)):
        for j in range(i+1,len(set_of_itemsets)):
            it_out= join_two_itemsets(set_of_itemsets[i],set_of_itemsets[j],items)
            if len(it_out) >0 :
                C.append(it_out)
            
    return C
"""
This function have 4 arguments first itemsets which is the list of items in list of items in
canditates list.

Second argument is 'record' wich is the list of all transactions.

Third argument is 'min_support' which is the minimum support provided by the user in percentage.

Fourth argument is 'prev_non_frequent_items' which dictionary of 
non frequent items with the key is the number of item in item sets.

This function will return list of frequent items based on the number of items in the item set,
list of support count for each itemset and dictionary of non frequent items.

For eg. for 1 item in itemset if pen occurs 10 times, notebook occurs 7 times 
and milk occurs 2 times in lists of all transaction and it min_support is 30% 
then the support_count is 10, 7 and 2 respectively,
support will be 50%,35% and 10%.
The list of frequent items will be [pen, notebook] because its support their 
more than 30% and these are freqent items.
The list of non frequent items will be [milk] because it support is less than 30%.
"""   
def get_frequent_items(itemsets,records, min_support, prev_non_frequent_items):
    L = [] #list of frequent items
    supp_count = []# list of support count
    new_non_frequent_items =[] # list of non frequent items.
    k= len(prev_non_frequent_items.keys())
    for i in range(len(itemsets)):
        non_frequent_items_before = False
        if k>0:
            for  item in prev_non_frequent_items[k]:
                if set(item).issubset(set(itemsets[i])):
                    non_frequent_items_before = True
                    break
        if not non_frequent_items_before:
            count = count_occurances(itemsets[i], records)
            if (100*(count/20)) >= min_support:
                L.append(itemsets[i])
                supp_count.append(count)
        else:
            new_non_frequent_items.append(itemsets[i])
   
    return L, supp_count, new_non_frequent_items

"""
This function have two arguments first is 'list_of_itemsets' which is 
list of itemsets.

Second argument is 'supp_count' which is the list pf suppurt count for eact item sets 
in the list of itemsets.

this function will print item set, frequency of the itemset and the suppor for the iutem set
"""
def print_table(list_of_itemsets,supp_count):
    t = PrettyTable(['Itemset', 'Frequency', 'Support (%)'])
    for k in range(len(list_of_itemsets)):
        t.add_row([list_of_itemsets[k] , supp_count[k], round(((supp_count[k]/20)*100),2)])
        #source: https://stackoverflow.com/questions/9535954/printing-lists-as-tabular-data
    print(t)
    
"""
This function will return all the combinations of itemsets
"""
def create_set_combinations(s):
    return list(chain.from_iterable(combinations(s,r) for r in range(1, len(s)+1)))

"""
This function will generates rule and return them.
"""
def generate_rules(X,X_S,S,conf,supp_x):
    rule = ""
    rule += "Freq. Itemset: {}\n".format(X)
    rule += "      Rule: {} -> {} \n".format(list(S),list(X_S))
    rule += "      Confidence: {}% ".format(conf)
    rule += "      Support: {}% \n\n".format(supp_x)
    rule+= "----------------------------------------------------------------------------------------------------------\n"
    return rule


# ### Creating initial L1 and list of support Count

# In[450]:


support_count_L ={} #dictionary of support count
freq_items, sup, new_non_frequent_items = get_frequent_items(C[itemset_size], records, min_support, non_frequent_items)
non_frequent_items.update({itemset_size:new_non_frequent_items}) #updating dictionary of non-frequent items
L.update({itemset_size:freq_items})# updaTING THE dictionary of frequent items
support_count_L.update({itemset_size:sup})#updating the dictionary of support counts
#print(L)
#print(support_count_L)


# ### Printing table of items, frequency and support
# 

# In[451]:


print("Table C1: ")
print_table(C[1],[count_occurances(it,records) for it in C[1]]) #printing table for C1
print("Table L1 : ")
print_table(L[1],support_count_L[1]) #printing table for L1


# ### Generetaing Candidates and L for different different k.

# In[453]:


k = itemset_size + 1 #number of items in itemsets
convergence = False # flag that will determine if there are still itemsets with k items in it

while not convergence:
    C.update({k: join_set_itemsets(L[k-1],items)})
    print("Table C{}".format(k))
    print_table(C[k],[count_occurances(it,records) for it in C[k]])
    f, supp, new_non_frequent_items = get_frequent_items(C[k], records, min_support, non_frequent_items)
    non_frequent_items.update({k: new_non_frequent_items})
    L.update({k: f})
    support_count_L.update({k: supp})
    if len(L[k]) == 0:
        convergence = True
    print("Table L{}".format(k))
    print_table(L[k],support_count_L[k])
    k+=1


# ### Generating the rules

# In[455]:


association_rules="" #string of accociation rules
for i in range(1,len(L)):
    for j in range(len(L[i])):
        sets_list = create_set_combinations(set(L[i][j]))
        sets_list.pop()#removing the last item from the set list pf 
        for z in sets_list:
            S=set(z) 
            X= set(L[i][j])
            X_S = set(X-S) #X-S
            count_x = count_occurances(X, records)
            supp_x = round(((count_x/20)*100),2)
            count_x_s = count_occurances(X_S, records)
            supp_x_s = count_occurances(X_S, records)
            count_s = count_occurances(S,records)
            supp_s = round(((count_s/20)*100),2)
            
            conf =  round(((supp_x/supp_s)*100),2)
            if conf > min_confidence and supp_x > min_support:
                association_rules+= generate_rules(X,X_S,S,conf,supp_x)
            
            
                                    
                                     
                                     


# In[456]:


print(association_rules)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




