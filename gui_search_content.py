from tkinter import *
from tkinter import scrolledtext
import tkinter as tk
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
    host="localhost",
    user="root",
    password="",
    database="cis2024_ir_content",
    autocommit=True,
)
cursor = db.cursor()

sql = "SELECT * FROM raw_data_2 ; "
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

    # visualization[doc[0] - 1] = "DocID" + str(doc[0]) + ":" + doc[1]

    visualization[doc[0] - 1] = doc[1]

tfidf_vectorizer = TfidfVectorizer(
    analyzer="word",
    tokenizer=identity_func,
    preprocessor=identity_func,
    token_pattern=None,
)

tfidf_vector = tfidf_vectorizer.fit_transform(docs)
print(tfidf_vector)


def search():
    query = search_text.get()
    query_seg = word_tokenize(query, keep_whitespace=False)
    query_vector = tfidf_vectorizer.transform([query_seg])

    results = cosine_similarity(tfidf_vector, query_vector)
    # print(query_seg)

    scores = {}
    doc_id = 0
    for score in results:
        scores[doc_id] = score
        doc_id += 1

    sorted_desc = dict(sorted(scores.items(), key=operator.itemgetter(1), reverse=True))

    count = 0
    result_text.delete("1.0", tk.END)
    for vis in sorted_desc:
        print(visualization[vis], scores[vis])
        result_text.insert(tk.END, f"{visualization[vis]} - {scores[vis]}\n")
        count += 1
        if count == 5:
            break


############################## User Interface ##################################
app = Tk()
app.title("Search content")
app.geometry("807x700+300+200")
app.configure(bg="#eff6ff")
app.resizable(False, False)


ASSETS_PATH = Path(__file__).resolve().parent / "assets"
image = Image.open(ASSETS_PATH / "bg5.png")
logo = ImageTk.PhotoImage(image)
label = Label(app, image=logo, bg="white")
label.place(x=0, y=0)

ASSETS_PATH = Path(__file__).resolve().parent / "assets"
image2 = Image.open(ASSETS_PATH / "button.png")
logo2 = ImageTk.PhotoImage(image2)
label2 = Button(
    app,
    image=logo2,
    bg="#798da4",
    command=search,
    border=0,
    activebackground="#798da4",
)
label2.place(x=20, y=635)

search_text = Entry(
    width=50,
    fg="black",
    border=0,
    bg="#ffffff",
    font=("Microsoft YaHei UI", 16),
)
search_text.place(x=140, y=180)
search_text.insert(0, "พิมพ์คำที่ต้องการค้นหา")

result_text = scrolledtext.ScrolledText(
    width=65,
    height=15,
    fg="#133958",
    bg="#f1f1f1",
    font=("Helvetica", 14),
    border=0,
)
result_text.place(x=30, y=260)
app.mainloop()
