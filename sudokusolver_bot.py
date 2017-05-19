import cv2
import telepot

from sudokuSolver import SudokuSolver


def _id_by_photo(photo):
    n = len(photo) - 1
    return photo[n]['file_id']


def send_message(chat_id, msg):
    return bot.sendMessage(chat_id, msg)


def send_photo(chat_id, image):
    try:
        bot.sendPhoto(chat_id, open(image, 'rb'))
    except Exception as ex:
        print(ex)
        send_message(chat_id, "Error sending image")


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        command = msg['text']

        if command == '/start':
            message = 'Welcome to Sudoku Solver Bot \
                      The bot is still in beta mode \
                      For now solves only flat image sudoku \
                      Give a try and enjoy!'
            send_message(chat_id, "Hi! I am Sudoku Solver Bot")
            send_message(chat_id, "I'm still in beta mode")
            send_message(chat_id, "For now I solve only flat sudoku")
            send_message(chat_id, "For example images from '@pic sudoku'")
            send_message(chat_id, "Try me and enjoy :)")

    elif content_type == 'photo':
        id = _id_by_photo(msg['photo'])
        path = 'files/'
        image = 'r' + id + '.jpg'
        res_name = path + 'res_' + image
        bot.download_file(id, path + image)
        solution = SudokuSolver().solve(path + image)
        if solution is False:
            send_message(chat_id, "Sorry but I didn't find the solution :(")
        else:
            cv2.imwrite(res_name, solution)
            send_photo(chat_id, res_name)


bot = telepot.Bot('token')
bot.message_loop(handle, run_forever=True)

