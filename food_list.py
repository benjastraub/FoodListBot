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
