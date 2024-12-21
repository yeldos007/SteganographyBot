import os
import dotenv
import telebot
import sys
from telebot import types
from telebot.types import InputMediaPhoto

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
print("Бот запустился....")

@bot.message_handler(commands=['start'])
def start_bot(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Encrypt")
    btn2 = types.KeyboardButton("Decrypt")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text=f"Hi! {message.from_user.first_name}!Send me a message for encryption or decryption.", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "Encrypt":
        bot.send_message(message.chat.id, "Send the text you want to hide:")
        bot.register_next_step_handler(message, get_text_for_encryption)
    elif message.text == "Decrypt":
        bot.send_message(message.chat.id, "Send the image (BMP) for decryption:")
        bot.register_next_step_handler(message, get_image_for_decryption)
    else:
        bot.send_message(message.chat.id, "I don't understand.")

def get_text_for_encryption(message):
    text_to_hide = message.text
    with open("text.txt", "w") as file:
        file.write(text_to_hide)
    bot.send_message(message.chat.id, "Now send the BMP image where you want to hide the text.")
    bot.register_next_step_handler(message, get_image_for_encryption)

def get_image_for_encryption(message):
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("start.bmp", "wb") as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, "Enter the degree of encryption: 1/2/4/8")
        bot.register_next_step_handler(message, encrypt_handler)
    else:
        bot.send_message(message.chat.id, "Please send a valid BMP image.")

def get_image_for_decryption(message):
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("encode.bmp", "wb") as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, "Enter the degree of decryption: 1/2/4/8")
        bot.register_next_step_handler(message, decrypt_handler)
    else:
        bot.send_message(message.chat.id, "Please send a valid BMP image.")

def encrypt_handler(message):
    try:
        degree = int(message.text.strip())
        if degree not in [1, 2, 4, 8]:
            raise ValueError("Degree must be 1, 2, 4, or 8")
        encrypt(degree)
        with open("encode.bmp", "rb") as file:
            bot.send_document(message.chat.id, file)
        bot.send_message(message.chat.id, "Text successfully encrypted!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error during encryption: {e}")

def decrypt_handler(message):
    try:
        degree = int(message.text.strip())
        if degree not in [1, 2, 4, 8]:
            raise ValueError("Degree must be 1, 2, 4, or 8")
        bot.send_message(message.chat.id, "Enter how many symbols to read:")
        bot.register_next_step_handler(message, lambda m: decrypt_step2(m, degree))
    except Exception as e:
        bot.send_message(message.chat.id, f"Error during decryption: {e}")

def decrypt_step2(message, degree):
    try:
        to_read = int(message.text.strip())
        decrypt(degree, to_read)
        with open("decoded.txt", "r") as file:
            decoded_text = file.read()
        bot.send_message(message.chat.id, f"Decrypted text: {decoded_text}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error during decryption: {e}")

def encrypt(degree):
    text_len = os.stat("text.txt").st_size
    img_len = os.stat("start.bmp").st_size
    if text_len >= img_len * degree / 8 - 54:
        raise ValueError("The text is too long")

    text = open("text.txt", "r")
    start_bmp = open("start.bmp", "rb")
    encode_bmp = open("encode.bmp", "wb")

    first54 = start_bmp.read(54)
    encode_bmp.write(first54)

    text_mask, img_mask = create_masks(degree)

    while True:
        symbol = text.read(1)
        if not symbol:
            break

        symbol = ord(symbol)

        for byte_amount in range(0, 8, degree):
            img_byte = int.from_bytes(start_bmp.read(1), sys.byteorder) & img_mask
            bits = symbol & text_mask
            bits >>= (8 - degree)
            img_byte |= bits

            encode_bmp.write(img_byte.to_bytes(1, sys.byteorder))
            symbol <<= degree

    encode_bmp.write(start_bmp.read())
    text.close()
    start_bmp.close()
    encode_bmp.close()

def decrypt(degree, to_read):
    encode_bmp = open("encode.bmp", "rb")
    decoded_txt = open("decoded.txt", "w")

    encode_bmp.seek(54)

    text_mask, img_mask = create_masks(degree)
    img_mask = ~img_mask

    text = ""

    for _ in range(to_read):
        symbol = 0

        for bits_read in range(0, 8, degree):
            img_byte = int.from_bytes(encode_bmp.read(1), sys.byteorder) & img_mask

            img_byte <<= (8 - degree)
            img_byte %= 256
            symbol |= img_byte
            if bits_read < 8 - degree:
                symbol <<= degree

        text += chr(symbol)

    decoded_txt.write(text)
    encode_bmp.close()
    decoded_txt.close()
    
def create_masks(degree):
    text_mask = 0b11111111
    img_mask = 0b11111111
    text_mask = text_mask << (8 - degree)
    text_mask %= 256

    img_mask >>= degree
    img_mask <<= degree
    return text_mask, img_mask

if __name__ == "__main__":
    bot.polling(non_stop=True)
