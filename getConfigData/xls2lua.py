# coding=utf-8
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from future import standard_library
from future.builtins import *
#py3 compatibility

import getConfigData.getFilePath
import datetime
import sys
import hashlib
import codecs
import json
from inspect import currentframe
from locale import getpreferredencoding
import os, shutil
from os import (listdir, mkdir, system)
from os.path import (isfile, join, splitext, exists, basename, isdir)
from collections import defaultdict

from xlrd import open_workbook, XLRDError
import unicodecsv as csv
import time
errorLog = open("./setuplog.txt", 'a', encoding="utf-8")

if not sys.stdout.encoding:
    reload(sys)
    sys.setdefaultencoding("utf-8")
output_encoding = sys.stdout.encoding
if not output_encoding or output_encoding == 'US-ASCII' or output_encoding == 'ascii':
    output_encoding = 'utf-8'
# print('check encoding', output_encoding)

if sys.stderr.encoding == 'cp936':
    class UnicodeStreamFilter(object):
        def __init__(self, target):
            self.target = target
            self.encoding = 'utf-8'
            self.errors = 'replace'
            self.encode_to = self.target.encoding

        def write(self, s):
            if isinstance(s, bytes):
                s = s.decode('utf-8')
            s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
            self.target.write(s)
    sys.stderr = UnicodeStreamFilter(sys.stderr)

#encoding = getpreferredencoding()

class formatstring(str):
    def __new__(cls, value):
        return str.__new__(cls, value)
    def __init__(self, value):
        pass

begin_temple = """
return {
"""
row_temple = """
    [%s] = {
"""
cell_temple = """\
        %s = %s,
"""
row_end_temple = """\
    },
"""
end_temple = """
}
"""
map_flag = '______IS__MAP______ = true,'

def assertx(value, message):
    if __debug__ and not value:
        #tb =
        #f = sys.exc_info()[2].tb_frame.f_back
        #back_frame = currentframe().f_back
        #lineno = back_frame.f_lineno - 1
        #filename = back_frame.f_code.co_filename
        #dataPreprocess = '\n' * lineno + 'assert False'
        try:
            code = compile('1 / 0', '', 'eval')
            exec(code)
        except ZeroDivisionError:
            tb = sys.exc_info()[2].tb_next
            assert tb
            # raise AssertionError, str(message).encode('utf-8'), tb
    return value

def csv_from_excel(xls_name):
    workbook = open_workbook(xls_name)#, encoding_override='gbk')
    #sh = wb.sheet_by_name('Sheet1')
    for sheet in workbook.sheets():
        with open(sheet.name + '.csv', 'wb') as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
            for rownum in range(sheet.nrows):
                writer.writerow(sheet.row_values(rownum))

def is_struct(val_type):
    return val_type.startswith('struct') or val_type.startswith('xstruct')

def force_int(val):
    try:
        try:
            fval = float(val)
        except:
            fval = eval(val)
        try:
            ival = int(val)
        except:
            ival = int(eval(val))
        assertx(abs(fval - ival) < 0.0001, "要求int,可能填入 float(int require):%s" % val)
        return ival
    except:
        raise
        # raise AssertionError, str("非法的int(invalid int value):%s" % val).encode('utf-8')

#基础类型
type_tbl = {
    'int': int,
    'float': float,
    'string': str,
    'formula': str,
    'format_string': formatstring,
    'bool': bool,
}


default_tbl = {
    'int': 0,
    'float': 0.0,
    'string': '',
    'formula': '',
    'format_string': formatstring(''),
    'bool': False,
}

legal_extra_types = ('default', 'key', 'ignored', "server", "client")

row_keys_ = {}
row_values_ = {}

# 是否客户端
# is_client = (sys.argv[1] =="client")
# print("-->> is_client", is_client)
def cell_to_value(col_type, value):
    if col_type.startswith('xstruct'):
        templates = col_type.split("(")[1].split(")")[0]
        template_lst = templates.split("|")
        value = str(value)
        values = value.strip()
        value_lst = values.split("|")
        value = {}
        for i, j in enumerate(template_lst):
            if i >= len(value_lst):
                break
            if j.find("[") != -1 and j.find("]") != -1:
                key = j.split("[")[1].split("]")[0]
                sub_col_type = j.split("[")[0]
            else:
                key = i + 1
                sub_col_type = j
            value[key] = cell_to_value(sub_col_type, value_lst[i])

    elif col_type.startswith('struct'):
        templates = col_type.split("(")[1].split(")")[0]
        template_lst = templates.split("|")
        value = str(value)
        values = value.strip()
        value_lst = values.split("|")
        value = {}
        for i, j in enumerate(template_lst):
            if i >= len(value_lst):
                # print('ERROR: struct data no empty, %s: %s' % (col_type, value))
                raise Exception('struct不允许默认值, 如果有必要尝试使用xstruct')
            if j.find("[") != -1 and j.find("]") != -1:
                key = j.split("[")[1].split("]")[0]
                sub_col_type = j.split("[")[0]
            else:
                key = i + 1
                sub_col_type = j
            value[key] = cell_to_value(sub_col_type, value_lst[i])
 
    elif col_type.startswith('list'):
        sub_col_type = col_type.split("<")[1].split(">")[0]
        value = str(value)
        values = value.strip()
        value_lst = values.split(",")
        value = {}
        for i, j in enumerate(value_lst):
            key = i + 1
            value[key] = cell_to_value(sub_col_type, j)

    elif col_type in type_tbl:
        if col_type == 'int':
            value = force_int(value)
        elif col_type == 'bool':
            if not isinstance(value, bool):
                try:
                    value = int(value)
                    if value == 0:
                        value = False
                    elif value == 1:
                        value = True
                    else:
                        errmsg = "不合法的bool值，可选[true | false | 0 | 1] 实际值->(%s)" % value
                        # print(errmsg)
                        raise Exception(errmsg)
                except:
                    raise
                # if isinstance(value, basestring):
                if isinstance(value, str):
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                    else:
                        errmsg = "不合法的bool值，可选[true | false | 0 | 1] 实际值->(%s)" % value
                        # print(errmsg)
                        raise Exception(errmsg)
        elif col_type == 'float':
            try:
                value = float(value)
            except:
                value = eval(value)
        elif col_type == 'string':
            try:
                fv = int(value)
                if fv == value:
                    value = fv
            except:
                pass

            value = str(value)
        elif col_type == 'format_string':
            try:
                fv = int(value)
                if fv == value:
                    value = fv
            except:
                pass

            value = formatstring(value)
        else:
            value = type_tbl[col_type](value)

    else:
        try:
            value = float(value)
            value = int(value)
            value = unicode(value)
        except:
            pass
        enum_name_tbl = enum_tbl[col_type]

        # if enum_name_tbl.has_key(value):
        if value in enum_name_tbl:
            value = enum_name_tbl[value]
        else:
            try:
                value = int(value)
            except:
                assertx(False, '未定义枚举值 [%s]:[%s]' % (col_type, value))
            assertx(value in enum_name_tbl.values(), '未定义枚举值 [%s]:[%s]' % (col_type, value))

    return value

def sheet_to_dict(sheet):
    type_row = sheet.row_values(0)
    name_row = sheet.row_values(1)
    if len(type_row) == 0 or len(name_row) == 0:
        # print('sheet type or name row not exist')
        return
    if not type_row[0] or not name_row[0]:
        # print('sheet type or name row invalid ')
        return
    col_types = []
    row_key = None
    ignored_names = []
    # 仅客户端使用的字段
    only_client_names = []
    # 仅服务器使用的字段
    only_server_names = []
    for i, column in enumerate(type_row):
        try:
            if not column:
                # print('info: colume %d is empty, ignore others behind' % (i + 1))
                type_row = type_row[:i]
                break
            col_type = column
            if column.find('@') != -1:
                splits = column.split('@')
                col_type = splits[0]
                splits = splits[1:]
                for sp in splits:
                    assertx(sp in legal_extra_types,
                            '@incorrect suffix after[%s], can only be %s' % (sp, ' '.join(legal_extra_types)))
                    if sp == 'ignored':
                        ignored_names.append(name_row[i])
                    elif sp == 'key':
                        row_key = name_row[i]
                        row_keys_[sheet.name] = row_key
                    elif sp == "server":
                        # 字段仅服务器使用
                        only_server_names.append(name_row[i])
                    elif sp == "client":
                        # 字段仅客户端使用
                        only_client_names.append(name_row[i])
            if col_type.startswith('list'):
                val_type = col_type.split('<')[1].split('>')[0]
                if val_type not in type_tbl and not is_struct(val_type):
                    assertx(val_type in enum_tbl, 'unknown emum type:[%s]' % val_type)
                col_type = 'list'

            elif col_type.startswith('xlist'):
                val_type = col_type.split('<')[1].split('>')[0]
                if val_type not in type_tbl and not is_struct(val_type):
                    assertx(val_type in enum_tbl, 'unknown emum type:[%s]' % val_type)
                col_type = 'xlist'

            elif col_type.startswith('dict'):
                val_type = col_type.split('<')[1].split('>')[0]
                if val_type not in type_tbl and not is_struct(val_type):
                    assertx(val_type in enum_tbl, 'unknown emum type[%s]' % val_type)
                col_type = 'dict'

            elif col_type not in type_tbl and not is_struct(col_type):
                assertx(col_type in enum_tbl, 'unknown emum type[%s]' % col_type)

            col_types.append(col_type)
        except:
            # print(sys.stderr.write('ERROR: row:%s column:[%s] \n' % (i + 1, column)))
            # print >> sys.stderr.write('ERROR: row:%s column:[%s] \n' % (i + 1, column))
            raise

    normal_name_tbl = {}
    list_name_tbl = defaultdict(list)
    for i, name in enumerate(name_row):
        if name.find('|') != -1:
            list_name_tbl[name].append(i)
        else:
            normal_name_tbl[name] = i

    title_row = sheet.row_values(2)
    keys_ = {}
    empty_row = set([''])
    for rownum in range(3, sheet.nrows):
        try:
            row = sheet.row_values(rownum)
            if set(row) == empty_row:
                break
            null_index_tbl = {}
            for i, column in enumerate(type_row):
                null_index_tbl[i] = (row[i] == '')

                col_type = col_types[i]

                if col_type == 'list':
                    if row[i] == '':
                        row[i] = []
                    else:
                        row[i] = str(row[i])
                        val_type = column.split('<')[1].split('>')[0]
                        values = [val.strip() for val in row[i].split(',')]
                        row[i] = [cell_to_value(val_type, val) for val in values]

                elif col_type == 'xlist':
                    if row[i] == '':
                        row[i] = []
                    else:
                        row[i] = str(row[i])
                        val_type = column.split('<')[1].split('>')[0]
                        values = [val.strip() for val in row[i].split('|')]
                        row[i] = [cell_to_value(val_type, val) for val in values]

                elif col_type == 'dict':
                    if row[i] == '':
                        row[i] = {}
                    else:
                        row[i] = str(row[i])
                        val_type = column.split('<')[1].split('>')[0]
                        values = [val.strip() for val in row[i].split(',')]
                        lsts = [cell_to_value(val_type, val) for val in values]
                        row[i] = {val['id']:val for val in lsts}

                elif row[i] == '' and (('@default' in column) or ('@ignored' in column)):
                    if col_type in type_tbl:
                        row[i] = default_tbl[col_type]
                    elif is_struct(col_type):
                        row[i] = {}
                    else:
                        row[i] = 0

                else:
                    assertx(row[i] != '', 'line%s column[%s] can not be empty' % (rownum + 1, title_row[i]))
                    row[i] = cell_to_value(col_type, row[i])
                    if name_row[i] == row_key:
                        assertx(row[i] not in keys_,
                                ' DUPLICATE key row:%s vs row:%s' % (title_row[i], row[i]))
                        keys_[row[i]] = True
            data = {}
            # for name, index in normal_name_tbl.iteritems():
            for name, index in normal_name_tbl.items():
                if name == '':
                    continue
                if name in ignored_names:
                    continue
                # # 导服务器的时候忽略仅有客户端的字段
                # if (not is_client) and (name in only_client_names):
                #     continue
                # # 导客户端的时候忽略仅为服务器的字段
                # if is_client and (name in only_server_names):
                #     continue
                data[name] = row[index]
            list_name_len_tbl = {}
            # for name, indexes in list_name_tbl.iteritems():
            for name, indexes in list_name_tbl.items():
                choosed_indexs = []
                first = False
                for i in reversed(indexes):
                    if not first and null_index_tbl[i]:
                        continue
                    if not first:
                        first = True
                    choosed_indexs.append(i)
                old_name = name
                name_num, name = name.split('|')
                data[name] = [
                    row[i] for i in reversed(choosed_indexs)]
                if name_num:
                    data_len = list_name_len_tbl.get(name_num)
                    if data_len:
                        assertx(len(data[name]) == data_len,
                        '合并列[%s]的长度[%s]与同组[%s]合并列长度[%s]不一致' %
                                (old_name, len(data[name]), name_num, data_len))
                    else:
                        list_name_len_tbl[name_num] = len(data[name])
        except:
            errorLog.write("@@@@@@@@@  WrongInfo: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
            errorLog.write('ERROR: row: %s column: %s， 列名是： [%s]\n' % (rownum + 1, i, title_row[i]))
            # print(sys.stderr.write('ERROR: row: %s column: %s[%s]\n' % (rownum + 1, i, title_row[i])))
            # print >> sys.stderr.write('ERROR: row: %s column: %s[%s]\n' % (rownum + 1, i, title_row[i]))
            raise
        yield data


def format_value(value):
    # if isinstance(value, basestring):
    if isinstance(value, str):
        if type(value) == formatstring:
            form = '[=[%s]=]'
            return form % value
        else:
            if '\n' in value:
                form = '[=[%s]=]'
            elif '"' in value:
                form = '[[%s]]' if "'" in value else "'%s'"
            else:
                form = '"%s"'

            return form % value
    elif isinstance(value, bool):
        if value:
            return "true"
        else:
            return "false"
    elif isinstance(value, list):
        value = ', '.join([format_value(v) for v in value])
        value = '{%s}' % value

    elif isinstance(value, dict):
        value = ', '.join(["[%s] = %s"%(format_value(k), format_value(v)) for k, v in value.items()])
        value = '{%s}' % value

    return str(value)

def to_lua(name, data, xls_name, output):
    if not exists(output):
        mkdir(output)
    lua_name = join(output, name + '.lua')
    with open(lua_name, 'wb') as file:
        comment = '-- %s' % xls_name
        file.write(comment.encode('utf-8'))
        file.write(begin_temple.encode('utf-8'))
        is_map = None
        for i, row in enumerate(data):
            key_name = row_keys_.get(name, 'id')
            if is_map == None and row.get(key_name) != None:
                is_map = True
            key = row.get(key_name, i + 1)

            # if isinstance(key, basestring):
            if isinstance(key, str):
                key = format_value(key)
            file.write((row_temple % key).encode('utf-8'))
            for key, value in row.items():
                # if isinstance(value, basestring):
                if isinstance(value, str):
                    value = format_value(value)
                elif isinstance(value, bool):
                    value = format_value(value)
                elif isinstance(value, list):
                    value = ', '.join([format_value(v) for v in value])
                    value = '{%s}' % value
                elif isinstance(value, dict):
                    value = ', '.join(["[%s] = %s"%(format_value(k), format_value(v)) for k, v in value.items()])
                    value = '{%s}' % value

                cell = cell_temple % (key, value)
                file.write(cell.encode('utf-8'))
            file.write(row_end_temple.encode('utf-8'))
        if is_map:
            file.write(map_flag.encode('utf-8'))
        else:
            pass
        file.write(end_temple.encode('utf-8'))
    return lua_name

def excel_sheets(*args, **kw):
    with open_workbook(*args, on_demand=True, ragged_rows=True, **kw) as (
    book):
        for i in range(book.nsheets):
            try:
                yield book.sheet_by_index(i)
            finally:
                book.unload_sheet(i)


def sheet_row_values(sheet, rowx):
    return (sheet.cell_value(rowx, colx)
            for colx in range(sheet.row_len(rowx)))

# 所有的结果输出字典
allExcelData = {}

def convet(xls_name, output, file_names_):
    workbook = open_workbook(xls_name)#, encoding_override='gbk')
    lua_list = []
    for sheet in workbook.sheets():
        if sheet.nrows == 0:
            continue
        if sheet.name.startswith('_'):
            # print('\t-- ignored:[%s].[%s]' % (xls_name.encode(output_encoding), sheet.name.encode(output_encoding)))
            continue
        try:
            # print('converting...: ', xls_name.encode(output_encoding), sheet.name.encode(output_encoding))
            # print('converting...: ', xls_name, "   ", sheet.name)
            assertx(sheet.name not in file_names_,
                    '%s %s 文件名 %s 重复' % (file_names_.get(sheet.name), xls_name, sheet.name))
            data = sheet_to_dict(sheet)
            allExcelData[sheet.name] = handleYieldData(data)
            if data:
                # lua_list.append(to_lua(sheet.name, data, xls_name, output))
                file_names_[sheet.name] = xls_name
        except Exception as e:
            errorLog.write(str('converting...: '+xls_name+"   "+sheet.name)+'\n')
            errorLog.write("******"*20+'\n')
            # print('converting...: ', xls_name, "   ", sheet.name)
            # print(sys.stderr.write('convert FAILED ' + xls_name.encode(output_encoding) + ' ' + sheet.name.encode(output_encoding) + '\n'))
            # print >> sys.stderr.write('convert FAILED ' + xls_name.encode(output_encoding) + ' ' + sheet.name.encode(output_encoding) + '\n')
            raise
    return lua_list

# def convet(xls_name, output, file_names_):
#     workbook = open_workbook(xls_name)#, encoding_override='gbk')
#     lua_list = []
#     fData = open("../data.txt", 'a', encoding='utf-8')
#     for sheet in workbook.sheets():
#         if sheet.nrows == 0:
#             continue
#         if sheet.name.startswith('_'):
#             # print('\t-- ignored:[%s].[%s]' % (xls_name.encode(output_encoding), sheet.name.encode(output_encoding)))
#             continue
#         try:
#             # print('converting...: ', xls_name.encode(output_encoding), sheet.name.encode(output_encoding))
#             assertx(sheet.name not in file_names_,
#                     '%s %s 文件名 %s 重复' % (file_names_.get(sheet.name), xls_name, sheet.name))
#             data = sheet_to_dict(sheet)
#             fData.write("\n@@@@@@@@ ExcelName = "+xls_name+"           $$$$$$$ sheetName = "+sheet.name)
#             fData.write('\n')
#             while(True):
#                 try:
#                     fData.write(str(next(data)))
#                 except StopIteration as e:
#                     break
#             if data:
#                 # lua_list.append(to_lua(sheet.name, data, xls_name, output))
#                 file_names_[sheet.name] = xls_name
#         except Exception as e:
#             # print >> sys.stderr.write('convert FAILED ' + xls_name.encode(output_encoding) + ' ' + sheet.name.encode(output_encoding) + '\n')
#             raise
#     fData.close()
#     return lua_list

# 把迭代器中的数据拿出来，然后保存在列表中
def handleYieldData(iterObj):
    tempList = []
    while(True):
        try:
            tempList.append((next(iterObj)))
        except StopIteration as e:
            break
    # print("RRRRRR", tempList)
    return tempList

enum_tbl = {}
keys = {}
lua_file_caches = {}

def file_md5(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def convet_enumerate(xls_name, path):
    # 处理分区表资源
    sub_files = []
    for name in listdir(path):
        p = join(path, name)
        if isfile(p) or name[0] == '.':
            continue
        for sub_name in listdir(p):
            sub_path = join(p, sub_name)
            if not isfile(sub_path):
                continue
            sub_files.append(sub_path)

    assertx(isfile(xls_name), 'enumerate.xls is required')
    with open_workbook(xls_name, on_demand=True) as workbook:
        assertx(workbook.nsheets == 1, 'only one sheet for enum')
        sheet = workbook.sheet_by_index(0)
    for row in sheet_to_dict(sheet):
        enum_name = row['enum_name']
        no_name = int(row['no_name'])
        # print(('converting enumerate:[%s]' % (row['file_name'])).encode(output_encoding))
        md5 = file_md5(path + row['file_name'])
        global keys
        # if not keys.has_key(md5):
        if md5 not in keys:
            keys = {}
        files = []
        emu_fn = row['file_name'][:-4]

        files.append(path + row['file_name'])
        for f in sub_files:
            if emu_fn in f:
                files.append(f)
        for index, fn in enumerate(files):
            # print('\t-> begin process xls', fn)
            with open_workbook(fn, on_demand=True) as workbook:
                try:
                    sheet_name = row['sheet_name']
                    cur_sheet_name = sheet_name
                    has_sheet = False
                    for s in workbook.sheet_names():
                        if s.startswith(sheet_name+"_") or s == sheet_name:
                            sheet = workbook.sheet_by_name(s)
                            cur_sheet_name = s
                            has_sheet = True
                            break
                    if not has_sheet:
                        continue
                except XLRDError as e:
                    # print('%s does not contain sheet named: %s' % (fn, cur_sheet_name))
                    if index == 0:
                        # print(sys.stderr.write('convert enum failed\n'))
                        # print >> sys.stderr.write('convert enum failed\n')
                        raise
                    else:
                        continue
            try:
                name_row = sheet.row_values(1)
                id_index = name_row.index('id')
                id_type = sheet.cell_value(0, id_index)
                if no_name == 0:
                    name_index = name_row.index('name')
                name_to_id = {}
                idx_ = {}
                pre_name_to_id = enum_tbl.get(enum_name)
                if pre_name_to_id:
                    # pre_idx_ = set(pre_name_to_id.itervalues())
                    pre_idx_ = set(pre_name_to_id.values())
                for rowx in range(3, sheet.nrows):
                    idx = sheet.cell_value(rowx, id_index)
                    if idx == '':
                       break
                    if no_name == 0:
                        name = sheet.cell_value(rowx, name_index)
                    else:
                        name = str(int(idx))
                    assertx(name not in name_to_id, '枚举名重复[%s]' % name)
                    assertx(idx not in idx_, '枚举名ID重复[%s]' % idx)
                    if pre_name_to_id:
                        assertx(name not in pre_name_to_id, '与其他同类型表 枚举名重复[%s]' % name)
                        assertx(idx not in pre_idx_, '与其他同类型表 枚举名ID重复[%s]' % idx)

                    try:
                        name = int(name)
                        name = unicode(name)
                    except:
                        pass
                    id_type = id_type.split('@')[0]
                    name_to_id[name] = cell_to_value(id_type, idx)
                    idx_[idx] = True
                if pre_name_to_id:
                    pre_name_to_id.update(name_to_id)
                    name_to_id = pre_name_to_id
                enum_tbl[enum_name] = name_to_id
            except Exception as e:
                # print(e)
                # print('enum error:' + row['file_name'])
                # print(sys.stderr.write('enum error:' + row['file_name'] + '\n'))
                # print >> sys.stderr.write('enum error:' + row['file_name'] + '\n')
                raise

tmp_keys = {}
def convet_xls_file(path, output, file_names_):
    root, ext = splitext(path)
    # print("root = ",root)
    if ext != '.xls':
        return
    head = basename(path)
    if head.startswith('_'):
        return

    xls_md5 = file_md5(path)

    # 是否需要重新导入
    # dirty = xls_md5 not in keys
    # if not dirty:
    #     lua_list = keys[xls_md5]
    #     for lua_file in lua_list:
    #         if not exists(lua_file):
    #             dirty = True
    #             break
    #         l_md5 = file_md5(lua_file)
    #         if l_md5 != lua_file_caches[lua_file]:
    #             dirty = True
    #             break
    dirty = True
    # 重新导入
    if dirty:
        lua_list = convet(path, output, file_names_)
        for f in lua_list:
            lua_file_caches[f] = file_md5(f)
        keys[xls_md5] = lua_list

    tmp_keys[xls_md5] = keys[xls_md5]

def remove_old_file(root):
    for f in os.listdir(root):
        path = join(root, f)
        if f.endswith(".lua"):
            if path not in lua_file_caches:
                # print("------->>!!! remove un used file", path)
                os.remove(path)
        elif isdir(path):
            remove_old_file(path)


# 获得所有excel表格得到的字典， 通过svn自动更新到最新的数据，并生成数据表
def getSvnExcelDictData():
    print(" 程序正在执行中……………………")

    svnCommon()
    PATH = './resource/'

    # PATH = iFilePath
    # # 属不同的目录
    # if is_client:
    #     OUTPUT = 'lua_data_raw_c/'
    # else:
    #     OUTPUT = 'lua_data_raw_s/'
    OUTPUT = "../testData/"
    JSON = 'xls2lua_cache2.json'
    JSON2 = 'lua_file_cache.json'
    OUTPUT_KEYS = OUTPUT + JSON
    lua_cache_path = OUTPUT + JSON2

    try:
        if exists(OUTPUT_KEYS):
            f = open(OUTPUT_KEYS, 'r')
            keys = json.loads(f.read(), strict=False)
            f.close()

        if exists(lua_cache_path):
            f = open(lua_cache_path, 'r')
            lua_file_caches = json.loads(f.read(), strict=False)
            f.close()
    except:
        keys = {}
        lua_file_caches = {}

    #  所有导表的文件
    file_names_ = {}
    convet_enumerate(join(PATH, 'enumerate.xls'), PATH)
    for name in listdir(PATH):
        path = join(PATH, name)
        if not isfile(path):
            continue
        convet_xls_file(path, OUTPUT, file_names_)

    # print('-' * 40)
    for name in listdir(PATH):
        path = join(PATH, name)
        if isfile(path) or name[0] == '.':
            continue
        file_names_ = {}
        # print('分区表资源%s' % name)
        for sub_name in listdir(path):
            sub_path = join(path, sub_name)
            if not isfile(sub_path):
                continue
            output = join(OUTPUT, name)
            # cache_path = join(CACHE_PATH, name)
            # print(sub_name)
            convet_xls_file(sub_path, output, file_names_)
        # print('-' * 20)

    # open(OUTPUT_KEYS, 'w').write(json.dumps(tmp_keys).decode('utf-8'))
    # open(lua_cache_path, 'w').write(json.dumps(lua_file_caches).decode('utf-8'))

    # remove_old_file(OUTPUT)

    # shutil.rmtree(OUTPUT)
    # shutil.copytree(CACHE_PATH, OUTPUT)
    # print("VVVVVVVVVVV", allExcelData)
    return allExcelData

# 获得所有excel表格得到的字典，通过配置的文件路径，读取对应路径的数据
def getLocalExcelDictData(iFilePath):
    print(" 程序正在执行中……………………")

    PATH = iFilePath
    # # 属不同的目录
    # if is_client:
    #     OUTPUT = 'lua_data_raw_c/'
    # else:
    #     OUTPUT = 'lua_data_raw_s/'
    OUTPUT = "../testData/"
    JSON = 'xls2lua_cache2.json'
    JSON2 = 'lua_file_cache.json'
    OUTPUT_KEYS = OUTPUT + JSON
    lua_cache_path = OUTPUT + JSON2

    try:
        if exists(OUTPUT_KEYS):
            f = open(OUTPUT_KEYS, 'r')
            keys = json.loads(f.read(), strict=False)
            f.close()

        if exists(lua_cache_path):
            f = open(lua_cache_path, 'r')
            lua_file_caches = json.loads(f.read(), strict=False)
            f.close()
    except:
        keys = {}
        lua_file_caches = {}

    #  所有导表的文件
    file_names_ = {}
    convet_enumerate(join(PATH, 'enumerate.xls'), PATH)
    for name in listdir(PATH):
        path = join(PATH, name)
        if not isfile(path):
            continue
        convet_xls_file(path, OUTPUT, file_names_)

    # print('-' * 40)
    for name in listdir(PATH):
        path = join(PATH, name)
        if isfile(path) or name[0] == '.':
            continue
        file_names_ = {}
        # print('分区表资源%s' % name)
        for sub_name in listdir(path):
            sub_path = join(path, sub_name)
            if not isfile(sub_path):
                continue
            output = join(OUTPUT, name)
            # cache_path = join(CACHE_PATH, name)
            # print(sub_name)
            convet_xls_file(sub_path, output, file_names_)
        # print('-' * 20)

    # open(OUTPUT_KEYS, 'w').write(json.dumps(tmp_keys).decode('utf-8'))
    # open(lua_cache_path, 'w').write(json.dumps(lua_file_caches).decode('utf-8'))

    # remove_old_file(OUTPUT)

    # shutil.rmtree(OUTPUT)
    # shutil.copytree(CACHE_PATH, OUTPUT)
    # print("VVVVVVVVVVV", allExcelData)
    return allExcelData


# 使用系统命令对提供的目录进行svn更新
def svnSimpleExecute(command):
    print(">> ", command)
    os.popen(command)

# 执行指令
def svnCommon():
    command1 = "svn checkout http://oa.ejoy.com/m1/p1/editor/config/resource"
    command2 = "svn cleanup"
    command3 = "cd ../"
    try:
        svnSimpleExecute(command1)
    except:
        svnSimpleExecute(command2)
        os.chdir('./resource/')
        svnSimpleExecute(command1)
        svnSimpleExecute(command3)
    finally:
        time.sleep(50)


if __name__ == '__main__':
    start = datetime.datetime.now()
    filePath = "E:\M1_SVN\Market_build\lss\config\\resource\\"
    print("**********",getLocalExcelDictData(filePath))
    # print("$$$$$$$$$$$$", getSvnExcelDictData())
    end = datetime.datetime.now()
    print("执行需要的时间是 ： ", end - start)

