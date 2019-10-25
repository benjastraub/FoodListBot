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
        self.list = defaultdict(int)
        # stores the instances of the meals according to the DB
        self.meal_list = None  # it'll be a list when loaded
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
        pass

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
        pass
