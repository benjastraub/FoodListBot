# telegram
import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)
import logging
# project
import token_key
import functions
import parameters
from bot_messages import MESSAGES
# others
import os
from collections import defaultdict


class FoodList:
    def __init__(self):
        # stores the needed ingridients
        # ingridient_name: [ingridient_instance, quantity]
        self.list = dict()
        # stores the instances of the meals according to the DB
        self.meal_list = None  # it'll be a dictionary when loaded
        # stores the instances of the ingridients according to the DB
        self.ingridients = None  # it'll be a dictionary when loaded
        # booleans to check state of the script
        self._adding_meals = False
        self._adding_ingridients = False
        self._removing_ingridients = False
        self._loading_meals = False
        self._loading_ingridients = False
        # language of the chat where te bot is beeing used
        self.language_code = None  # it'll be a string
        # personalized keyboard elements
        self._keyboard = None
        # bot elements
        self.telegram_bot_init()
        # bot handlers
        self.handlers_init()

    @property
    def adding_meals(self):
        return self._adding_meals

    @adding_meals.setter
    def adding_meals(self, value):
        """
        set self._adding_meals to value.
        If value == True, it assigns False to the other two atributes
        """
        self._adding_meals = value
        if value:
            self._adding_ingridients = not value
            self._removing_ingridients = not value

    @property
    def adding_ingridients(self):
        return self._adding_ingridients

    @adding_ingridients.setter
    def adding_ingridients(self, value):
        """
        set self._adding_ingridients to value.
        If value == True, it assigns False to the other two atributes
        """
        self._adding_ingridients = value
        if value:
            self._adding_meals = not value
            self._removing_ingridients = not value

    @property
    def removing_ingridients(self):
        return self._removing_ingridients

    @removing_ingridients.setter
    def removing_ingridients(self, value):
        """
        set self._removing_ingridients to value.
        If value == True, it assigns False to the other two atributes
        """
        self._removing_ingridients = value
        if value:
            self._adding_ingridients = not value
            self._adding_meals = not value

    @property
    def loading_meals(self):
        return self._loading_meals

    @loading_meals.setter
    def loading_meals(self, value):
        """
        set self._loading_meals to value.
        If value == True, it assigns False to the other atribute
        """
        self._loading_meals = value
        if value:
            self._loading_ingridients = not value

    @property
    def loading_ingridients(self):
        return self._loading_ingridients

    @loading_ingridients.setter
    def loading_ingridients(self, value):
        """
        set self._loading_ingridients to value.
        If value == True, it assigns False to the other atribute
        """
        self._loading_ingridients = value
        if value:
            self._loading_meals = not value

    @property
    def keyboard(self):
        return self._keyboard

    @keyboard.setter
    def keyboard(self, value):
        if value is None:
            self._keyboard = telegram.ReplyKeyboardRemove()
        elif value == "add_ingridients":
            keyboard = [[key] for key in self.ingridients]
            self._keyboard = telegram.ReplyKeyboardMarkup(keyboard)
        elif value == "remove_ingridients":
            keyboard = [[key] for key in self.list]
            self._keyboard = telegram.ReplyKeyboardMarkup(keyboard)
        elif value == "add_meals":
            keyboard = [[key] for key in self.meal_list]
            self._keyboard = telegram.ReplyKeyboardMarkup(keyboard)

    def telegram_bot_init(self):
        # ussed for debugging
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s -\
 %(message)s", level=logging.INFO)
        # updater
        self.updater = Updater(token=token_key.token, use_context=True)
        # fetch starts
        self.updater.start_polling()
        # dispatcher
        self.dispatcher = self.updater.dispatcher

    def handlers_init(self):
        # text messages
        text_handler = MessageHandler(Filters.text, self.text_message)
        self.dispatcher.add_handler(text_handler)
        # files attachments
        file_handler = MessageHandler(Filters.document, self.file_message)
        self.dispatcher.add_handler(file_handler)
        # /start
        start_handler = CommandHandler("start", self.start)
        self.dispatcher.add_handler(start_handler)
        # /load_meals
        load_meals_handler = CommandHandler("load_meals", self.load_meals)
        self.dispatcher.add_handler(load_meals_handler)
        # /load_ingridients
        load_ingridients_handler = CommandHandler("load_ingridients",
                                                  self.load_ingridients)
        self.dispatcher.add_handler(load_ingridients_handler)
        # /add_ingridients
        add_ingridients_handler = CommandHandler("add_ingridients",
                                                 self.add_ingridients)
        self.dispatcher.add_handler(add_ingridients_handler)
        # /remove_ingridients
        remove_ingridients_handler = CommandHandler("remove_ingridients",
                                                    self.remove_ingridients)
        self.dispatcher.remove_handler(remove_ingridients_handler)
        # /add_meals
        add_meals_handler = CommandHandler("add_meals", self.add_meals)
        self.dispatcher.add_handler(add_meals_handler)
        # /stop
        stop_handler = CommandHandler("stop", self.stop)
        self.dispatcher.add_handler(stop_handler)
        # /help
        help_handler = CommandHandler("help", self.help)
        self.dispatcher.add_handler(help_handler)
        # unknown
        unknown_handler = MessageHandler(Filters.command, self.unknown)
        self.dispatcher.add_handler(unknown_handler)

    def text_message(self, update, context):
        if self.adding_meals:
            typed_meal = update.message.text
            meal = self.meal_list.get(typed_meal)
            for ingridient in meal.ingridients:
                if ingridient.name in self.list.keys():
                    self.list[ingridient.name][1] += 1
                else:
                    self.list[ingridient.name] = [ingridient, 1]
        elif self.adding_ingridients:
            typed_ingridient = update.message.text
            ingridient = self.ingridients.get(typed_ingridient)
            if ingridient.name in self.list.keys():
                self.list[ingridient.name][1] += 1
            else:
                self.list[ingridient.name] = [ingridient, 1]
        elif self.removing_ingridients:
            typed_ingridient = update.message.text
            if typed_ingridient in self.list.keys():
                self.list[typed_ingridient][1] -= 1
                if self.list[typed_ingridient][1] == 0:
                    del self.list[typed_ingridient]

    def file_message(self, update, context):
        if self.loading_meals:
            file_type = "_meals"
        elif self.load_ingridients:
            file_type = "_ingridients"
        else:
            return 0
        file_name = str(update.message.chat.id) + file_type + ".csv"
        file = context.bot.get_file(update.message.document.file_id)
        file.download(file_name)

    def start(self, update, context):
        # we get user language
        self.language_code = update._effective_user.language_code
        # greeting message is send
        to_write = MESSAGES["start1"]
        self.keyboard = None
        self.send_message(update, context, to_write)
        # we check if the user has associated files
        meals_file_name = str(update.message.chat.id) + "_meals" + ".csv"
        ingridients_file_name = str(update.message.chat.id) + "_ingridients" +\
            ".csv"
        # if the user does have files
        if os.path.exists(meals_file_name) and\
                os.path.exists(ingridients_file_name):
            # second start message is send
            to_write = MESSAGES["start2"]
            self.send_message(update, context, to_write)
            # instances of  meals and ingridients are created
            self.instance_ingridients(ingridients_file_name)
            self.instance_meals(meals_file_name)
            # we set this bools to False so no more files are proccesed
            self.loading_meals = False
            self.loading_ingridients = False
        # if the user does not have files
        else:
            # a message with instructions is send
            to_write = MESSAGES["start3"]
            self.send_message(update, context, to_write)

    def load_meals(self, update, context):
        to_write = MESSAGES["load_meals"]
        self.send_message(update, context, to_write)
        self.loading_meals = True

    def load_ingridients(self, update, context):
        to_write = MESSAGES["load_ingridients"]
        self.send_message(update, context, to_write)
        self.loading_ingridients = True

    def add_ingridients(self, update, context):
        self.keyboard = "add_ingridients"
        self.adding_ingridients = True
        to_write = functions.list_to_text(sorted(self.list.items(),
                                          key=lambda k: k[0].category))
        self.send_message(update, context, to_write)

    def remove_ingridients(self, update, context):
        self.keyboard = "remove_ingridients"
        self.removing_ingridients = True
        to_write = functions.list_to_text(sorted(self.list.items(),
                                          key=lambda k: k[0].category))
        self.send_message(update, context, to_write)

    def add_meals(self, update, context):
        self.keyboard = "add_meals"
        self.adding_meals = True
        to_write = functions.list_to_text(sorted(self.list.items(),
                                          key=lambda k: k[0].category))
        self.send_message(update, context, to_write)

    def stop(self, update, context):
        pass

    def help(self, update, context):
        pass

    def unknown(self, update, context):
        pass

    def send_message(self, update, context, text):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text, replay_markup=self.keyboard,
                                 parse_mode=telegram.ParseMode.MARKDOWN)

    def instance_ingridients(self, path):
        self.ingridients = functions.load_ingridients(path)

    def instance_meals(self, path):
        self.meal_list = functions.load_meals(path, self.ingridients)
