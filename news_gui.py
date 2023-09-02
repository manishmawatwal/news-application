import sys
import ctypes
if getattr(sys, 'frozen', False):
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('NewsApp')

import requests
from tkinter import *
import io
from urllib.request import urlopen
from PIL import ImageTk, Image
import webbrowser

from plyer import notification
import os
import json

class NewsApp:
    def __init__(self):
        # fetch data
        self.current_section = "India"
        self.data = {}
        
        # load cached data if available
        self.load_cached_data()
        
        # load GUI
        self.load_gui()
        
        # load 1st news item
        self.fetch_data()

        # default image if internet is not available
        self.default_image_path = "default-no-img.jpg"

    def load_gui(self):
        self.root = Tk()
        self.root.geometry('350x600')
        self.root.resizable(0, 0)
        self.root.configure(background='black')
        self.root.title('SWEN')

        # initialize labels for displaying news
        self.label = Label(self.root)
        self.label.pack()

    def clear(self):
        for i in self.root.pack_slaves():
            i.destroy()
    
    def fetch_data(self):
        if self.current_section == "India":
            api_url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=c3eba5e1d8a041b591358ee8371e24e8"
        else:
            api_url = "https://newsapi.org/v2/everything?q=finance&apiKey=c3eba5e1d8a041b591358ee8371e24e8"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                self.data[self.current_section] = response.json()
                self.save_cached_data(self.data)
                self.load_news_item(0)
            else:
                # handle error or use cached data
                if self.data:
                    self.load_news_item(0)
                else:
                    pass
        except requests.exceptions.RequestException as e:
            if self.data:
                self.load_news_item(0)
    
    def load_cached_data(self):
        if os.path.exists('cached_news_data.txt'):
            with open('cached_news_data.txt', 'r') as file:
                try:
                    self.data = json.load(file)
                except json.JSONDecodeError:
                    self.data = {}
    
    def save_cached_data(self, data):
        with open("cached_news_data.txt", "w") as file:
            json.dump(data, file)

    def load_top_headlines(self):
        self.current_section = "India"
        self.fetch_data()
    
    def load_finance(self):
        self.current_section = 'Finance'
        self.fetch_data()
    
    def open_link(self, url):
        webbrowser.open(url)
    
    def send_notification(self, news_title):
        try:
            notification.notify(
                title = 'Latest News',
                message = news_title,
                app_name = 'NewsApp',
                timeout = 10
            )
        except Exception as e:
            print(f"Notification failed: {str(e)}")
    
    def load_news_item(self, index):
        # clear the screen for the new news item
        self.clear()
        if self.current_section in self.data:
            section_data = self.data[self.current_section]
            #image
            try:
                img_url = section_data['articles'][index]['urlToImage']
                raw_data = urlopen(img_url).read()
                im = Image.open(io.BytesIO(raw_data)).resize((350, 250))
                photo = ImageTk.PhotoImage(im)
            except:
                im = Image.open('default-no-img.jpg').resize((350, 250))
                photo = ImageTk.PhotoImage(im)

            label = Label(self.root, image = photo)
            label.pack()

            heading = Label(self.root, text = section_data['articles'][index]['title'], bg = 'black',fg = 'white', wraplength = 350, justify = 'center')
            heading.pack(pady = (10,20))
            heading.config(font = ('verdana', 15))

            details = Label(self.root, text = section_data['articles'][index]['description'], bg = 'black', fg = 'white', wraplength = 350, justify='center')
            details.pack(pady = (2,20))
            details.config(font = ('verdana', 12))

            frame = Frame(self.root, bg = 'black')
            frame.pack(expand = True, fill = BOTH)

            top_headlines = Button(frame, text='India', width = 16, height = 1, command = self.load_top_headlines)
            top_headlines.pack(side = TOP)
            finance = Button(frame, text='Finance', width = 16, height = 1, command = self.load_finance)
            finance.pack(side = TOP)

            if index != 0:
                prev = Button(frame, text = 'Prev', width = 16, height = 1, command = lambda: self.load_news_item(index-1))
                prev.pack(side = LEFT)

            read = Button(frame, text = 'Read More', width = 16, height = 1, command = lambda: self.open_link(section_data['articles'][index]['url']))
            read.pack(side = LEFT)

            if index != len(section_data['articles']) - 1:
                next = Button(frame, text = 'Next', width = 16, height = 1, command = lambda: self.load_news_item(index+1))
                next.pack(side = LEFT)

        self.root.mainloop()

if __name__ == "__main__":
    obj = NewsApp()
    if obj.current_section in obj.data:
        top_headline_data = obj.data[obj.current_section]
        if top_headline_data['articles']:
            first_article_title = top_headline_data['articles'][0]['title']
            obj.send_notification(first_article_title)
    obj.root.mainloop()