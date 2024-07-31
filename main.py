import os
import time
import json
import threading
import re
from tkinter import *
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
from PIL import Image, ImageTk
from fpdf import FPDF

class Chatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("UNLINK CHATBOT")
        self.root.geometry("500x600+0+0")
        self.root.minsize(400, 400)
        self.root.configure(bg='#ffffff')
        self.root.bind('<Return>', self.enter_func)

        self.user_name = None
        self.typing = False
        self.chat_history = []
        self.load_responses()
        self.load_profile()

        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save Chat", command=self.save_chat)
        self.file_menu.add_command(label="Load Chat", command=self.load_chat)
        self.file_menu.add_command(label="Export as PDF", command=self.export_pdf)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Clear Chat", command=self.clear)
        self.edit_menu.add_command(label="Change Background Color", command=self.change_bg_color)

        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Change Font Size", command=self.change_font_size)
        self.view_menu.add_command(label="Show Emoji Menu", command=self.show_emoji_menu)

        self.avatar_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Avatar", menu=self.avatar_menu)
        self.avatar_menu.add_command(label="Change Avatar", command=self.change_avatar)
        
        self.profile_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Profile", menu=self.profile_menu)
        self.profile_menu.add_command(label="Edit Profile", command=self.edit_profile)
        
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

        main_frame = Frame(self.root, bg='#ffffff')
        main_frame.pack(fill=BOTH, expand=True)

        img_chat = Image.open('images.png')
        img_chat = img_chat.resize((30, 30))
        self.photoimg = ImageTk.PhotoImage(img_chat)
        self.avatar_img = self.photoimg

        self.title_frame = Frame(main_frame, bg='#ffffff')
        self.title_frame.pack(side=TOP, fill=X)

        self.avatar_label = Label(self.title_frame, image=self.avatar_img, bg='#ffffff')
        self.avatar_label.pack(side=LEFT, padx=5)

        self.title_label = Label(self.title_frame, text='Chat with Unlink Chatbot', font=('Helvetica', 14, 'bold'), fg='#00796b', bg='#ffffff')
        self.title_label.pack(side=LEFT, padx=5)

        self.online_status = Label(self.title_frame, text='We\'re online', font=('Helvetica', 8), fg='#00796b', bg='#ffffff')
        self.online_status.pack(side=LEFT, padx=5)

        self.minimize_button = Button(self.title_frame, text="_", font=('Helvetica', 8), command=self.minimize_chat, bg='#ffffff')
        self.minimize_button.pack(side=RIGHT, padx=5)

        self.scroll_y = ttk.Scrollbar(main_frame, orient=VERTICAL)
        self.text = Text(main_frame, wrap=WORD, yscrollcommand=self.scroll_y.set, bg='#f9f9f9', fg='#000000', font=('Helvetica', 10))
        self.scroll_y.config(command=self.text.yview)
        self.scroll_y.pack(side=RIGHT, fill=Y)
        self.text.pack(fill=BOTH, expand=True)

        btn_frame = Frame(self.root, bg='#ffffff')
        btn_frame.pack(side=BOTTOM, fill=X, pady=5)

        label_1 = Label(btn_frame, text="TYPE SOMETHING", font=('Helvetica', 8, 'bold'), fg='#00796b', bg='#ffffff')
        label_1.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        self.entry = StringVar()
        self.entry1 = ttk.Entry(btn_frame, textvariable=self.entry, font=('Helvetica', 10))
        self.entry1.grid(row=0, column=1, padx=5, pady=5, sticky=W)

        self.send = Button(btn_frame, text="Send", command=self.send, font=('Helvetica', 10, 'bold'), width=8, bg='#00796b', fg='#ffffff', relief=RAISED)
        self.send.grid(row=0, column=2, padx=5, pady=5, sticky=W)

        self.clear_btn = Button(btn_frame, text="Clear", command=self.clear, font=('Helvetica', 8, 'bold'), width=10, fg='#ffffff', bg='#e53935', relief=RAISED)
        self.clear_btn.grid(row=1, column=0, padx=5, pady=5, sticky=W)

        self.emoji_btn = Button(btn_frame, text="😀", command=self.show_emoji_menu, font=('Helvetica', 10, 'bold'), width=3, bg='#00796b', fg='#ffffff', relief=RAISED)
        self.emoji_btn.grid(row=0, column=3, padx=5, pady=5, sticky=W)

        self.file_btn = Button(btn_frame, text="Attach", command=self.attach_file, font=('Helvetica', 10, 'bold'), width=6, bg='#00796b', fg='#ffffff', relief=RAISED)
        self.file_btn.grid(row=0, column=4, padx=5, pady=5, sticky=W)

        self.msg = ''
        self.label_l1 = Label(btn_frame, text=self.msg, font=('Helvetica', 8, 'bold'), fg='#e53935', bg='#ffffff')
        self.label_l1.grid(row=1, column=1, padx=5, pady=5, sticky=W)

        self.text.tag_configure('user', foreground='blue', justify='right', background='#e0f7fa')
        self.text.tag_configure('bot', foreground='green', justify='left', background='#f0f0f0')
        self.text.tag_configure('timestamp', foreground='gray', font=('Helvetica', 6))


        self.status_bar = Label(self.root, text="Welcome to UNLINK Chatbot", bd=1, relief=SUNKEN, anchor=W, bg='#ffffff')
        self.status_bar.pack(side=BOTTOM, fill=X)

        self.emoji_menu = Menu(self.root, tearoff=0)
        self.emojis = ["😀", "😂", "😊", "😍", "😜", "😎", "😭", "😡", "👍", "🙏"]

        for emoji in self.emojis:
            self.emoji_menu.add_command(label=emoji, command=lambda e=emoji: self.insert_emoji(e))

        self.ask_name()

    def load_responses(self):
        try:
            with open('data/dialogs.json', 'r') as file:
                self.responses = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to load responses: {e}")
            self.responses = []

    def ask_name(self):
        self.text.insert(END, '\nBot: Hello! What is your name?\n', 'bot')
        self.status_bar.config(text="Bot is waiting for your name...")

    def enter_func(self, event):
        self.send.invoke()
        self.entry.set('')

    def clear(self):
        self.text.delete('1.0', END)
        self.entry.set('')

    def show_emoji_menu(self):
        self.emoji_menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def insert_emoji(self, emoji):
        self.entry.set(self.entry.get() + emoji)

    def save_chat(self):
     try:
        with open("chat_history.txt", "w", encoding="utf-8") as file:
            file.write(self.text.get("1.0", END))
        messagebox.showinfo("Save Successful", "Chat history saved successfully.")
     except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save chat history: {e}")


    def load_chat(self):
        try:
            with open("chat_history.txt", "r") as file:
                self.text.delete("1.0", END)
                self.text.insert("1.0", file.read())
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "No previous chat history found.")

    def export_pdf(self):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            chat_text = self.text.get("1.0", END)
            for line in chat_text.split('\n'):
                pdf.cell(200, 10, txt=line, ln=True)
            pdf.output("chat_history.pdf")
            messagebox.showinfo("PDF Exported", "Chat history exported as PDF successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF: {e}")

    def send(self):
        self.typing = True
        user_msg = self.entry.get().strip()
        if user_msg:
            self.text.insert(END, f'You: {user_msg}\n', 'user')
            self.chat_history.append({'You': user_msg})
            self.status_bar.config(text="You are typing...")

            threading.Thread(target=self.bot_response, args=(user_msg,)).start()

    def bot_response(self, user_msg):
        time.sleep(1)
        response = self.find_response(user_msg)
        self.text.insert(END, f'Bot: {response}\n', 'bot')
        self.chat_history.append({'Bot': response})
        self.status_bar.config(text="Bot has responded.")
        self.typing = False

    def find_response(self, user_msg):
        name_pattern = re.compile(r'\b(?:my name is|i am|i\'m)\s*(\w+)', re.IGNORECASE)
        match = name_pattern.search(user_msg)
        if match:
            self.user_name = match.group(1)
            self.title_label.config(text=f'Chat with {self.user_name}')
            return f'Nice to meet you, {self.user_name}!'
        
        for dialog in self.responses:
            if dialog['input'].lower() in user_msg.lower():
                return dialog['response']
        return "I'm sorry, I don't understand that."

    def minimize_chat(self):
        if self.root.state() == 'normal':
            self.root.iconify()

    def change_avatar(self):
        avatar_path = filedialog.askopenfilename(title="Select Avatar", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if avatar_path:
            self.avatar_img = ImageTk.PhotoImage(Image.open(avatar_path).resize((30, 30)))
            self.avatar_label.config(image=self.avatar_img)
    
    def change_bg_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.text.config(bg=color)
            self.status_bar.config(bg=color)

    def change_font_size(self):
        size = simpledialog.askinteger("Font Size", "Enter Font Size:", minvalue=6, maxvalue=24)
        if size:
            self.text.config(font=("Helvetica", size))

    def attach_file(self):
        file_path = filedialog.askopenfilename(title="Select File")
        if file_path:
            self.text.insert(END, f'\nYou attached a file: {os.path.basename(file_path)}\n', 'user')
            self.text.insert(END, f'\nBot: I got this file !! How can i help you ?\n', 'bot')

    def edit_profile(self):
        self.user_name = simpledialog.askstring("Edit Profile", "Enter your name:")
        if self.user_name:
            self.title_label.config(text=f'Chat with {self.user_name}')
            self.text.insert(END, f'\nBot: Nice to meet you, {self.user_name}!\n', 'bot')

    def load_profile(self):
        profile_path = 'profile.json'
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as file:
                    profile_data = json.load(file)
                    self.user_name = profile_data.get('name', 'Unlink Chatbot')
                    self.title_label.config(text=f'Chat with {self.user_name}')
            except (FileNotFoundError, json.JSONDecodeError):
                self.user_name = 'Unlink Chatbot'
        else:
            self.user_name = 'Unlink Chatbot'

    def show_about(self):
        messagebox.showinfo("About", "UNLINK CHATBOT v1.0\nDeveloped by Bhawana Chauhan")

if __name__ == '__main__':
    root = Tk()
    chatbot = Chatbot(root)
    root.mainloop()
