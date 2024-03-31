from tkinter import *
from tkinter import scrolledtext
import tkinter as tk  # Added import
import operator
import pymysql
from pathlib import Path
from PIL import Image, ImageTk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords
import re
import string

####################### function search content for kuse of ir sucject #########################################
stop_words = thai_stopwords()


def identity_func(text):
    return text


def perform_removal(word):
    word = word.strip()
    word = word.lower()
    word = word.translate(str.maketrans("", "", string.punctuation))
    if word.isdigit() or (word in stop_words):
        return ""
    else:
        return word


db = pymysql.connect(
    host="localhost", user="root", password="", database="ir_content", autocommit=True
)
cursor = db.cursor()

sql = "SELECT * FROM raw_data_3 ; "
cursor.execute(sql)
data = cursor.fetchall()
visualization = {}

docs = []
for doc in data:
    text = doc[2]
    word_seg = word_tokenize(text, keep_whitespace=False)
    word_seg = list(map(perform_removal, word_seg))
    word_seg = list(filter(lambda word: (word != ""), word_seg))
    docs.append(word_seg)

    visualization[doc[0] - 1] = doc[1]

tfidf_vectorizer = TfidfVectorizer(
    analyzer="word",
    tokenizer=identity_func,
    preprocessor=identity_func,
    token_pattern=None,
)

tfidf_vector = tfidf_vectorizer.fit_transform(docs)


def search():
    query = search_text.get()
    query_seg = word_tokenize(query, keep_whitespace=False)
    query_vector = tfidf_vectorizer.transform([query_seg])

    results = cosine_similarity(tfidf_vector, query_vector)
    print(query_seg)

    scores = {}
    doc_id = 0
    for score in results:
        scores[doc_id] = score
        doc_id += 1

    sorted_desc = dict(sorted(scores.items(), key=operator.itemgetter(1), reverse=True))

    count = 0
    result_text.delete("1.0", tk.END)
    for vis in sorted_desc:
        result_text.insert(tk.END, f"{visualization[vis]} - {scores[vis]}\n")
        count += 1
        if count == 5:
            break


############################## User Interface ##################################
app = Tk()
app.title("Search content")
app.geometry("1300x813+300+200")
app.configure(bg="#eff6ff")
app.resizable(False, False)

# frame = Frame(app, width=1100, height=500, bg="white", borderwidth=20)
# frame.place(x=90, y=50)

ASSETS_PATH = Path(__file__).resolve().parent / "assets"
image = Image.open(ASSETS_PATH / "bg2.png")
logo = ImageTk.PhotoImage(image)
label = Label(app, image=logo, bg="white")
label.place(x=0, y=0)

ASSETS_PATH = Path(__file__).resolve().parent / "assets"
image2 = Image.open(ASSETS_PATH / "search2.png")
logo2 = ImageTk.PhotoImage(image2)
label2 = Button(
    app,
    image=logo2,
    bg="#75b9ff",
    command=search,
    border=0,
)
label2.place(x=715, y=230)

# heading = Label(
#     # frame,
#     text="Seach Content",
#     fg="#ffffff",
#     bg="#7cbbf4",
#     font=("Microsoft YaHei UI", 50, "bold"),
# )
# heading.place(x=480, y=32)

search_text = Entry(
    width=27,
    fg="white",
    border=0,
    bg="#75b9ff",
    font=("Microsoft YaHei UI", 20, "bold"),
)
search_text.place(x=160, y=235)
search_text.insert(0, "พิมพ์คำที่ต้องการค้นหา")

# Frame(
#     frame,
#     width=500,
#     height=1,
#     bg="#d0d0d0",
# ).place(x=480, y=130)

# Button(
#     frame,
#     width=40,
#     pady=2,
#     text="ค้นหา",
#     bg="#7cbbf4",
#     fg="black",
#     border=0,
#     font=("Microsoft YaHei UI Light", 16),
#     command=search,
# ).place(x=480, y=140)

# label = Label(
#     frame,
#     text="แสดงผลลัพธ์",
#     bg="white",
#     fg="#57a1f8",
#     font=("Microsoft YaHei UI Light", 18, "bold"),
# )
# label.place(x=480, y=200)

result_text = scrolledtext.ScrolledText(
    width=50,
    height=9,
    fg="#5c92ca",
    font=("Helvetica", 14),
    border=0,
)
result_text.place(x=160, y=320)

app.mainloop()
