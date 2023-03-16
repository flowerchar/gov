import tkinter as tk
from tkinter import ttk

# 创建主窗口
root = tk.Tk()
root.geometry("400x300")

# 创建表格
table = ttk.Treeview(root, columns=("column1", "column2", "column3"), show="headings")
table.heading("column1", text="Column 1")
table.heading("column2", text="Column 2")
table.heading("column3", text="Column 3")

# 添加表格数据
for i in range(10):
    table.insert("", "end", values=("Row " + str(i), "Data " + str(i), "More Data " + str(i)))

# 创建滚动条
scrollbar = ttk.Scrollbar(root, orient="vertical", command=table.yview)
scrollbar.pack(side="right", fill="y")

# 将滚动条关联到表格
table.configure(yscrollcommand=scrollbar.set)

# 显示表格
table.pack(side="left", fill="both", expand=True)

# 运行主循环
root.mainloop()