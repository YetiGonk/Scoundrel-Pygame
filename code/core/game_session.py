class GameSession:
    """Holds all game state for a single playthrough"""
    def __init__(self, floor_type="dungeon"):
        self.player = Player()
        self.deck = Deck(floor_type)
        self.discard_pile = DiscardPile()
        self.room = Room()
        self.current_floor = floor_type
        
        self.completed_rooms = 0
        self.floor_completed = False
        self.ran_last_turn = False