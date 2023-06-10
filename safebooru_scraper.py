"""important"""
from io import BytesIO
import tkinter
import math
import pyperclip
from bs4 import BeautifulSoup
import requests
from PIL import ImageTk, Image


class Kurumi:
    """class docstring shut up pylint"""

    def copy_image_link(self):
        """copies image link to clipobard"""
        pyperclip.copy(self.pic_link)

    def __init__(self, root):
        """innit bruv"""
        self.root = root
        self.page_num = 0
        self.counter = 38
        self.safebooru_link = "https://safebooru.org/index.php?page=post&s=list&tags="
        self.search_tags = "tokisaki_kurum* date_a_li*"

        self.root.geometry("1920x1080")
        self.root.title("Safebooru Waifu Scraper")

        self.canvas = tkinter.Canvas(self.root, width=0, height=0)
        self.tags_label = tkinter.Text(self.root, font="Helvetica, 10", bg="#F0F0ED")
        self.copy_button = tkinter.Button(
            self.root, text="Copy Image Link", command=self.copy_image_link
        )
        self.search_bar = tkinter.Entry(self.root, width=75)

        self.root.bind("<Left>", self.left_key)
        self.root.bind("<Right>", self.right_key)
        self.search_bar.bind("<Return>", self.update_search)

        self.canvas.grid(row=0, column=0, padx=2, rowspan=3)
        self.tags_label.grid(row=1, column=1, pady=2)
        self.copy_button.grid(row=2, column=1, pady=2)
        self.search_bar.grid(row=0, column=1, pady=2)

        self.search_bar.insert(0, self.search_tags)
        self.start()

    def update_search(self, event):
        """update search in search bar"""
        self.search_tags = self.search_bar.get().strip()
        self.page_num = 0
        self.counter = 0
        self.safebooru_link = "https://safebooru.org/index.php?page=post&s=list&tags="
        self.start()

    def left_key(self, event):
        """go back"""
        if self.counter == 0 and self.page_num == 0:
            # first image of first page
            print("You're at the first image!")
            return
        if self.counter == 0 and self.page_num > 0:
            self.page_num -= 1
            self.change_page_link()
            self.get_thumbnails()
            self.counter = len(self.thumbnails) - 1
        else:
            self.counter -= 1

        self.display_image()

    def right_key(self, event):
        """go forward"""
        if self.counter == len(self.thumbnails) - 1 and len(self.thumbnails) < 40:
            # last image of last page
            print("Last image!")
            return
        if self.counter == len(self.thumbnails) - 1:
            self.page_num += 1
            self.change_page_link()
            self.get_thumbnails()
            self.counter = 0
        else:
            self.counter += 1

        self.display_image()

    def start(self):
        """just starts the search"""
        self.generate_link()
        self.get_thumbnails()
        self.display_image()

    def generate_link(self):
        """generates the proper safebooru link on init"""
        tags_split = self.search_tags.split()
        for tag in tags_split:
            self.safebooru_link += tag + "+"
        self.safebooru_link = self.safebooru_link[:-1] + f"&pid={40*self.page_num}"

        print(self.safebooru_link)

    def change_page_link(self):
        """changes pages"""
        index = 54 + len(self.search_tags)
        self.safebooru_link = self.safebooru_link[:index] + f"&pid={40*self.page_num}"
        print(self.safebooru_link)

    def get_thumbnails(self):
        """gets the safebooru thumbnails from the page"""
        html_text = requests.get(self.safebooru_link, timeout=10).text
        soup1 = BeautifulSoup(html_text, "lxml")
        self.thumbnails = soup1.find_all("span", class_="thumb")

    def display_image(self):
        """displays image"""
        try:
            # just in case the search link is bunk
            imagelink = (
                "https://safebooru.org/"
                + self.thumbnails[self.counter].find("a")["href"]
            )
        except:  # yea idk any exceptions
            self.search_bar.delete(0, tkinter.END)
            self.search_bar.insert(0, "Search unsuccessful")
            return

        image_html_text = requests.get(imagelink, timeout=10).text

        soup2 = BeautifulSoup(image_html_text, "lxml")
        pic = soup2.find("img", id="image")
        self.pic_link = pic["src"]
        self.pic_tags = pic["alt"]
        print(self.pic_link)
        response = requests.get(self.pic_link, timeout=10)
        img = Image.open(BytesIO(response.content))
        pic_width, pic_height = img.size

        # adjust width and/or height if the picture is too big
        if pic_width > 1920 or pic_height > 1080:
            w_adjust = 1920 / pic_width
            h_adjust = 1080 / pic_height
            if w_adjust < h_adjust:
                pic_width = math.floor(pic_width * w_adjust)
                pic_height = math.floor(pic_height * w_adjust)
            else:
                pic_width = math.floor(pic_width * h_adjust)
                pic_height = math.floor(pic_height * h_adjust)
            img = img.resize((pic_width, pic_height), Image.LANCZOS)

        # puts pic into the canvas
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.config(width=pic_width, height=pic_height)
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        self.tags_label.delete(1.0, tkinter.END)
        self.tags_label.insert(1.0, f"Tags: {self.pic_tags}")


def main():
    """main function... duh"""
    root = tkinter.Tk()
    safebooru_webscraper = Kurumi(root)
    root.mainloop()


if __name__ == "__main__":
    main()
    print("Program exited")
