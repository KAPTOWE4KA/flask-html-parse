import sqlite3
import time
from sqlalchemy import Column, Integer, String, Numeric, create_engine, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from sql_controller import TableController

engine = create_engine('sqlite:///orm.sqlite', echo=True)

Base = declarative_base()


Game_To_Game_Tags = Table(
    'games_to_game_tags',
    Base.metadata,
    Column('game_id', ForeignKey('games.id')),
    Column('game_tags_id', ForeignKey('game_tags.id'))
)


class Game_Tags(Base):
    __tablename__ = 'game_tags'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name


class Games(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    release_date = Column(String(50))
    discount = Column(Integer, nullable=True)
    instance_price = Column(Integer, nullable=True)
    final_price = Column(Integer)
    link = Column(String(255))
    image_link = Column(String(255))
    valute_symbol = Column(String(5))
    tags = relationship(
        "Game_Tags",
        secondary=Game_To_Game_Tags,
        backref="games")

    def __init__(self, gid, name, release_date, final_price, link, image_link, valute_symbol, discount=None, instance_price=None):
        self.id = gid
        self.name = name
        self.release_date = release_date
        self.discount = discount
        self.instance_price = instance_price
        self.final_price = final_price
        self.link = link
        self.image_link = image_link
        self.valute_symbol = valute_symbol

class Game:
    def __init__(self, gid=0, name="noname", release_date="", discount=0, instance_price=0, final_price=0, link=0, image_link=0, valute_symbol="", tags=[]):
        self.id = gid
        self.name = name
        self.release_date = release_date
        self.discount = discount
        self.instance_price = instance_price
        self.final_price = final_price
        self.link = link
        self.image_link = image_link
        self.valute_symbol = valute_symbol
        self.tags = tags
        self.games_table = TableController(file="steam_games.sqlite", t_name="games")
        self.games_table.test_connect()
        self.tags_table = TableController(file="steam_games.sqlite", t_name="game_tags")
        self.tags_table.test_connect()
        self.g2t_table = TableController(file="steam_games.sqlite", t_name="game_to_game_tags")
        self.g2t_table.test_connect()

    def insert(self):
        if self.games_table.select(columns=["name"], where=f"name = '{self.name}' or id = {self.id}", show_query=False).__len__()>0:
            print(f"Game with id: {self.id} already exist")
            return -1  # запись уже есть в базе
        elif self.id==0 or self.name=="noname" or self.valute_symbol=="":
            return -2  # не все важные поля заполнены 
        else:
            try:
                #adding game to table
                self.games_table.insert(columns=["id", "name", "release_date", "discount", "instance_price", "final_price", "link", "image_link", "valute_symbol"],
                                    values=[self.id, f"'{self.name}'", f"'{self.release_date}'", self.discount, self.instance_price, self.final_price, 
                                            f"'{self.link}'", f"'{self.image_link}'", f"'{self.valute_symbol}'"], show_query=False)
                #adding tags to table
                for tag in self.tags:
                    if self.tags_table.select(columns=["name"], where=f"name = '{tag}'", show_query=False).__len__() == 0:
                        self.tags_table.insert(columns=["name"], values=[f"'{tag}'"], show_query=False)
                        tagid = self.tags_table.select(columns=["id"], where=f"name = '{tag}'", show_query=False)[0][0]
                        #adding links : game -<= tags
                        if self.g2t_table.select(columns=["game_id", "tag_id"], where=f"game_id = {self.id} and tag_id = {tagid}", show_query=False).__len__()==0:
                            self.g2t_table.insert(columns=["game_id", "tag_id"], values=[self.id, tagid], show_query=False)
                    else:
                        tagid = self.tags_table.select(columns=["id"], where=f"name = '{tag}'", show_query=False)[0][0]
                        if self.g2t_table.select(columns=["game_id", "tag_id"], where=f"game_id = {self.id} and tag_id = {tagid}", show_query=False).__len__()==0:
                            self.g2t_table.insert(columns=["game_id", "tag_id"], values=[self.id, tagid], show_query=False)
                print(f"ИГРА {self.name} была УСПЕШНО ДОБАВЛЕНА")
            except Exception as e:
                self.games_table.delete(where=f"id = {self.id}")
                self.g2t_table.delete(where=f"game_id = {self.id}")
                print(e.__str__())
                return -3  # ошибка в query
        