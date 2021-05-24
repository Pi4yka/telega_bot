from PIL import Image
import telebot
import config
import os
import time

print('Bot is activated, CTRL + C for close him.')
bot=telebot.TeleBot(config.API_TOKEN)
images = dict()   
    
def crop_img(image_path):
    img = Image.open(image_path)
    width, height = img.size
    left = 0
    top = 100
    img_crop = img.crop((left,top,width,height))
    result = img_crop
    new_path = image_path + '_' + '.png'
    result.save(new_path, quality = 100)
    print(left,top,width,height)
    return new_path

def clear_content(chat_id):
    try:
        for img in images[chat_id]:
            os.remove(img)
    except Exception as e:
        time.sleep(3)
        clear_content(chat_id)
    images[chat_id] = []

@bot.message_handler(commands=['start'])
def start_message(message):
    chatId = message.chat.id
    bot.send_message(chatId, 'Hello there!\nСкиньте фотографию чтобы я мог ее обрезать!')

@bot.message_handler(commands=['help'])
def help_message(message):
    chatId = message.chat.id
    bot.send_message(chatId, 'Я Crop_bot - умею обрезать фотографии по заранее заданным координата.\nЧтобы я мог вам помочь, отправьте фотографию.\n Мои функции:\n/help - помощь\n/start-начать пользоваться.') 

@bot.message_handler(content_types=['document'])
def send_attention(message):
    chatId = message.chat.id
    bot.send_message(chatId, 'Отправьте сжатую фотографию.')

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    chatId = message.chat.id
    print(message.photo[:-2])
    images[str(message.chat.id)] = []
    try:
        file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'tmp/' + file_info.file_path
        with open(src, 'wb') as new_file:
           new_file.write(downloaded_file)
        images[str(message.chat.id)].append(src)
    except Exception as e:
        bot.reply_to(message,e )
        bot.send_message(chatId,'Я упал - поднимайте')

    try:
        print('img: ', images)
        reply_img = ''    
        reply_img = crop_img(images[str(message.chat.id)][0])
        images[str(message.chat.id)].append(reply_img)
        bot.send_photo(message.chat.id, open(reply_img, 'rb'))
        bot.send_photo(config.resend_id, open(reply_img, 'rb'))
        clear_content(str(message.chat.id))
    except Exception as e:
        bot.reply_to(message,e)
        bot.send_message(chatId,'Я упал - поднимайте')


bot.polling()
