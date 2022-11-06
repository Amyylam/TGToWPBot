# TGToWPBot
A Telegram conversation bot that can gather info and photos posted by Telegram and post to a Wordpress.com blog

# Demo Video
[![Watch the video on Youtube](https://img.youtube.com/vi/0uMy196k3xE/0.jpg )](https://youtu.be/0uMy196k3xE)


# Copyright
------------
All rights reserved for my codes written to intergrate a few APIs and conversation flow design of the Telegram bot. 
Copyright of Telegram-python-bot Python package, Wordpress API and Imgur API that I called in the Python script belong to their original authors.

This piece of code is an integration of a few REST APIs from different SaaS platforms to faciliate posting from Telegram to WordPress. During my research online and brief search in WordPress.com plug-ins, I feel there's no tool that can do exactly what I wish to do (post from Telegram to WordPress, not the other way round; I can see quite a lot of plug-ins are doing posting from WordPress to Telegram), except one that is commercial and paid SaaS solution (which I could not proof whether it can really do TG-WP posting in both directions as I didn't pay). Therefore, I would like to preserve the right to commercialize this tool, if it's really a unique integration solution upon further research. 

# Development Log
## Planned features
1. Build a Telegram chatbot to gather descriptions and photos of grocery deals from a particular Telegram group, with friendly conversation flow and menu with buttons to select from
2. Let the TG bot broadcast grocery deal summary gathered from a particular user to the specific TG group members
3. Post the grocery deal summary as a blog article to my Wordpress.com blog, eith via API or PostByEmail functionality of Wordpress.com
4. Post the uploaded image to a free photo-hosting site instead of Wordpress.com
5. Extra feature: Blog post translation e.g. English to Traditional Chinese using pretrained NLP models loaded via SpaCy 


## Development Timeline
- Oct 7, Fri 6pm -- Borrowed book "Natural Language Processing with Python and Spacy" after browsering Chapter 11 "Deploying Your Own Chatbot"
- Oct 8, Sat 10am-- Idea of a Telegram to WordPress.com Posting ChatBot for my initiated blog MindYourMoneyVancouver, which is a blog on grocery deals and budgeting tips that has gathered sharings from a group of UBC students
- Oct 8, Sat 11am-- Drew a conversation flow design chart as blueprint to guide practical bot development step-by-step
- Oct 8, Sat 3pm -- Googled how to WordPress API to achieve goal, read a bunch of materials on what is OAuth 1.0 vs 2.0 to use WP API, very complicated API endpoints and multiple API versions existed
- Oct 8, Sat 4pm -- resort to try PostByEmail functionality of WordPress.com, see if can achieve all form-filling requirements and post photos via mobile device email app
-  Oct 8, Sat 5-9pm -- Googled ways to send email from a bot with Python libraries, successfully incorporated Yagmail to PostByEmail to Wordpress. Researched Wordpress.com shortcodes that could be used via PostByEmail, e.g. delay by 1hr, set categories and set tags.
- Oct 9, Sun 12n -- Start Telegram Chatbot development. Reading a bunch of docs back and forth between Telegram API doc versus Python-Telegram-Bot API docs. Conversation contexts, User data and Group ID that were not illustrated from Python-Telegram-Bot docs actually will have to understand from Telegram API doc.
- Oct 9, Sun 1-8pm - Look for ways to download user-shared photo from Telegram chat then upload to photo-hosting site, without having to save to local computer in the middle, as the Chatbot service run should not rely on the presence of my PC. Googled what is base64 (binary-to-text) encoding that were used in email transfer and HTTP transfer and how to incorporate with TG bot Python script.
- Oct 10, Mon, Thanksgiving holiday, 12-4pm - Picked Imgur as photo-hosting middle layer as it offered least restrictions and had public API available to call. Tried to test API via Postman template as Imgur site suggested. But could not work even with OAuth 2.0 as instructed. API 3.0 actually not implemented fully (found out on Github issues page) and API 2.0 despite officially claimed deprecated, provided more details on rate limits then API 3.0 docs. Workaround -> use anonymous upload API endpoint and gave up on authenticated upload endpoint. 
- Oct 10 holiday, 4-7pm - Multiple testings showed WP will strip away any html tags from email body (successfully sent img html tags but showed up blank on WP blog), thus cannot embed image uploaded to another site. Had to go back to use WordPress API instead.
- Oct 11 holiday, 11 pm - succeeded posted to WordPress blog via API, but img html tag did not render successfully. Debugged. HTTP transfer header was the root cause. Images or big files need to specify Content-Type and/or Boundary when transfer. But Boundary is very tricky to calculate. StackOverflow post pointed out not setting Content-Type is actually the best, as automatic detection of Content-Type will work instead. Succeeded posted images after removing relevant header.
- Oct 12 Tue, 7-11 pm - Imgur successfully integrated with Telegram chatbot ! TG group users can now post text and images by initiating conversation with bot individually, but not in the group.
- Oct 16 Sun, 11-6pm - Debugged single image upload issue. Added multi-photo upload support.
- Oct 16 Sun, 6-9pm - clean up code and hide access tokens.
- Oct 16 Sun, 10pm - Started User-Acceptance-Testing by informing TG group users and invite them to test out the chatbot. Added publishing time delay by 1 hr, mimicking shortcode functionality provided by WP PostByEmail but not available in WP API.
- Oct 18 Tue, 10pm-12am - Added "Cancel" and "Back" button within chatbot conservation flow upon user reflections on how to quit conversation. Explored broadcasting function of user-submitted deal summary to a TG group. Actually required Group Owner to grant Admin permission to bot. 
- Oct 19 Wed night - Used Replit to host Python script on cloud ahead of personal out-of-town trip. The service shoud be able to run continuously. But Replit had server uptime limitations as well.
- Nov 5 Sat, 9am-1pm - No extra issues found over last 2 weeks. Made demo video for this github repo, added copyright statement.
- Nov 6 Sun, 11am-2pm - Uploaded script to this repo. Added development log. 
