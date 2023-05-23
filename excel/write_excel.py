import openpyxl as op

def write_to_excel(data:str, file_name:str):
    wb = op.Workbook()
    ws = wb['Sheet']
    ws.append(['序号','地区', '词频'])
    for index, loc in enumerate(data):
        ws.append([index+1, loc, data[loc]])
    wb.save(file_name)