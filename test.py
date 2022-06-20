from class_game import Game_To_Game_Tags, Game_Tags, Games, Base, engine
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, joinedload
from main import table

if __name__=='__main__':
    # Создание таблицы
    Base.metadata.create_all(engine)
    # Создание сессии
    # create a configured "Session" class
    Session = sessionmaker(bind=engine)
    session = Session()

    game = Games(1, "Mario", "TODAY", 50, 1000, 500, "www.nintendo.com", "/image-link", "TGN")

    temp_tag = session.query(Game_Tags).filter_by(name="Action").first()
    if temp_tag:
        game.tags.append(temp_tag)
    else:
        game.tags.append(Game_Tags("Action"))

    temp_tag = session.query(Game_Tags).filter_by(name="Platformer").first()
    if temp_tag:
        game.tags.append(temp_tag)
    else:
        game.tags.append(Game_Tags("Platformer"))

    session.add(game)#.prefix_with("OR IGNORE")
    session.commit()

    q = session.query(Games).options(joinedload(Games.tags))
    print(q)

    session.delete(game)
    session.commit()

    table()