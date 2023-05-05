from telegram.ext import CommandHandler, MessageHandler, filters, Application
import os
import sys
import random
import argparse
from hmt_scraper import get_wartenummer
import pickle
import datetime
import logging

# own logging handler to avoid log flooding through apscheduler and requests
# logger = logging.getLogger(__name__)

# enables a basic logging procedure
logging.basicConfig(
    filename="output.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %I:%M:%S%p",
)


parser = argparse.ArgumentParser(description='parameters for the HMT-Bot')
parser.add_argument('--fetch_interval', type=int, default=10,
                    help='set the time interval in which to scrape the website')
parser.add_argument('--data_location',
                    type=str, default='/home/emil/HMT-Fetch-Bot/data.pkl',
                    help='set the full path to the data.pkl file')
args = parser.parse_args()


# answers the bot gives to user-messages that are not registered commands.
# some are more funny than others.
answers = ['What are you doing?', 'Do you need some /help?', '#human',
           'Please stop it...', 'You lost!?',
           'Come on.', 'It is not funny', 'Ok, boomer.',
           'It is actually not that hard to use me correctly...']


async def welcome(update, context):
    await update.message.reply_text('Hey, I am the HMT-Wartenummer-Fetch-Bot. '
            'I basically tell you when your wartenummer is due for use. '
            'In order to do that, you just have to give me your wartenummer '
            'via the \'save\' command, for example: /save 5. To stop my '
            'notifications, just send /stop. If you want to know what the '
            'current wartenummer is, do /wartenummer.')


async def help(update, context):
    # gives an overview over the commands
    await update.message.reply_text("Sure, these are the commands you can use:"
            '\n/help: displays this help text.'
            '\n/start x: activates the notification of wartenummer x.'
            '\n/stop: stops the notifications.'
            '\n/wartenummer: fetches the current wartenummer.')


async def send_alert(context):
    # most important function of the bot: fetches the current wartenummer
    # and notifies the user who saved that wartenummer.
    wartenummer = get_wartenummer()
    with open(args.data_location, 'rb') as handle:
        data = pickle.load(handle)
    for key, value in data.items():
        if wartenummer.strip() == value:
            await context.bot.send_message(chat_id=key,
                                           text='Hurry, its your turn on the '
                                           'waiting list!')


async def print_wartenummer(update, context):
    # fetches the current wartenummer and displays it when asked.
    wartenummer = get_wartenummer()
    await update.message.reply_text(f'The current wartenummer is: {wartenummer}')


async def save_user_wartenummer(update, context):
    # saves the given Wartenummer with the chat-id
    wartenummer = update.message.text[5:].strip()
    chat_id = get_chat_id(update, context)
    # checks for invalid input and informs the User about that
    allowed_symbols = [str(i) for i in range(201)] + ['-']
    if wartenummer not in allowed_symbols:
        await update.message.reply_text('Something was wrong with your input, '
                                        'please try again!')
        logging.warning(f'User {chat_id} tried to save an unsupported symbol.')
        return

    # read data
    with open(args.data_location, 'rb') as handle:
        data = pickle.load(handle)
    data[chat_id] = wartenummer
    # write data
    with open(args.data_location, 'wb') as handle:
        pickle.dump(data, handle)
    # write statistics
    now = str(datetime.datetime.now())
    output = f'\n{chat_id}, {wartenummer}, {now}'
    with open('stat.csv', 'a') as file:
        file.write(output)
    logging.info(f'A wartenummer has been saved with the following data: {output}')
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
                                    + 'stopped.')


def flush():
    # flushes the data file every evening.
    # not used anymore, due to the usage of a mechanical time switch.
    data = {}
    with open(args.data_location, 'wb') as handle:
        pickle.dump(data, handle)


def get_chat_id(update, context):
    # extracts the users unique chat_id in order to be able to send
    # notifications to the user.
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
    # erasing data on every fresh start and checking for the correct data file
    # path.
    data = {}
    try:
        with open(args.data_location, 'wb') as handle:
            pickle.dump(data, handle)
    except FileNotFoundError:
        logging.error(f'Wrong file path has been given: {args.data_location}')
        print(f'File {args.data_location} not found.\nSpecify the correct '
              'file path via the --data_location flag.')
        sys.exit(1)

    #
    # Run the bot
    #
    # starts the application with a personal telegram bot token, that, in this
    # case, is saved in an environment variable.
    application = Application.builder().token(os.environ['HMTBOTKEY']).build()

    # maps telegram commands to functions
    application.add_handler(CommandHandler(["start"], welcome))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("save", save_user_wartenummer))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("wartenummer", print_wartenummer))
    application.add_handler(MessageHandler(filters.TEXT
                                           & ~filters.COMMAND, echo))

    # periodicaly fetches the wartenummer
    job_queue = application.job_queue
    job_queue.run_repeating(send_alert,
                            interval=args.fetch_interval,
                            first=10)

    logging.info('Started bot.')

    # runs the bot until the application is stopped, either by hitting CTRL-C
    # or, in my setup, by a systemd induced system shutdown.
    application.run_polling()


if __name__ == "__main__":
    main()

