from flask import Flask,request,make_response
from flask.helpers import make_response
from flask_restx import Api, Resource, fields
import sqlite3
from datetime import datetime

app = Flask(__name__)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
)

def connection_db(data): #try's connecting to sqlite
    conn = None
    try:
        conn = sqlite3.connect(data)
    except sqlite3.error as e:
        print(e)
    return conn 

def auth_required(username,password): #authorization for write operations
    conn = connection_db("authenticate.sqlite")
    cursor = conn.execute("Select * from authorize")
    for row in cursor.fetchall():
        if(row[0]==username and row[1]==password):
           return True
    return False

ns = api.namespace('todos', description='All operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'due_by':fields.Date(required=True,description='task finish date'),
    'status':fields.String(required=True,description='status of the task')
})
   
class TodoDAO(object):
    def get(self, id):
        conn = connection_db("todo.sqlite")
        cursor = conn.execute("Select * from todos")
        dict={}
        for row in cursor.fetchall():
            if row[0]==id:
                dict['id'] = row[0];
                dict['task'] = row[1]
                dict['due_by']=row[2]
                dict['status'] = row[3]
                return dict;
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        conn = connection_db("todo.sqlite")
        cursor = conn.cursor()
        todo = data
        sql = """INSERT INTO todos(toid,description,due_by_date,status)
                 VALUES (?,?,?,?)"""
        cursor.execute(sql,(todo['id'],todo['task'],todo['due_by'],todo['status']))
        conn.commit()
        return todo

    def update(self, id, data):
        conn = connection_db("todo.sqlite")
        sql = """UPDATE todos SET 
                 description=?,
                 due_by_date=?,
                 status=? 
                 WHERE toid=?"""
        conn.execute(sql,(data['task'],data['due_by'],data['status'],id))  
        conn.commit()  
        todo = self.get(id)
        return todo

    def delete(self, id):
        conn = connection_db("todo.sqlite")
        sql = """DELETE FROM todos WHERE toid=?"""
        conn.execute(sql,(id,))
        conn.commit()
        return "The todo with ID {} has been deleted".format(id),200

DAO = TodoDAO()
@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    
    def get(self):
        '''List all tasks'''
        conn = connection_db("todo.sqlite")
        cursor = conn.execute("Select * from todos")
        details = [
            dict(id=row[0],task=row[1],due_by=row[2],status=row[3])
            for row in cursor.fetchall()
        ]
        return details

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)

    def post(self):
        '''Create a new task'''
        username = input("Enter your username:")
        password = input("Enter your password:")
        if(auth_required(username=username,password=password)):
            return DAO.create(api.payload), 201
        else:
            return {'message':'Invalid username of password'}    

@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')

class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
   
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        username = input("Enter your username:")
        password = input("Enter your password:")
        if(auth_required(username,password)):
            return DAO.delete(id)
        else:
            return {'message':'Invalid username of password'}

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        username = input("Enter your username:")
        password = input("Enter your password:")
        if(auth_required(username=username,password=password)):
            return DAO.update(id, api.payload)
        else:
            return {'message':'Invalid username of password'}

class ADue(Resource):
    def get(self,date):
        conn = connection_db("todo.sqlite")
        cursor = conn.execute("SELECT * FROM todos")
        dues = []
        dict={}
        for row in cursor.fetchall():
            if(row[2]==date):
                dict['id'] = row[0]
                dict['task'] = row[1]
                dict['due_by'] = row[2]
                dict['status'] = row[3]
                dues.append(dict)
            dict={}
        return dues  

class AOverDue(Resource):
    def get(self):
        s = str(datetime.date(datetime.now()))
        curr = connection_db("todo.sqlite")
        cursor = curr.execute("Select * from todos")
        dues = []
        dict={}
        for row in cursor.fetchall():
            if(s>row[2]):
                dict['id'] = row[0]
                dict['task'] = row[1]
                dict['due_by'] = row[2]
                dict['status'] = row[3]
                dues.append(dict)
            dict = {}
        return dues  

class Finished(Resource):
    def get(self):
        curr = connection_db("todo.sqlite")
        cursor = curr.execute("Select * from todos")
        dues = []
        dict={}
        for row in cursor.fetchall():
            if(row[3]=='finished'):
                dict['id'] = row[0]
                dict['task'] = row[1]
                dict['due_by'] = row[2]
                dict['status'] = row[3]
                dues.append(dict)
            dict = {}
        return dues

api.add_resource(ADue,"/due/<string:date>")
api.add_resource(AOverDue,"/overdue/")
api.add_resource(Finished,"/finished/")

if __name__ == '__main__':
    app.run(debug=True)