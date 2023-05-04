from telegram.ext import CommandHandler, MessageHandler, filters, Application
import os
import random
import argparse
from hmt_scraper import get_wartenummer
import pickle
import datetime

parser = argparse.ArgumentParser(description='parameters for the HMT-Bot')
parser.add_argument('--fetch_interval', type=int, default=10,
                    help='set the time interval in which to scrape the website')
parser.add_argument('--data_location',
                    type=str, default='/home/emil/HMT-Fetch-Bot/data.pkl',
                    help='set the full path to the data.pkl file')
args = parser.parse_args()


answers = ['What are you doing?', 'Do you need some /help?', '#human',
           u'\uE333', 'Please stop it...', 'You lost!?',
           'Come on.', 'It is not funny']


async def welcome(update, context):
    await update.message.reply_text('Hey, I am the HMT-Wartenummer-Fetch-Bot. '
            'I basically tell you when your wartenummer is due for use. '
            'In order to do that, you just have to give me your wartenummer '
            'via the \'save\' command, for example: /save 5')


async def help(update, context):
    # gives an overview over the commands
    await update.message.reply_text("Sure, these are the commands you can use:"
            '\n/start: starts bot and displays introduction.'
            '\n/help: displays this help text.'
            '\n/start x: activates the notification of wartenummer x.'
            '\n/stop: stops the notifications.'
            '\n/wartenummer: fetches the current wartenummer')


async def send_alert(context):
    wartenummer = get_wartenummer()
    with open(args.data_location, 'rb') as handle:
        data = pickle.load(handle)
    for key, value in data.items():
        if wartenummer.strip() == value:
            await context.bot.send_message(chat_id=key,
                                           text='Hurry, its your turn on the '
                                           'waiting list!')


async def print_wartenummer(update, context):
    wartenummer = get_wartenummer()
    await update.message.reply_text(f'The current wartenummer is: {wartenummer}')


async def save_user_wartenummer(update, context):
    # saves the given Wartenummer with the chat-id
    wartenummer = update.message.text[5:].strip()
    # checks for invalid input and informs the User about that
    allowed_symbols = [str(i) for i in range(201)] + ['-']
    if wartenummer not in allowed_symbols:
        await update.message.reply_text('Something was wrong with your input, '
                                        'please try again!')
        return

    # read data
    with open(args.data_location, 'rb') as handle:
        data = pickle.load(handle)
    chat_id = get_chat_id(update, context)
    data[chat_id] = wartenummer
    # write data
    with open(args.data_location, 'wb') as handle:
        pickle.dump(data, handle)
    # write statistics
    now = str(datetime.datetime.now())
    output = f'\n{chat_id}, {wartenummer}, {now}'
    with open('stat.csv', 'a') as file:
        file.write(output)
    # send message
    await update.message.reply_text("Ok, your wartenummer has been saved. "
                                    + "I will send you a message when it is "
                                    + "due :)")


async def stop(update, context):
    # stops the bot from sending alerts to a specific user
    chat_id = get_chat_id(update, context)
    with open(args.data_location, 'rb') as handle:
        data = pickle.load(handle)
    data.pop(chat_id)
    with open(args.data_location, 'wb') as handle:
        pickle.dump(data, handle)
    await update.message.reply_text('The alert for you wartenummer has been '
                                    + 'stopped')


def flush():
    # flushes the data file every evening.
    # not used anymore, due to the usage of a time switch
    data = {}
    with open(args.data_location, 'wb') as handle:
        pickle.dump(data, handle)


def get_chat_id(update, context):
    chat_id = -1

    if update.message is not None:
        # text message
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        # callback message
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        # answer in Poll
        chat_id = context.bot_data[update.poll.id]

    return chat_id


async def echo(update, context):
    await update.message.reply_text(answers[random.randint(0, len(answers)-1)])


def main():
    # erasing data on every fresh start
    data = {}
    with open(args.data_location, 'wb') as handle:
        pickle.dump(data, handle)

    # Run bot
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ['HMTBOTKEY']).build()

    # map telegram commands to functions
    application.add_handler(CommandHandler(["start"], welcome))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("save", save_user_wartenummer))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("wartenummer", print_wartenummer))
    application.add_handler(MessageHandler(filters.TEXT
                                           & ~filters.COMMAND, echo))

    # periodicaly fetch the wartenummer
    job_queue = application.job_queue
    job_queue.run_repeating(send_alert,
                            interval=args.fetch_interval,
                            first=10)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

