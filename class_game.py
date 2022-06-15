from sql_controller import TableController

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
        if self.games_table.select(columns=["name"], where=f"name = {self.name} or id = {self.id}").__len__()>0:
            print(f"Game with id: {self.id} already exist")
            return -1  # запись уже есть в базе
        elif self.id==0 or self.name=="noname" or self.valute_symbol=="":
            return -2  # не все важные поля заполнены 
        else:
            try:
                #adding game to table
                self.games_table.insert(columns=["id", "name", "release_date", "discount", "instance_price", "final_price", "link", "image_link", "valute_symbol"],
                                    values=[self.id, f"'{self.name}'", f"'{self.release_date}'", self.discount, self.instance_price, self.final_price, 
                                            f"'{self.link}'", f"'{self.image_link}'", f"'{self.valute_symbol}'"], show_query=True)
                #adding tags to table
                for tag in self.tags:
                    if self.tags_table.select(columns=["name"], where=f"name = {self.name}").__len__() == 0:
                        tagid = self.tags_table.select(columns=["max(id)"])+1
                        self.tags_table.insert(columns=["id", "name"], values=[tagid, tag])
                        #adding links : game -<= tags
                        if self.g2t_table.select(columns=["game_id", "tag_id"], where=f"game_id = {self.id}, tag_id = {tagid}").__len__()==0:
                            self.g2t_table.insert(columns=["game_id", "tag_id"], values=[self.name, tagid])
            except:
                return -3  # ошибка в query
        