from colorama import init, Fore
from PIL import Image
import requests
from io import BytesIO
import sys
import shutil
import feedparser
import os
import climage
from datetime import datetime

class NewsWindow:
    def __init__(self):
        init(autoreset=True)
        self.rss_url = "https://lenta.ru/rss"
        self.news_entries = self.fetch_news()
        self.current_entry = 0
        self.max_entries_displayed = 10  # Количество новостей для отображения
        self.term_height, self.term_width = shutil.get_terminal_size()

    def fetch_news(self):
        feed = feedparser.parse(self.rss_url)
        return feed.entries

    def convert_pubdate(self, pubdate_str):
        # Преобразование строки в объект datetime
        pubdate_obj = datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %z")

        # Преобразование в нужный формат
        formatted_date = pubdate_obj.strftime("%d.%m.%YT%H:%M")
        return formatted_date

    def display_news(self):
        start_index = self.current_entry
        end_index = start_index + self.max_entries_displayed

        for i, entry in enumerate(self.news_entries[start_index:end_index]):
            title = entry.get("title", "")
            formatted_date = self.convert_pubdate(entry['published'])
            description = entry.get("description", "")
            enclosures = entry.get("links", [])
            enclosure_url = next((enc.get("href", "") for enc in enclosures if enc.get("rel") == "enclosure"), "")

            if title and isinstance(title, str):
                print(Fore.CYAN + f"{i + 1}. {title}")

            if description:
                try:
                    if isinstance(description, str):
                        print(formatted_date+"\n")
                        print(description)
                    else:
                        print("No description available")
                except Exception as e:
                    print(f"Error displaying description: {e}")

            if enclosure_url:
                self.display_image(enclosure_url)

            print("\n" + "-" * int(self.term_width))

    def display_image(self, image_url):
        try:
            response = requests.get(image_url, stream=True)
            img = Image.open(BytesIO(response.content)).convert('RGB')

            # Новые размеры с учетом пропорций
            
            #img = img.resize((img.size[1], 60), resample=Image.LANCZOS)
            
            # Convert the image to a numpy array
            converted = climage.convert_pil(img, is_unicode=True, width=200)
            print(converted)
            
        except Exception as e:
            print(f"Error displaying image: {e}")

    def scroll_down(self):
        self.current_entry += 1
        if self.current_entry + self.max_entries_displayed > len(self.news_entries):
            self.current_entry = len(self.news_entries) - self.max_entries_displayed

    def scroll_up(self):
        self.current_entry -= 1
        if self.current_entry < 0:
            self.current_entry = 0

    def run(self):
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')  # очистка экрана
            self.display_news()
            key = input("Press 'q' to quit, 'j' to scroll down, 'k' to scroll up: ")

            if key == 'q':
                sys.exit()
            elif key == 'j':
                self.scroll_down()
            elif key == 'k':
                self.scroll_up()

def main():
    news_window = NewsWindow()
    news_window.run()

if __name__ == "__main__":
    main()
