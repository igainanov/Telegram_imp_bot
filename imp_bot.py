import re
import time
import requests
import random
import logging
import telebot
from telebot import types
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

# add logging to get the messages in the console
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# create 2 lists with bot responses with random function
list_agreement = ["'                 OK                 '", "'            Let's see            '",
                  "'             Shoot!             '", "'            You do it            '",
                  "'       Make a choice       '", "'         Here you go         '",
                  "'     That's the menu     '", "'         I'm all yours         '",
                  "'       Have your time      '"]
list_thanks = ["'                 Truly yours                 '",
               "'I am quite grateful to your generous patience'",
               "'      Looking forward to using me again      '",
               "'                Thanks a lot!                '",
               "'                   Be safe!                   '",
               "'            I wish you come back            '"]


def run_imp_bot(token: str) -> None:
    """ Runs bot that get financial indexes, Moon's and Solar system planets' data"""
    bot = telebot.TeleBot(token, parse_mode=None)

    @bot.message_handler(commands=['start'])
    def welcome_messages(message):
        """ Creates welcome message and initial keyboard"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Financial Data Sounds Good!")
        markup.add(btn1)
        btn2 = types.KeyboardButton("To the Moon Data and Back!")
        markup.add(btn2)
        btn3 = types.KeyboardButton("Planets' Data Rules the World!")
        markup.add(btn3)
        bot.send_message(message.from_user.id, f"Hi, {message.from_user.username}!\nWant to know the Earth's financial,"
                                               f"\nthe Moon's or Solar system planets' data?", reply_markup=markup)

    def create_keyboard():
        """ The financial indexes menu"""
        keyboard = types.InlineKeyboardMarkup()
        key_dowjones = types.InlineKeyboardButton(text='Dow Jones', callback_data='dowjones')
        keyboard.add(key_dowjones)
        key_snp500 = types.InlineKeyboardButton(text='S&P 500', callback_data='snp500')
        keyboard.add(key_snp500)
        key_nasdaq = types.InlineKeyboardButton(text='Nasdaq', callback_data='nasdaq')
        keyboard.add(key_nasdaq)
        key_moex = types.InlineKeyboardButton(text='MOEX', callback_data='moex')
        keyboard.add(key_moex)
        key_rtsi = types.InlineKeyboardButton(text='RTSI', callback_data='rtsi')
        keyboard.add(key_rtsi)
        return keyboard

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        """ Responds to particular menu selection"""
        if message.text == "Financial Data Sounds Good!":
            keyboard = create_keyboard()
            bot.send_message(message.from_user.id, random.choice(list_agreement), reply_markup=keyboard)
        elif message.text == "To the Moon Data and Back!":
            page_moon = requests.get("https://sunsetsunrisetime.com/lunar-days")
            # check the connection with the Internet
            if page_moon.status_code != 200:
                bot.send_message(message.from_user.id, 'Oops! Looks like I am out of order...')
            # parses the static website page
            soup_moon = BeautifulSoup(page_moon.text, "html.parser")
            moon_value = soup_moon.findAll('div', class_="moon-today-days block")
            moon_data_raw_lst = re.split(r'\n\n', moon_value[0].text, maxsplit=1)
            moon_data1_raw_str = ''.join(moon_data_raw_lst[1])
            moon_data2_raw_lst = re.split(r'\n\n\n\n\n', moon_data1_raw_str, maxsplit=0)
            moon_data = re.sub(r'(\d*)/(\d*)/(\d*)', r'\2.\1.\3', moon_data2_raw_lst[0])
            bot.send_message(message.from_user.id, moon_data)
            # sends the bot random thank you message after finding the financial data
            bot.send_message(message.from_user.id, random.choice(list_thanks))
        elif message.text == "Planets' Data Rules the World!":
            page_planets = requests.get("https://www.theplanetstoday.com/astrology.html#")
            # check the connection with the Internet
            if page_planets.status_code != 200:
                bot.send_message(message.from_user.id, 'Oops! Looks like I am out of order...')
            # parses the static website page
            soup_planets = BeautifulSoup(page_planets.text, "html.parser")
            planets_value = soup_planets.findAll('div',
                                     style="border: 1px #888 solid; border-radius:20px; margin-top:20px; padding:10px")
            planets_data1_lst = re.split(r' \w+ enters \w+ at ', planets_value[0].text, maxsplit=0)
            planets_data1_str = ' '.join(planets_data1_lst)
            planets_data2_lst = re.split(r' \w+ goes Station Retrograde in \w+ at ', planets_data1_str, maxsplit=0)
            planets_data2_str = ' '.join(planets_data2_lst)[217:]
            bot.send_message(message.from_user.id, f"Here is a list of each planet (including Pluto and Chiron) showing"
                                                   f" which sign they are currently in: {planets_data2_str}")
            # sends the bot random thank you message after finding the planets' data
            bot.send_message(message.from_user.id, random.choice(list_thanks))
        else:
            # responds to non-standard text entry
            bot.send_message(message.from_user.id, f"I have no idea what you mean. Try to input /start.")

        @bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            """ Responds to financial indexes keyboard calls"""

            page_indexes = requests.get('https://www.investing.com/indices/major-indices')

            # check the connection with the Internet
            if page_indexes.status_code != 200:
                bot.send_message(call.message.chat.id, 'Oops! Looks like I am out of order...')

            # parses the static website page
            soup_indexes = BeautifulSoup(page_indexes.text, "html.parser")
            index_value = soup_indexes.findAll('td', class_='datatable_cell__0y0eu datatable_cell--align-end__fwomz'
                                                            ' table-browser_col-last__pZaq6')

            # creates the helper dictionary for appropriate calls
            helper = {'dowjones': ['Dow Jones', 0, 1],
                          'snp500': ['S&P 500', 1, 2],
                          'nasdaq': ['Nasdaq', 2, 3],
                          'moex': ['MOEX', 21, 22],
                          'rtsi': ['RTSI', 22, 23]}[call.data]

            info_value = index_value[helper[1]]
            index_value = re.sub(r'[^0-9.]', "", info_value.text)

            bot.send_message(call.message.chat.id, f"The current stock market index {helper[0]} is {index_value},\n"
                                               f" let's dig some relevant stats...")

            # parse the dinamic website page
            browser = webdriver.Chrome()
            browser.maximize_window()
            browser.get("https://www.investing.com/indices/major-indices")
            performance = '//*[@id="__next"]/div[2]/div/div/div[2]/main/div[3]/div[1]/button[2]/span'
            table_perf = browser.find_element(by=By.XPATH, value=performance)
            table_perf.click()
            time.sleep(3)

            change_xpath_dflt = '//*[@id="__next"]/div[2]/div/div/div[2]/main/div[4]/div/table/tbody/tr[1]/td[3]'

            # create 2 lists for using them in bot's response generation
            duration = ['the day\'s', 'one week\'s', 'one month\'s', 'the year-to-date', 'one year\'s', 'three years\'']
            str_no = [3, 4, 5, 6, 7, 8]

            # create cycle for bot response using 2 lists of arguments
            for duration, str_no in zip(duration, str_no):
                lst_change = list(change_xpath_dflt)
                lst_change[-8] = str(helper[2])
                lst_change[-2] = str(str_no)
                change = ''.join(lst_change)
                index_change = browser.find_element(by=By.XPATH, value=change).text
                bot.send_message(call.message.chat.id, f"{duration} change is {index_change}")

            # sends the bot random thank you message after finding the financial data
            bot.send_message(call.message.chat.id, random.choice(list_thanks), reply_markup=create_keyboard())

    # start the bot
    bot.infinity_polling()
