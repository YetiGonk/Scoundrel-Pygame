class Player:
    def __init__(self, life_points=20, max_life=20):
        self.life_points = life_points
        self.max_life = max_life
        self.inventory = []
        self.equipped_weapon = None
        self.defeated_monsters = []
        self.max_inventory_size = 2
    
    def take_damage(self, amount):
        self.life_points = max(0, self.life_points - amount)
        return self.life_points <= 0  # Returns True if dead
    
    def heal(self, amount):
        self.life_points = min(self.max_life, self.life_points + amount)
    
    def can_add_to_inventory(self):
        return len(self.inventory) < self.max_inventory_size
    
    def equip_weapon(self, weapon):
        self.equipped_weapon = weapon
    
    def has_weapon(self):
        return self.equipped_weapon is not None