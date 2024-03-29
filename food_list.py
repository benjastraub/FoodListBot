# telegram
import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)
import logging
# project
import token_key
import functions
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
        """
        it assigns a telegram replay keyboard to self._keyboard
        """
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
        self.dispatcher.add_handler(remove_ingridients_handler)
        # /add_meals
        add_meals_handler = CommandHandler("add_meals", self.add_meals)
        self.dispatcher.add_handler(add_meals_handler)
        # /see_list
        see_list_handler = CommandHandler("see_list", self.see_list)
        self.dispatcher.add_handler(see_list_handler)
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
        """
        this function handles text messages without commands. Depending on the
        last command used it might add ingridients from a meal to the list,
        a particular ingridient, remove an ingridient from the list or do
        nothing
        """
        # check mode
        if self.adding_meals:
            # text from the message is retrieved
            typed_meal = update.message.text
            # we get the instance from  the meal list. It might be None
            meal = self.meal_list.get(typed_meal)
            try:
                # might produce an AttributeError if ingridients is None
                # every ingridient in the meal is checked
                for ingridient in meal.ingridients:
                    # if it's already in self.list the quantity increases
                    if ingridient.name in self.list.keys():
                        self.list[ingridient.name][1] += 1
                    else:
                        # the instance is added to the list
                        self.list[ingridient.name] = [ingridient, 1]
                # the list is transformed to text
                to_write = functions.list_to_text(sorted(self.list.values(),
                                                  key=lambda x: x[0].category))
            except AttributeError:
                to_write = MESSAGES["meal_error"]
            # message is send
            self.send_message(update, context, to_write)
        # check mode
        elif self.adding_ingridients:
            # text from the message is retrieved
            typed_ingridient = update.message.text
            # we get the instance from  the ingridients list. It might be None
            ingridient = self.ingridients.get(typed_ingridient)
            try:
                # might produce an AttributeError if ingridients is None
                # if it's already in self.list the quantity increases
                if ingridient.name in self.list.keys():
                    self.list[ingridient.name][1] += 1
                else:
                    # the instance is added to the list
                    self.list[ingridient.name] = [ingridient, 1]
                # the list is transformed to text
                to_write = functions.list_to_text(sorted(self.list.values(),
                                                  key=lambda x: x[0].category))
            except AttributeError:
                to_write = MESSAGES["add_ingridient_error"]
            # message is send
            self.send_message(update, context, to_write)
        # check mode
        elif self.removing_ingridients:
            # text from the message is retrieved
            typed_ingridient = update.message.text
            try:
                # might produce a KeyError if typed_meal is not in self.list
                # decreases amounot of the ingridient
                self.list[typed_ingridient][1] -= 1
                # remove igridient from list when the quantity is 0
                if self.list[typed_ingridient][1] == 0:
                    del self.list[typed_ingridient]
                # the list is transformed to text
                to_write = functions.list_to_text(sorted(self.list.values(),
                                                  key=lambda x: x[0].category))
            except KeyError:
                to_write = MESSAGES["remove_ingridient_error"]
            # message is send
            self.keyboard = "remove_ingridients"
            self.send_message(update, context, to_write)

    def file_message(self, update, context):
        """
        if the commands /load_meals or /load_ingridients were used, this will
        save files with the code of the chat
        """
        # asigns file_tipe according to the program status
        if self.loading_meals:
            file_type = "_meals"
        elif self.load_ingridients:
            file_type = "_ingridients"
        else:
            # if the script isn't loading_meals or loading_ingridients
            # do a return so the function stop
            return 0
        # unique file name is created
        file_name = str(update.message.chat.id) + file_type + ".csv"
        # the file is retrieved from the chat
        file = context.bot.get_file(update.message.document.file_id)
        # the file is downloaded
        file.download(file_name)

    def start(self, update, context):
        # we get user language
        self.language_code = update._effective_user.language_code
        # greeting message is send
        to_write = MESSAGES["start1"]
        self.keyboard = None
        self.send_message(update, context, to_write, False)
        # we check if the user has associated files
        meals_file_name = str(update.message.chat.id) + "_meals" + ".csv"
        ingridients_file_name = str(update.message.chat.id) + "_ingridients" +\
            ".csv"
        # if the user does have files
        if os.path.exists(meals_file_name) and\
                os.path.exists(ingridients_file_name):
            # second start message is send
            to_write = MESSAGES["start2"]
            self.send_message(update, context, to_write, False)
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
            self.send_message(update, context, to_write, False)

    def load_meals(self, update, context):
        # keyboard assignment
        self.keyboard = None
        # message is assigned
        to_write = MESSAGES["load_meals"]
        # message is send
        self.send_message(update, context, to_write, False)
        # set status to True and the others to False
        self.loading_meals = True

    def load_ingridients(self, update, context):
        # keyboard assignment
        self.keyboard = None
        # message is assigned
        to_write = MESSAGES["load_ingridients"]
        # message is send
        self.send_message(update, context, to_write, False)
        # set status to True and the others to False
        self.loading_ingridients = True

    def add_ingridients(self, update, context):
        # keyboard assignment
        self.keyboard = "add_ingridients"
        # set status to True and the others to False
        self.adding_ingridients = True
        # message is created according to the list
        to_write = functions.list_to_text(sorted(self.list.values(),
                                          key=lambda x: x[0].category))
        # message is send
        self.send_message(update, context, to_write)

    def remove_ingridients(self, update, context):
        # keyboard assignment
        self.keyboard = "remove_ingridients"
        # set status to True and the others to False
        self.removing_ingridients = True
        # message is created according to the list
        to_write = functions.list_to_text(sorted(self.list.values(),
                                          key=lambda x: x[0].category))
        # message is send
        self.send_message(update, context, to_write)

    def add_meals(self, update, context):
        # keyboard assignment
        self.keyboard = "add_meals"
        # set status to True and the others to False
        self.adding_meals = True
        # message is created according to the list
        to_write = functions.list_to_text(sorted(self.list.values(),
                                          key=lambda x: x[0].category))
        # message is send
        self.send_message(update, context, to_write)

    def see_list(self, update, context):
        # keyboard assignment
        self.keyboard = None
        # this makes adding_meals True
        # and adding_ingridients and removing_ingridients False
        self.adding_meals = True
        # then, this makes adding_ingridients False
        self.adding_meals = False
        # message is created according to the list
        to_write = functions.list_to_text(sorted(self.list.values(),
                                          key=lambda x: x[0].category))
        # message is send
        self.send_message(update, context, to_write)

    def stop(self, update, context):
        # keyboard assignment
        self.keyboard = None
        # message is assigned
        to_write = MESSAGES["stop"]
        # message is send
        self.send_message(update, context, to_write, False)
        self.updater.stop()

    def help(self, update, context):
        # keyboard assignment
        self.keyboard = None
        # message is assigned
        to_write = MESSAGES["unknown"]
        # message is send
        self.send_message(update, context, to_write, False)

    def unknown(self, update, context):
        # keyboard assignment
        self.keyboard = None
        # message is assigned
        to_write = MESSAGES["unknown"]
        # message is send
        self.send_message(update, context, to_write, False)

    def send_message(self, update, context, text, markdown=True):
        """
        send message with text as the content of it. The function uses the
        update and context of the chart. 
        """
        if markdown:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text, reply_markup=self.keyboard,
                                     parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text, reply_markup=self.keyboard)

    def instance_ingridients(self, path):
        """load the ingridients from the csv"""
        self.ingridients = functions.load_ingridients(path)

    def instance_meals(self, path):
        """Load the meals from the csv"""
        self.meal_list = functions.load_meals(path, self.ingridients)
