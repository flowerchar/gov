import time
from tkinter import ttk
from tkinter import *

from database.mysql import useDBStore

db_data = tuple()
DB = useDBStore()

root = Tk()
def begin_month(event):
    date[1] = beginMon.get()
def finish_year(event):
    date[2] = finishYear.get()
def finish_month(event):
    date[3] = finishMon.get()
def begin_year(event):
    date[0] = beginYear.get()
def btn_click():
    for i in tree_date.get_children():
        tree_date.delete(i)
    TIME = f'{date[0]}-0{date[1]}_{date[2]}-0{date[3]}'
    db_data = DB.search_mysql(TIME)
    for index, value in enumerate(db_data):
        tree_date.insert('',index,text=f'{index+1}',  values=(index+1, value[0], value[1]))
    DB.draw_cloud(TIME)

if __name__ == '__main__':



    # 时间变量声明
    beginYear = StringVar()
    beginMon = StringVar()
    finishYear = StringVar()
    finishMon = StringVar()
    date = [0,0,0,0]

    root.title('市州区县词频统计')
    height = root.winfo_screenheight()
    width = root.winfo_screenwidth()
    root.geometry(f'800x600+{(width-800)//2}+{(height-600)//2}')

    CurrentTimeLabel = Label(root,relief='raised', text=time.strftime("%Y-%m-%d"), foreground='green', font=("黑体",80),
                             image='::tk::icons::information',cursor='mouse',bitmap='hourglass',compound='left')
    box = ttk.Combobox(root, textvariable=beginYear,values=[str(i) for i in range(2015,2024)])
    box2 = ttk.Combobox(root, textvariable=beginMon,values=[str(i) for i in range(1,13)])
    box.bind("<<ComboboxSelected>>", begin_year)
    box2.bind("<<ComboboxSelected>>", begin_month)
    box3 = ttk.Combobox(root, textvariable=finishYear,values=[str(i) for i in range(2015,2024)])
    box4 = ttk.Combobox(root, textvariable=finishMon,values=[str(i) for i in range(1,13)])
    box3.bind("<<ComboboxSelected>>", finish_year)
    box4.bind("<<ComboboxSelected>>", finish_month)
    btn = Button(root,text='查询',command=btn_click)

    tree_date = ttk.Treeview(root, columns=('index', 'title', 'url'), show='headings')
    tree_date.heading('index', text='序号')
    tree_date.heading('title', text='标题')
    tree_date.heading('url', text='链接')

    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree_date.yview)
    tree_date.configure(yscrollcommand=scrollbar.set)

    CurrentTimeLabel.pack()
    ttk.Separator(root).pack(fill="x", pady=5)  # 添加分割
    box.pack()
    box2.pack()
    ttk.Separator(root).pack(fill="x", pady=5)  # 添加分割
    box3.pack()
    box4.pack()
    btn.pack()
    tree_date.pack(side='left',fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    root.mainloop()

