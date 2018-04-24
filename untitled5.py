# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 15:02:20 2018

@author: hhgood
"""

#encoding=utf-8
import io
# allows for image formats other than gif
try:
  # Python2
  import Tkinter as tk
  from urllib2 import urlopen
except ImportError:
  # Python3
  import tkinter as tk
  from urllib.request import urlopen
import requests
import mysql.connector as MySQLdb
import bs4
from PIL import Image,ImageTk
path='https://www.xiachufang.com'
category='/category'
page='?page='
recipe='recipe/'
database='food'
def get_html(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status
        r.encoding = 'UTF-8'
        return r.text
    except:
        return "someting wrong"
class Data(object):
    def __init__(self,path,category,recipe):
        self.path=path
        self.category=category
        self.recipe=recipe
#    def __del__(self):
#        self.con.close()
#        self.conn.close()
    def connect(self):
        try:
            self.conn=MySQLdb.connect(user='root',password='',database='food')
            self.con=self.conn.cursor()
            return "success connect"
        except:
            return "fail connect"
    def CreateDataTable(self):
# 创建数据库表
#        self.con.execute('drop table food_picture')
#        self.con.execute('drop table food_recipe')
#        self.con.execute('drop table kind_food')
#        self.con.execute('drop table cook_kind_1')
#        self.con.execute('drop table cook_kind_2')
#        self.con.execute('drop table cook_kind_3')       
        
        self.con.execute('create table food_picture(food_url varchar(50),step_words text,step_picture varchar(150)) ')
        self.con.execute('create table food_recipe(food_url varchar(50),recipe varchar(50),amount varchar(50))')
        self.con.execute('create table kind_food(kind_url varchar(50),name varchar(50),url varchar(50))')
        self.con.execute('create table cook_kind_1(name_1 varchar(50))')
        self.con.execute('create table cook_kind_2(name_1 varchar(50),name_2 varchar(50),name_2_url varchar(50)) ')
        self.con.execute('create table cook_kind_3(name_2 varchar(50),name_3 varchar(50),name_3_url varchar(50)) ')
        self.conn.commit()
    def CreateCookBook(self): ###########################table cook_kind_1,2,3
        html=get_html(self.path+self.category)
        soup = bs4.BeautifulSoup(html, 'lxml')
        second_file=soup.find_all('div',class_='cates-list clearfix has-bottom-border pb20 mb20')
        for second in second_file:
            second_index=second.find('h3',class_='font20 m0').text
            self.con.execute('insert into cook_kind_1(name_1) values(%s)',[second_index])
#            third_file=second.find('div',class_='cates-list-all clearfix hidden')
            third_index=second.find_all('h4',class_='font16')
            third_name =second.find_all('ul',class_=' has-bottom-border')
            third_name.append(second.find('ul',class_='cates-border-none has-bottom-border'))
            lenth=len(third_index)
            for i in range(lenth):
                forth_index=third_name[i].find_all('li')
                self.con.execute('insert into cook_kind_2(name_1,name_2) values(%s,%s)',[second_index,third_index[i].text.strip()])
                for j in forth_index:
                    self.con.execute('insert into cook_kind_3(name_2,name_3,name_3_url) values(%s,%s,%s)',[third_index[i].text.strip(),j.a.text,j.a['href']])
        self.conn.commit()
        
        
        
    def get_content(self,url):#################### table food_recipe,food_picture
        html = get_html(url)
        soup = bs4.BeautifulSoup(html, 'lxml')
        title=soup.find('h1',class_='page-title').text.strip()
#        print(title)
#        title=url
        recipe=soup.find('div',class_='ings')
        name=recipe.find_all('td', class_='name')
        unit=recipe.find_all('td', class_='unit')
        for i in range(len(name)):
            self.con.execute('insert into food_recipe(food_url ,recipe ,amount) values(%s,%s,%s)',[title,name[i].text.strip(),unit[i].text.strip()])
        steps_list = soup.find('div', class_='steps')
        steps = steps_list.find_all('li')
        for i in range(len(steps)):
            try:
                img_name = steps[i].find('p',class_='text').text.strip()
            except:
                img_name=None
#            print('  '+img_name)
            try:
                img_url=steps[i].find('img')['src']
            except:
                img_url=None
            self.con.execute('insert into food_picture(food_url ,step_words,step_picture) values(%s,%s,%s)',[title,img_name.encode(),img_url])
    def crawler(self,name):##########################  table kind_food
#        count=1
        page_number=1
        while True:
            new_url=self.path+str(name)+'?page='+str(page_number)
            print(new_url)
            html = get_html(new_url)
            soup = bs4.BeautifulSoup(html, 'lxml')
            cook=soup.find('div',class_='normal-recipe-list')
            if cook==None:
                break
            cook_list=cook.find_all('li')
#            count=len(cook_list)
            for c in cook_list:
                self.con.execute("insert into kind_food(kind_url,name,url) values('%s','%s','%s')"%(str(name),c.p.text.strip(),c.a['href']))
                self.get_content(self.path+c.a['href'])
            page_number+=1
            self.conn.commit()
    def search_1(self,var):
        self.con.execute("select distinct food_url from food_recipe where recipe=%s",[var])
#        self.con.execute("select name from kind_food where url in (select distinct food_url from food_recipe where recipe=%s)",[var])
    def search_2(self,var):
        self.con.execute("select distinct food_url from food_picture where step_words like %s",['%'+var+'%'])
#        self.con.execute("select name from kind_food where url in (select distinct food_url from food_picture where step_words like %s)",['%'+var+'%'])
    def search_3(self,var):
        self.con.execute("select name from kind_food where name like %s",['%'+var+'%'])

data=Data(path,category,recipe) 
window=tk.Tk()
h=800
w=1000
window.geometry('%dx%d'%(h,w))
window.title(path)
#tk.Label(window,text=path).pack()
frame_l=tk.Frame(window,width=400)
frame_l.place(x=0,y=0)
frame_r=tk.Frame(window,width=400)
frame_r.place(x=400,y=0)

tk.Label(frame_l,text="功能").pack()

var_1=tk.Variable()
var_1.set("未连接")
var_2=tk.Variable()
var_2.set("未构建")
var_3=tk.StringVar()
var_4=tk.StringVar() 
var_5=tk.StringVar() 
var_6=tk.StringVar() 
var_7=tk.StringVar()
var_7.set('0')
var_8=tk.StringVar()
var_9=tk.StringVar() 
var_10=tk.StringVar() 
var_11=tk.StringVar()
var_11.set("目录")
var_12=tk.StringVar()
var_12.set("步骤") 
var_13=tk.StringVar()
var_13.set("用料")
var_14=tk.StringVar()
var_14.set("搜索结果")


def link():
    var_1.set(data.connect())
tk.Button(frame_l,text='连接数据库',command=link).pack()
def create():
    try:
        data.CreateDataTable() 
        data.CreateCookBook()
        data.conn.commit()
        var_2.set("构建成功")
    except:
#        raise
        var_2.set("已构建")
#    data.con.execute('select name_3 from cook_kind_3' )
    data.con.execute('select name_1 from cook_kind_1' )
    var_4.set(data.con.fetchall())
tk.Button(frame_l,text='构建数据库',command=create).pack()

def fill_1():
    value=lb.get(lb.curselection())
    data.con.execute("select name_3_url from cook_kind_3 where name_3='%s'"%(value) )
    result=data.con.fetchone()[0]
    try:
        data.crawler(result)
        var_3.set(result+'success')
    except:
        var_3.set(result+'fail')
        raise
tk.Button(frame_l,text='填充数据库_1',command=fill_1).pack()
tk.Label(frame_l,textvariable=var_3,bg='green',font=('Arial',12)).pack()

def back_detail():
    value=lb.get(lb.curselection())
    data.con.execute("select name_3 from cook_kind_3 where name_2=(select name_2 from cook_kind_3 where name_3_url=(select kind_url from kind_food where name=%s))",value)
    result=data.con.fetchall()
    if result==[]:
        data.con.execute("select name_2 from cook_kind_2 where name_1=(select name_1 from cook_kind_2 where name_2=(select name_2 from cook_kind_3 where name_3=%s))",value)
        result=data.con.fetchall()
        if result==[]:
            data.con.execute("select name_1 from cook_kind_1") 
            result=data.con.fetchall()
    var_4.set(result)
    var_11.set('目录('+str(len(result))+')')
tk.Button(frame_l,text='回退细节_1',command=back_detail).pack()

def fill_detail():
    value=lb.get(lb.curselection())
    data.con.execute("select name_2 from cook_kind_2 where name_1='%s'"%(value))
    result=data.con.fetchall()
    if result==[]:
        data.con.execute("select name_3 from cook_kind_3 where name_2='%s'"%(value))
        result=data.con.fetchall()
        if result==[]:
            data.con.execute("select name from kind_food where kind_url=(select name_3_url from cook_kind_3 where name_3='%s')"%(value))
            result=data.con.fetchall()
            if result==[]:
                var_9.set(value)
                var_10.set(value)
                fill_2()
                fill_4()
                return 
    var_4.set(result)
    var_11.set('目录('+str(len(result))+')')
tk.Button(frame_l,text='显示细节_1',command=fill_detail).pack()
tk.Label(frame_l,text='搜索输入').pack()

e=tk.Entry(frame_l)
e.pack()
def Search_1():
    var=e.get()
    data.search_1(var)
    result=data.con.fetchall()
#    t.insert('end',result)
    var_5.set(result)
    var_14.set('搜索结果('+str(len(result))+')')
tk.Button(frame_l,text="用料搜索",command=Search_1).pack()
#t.pack()

def Search_2():
    var=e.get()
    data.search_2(var)
    result=data.con.fetchall()
    var_5.set(result)
    var_14.set('搜索结果('+str(len(result))+')')
#    t.insert('end',result)
tk.Button(frame_l,text="工艺搜索",command=Search_2).pack()

def Search_3():
    var=e.get()
    data.search_3(var)
    result=data.con.fetchall()
    var_5.set(result)
    var_14.set('搜索结果('+str(len(result))+')')
#    t.insert('end',result)
tk.Button(frame_l,text="菜名搜索",command=Search_3).pack()
tk.Label(frame_l,textvariable=var_14).pack()
lb_2=tk.Listbox(frame_l,listvariable=var_5)
lb_2.pack()

def fill_2():
    try:
        value=lb_2.get(lb_2.curselection())
    except:
        value=lb.get(lb.curselection())
    data.con.execute("select step_words from food_picture where food_url='%s'"%(value))
    result=data.con.fetchall()
    var_6.set(result)
    var_9.set(value)
    var_12.set('步骤('+str(len(result))+')')
tk.Button(frame_l,text='显示做菜步骤_1_2',command=fill_2).pack()

def fill_4():
    try:
        value=lb_2.get(lb_2.curselection())
    except:
        value=lb.get(lb.curselection())
    data.con.execute("select recipe from food_recipe where food_url=%s",value)
    result=data.con.fetchall()
    var_8.set(result)
    var_10.set(value)
    var_13.set('用料('+str(len(result))+')')
tk.Button(frame_l,text='显示用料_1_2',command=fill_4).pack()

def fill_3():
    value=lb_3.get(lb_3.curselection())
    data.con.execute("select step_picture from food_picture where step_words=%s",value)
    img_url=data.con.fetchone()[0]
    print(img_url)
    if img_url!=None:
        image_bytes = urlopen(img_url).read()
        data_stream = io.BytesIO(image_bytes)
        pil_image = Image.open(data_stream)
        tk_image = ImageTk.PhotoImage(pil_image)
        label.config(image=tk_image)
        label.image=tk_image
    else :
        label.config(text='空')
        label.config(image=None)
tk.Button(frame_l,text='显示图片_3',command=fill_3).pack()
label = tk.Label(frame_l)
label.pack()
tk.Label(frame_l,text='picture').pack()
####################################################################################################################
tk.Label(frame_r,text="结果").pack()
tk.Label(frame_r,textvariable=var_1).pack()
tk.Label(frame_r,textvariable=var_2).pack()
frame_list=tk.Frame(frame_r)
frame_list.pack()
tk.Label(frame_list,textvariable=var_11).pack()
lb=tk.Listbox(frame_list,listvariable=var_4)
lb.pack()

frame_list_2=tk.Frame(frame_r)
frame_list_2.pack()


def count():
    try:
        value=lb_2.get(lb_2.curselection())
    except:
        value=lb.get(lb.curselection())
    data.con.execute("select step_picture from food_picture where food_url='%s'"%(value))
    result=data.con.fetchall()
    number=0
    for i in result:
        if i!=None:
            number+=1
    print(number)
    var_7.set(str(number))
tk.Label(frame_list_2,textvariable=var_7).pack()
tk.Button(frame_list_2,text='图片数量_1_2',command=count).pack()
tk.Label(frame_list_2,textvariable=var_9,bg='green',font=('Arial',12)).pack()
tk.Label(frame_list_2,textvariable=var_12).pack()
lb_3=tk.Listbox(frame_list_2,listvariable=var_6)
lb_3.pack()



#frame=tk.Frame(window,width=1000,height=1000)
#frame.pack()
#t = tk.Text(frame_r,height=2)
#scrollbar.config(command=t.yview)
#scrollbar=tk.Scrollbar(frame,orient='vertical')
#scrollbar.pack(side='right', fill='y')
#window.title('test')



#    with open(value+'.png','wb+') as f:
#        f.write(requests.get(img_url).content)
frame_list_2=tk.Frame(frame_r)
frame_list_2.pack()


#frame_picture=tk.Toplevel()



tk.Label(frame_list_2,textvariable=var_10,bg='green',font=('Arial',12)).pack()
tk.Label(frame_list_2,textvariable=var_13).pack()
lb_4=tk.Listbox(frame_list_2,listvariable=var_8)
lb_4.pack()


#result=0
#def show_me():
#    var=e.get()
#    data.con.execute('select step_words from food_picture where food_url=%s',[var])
#    result=data.con.fetchall()
#    var_6.set(result)
#tk.Button(frame_l,text='search',command=show_me).pack()

window.mainloop()
