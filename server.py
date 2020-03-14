#%%
class TodoItem:
    
    def __init__(self,content:str):
        self.content = content


#%%
from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for

import sqlite3
import os
import simplejson as json
import datetime

def initDB():
    if os.access('todo.db',os.R_OK | os.W_OK):
        print('can access to db')
    else:
        print('can''t access to db, and try to init db')
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE TODO
        (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CONTENT TEXT NOT NULL,
            ADDTIME DATETIME NOT NULL,
            COMPLETETIME DATETIME,
            WORKTIMECOUNT INT DEFAULT 0,
            COMPLETED BOOLEAN DEFAULT FALSE
        );''')

        c.execute('''CREATE TABLE EVENT
        (
            STARTTIME DATETIME NOT NULL,
            ENDTIME DATETIME NOT NULL,
            CONTENT TEXT NOT NULL
        );''')

        conn.commit()
        conn.close()

def fetchTodoList():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    todolists = c.execute('SELECT * FROM TODO').fetchall()
    conn.close()
    return todolists

def _addTodo(values:tuple):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('INSERT INTO TODO(CONTENT,ADDTIME) VALUES '  + str(values) )
    pk = tuple(c.execute('SELECT LAST_INSERT_ROWID()'))[0][0] # 0 is pk
    conn.commit()
    conn.close()
    return pk
def _deleteTodo(pk:int):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('DELETE FROM TODO WHERE ID = ' + str(pk))
    conn.commit()
    conn.close()


def _updateTodo(newContent:str,pk:int):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('UPDATE TODO set CONTENT = \'' + newContent + '\' WHERE ID = ' + str(pk))
    conn.commit()
    conn.close()

def _addTodoTimeCount(timelapse:int,pk:int):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('UPDATE TODO set WORKTIMECOUNT = WORKTIMECOUNT + ' + str(timelapse) + ' WHERE ID = ' + str(pk))
    conn.commit()
    conn.close()

def _addEvent(values:tuple):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('''INSERT INTO EVENT(STARTTIME,ENDTIME,CONTENT) VALUES ''' + str(values))
    conn.commit()
    conn.close()

def _getEvent(dayrange:tuple):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    sqlcommand = 'SELECT * FROM EVENT WHERE STARTTIME BETWEEN '+ '\'' + dayrange[0] + '\' and \'' + dayrange[1] + '\''
    eventlist = list(c.execute(sqlcommand))
    conn.commit()
    conn.close()
    return eventlist

app = Flask(__name__)

@app.route('/',methods=['Get'])
def index():
    return render_template('index.html')

@app.route('/gettodo',methods=['Get'])
def getTODO():
    rp = {}
    todolists = fetchTodoList()
    for item in todolists:
        rp[item[0]] = {'pk':item[0],'content':item[1]}        
    return json.dumps(rp)

@app.route('/deletetodo',methods=['Post'])
def deleteTodo():
    pk = json.loads(request.data)['pk']
    assert type(pk) is int 
    _deleteTodo(pk)
    return json.dumps({'status':200})

@app.route('/updatetodo',methods=['Post'])
def updateTodo():
    data = json.loads(request.data)
    pk = data['pk']
    newContent = data['content']
    assert type(pk) is int
    assert type(newContent) is str
    _updateTodo(newContent,pk)
    return json.dumps({'status':200})

@app.route('/addtodo',methods=['Post'])
def addTodo():
    content= json.loads(request.data)['content']
    _now = datetime.datetime.now().__str__()
    assert type(content) is str
    assert content!=''
    _values = (content,_now)
    pk = _addTodo(_values)
    return json.dumps({'status':200,'pk':pk})

@app.route('/tomato',methods=['Post'])
def tomatoDone():
    _data = json.loads(request.data)
    _content = _data['content']
    _timelapse = _data['timelapse']
    _pk = _data['pk']
    _start_time = str(datetime.datetime.now() - datetime.timedelta(minutes=_timelapse))
    _end_time = str(datetime.datetime.now())
    assert type(_content) is str
    assert _content is not ''
    if _content != 'BREAK':
        _addTodoTimeCount(_timelapse,_pk)
    _addEvent((_start_time,_end_time,_content))
    return json.dumps({'status':200})

@app.route('/event',methods=['Get'])
def getEvent():
    timestamp = int(request.args.get('day'))
    day = datetime.datetime.fromtimestamp(timestamp * 0.001).date()
    nextday = day + datetime.timedelta(days=1)
    _dtmin = datetime.datetime.combine(day,datetime.time.min)
    _dtmax = datetime.datetime.combine(nextday,datetime.time.min)
    dayrange = (str(_dtmin),str(_dtmax))
    event_list = _getEvent(dayrange)
    _event_dict = {}
    for id,event in zip(range(0,len(event_list)),event_list):
        _event_dict[id] = {'st':event[0],'et':event[1],'ct':event[2]}
    return json.dumps(_event_dict)

#%%

if __name__ == "__main__":
    initDB()
    app.run()
    print(fetchTodoList())

# %%
