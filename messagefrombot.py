import tkinter as tk
import asyncio
import threading
import pyperclip # Для копирования текста в буфер обмена (иногда бывают проблемы со вставкой)

from __init__ import *

CHANNEL_ID = 1156941990672466020 # id канала "『🌐』основной"

# Функция для запуска графического интерфейса
def run_tk():
    #text_selected = tk.Text()  # Define text_selected

    # Функция для обработки нажатия кнопки "Отправить"
    def on_button_click():
        try:
            channel_id = int(entry.get()) if entry.get() else CHANNEL_ID  # Получение ID канала из поля ввода

            asyncio.run_coroutine_threadsafe(MyBot.message(channel_id, text.get(1.0, tk.END)), loop)
        except Exception as e:
            error(f"Send error click: {e}")
        
    root = tk.Tk()  # Создание главного окна
    
    root.bind('<Control-v>', lambda event: text_selected.insert(tk.END, pyperclip.paste()))
    
    root.title("Message from bot")  # Установка заголовка окна
    root.geometry("400x400")  # Установка размеров окна

    label = tk.Label(root, text="ID")
    label.pack(pady=1, padx=10)
    entry = tk.Entry(root, width=50) # Создание поля ввода
    entry.pack(pady=10, padx=10)

    paste_entry_button = tk.Button(root, text="Вставить", command=lambda: entry.insert(tk.END, pyperclip.paste()))  # Создание кнопки "Вставить" для поля ввода
    paste_entry_button.pack(pady=5,padx=10)


    label = tk.Label(root, text="Message")
    label.pack(pady=1, padx=10)
    
    button = tk.Button(root, text="Отправить", command=on_button_click)  # Создание кнопки "Отправить"
    button.pack(pady=10)

    text = tk.Text(root, width=50, height=10, bd=2) # Создание текстового поля
    text.pack(pady=10, padx=10)

    paste_text_button = tk.Button(root, text="Вставить", command=lambda: text.insert(tk.END, pyperclip.paste()))  # Создание кнопки "Вставить" для текстового поля
    paste_text_button.pack(pady=5,padx=10) 
    
    root.mainloop()  # Запуск главного цикла обработки событий
# Функция для запуска графического интерфейса в асинхронном режиме
async def tk_main():
    global loop
    loop = asyncio.get_running_loop()
    
    if threading.current_thread().is_alive():
        threading.Thread(target=run_tk, daemon=True).start()

class MyBot():
    # Обработчик события подключения к Discord
    @bot.event
    async def on_connect():
        print(f'{Fore.YELLOW}{Style.BRIGHT}=========================')
        print(f'Connection to discord.com')
        print(f'Token: {hide(TOKEN)}')
        print(f'ID: {bot.user.id}')
        print('Prefix:' + PREFIX)
        print(f'{Fore.YELLOW}{Style.BRIGHT}=========================')

        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Zzzzzz..."))

    # Обработчик события успешного входа бота в систему Discord
    @bot.event
    async def on_ready():
        print(f'{Fore.GREEN}{Style.BRIGHT}=========================')
        print(f'Bot logged in as - ')
        print(f'Username: {bot.user.name}')
        print(f'ID: {bot.user.id}')
        print(f'{Fore.GREEN}{Style.BRIGHT}=========================')
        print("Bot connected")
        print(Style.BRIGHT + "\n\nLogs:\n")

        activity = discord.Activity(type=discord.ActivityType.watching, name="видео от Laidfin")
        await bot.change_presence(status=discord.Status.online, activity=activity)

    # Асинхронная функция для отправки сообщения в указанный канал
    async def message(id, message):
        try:
            channel = bot.get_channel(id)
            output(channel, message)
            await channel.send(message)
        except Exception as e:
            error(f"Send error: {e}")

    # Асинхронная функция для запуска бота
    async def start():
        await bot.start(TOKEN)

async def main():
    await tk_main()
    await MyBot.start()

asyncio.run(main())
