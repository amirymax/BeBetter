class Player:
    def __init__(self, user_id):
        self.user_id = user_id
        self.name = None
        self.category = None
        self.state = None
        
    def set_name(self, name):
        self.name = name

    def set_category(self, category):
        self.category = category
        