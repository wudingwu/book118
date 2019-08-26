from tkinter import *
import re
import requests
import time
import json
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36" ,
         "Host": "max.book118.com" ,
         "Cookie": "CLIENT_SYS_UN_ID=3rvhcV1f4DgWH0yqDYVhAg==; __cfduid=d51e45c2c03b2a26c5b157a92b027467a1566564408; Hm_lvt_f32e81852cb54f29133561587adb93c1=1566564407; PHPSESSID=04bked12s8ere38s1ag937eaq0; a_7032156124002020=1; Hm_lvt_5d91dc9c92e499ab00ba867fc2294136=1566564689; a_7033023124002020=1; a_7033043124002020=1; a_6035020151002022=1; a_7021143124002020=1; PREVIEWHISTORYPAGES=214671580_63,214672312_68,214672390_13; 94ca48fd8a42333b=1566572872%2C-2; Book118UserFlag=%7B%22214672390%22%3A1566564419%2C%22214672417%22%3A1566566926%2C%22214672431%22%3A1566566971%2C%22214672312%22%3A1566570359%2C%22214671580%22%3A1566572872%7D; Book118UserFlag__ckMd5=c7bffd605722c537; Hm_lpvt_f32e81852cb54f29133561587adb93c1=1566572871; 30d8fb61e609cac11=1566572879%2C1; 30d8fb61e609cac39=1566572879%2C2; Hm_lpvt_5d91dc9c92e499ab00ba867fc2294136=1566572878"}


def getViewToken(url):
    bookID = url.split("/")[-1][:-5]
    bookUrl = "https://max.book118.com/index.php?g=Home&m=NewView&a=index&aid=%s" % bookID
    bookReq = requests.get(url=bookUrl, headers=headers)
    reqText = bookReq.text
    # print(reqText)
    regex = r'aid.*view_token.*}'
    findAidToken = re.findall(regex, reqText)[0].split(",")
    aid = findAidToken[0][15:-2]
    token = findAidToken[1][13:-2]
    return aid,token

def getPicUrl(aid,token):
    pageApi='https://openapi.book118.com/getPreview.html?&project_id=1&aid=%s&view_token=%s&page=1'%(aid,token)
    pageReq = requests.get(url=pageApi)
    reqJson=json.loads(pageReq.text[12:-2])
    pageDict=reqJson["data"]
    maxPage=int(reqJson["pages"]["preview"])
    time.sleep(10)
    for i in range(7,maxPage,6):
        pageIApi = 'https://openapi.book118.com/getPreview.html?&project_id=1&aid=%s&view_token=%s&page=%s' % (aid, token,i)
        # print(pageIApi)
        pageIReq = requests.get(url=pageIApi)
        reqIJson = json.loads(pageIReq.text[12:-2])
        pageIDict = reqIJson["data"]
        # print(pageIDict)
        pageDict.update(pageIDict)
        time.sleep(3)
    return maxPage,pageDict

def bookPageDownload(url):
    aid,token = getViewToken(url)
    maxPage,pageDict = getPicUrl(aid, token)
    pageUrllist=[]
    for i in range(1,maxPage):
        key=str(i)
        pageUrl="http:"+pageDict[key]
        pageUrllist.append(pageUrl)
    return aid,pageUrllist

def makePDF(aid,pageUrlList):
    deskPath = os.path.join(os.path.expanduser("~"), 'Desktop')
    pdf_path = deskPath + "/Book_" + aid + ".pdf"
    pdf = canvas.Canvas(pdf_path)
    (w, h) = landscape(A4)
    for pageUrl in pageUrlList:
        try:
            pdf.drawImage(pageUrl, 0, 0, h, w)
            pdf.showPage()
            time.sleep(3)
        except:
            continue
    pdf.save()
    return True

def book118Pdf(url):
    aid,pageUrlList = bookPageDownload(url)
    # print(pageUrlList)
    makePDF(aid,pageUrlList)
    if makePDF:
        return "Book_"+aid+"已下载到桌面,请查看并修改书名"

class App:
    def __init__(self, master):
        self.master = master
        self.initWidgets()

    def initWidgets(self):
        self.label = Label(self.master, width=30)
        self.label['font'] = ('StSong', 20, 'bold')
        self.label['bg'] = '#dddddd'
        self.label['text'] = '请把书籍地址复制到下面的输入框'
        self.label.pack()
        self.st = StringVar()
        # 创建Entry组件，将其textvariable绑定到self.st变量
        self.Entry1 = Entry(self.master, textvariable=self.st, bd=3,
                            bg="#5F9EA0", font=('StSong', 18)).pack(fill=BOTH, expand=YES)
        bn = Button(self.master, text='开始下载', bg="#dddddd", fg="blue", font=('StSong', 18, 'bold'),
                    command=self.download)
        bn.pack()
        self.text = Text(self.master,
                         width=44,
                         height=4,
                         font=('StSong', 20),
                         foreground='blue')
        self.text.pack(fill=BOTH, expand=YES)

    def download(self):
        urlGetFromUser = self.st.get()
        # print(urlGetFromUser)
        book118Pdf(urlGetFromUser)
        message=book118Pdf(urlGetFromUser)
        self.text.insert(END, message)

root = Tk()
root.geometry('850x300')
root.title("MaxBook下载")
App(root)
root.mainloop()