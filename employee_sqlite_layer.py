import sqlite3


class Sqlite_Position:
    def __init__(self, search_terms=None, kw=None):
        self.conn = sqlite3.connect('data/position_data.db')
        self.table_name = search_terms
        self.position_name = kw[0]
        self.position_salary = kw[1]
        self.position_describe = kw[2]
        self.position_other_requirement = kw[3]
        self.position_url = kw[4]

    def create_table(self):
        if self.conn.execute(f'select *from {self.table_name}'):
            pass
        else:
            self.conn.execute(f'''
            CREATE TABLE {self.table_name} (
            position_id INTEGER PRIMARY KEY NOT NULL , -- '主键ID'
            position_name TEXT NOT NULL , -- '职位名称'
            position_salary TEXT NOT NULL , -- '职位薪资'
            position_describe TEXT NOT NULL , -- '职位描述'
            position_other_requirement TEXT NOT NULL null , -- '其他要求'
            position_url TEXT NOT NULL -- '职位地址'
            )
            ''')

    def insert_data(self):
        self.conn.execute(f'''
        INSERT INTO {self.table_name} ( 
        position_name, position_salary, position_describe, position_other_requirement, position_url
        )
        VALUES 
        (
        '{self.position_name}', 
        '{self.position_salary}', 
        '{self.position_describe}', 
        '{self.position_other_requirement}', 
        '{self.position_url}'
        );
        ''')
        self.conn.commit()

    def delete_data(self, p_id=None):
        self.conn.execute(f'DELETE FROM {self.table_name} WHERE position_id = {p_id}')
        self.conn.commit()

    def update_data(self):
        self.insert_data()

    def select_data(self):
        data = None
        try:
            # <class 'sqlite3.Cursor'>
            data = self.conn.execute(f'''
            SELECT 
            position_id, position_name, position_salary, position_describe, position_other_requirement, position_url
            FROM
            {self.table_name}
            ''')
        except sqlite3.OperationalError as e:
            print(repr(e))
        finally:
            return data

    def close_conn(self):
        self.conn.close()


class Sqlite_Personal:
    def __init__(self, table_name=None, ):
        self.conn = sqlite3.connect('position_data.db')
        self.table_name = table_name

    def create_table(self):
        pass

    def insert_data(self):
        pass

    def delete_data(self):
        pass

    def update_data(self):
        pass

    def select_data(self):
        pass
