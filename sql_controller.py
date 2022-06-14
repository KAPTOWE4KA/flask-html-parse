import os.path
import sqlite3


class TableController:
    def __init__(self, file="db.sqlite", t_name=""):
        self.file_name = file
        self.table_name = t_name

    def test_connect(self):
        if not os.path.exists(self.file_name):
            raise sqlite3.OperationalError("DB not found")
        conn = sqlite3.connect(self.file_name)
        cur = conn.cursor()
        query = f"select * from {self.table_name}"
        #print("Test Querry: "+query)
        cur.execute(query)
        return 1

    def select(self, columns=["*"], where="", order_by="", show_query=False):
        query = f"SELECT {', '.join(str(col) for col in columns)} from {self.table_name}"
        if len(where) > 0:
            query += f" where {where}"
        if len(order_by) > 0:
            query += f" ORDER BY {order_by}"
        cur = sqlite3.connect(self.file_name).cursor()
        if show_query:
            print(query)
        cur.execute(query)
        return cur.fetchall()

    def insert(self, columns: list, values: list, show_query=False):
        #insert into game_tags(name) values ('Puzzle')
        query = f"INSERT INTO {self.table_name}({', '.join(str(col) for col in columns)}) VALUES({', '.join(str(val) for val in values)}) "
        con = sqlite3.connect(self.file_name)
        cur = con.cursor()
        if show_query:
            print(query)
        cur.execute(query)
        con.commit()
        return cur.fetchall()

    def delete(self, where="", show_query=False):
        query = f"DELETE FROM {self.table_name}"
        if len(where) > 1:
            query += f" WHERE {where}"
        con = sqlite3.connect(self.file_name)
        cur = con.cursor()
        if show_query:
            print(query)
        cur.execute(query)
        con.commit()
        return cur.fetchall()

    def _custom_query_(self, query):
        con = sqlite3.connect(self.file_name)
        cur = con.cursor()
        cur.execute(query)
        con.commit()
        return cur.fetchall()


if __name__ == '__main__':
    tc1 = TableController(file="steam_games.sqlite", t_name="game_tags", columns=["id", "name"])
    tc1.test_connect()
    for row in tc1.select(show_query=True):
        print(", ".join([str(r) for r in row]))

    for row in tc1.select(columns=["name"], where="name like '%n%'", show_query=True):
        print(", ".join([str(r) for r in row]))

    tc1.insert(columns=['name'], values=['\"Racing\"'], show_query=True)

    for row in tc1.select(order_by="name DESC", show_query=True):
        print(", ".join([str(r) for r in row]))

    tc1.delete(where=" name like '%Rac%'")

    for row in tc1._custom_query_("select games.id, games.name, game_tags.name "
                                "from games, game_tags, game_to_game_tags "
                                "where games.id = game_to_game_tags.game_id and game_tags.id = game_to_game_tags.tag_id"):
        print(", ".join([str(r) for r in row]))
else:
    print("Not in main thread")
