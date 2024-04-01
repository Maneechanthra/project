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
stop_words = thai_stopwords()  # นำเข้าคำหยุดภาษาไทย


# ฟังก์ชัน identity_func ทำหน้าที่รับข้อความเข้ามาแล้วคืนค่าเดิม
def identity_func(text):
    return text


# ฟังก์ชัน perform_removal ใช้สำหรับลบเครื่องหมายวรรคตอน แปลงเป็นตัวพิมพ์เล็ก และตรวจสอบคำใน stop_words หรือไม่
def perform_removal(word):
    word = word.strip()  # ลบช่องว่างที่อยู่ด้านหน้าและด้านหลังของคำ
    word = word.lower()  # แปลงเป็นตัวพิมพ์เล็กทั้งหมด
    word = word.translate(
        str.maketrans("", "", string.punctuation)
    )  # ลบเครื่องหมายวรรคตอน
    if word.isdigit() or (
        word in stop_words
    ):  # ตรวจสอบว่าคำเป็นตัวเลขหรือเป็น stop word หรือไม่
        return ""  # คืนค่าว่างถ้าเป็นเงื่อนไขดังกล่าว
    else:
        return word  # คืนค่าคำที่ผ่านการกรองแล้ว


# เชื่อมต่อกับฐานข้อมูล MySQL
db = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="cis2024_ir_content",
    autocommit=True,
)
cursor = db.cursor()

# สร้างคำสั่ง SQL เพื่อดึงข้อมูลทั้งหมดจากตาราง raw_data_2
sql = "SELECT * FROM raw_data_2 ; "
cursor.execute(sql)
data = cursor.fetchall()

visualization = {}  # สร้างพจนานุกรมเพื่อเก็บชื่อของเอกสาร

docs = []  # สร้างลิสต์เพื่อเก็บคำศัพท์ของเอกสารทั้งหมด
for doc in data:
    text = doc[2]  # นำข้อความจากฟิลด์ที่สามของเอกสาร
    word_seg = word_tokenize(text, keep_whitespace=False)  # แบ่งคำในข้อความ
    word_seg = list(map(perform_removal, word_seg))  # ลบคำที่ไม่จำเป็นออกจากข้อความ
    word_seg = list(filter(lambda word: (word != ""), word_seg))  # กรองคำที่ว่างออก
    docs.append(word_seg)  # เพิ่มคำศัพท์ที่ผ่านการกรองลงในลิสต์

    visualization[doc[0] - 1] = doc[1]  # เก็บชื่อของเอกสารลงในพจนานุกรม

# สร้างเวกเตอร์ TF-IDF จากคำศัพท์ที่เก็บไว้
tfidf_vectorizer = TfidfVectorizer(
    analyzer="word",
    tokenizer=identity_func,
    preprocessor=identity_func,
    token_pattern=None,
)
tfidf_vector = tfidf_vectorizer.fit_transform(
    docs
)  # ทำการ fit ข้อมูลเพื่อให้ได้เวกเตอร์ TF-IDF


# ฟังก์ชัน search ใช้สำหรับค้นหาเอกสารตามคำค้นหา
def search():
    query = search_text.get()  # รับข้อความที่ใส่ในช่องค้นหา
    query_seg = word_tokenize(query, keep_whitespace=False)  # แบ่งคำในข้อความคำค้นหา
    query_vector = tfidf_vectorizer.transform(
        [query_seg]
    )  # แปลงคำค้นหาเป็นเวกเตอร์ TF-IDF

    results = cosine_similarity(
        tfidf_vector, query_vector
    )  # คำนวณความคล้ายคลึงโดยใช้ cosine similarity

    scores = {}  # สร้างพจนานุกรมเพื่อเก็บคะแนนการค้นหาของแต่ละเอกสาร
    doc_id = 0
    for score in results:
        scores[doc_id] = score  # เก็บคะแนนการค้นหาลงในพจนานุกรม
        doc_id += 1

    sorted_desc = dict(
        sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
    )  # เรียงลำดับคะแนนจากมากไปน้อย

    count = 0
    result_text.delete("1.0", tk.END)  # ลบข้อความในช่องแสดงผลลัพธ์ที่แสดงบน GUI
    for vis in sorted_desc:
        print(visualization[vis], scores[vis])  # พิมพ์ชื่อของเอกสารและคะแนนความคล้ายคลึง
        result_text.insert(
            tk.END, f"{visualization[vis]} - {scores[vis]}\n"
        )  # แสดงชื่อเอกสารและคะแนนบน GUI
        count += 1
        if count == 5:
            break


# ส่วนนี้คือส่วนหน้า GUI ซึ่งไม่ได้ให้ข้อมูลเกี่ยวกับการประมวลผลข้อมูลและการค้นหา เพราะฉะนั้นไม่ได้ทำการอธิบายโค้ดในส่วนนี้


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
