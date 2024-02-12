from tkinter import Tk, Button, Frame, Label, PhotoImage, Canvas
from PIL import Image, ImageTk

def fit(image: Image.Image, box: tuple[int, int]):
    if image.width > image.height:
        width = box[0]
        r = width / image.width
        height = image.height * r

        return image.resize((int(width), int(height)))
    height = box[1]
    r = height / image.height
    width = image.width * r

    return image.resize((int(width), int(height)))

def center(canvas: Canvas, image: Image.Image, size: tuple[int, int]):
    img = ImageTk.PhotoImage(fit(image, size))

    canvas.create_image((size[0] - img.width()) // 2, (size[1] - img.height()) // 2, image=img, anchor="nw")
    canvas.image = img
    

class UIManager:
    def __init__(self):
        self.root = Tk()
        self.load_init()
        self.root.mainloop()

    def load_init(self):
        b = Button(self.root, text="Join Game", command=self.join)
        b.pack()

    def join(self):
        pass

    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()

    def load_game(self):
        opponent_frame = Frame(self.root)

        for index, player in enumerate(players):
            name = Label(opponent_frame, text=player[1])
            name.grid(row=0, column=index)

            cards = Label(opponent_frame, text=player[2])
            cards.grid(row=1, column=index)

        opponent_frame.grid(row=0, column=0, sticky="")

        pile_size = (100, 100)

        pile_frame = Canvas(self.root, width=pile_size[0], height=pile_size[1])
        center(pile_frame, Image.open("assets/0 blue.svg.png"), pile_size)

        pile_frame.grid(row=1, column=0)

        hand_frame = Frame(self.root)

        hand_frame.grid(row=2)
