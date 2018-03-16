# EncryptedMessenger

This is a small encrypted peer to peer messenger application.   


I've been frustrated with a lot of the messaging software I've tried over the past few years.   
Some spam you with ads, others rely on featureless, decade old technology and some just plain don't work with recurring bugs
that are left unfixed for years. (Looking at you Discord, with the repeating message bug...).  
Also you have to send all your data to some random company and assume they won't peek at your conversations for profit.  


This software aims to solve these problem but realistically it's far from being there yet. It's mostly been a learning tool 
for me so I wouldn't rely on the encryption to keep your messages safe. Tho' I suppose since it's peer to peer the risk is 
mitigated, and the encryption, even if flawed in some unknown way, should keep them safe from automatic data mining by
whatever pipes you send them through.

# Docs

The docs are available here: https://encrypted-messenger-docs.herokuapp.com/

# Quickstart

Just clone the directory and run:  
`python ui/app.py`

You'll have to figure out the dependencies yourself because I haven't gone around to documenting them.  
They should all be available through pip except PyQt5 where you need version 5.5 which is hard to find.  
I'm in the process of updating it to work with the most recent version but it takes time.  
