import json
import sqlite3
import logging
import traceback
from threading import Lock

class Log(Exception):
    def __init__(self):
        self.func_name = traceback.extract_stack(None, 2)[0][2]

    def Pass(self, chat_id):
        logging.error(str(chat_id) + f":Pass exception occurred in " + self.func_name + f" -> {traceback.format_exc()}")
        # logging.info((chat_id + f":Pass exception occurred in " + self.func_name))

    def Warn(self, chat_id='Unknown', msg=' '):
        logging.warning(str(chat_id) + ": " + f"An Unexcepted error occurred in " + self.func_name + ". " + msg + "-> ",
                        exc_info=True)

    def Info(self, chat_id, txt):
        logging.info(chat_id + ": " + txt)

    def In(self, chat_id: object) -> object:
        logging.info(str(chat_id) + ": in " + self.func_name)

    def Choice(self, chat_id, txt):
        logging.info(chat_id + ": Action: " + txt)

log = Log()

class wrapper:
    def __init__(self):
        self.mutex = Lock()

    def wrap(self, pre, post):
        def decorate(func):
            def call(*args, **kwargs):
                self.mutex.acquire(1)
                result = func(*args, **kwargs)
                self.mutex.release()
                return result

            return call

        return decorate

    def trace_in(self, func, *args, **kwargs):
        self.mutex.acquire(1)

    def trace_out(self, func, *args, **kwargs):
        self.mutex.release()


class Myjson:
    w = wrapper()

    def __init__(self, file_path):
        self.file = file_path

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def get(self, key=False):
        with open(self.file, encoding='utf-8') as json_file:
            data = json.load(json_file)
            if not key:
                return data
            elif key in data:
                return data[key]
            return None

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def set(self, key, value):
        with open(self.file) as json_file:
            data = json.load(json_file)
            data[key] = value
        with open(self.file, 'w') as outfile:
            json.dump(data, outfile)

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def add_to_list(self, key, value, uniqeList = False):
        with open(self.file) as json_file:
            data = json.load(json_file)
            if uniqeList:
                if value not in data[key]:
                    data.setdefault(key, []).append(value)
                else:
                    return None
            else:
                data.setdefault(key, []).append(value)

        # Save JSON file
        with open(self.file, 'w') as outfile:
            json.dump(data, outfile)

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def delVal(self, key):
        with open(self.file) as json_file:
            data = json.load(json_file)
            data.pop(key, None)

        with open(self.file, 'w') as outfile:
            json.dump(data, outfile)

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def dump(self, data):
        # Save JSON file
        with open(self.file, 'w') as outfile:
            json.dump(data, outfile)

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def CompareMasterJson(self, slaveFile):
        master = self.get()
        slaveFile.dump(list(set(slaveFile.get()) - set(master)))


class DBgetset:
    w = wrapper()

    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.c = self.connection.cursor()

    def fix(self, values):
        newStr = ""
        for value in values:
            ask = (value != 'NULL')
            newStr += f"'{str(value)}'," if ask else 'NULL,'
        return newStr[:-1]

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def get(self, table, select='*', where='TRUE'):
        where = '' if where=='TRUE' else 'WHERE '+where
        self.c.execute(f"SELECT {select} FROM {table} {where}")
        # SQL_Query = pd.read_sql_query(f"SELECT {select} FROM {table} WHERE {where} ORDER BY 1", self.connection)
        return self.c.fetchall()

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def insert(self, table, values):
        self.c.execute(f"INSERT INTO {table} VALUES ({self.fix(values)})")
        self.connection.commit()

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def insert_replace(self, table, values):
        self.c.execute(f"INSERT OR REPLACE INTO {table} VALUES ({self.fix(values)})")
        self.connection.commit()

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def update(self, table, set, where):
        '''

        usage example:
        update("users", {"username": "til", "age": 5}, WHERE statement)

        '''
        set_string = ""
        for value in set:
            set_string += f'{value} = {set[value]}, '
        set_string = set_string[:-2]
        print(set_string)
        self.c.execute(f"UPDATE {table} SET {set_string} WHERE {where}")
        self.connection.commit()

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def delete(self, table, where):
        try:
            self.c.execute(f"DELETE FROM {table} WHERE {where}")
            self.connection.commit()
            return True
        except:
            return False
