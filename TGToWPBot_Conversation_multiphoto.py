# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 16:56:20 2022
TG bot conversation flow reference:
    https://github.com/python-telegram-bot/python-telegram-bot/blob/v13.x/examples/conversationbot.py
    https://github.com/python-telegram-bot/python-telegram-bot/blob/v13.x/examples/conversationbot2.py

"""
import os 

TGbot_token = open(os.path.join(pw_folder,"TG_bot_token.txt")).read()
WPaccess_token = open(os.path.join(pw_folder,"WPaccess_token.txt")).read()
ImgurClientID = open(os.path.join(pw_folder,"ImgurClientID.txt")).read()
group_id = open(os.path.join(pw_folder,"BroadcastGroupID.txt")).read()

from typing import Dict

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    Filters,
)

CHOOSING, TYPING_REPLY, TYPING_CHOICE, UPLOAD_PHOTO, PUBLISH = range(5)

reply_keyboard = [
    ["The deal", "Photo"],
    ["Usual price", "Store Location"],
    ["Additional Info","Done"],
    ["Cancel"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

additional_reply_keyboard = [
    ["Description"],
    ["Tags"],
    ["Category"],
    ["Back"]
]

additional_markup = ReplyKeyboardMarkup(additional_reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} : {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

def PostBlog(update:Update,context:CallbackContext):
    import requests
    import urllib 
    access_token_depercent = urllib.parse.unquote(WPaccess_token)
    WPSite = "mindyourmoneyvancouver.wordpress.com"
    url = f"https://public-api.wordpress.com/rest/v1.1/sites/{WPSite}/posts/new"
    
    user_data = context.user_data
    title =  user_data.get("The deal", user_data.get("PhotoCaption", None))
    publishtime = user_data.get("PublishTime")
    categories = user_data.get("Category","Good Deals")
    tags = user_data.get("Tags",None)
    
    img_html = ""
    # handle upload of multiple photos
    if user_data.get("Photos",None):
        for (index,img_url, photo_caption) in user_data['Photos']:
            img_html += f"<p> <img alt='{photo_caption}' src='{img_url}'> <br/> {photo_caption if photo_caption else '' } </p>"
    
    upload_data = {k:v for k,v in user_data.items() if not k.startswith("Photo")}
    
    body = facts_to_str(upload_data)
    
    combined_text =  body + img_html
    print(combined_text)
    
    payload={'title': title,
    'content': combined_text,
    'status': 'pending',
     'sticky':True,
     'categories':categories,
     'tags':tags,
     'date':publishtime
     }
    
    files = []
    
    headers = {
      'Authorization': 'Bearer '+access_token_depercent 
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        print(response.text)
        blogpost_link =response.json()['URL']
    except:
        print(response.text)
        blogpost_link = None
    
    return blogpost_link



def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text(
        "Hi! What amazing deal did you find today? "
        "Tell me more about it and I can share to more people!",
        reply_markup=markup,
    )
    #print(context.user_data) #empty at the begining

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data["choice"] = text
    update.message.reply_text(f"{text}? Yes, I would love to hear about that!")

    return TYPING_REPLY


def custom_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for a description of a custom category."""
    update.message.reply_text(
        'What additional info would you like to add?',
        reply_markup=additional_markup,
    )

    return TYPING_CHOICE


def received_information(update: Update, context: CallbackContext) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    author = update.message.from_user.first_name
    user_data["SubmittedBy"] = author
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]
    
    upload_data = {k:v for k,v in user_data.items() if not k.startswith("Photo")}

    update.message.reply_text(
        "Nice! " #So this is the summary of the deal:
        f"{facts_to_str(upload_data)} \n\n"
        "You can tell me more, or edit previous provided information",
        reply_markup=markup,
    )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    import datetime
    
    user_data = context.user_data
    print(user_data)
    if "choice" in user_data:
        del user_data["choice"]
    
    # sanity check before posting to Wordpress
    if "The deal" not in user_data: # missing title
        update.message.reply_text("Missing a title for the post ... finding photo caption to fill in title ...")
        if "PhotoCaption" not in user_data:
            update.message.reply_text("Photo caption is also missing ..."
                                      "Please provide either The deal or photo caption",
                                      reply_markup=markup)
            return CHOOSING #exit back to main menu to provide more info before posting
    
    upload_data = {k:v for k,v in user_data.items() if not k.startswith("PhotoCaption") and not k.startswith("PhotoLink")}
    
    
    
    photo_count =  len(user_data.get('Photos',[]))
    photo_count_statement = f"Plus {photo_count} photo(s)" if photo_count > 0 else ""
    
    current_timestamp = datetime.datetime.now()
    delayed_timestamp = current_timestamp + datetime.timedelta(hours=1) #hr_delay = 1
    publish_time = delayed_timestamp.astimezone().replace(microsecond=0).isoformat() #format is "2022-10-16T20:32:25-07:00"
    user_data['PublishTime'] = publish_time

    update.message.reply_text(
        f"Summary of facts about the deal: {facts_to_str(upload_data)} \n {photo_count_statement} \n\n"
        "Cool! We have everything to write a post!",
        reply_markup=ReplyKeyboardRemove()
    )
    
    try:
        blogpost_link = PostBlog(update,context)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Done! Posted to: {blogpost_link} with 1 hour delay. (Group members have more time to act on the deal if there's limited quantity left.)")
        context.bot.send_message(chat_id=group_id, text=f" {user_data['SubmittedBy']} just shared a deal {facts_to_str(upload_data)}")
        
        user_data.clear() # if not clear, then next post will have img/title from previous post when info is not provided
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Posting not successful. Will have to try again")
        
        

    return ConversationHandler.END

def photo_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for photo."""
    update.message.reply_text(
            "Do you have a photo to share? You can also write caption after selecting photo and before clicking send")

    return UPLOAD_PHOTO


def PostImage(update:Update,context:CallbackContext):
    import requests
    import base64
    url = "https://api.imgur.com/3/image"

    photo_fileid = update.message.photo[-1].get_file()
    photo_caption = update.message.caption
    context.user_data["PhotoCaption"] = update.message.caption
    
    byte_obj = photo_fileid.download_as_bytearray()
    base64_encoded = base64.b64encode(byte_obj).decode()
        
    headers = {'Authorization': 'Client-ID '+ImgurClientID}
    payload = { 'image': base64_encoded,
               'type': 'base64',
               'title':photo_caption
               }
        
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.headers)
    
    if response.json()['success'] == True: 
        print(response.text)
        
        file_link = response.json()['data']['link']
    
        img_html = f"<img alt='{photo_caption}' src='{file_link}'>"
        print(img_html)
        context.user_data["PhotoLink"] = file_link
        
        # handle multiple photo upload
        if not context.user_data.get("Photos"):
            context.user_data['Photos'] = [(1,file_link,photo_caption)]
        else:
            photo_uploaded_count = len(context.user_data['Photos'])
            context.user_data['Photos'].append((photo_uploaded_count+1,file_link,photo_caption))
            
        context.bot.send_message(chat_id=update.effective_chat.id, text="Image well received !")
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                  parse_mode = 'markdown',
                                 
                                 text = f"image of caption \n {photo_caption} \n is uploaded to this url:{file_link}. \n"
                                 "Anything else to add to the post?",

                                 reply_markup=markup)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text="Upload failed. May have hitted rate limit",
                                 reply_markup=markup,)
        
    return CHOOSING


def Cancel(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    update.message.reply_text(
        f"Come back when you're ready to share! \n",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def Backtomain(update: Update, context: CallbackContext) -> int:
    """Back to Regular Choice Menu"""
    update.message.reply_text(
        "Going back to main menu ... ",
        reply_markup=markup,
    )

    return CHOOSING


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TGbot_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(The deal|Usual price|Store Location)$'), regular_choice
                ),
                MessageHandler(Filters.regex('^Additional Info$'), custom_choice),
                MessageHandler(Filters.regex('^Photo$'), photo_choice),
                MessageHandler(Filters.regex('^Cancel$'), Cancel),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')| Filters.regex('^Back$')), 
                    regular_choice
                ),
                MessageHandler(
                    Filters.text & Filters.regex('^Back$'), 
                    Backtomain
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    received_information,
                )
            ],
            UPLOAD_PHOTO: [
                MessageHandler(
                    Filters.photo,PostImage)
                    
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()