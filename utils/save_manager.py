"""Save Manager for handling persistent game data in Scoundrel."""
import os
import json
import pygame
import datetime

class SaveManager:
    """Manages saving and loading of persistent game data."""
    
    def __init__(self):
        """Initialize the save manager."""
        # Create save directory if it doesn't exist
        self.save_dir = os.path.join(os.path.expanduser("~"), ".scoundrel")
        print(self.save_dir)
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Save file paths
        self.settings_path = os.path.join(self.save_dir, "settings.json")
        self.game_save_path = os.path.join(self.save_dir, "game_save.json")
        
        # Default settings
        self.default_settings = {
            "sound_volume": 0.7,
            "music_volume": 0.5,
            "fullscreen": False,
            "resolution": [800, 600]
        }
        
        # Load or create settings file
        self.settings = self._load_or_create(self.settings_path, self.default_settings)
        
    def _load_or_create(self, path, default_data):
        """Load a JSON file or create it with default data if it doesn't exist."""
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
            else:
                with open(path, 'w') as f:
                    json.dump(default_data, f)
                return default_data
        except Exception as e:
            print(f"Error loading/creating {path}: {e}")
            return default_data.copy()
    
    def save_settings(self, settings=None):
        """Save settings to disk."""
        if settings:
            self.settings = settings
        self._save_to_file(self.settings_path, self.settings)
    
    def _save_to_file(self, path, data):
        """Save data to a JSON file."""
        try:
            with open(path, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving to {path}: {e}")
            return False
    
    def save_game_state(self, game_manager):
        """Save the current game state."""
        # Create a dictionary to store all the necessary game state
        save_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "player": {
                "gold": game_manager.player_gold,
                "life_points": game_manager.game_data["life_points"],
                "max_life": game_manager.game_data["max_life"]
            },
            "floor_manager": {
                "floors": game_manager.floor_manager.floors,
                "current_floor_index": game_manager.floor_manager.current_floor_index,
                "current_room": game_manager.floor_manager.current_room
            },
            "items": [],
            "spells": [],
            "deck_system": {
                "delving_deck": [],
                "card_library": []
            },
            "game_flags": {
                "victory": game_manager.game_data.get("victory", False),
                "run_complete": game_manager.game_data.get("run_complete", False),
                "coming_from_merchant": getattr(game_manager, "coming_from_merchant", False)
            },
            "cards": {
                "equipped_weapon": self._serialize_equipped_weapon(game_manager.equipped_weapon),
                "defeated_monsters": [],
                "last_card_data": self._serialize_card(getattr(game_manager, "last_card_data", None)),
            }
        }
        
        # Add defeated monsters
        for monster in getattr(game_manager, "defeated_monsters", []):
            monster_data = self._serialize_card(monster)
            if monster_data:
                save_data["cards"]["defeated_monsters"].append(monster_data)
        
        # If there's a playing state with additional state, save it
        if 'playing' in game_manager.states and game_manager.states['playing']:
            playing_state = game_manager.states['playing']
            
            # Add playing state specific data
            save_data["playing_state"] = {
                "completed_rooms": getattr(playing_state, "completed_rooms", 0),
                "total_rooms_on_floor": getattr(playing_state, "total_rooms_on_floor", 0),
                # Always save floor_completed as False to prevent auto-completion on load
                "floor_completed": False,
                # Reset these room state flags to prevent incorrect state transitions on load
                "gold_reward_given": False,
                "room_completion_in_progress": False,
                "merchant_transition_started": False,
                "is_running": getattr(playing_state, "is_running", False),
                "ran_last_turn": getattr(playing_state, "ran_last_turn", False),
                "damage_shield": getattr(playing_state, "damage_shield", 0),
                "inventory": []
            }
            
            # Save inventory from playing state 
            for inventory_card in getattr(playing_state, "inventory", []):
                card_data = self._serialize_card(inventory_card)
                if card_data:
                    save_data["playing_state"]["inventory"].append(card_data)
        
        # Save items
        for item in game_manager.item_manager.player_items:
            save_data["items"].append({
                "name": item.name,
                "description": item.description,
                "type": item.type,
                "rarity": item.rarity,
                "durability": item.durability,
                "max_durability": item.max_durability,
                "effect": item.effect,
                "icon": item.icon,
                "price": item.price
            })
        
        # Save spells
        for spell in game_manager.spell_manager.player_spells:
            save_data["spells"].append({
                "name": spell.name,
                "description": spell.description,
                "rarity": spell.rarity,
                "memory_points": spell.memory_points,
                "remaining_memory": spell.remaining_memory,
                "effect": spell.effect,
                "icon": spell.icon,
                "price": spell.price
            })
        
        # Save card collections
        for card_data in game_manager.delving_deck:
            save_data["deck_system"]["delving_deck"].append(card_data)
            
        for card_data in game_manager.card_library:
            save_data["deck_system"]["card_library"].append(card_data)
        
        # Save to file
        return self._save_to_file(self.game_save_path, save_data)
    
    def _serialize_equipped_weapon(self, equipped_weapon):
        """Serialize equipped weapon data in the correct format."""
        if not equipped_weapon or "node" not in equipped_weapon:
            return None
            
        weapon_card = equipped_weapon.get("node")
        card_data = self._serialize_card(weapon_card)
        
        # Add additional weapon data that might be needed
        if card_data:
            # Add the suit and value directly to the equipped_weapon dict
            card_data["value"] = getattr(weapon_card, "value", 0)
            card_data["suit"] = getattr(weapon_card, "suit", "")
            
        return card_data
    
    def _serialize_card(self, card):
        """Convert a card object to a serializable dict."""
        if card is None:
            return None
            
        card_data = {
            "suit": card.suit,
            "value": card.value,
            "floor_type": getattr(card, "floor_type", "dungeon"),
            "type": getattr(card, "type", ""),
            "name": getattr(card, "name", ""),
        }
        
        # Add type-specific properties
        if hasattr(card, "weapon_type"):
            card_data["weapon_type"] = card.weapon_type
        if hasattr(card, "damage_type"):
            card_data["damage_type"] = card.damage_type
        if hasattr(card, "monster_type"):
            card_data["monster_type"] = card.monster_type
            
        return card_data
    
    def load_game_state(self, game_manager):
        """Load a saved game state."""
        save_data = self._load_or_create(self.game_save_path, None)
        if not save_data:
            return False
        
        try:
            # Load player stats
            game_manager.player_gold = save_data["player"]["gold"]
            game_manager.game_data["life_points"] = save_data["player"]["life_points"]
            game_manager.game_data["max_life"] = save_data["player"]["max_life"]
            
            # Load floor state
            game_manager.floor_manager.floors = save_data["floor_manager"]["floors"]
            game_manager.floor_manager.current_floor_index = save_data["floor_manager"]["current_floor_index"]
            game_manager.floor_manager.current_room = save_data["floor_manager"]["current_room"]
            
            # Load game flags
            if "game_flags" in save_data:
                for key, value in save_data["game_flags"].items():
                    if key in ["victory", "run_complete"]:
                        game_manager.game_data[key] = value
                    else:
                        setattr(game_manager, key, value)
            
            # Clear existing items and spells
            game_manager.item_manager.player_items = []
            game_manager.spell_manager.player_spells = []
            
            # Load items
            from item_manager import Item
            for item_data in save_data.get("items", []):
                item = Item(item_data)
                game_manager.item_manager.player_items.append(item)
            
            # Load spells
            from spell_manager import Spell
            for spell_data in save_data.get("spells", []):
                spell = Spell(spell_data)
                game_manager.spell_manager.player_spells.append(spell)
            
            # Load card collections
            game_manager.delving_deck = save_data["deck_system"]["delving_deck"]
            game_manager.card_library = save_data["deck_system"]["card_library"]
            
            # Prepare to load cards
            from components.card import Card
            
            # Load card data
            if "cards" in save_data:
                # Load equipped weapon
                if save_data["cards"].get("equipped_weapon"):
                    card_data = save_data["cards"]["equipped_weapon"]
                    weapon_card = self._create_card_from_data(card_data)
                    
                    if weapon_card:
                        # Set the equipped weapon
                        game_manager.equipped_weapon = {
                            "node": weapon_card,
                            "value": weapon_card.value,
                            "suit": weapon_card.suit
                        }
                
                # Load defeated monsters
                game_manager.defeated_monsters = []
                for monster_data in save_data["cards"].get("defeated_monsters", []):
                    monster_card = self._create_card_from_data(monster_data)
                    if monster_card:
                        game_manager.defeated_monsters.append(monster_card)
                
                # Load last card data if it exists
                if save_data["cards"].get("last_card_data"):
                    game_manager.last_card_data = save_data["cards"]["last_card_data"]
            
            # Load playing state data if exists
            if "playing_state" in save_data and "playing" in game_manager.states:
                playing_state = game_manager.states["playing"]
                
                # Set flags and counters
                for key, value in save_data["playing_state"].items():
                    if key != "inventory" and key != "floor_completed":  # Handle inventory separately and don't overwrite floor_completed
                        setattr(playing_state, key, value)
                
                # Don't load floor_completed from save - when a new floor is loaded, it shouldn't be already completed
                # This ensures the floor_completed flag initialized in _initialize_card_visuals as False remains False
                
                # Load inventory cards
                playing_state.inventory = []
                for card_data in save_data["playing_state"].get("inventory", []):
                    inventory_card = self._create_card_from_data(card_data)
                    if inventory_card:
                        playing_state.inventory.append(inventory_card)
            
            return True
        except Exception as e:
            print(f"Error loading game state: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_card_from_data(self, card_data):
        """Create a Card object from serialized data."""
        if not card_data:
            return None
            
        from components.card import Card
        
        try:
            # Create basic card 
            suit = card_data.get("suit", "spades")
            value = card_data.get("value", 2)
            floor_type = card_data.get("floor_type", "dungeon")
            
            card = Card(suit, value, floor_type)
            
            # Set additional card properties
            for key, value in card_data.items():
                if key not in ["suit", "value", "floor_type"]:
                    setattr(card, key, value)
            
            return card
        except Exception as e:
            print(f"Error creating card: {e}")
            return None
    
    def has_saved_game(self):
        """Check if there is a saved game."""
        return os.path.exists(self.game_save_path)
    
    def get_saved_game_info(self):
        """Get basic info about the saved game."""
        if not self.has_saved_game():
            return None
            
        save_data = self._load_or_create(self.game_save_path, None)
        if not save_data:
            return None
        
        # Extract basic info for display
        try:
            timestamp = save_data.get("timestamp", "Unknown date")
            if isinstance(timestamp, str):
                try:
                    # Convert ISO timestamp to readable format
                    dt = datetime.datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%b %d, %Y %H:%M")
                except:
                    pass
                    
            # Extract basic game progress stats
            current_floor = save_data["floor_manager"]["current_floor_index"] + 1
            total_floors = len(save_data["floor_manager"]["floors"])
            current_room = save_data["floor_manager"]["current_room"]
            gold = save_data["player"]["gold"]
            health = save_data["player"]["life_points"]
            max_health = save_data["player"]["max_life"]
            
            # Count items and spells
            item_count = len(save_data.get("items", []))
            spell_count = len(save_data.get("spells", []))
            
            return {
                "timestamp": timestamp,
                "current_floor": current_floor,
                "total_floors": total_floors,
                "current_room": current_room,
                "gold": gold,
                "health": f"{health}/{max_health}",
                "items": item_count,
                "spells": spell_count
            }
        except Exception as e:
            print(f"Error getting saved game info: {e}")
            return None
    
    def get_settings(self):
        """Get the current settings."""
        return self.settings
    
    def delete_saved_game(self):
        """Delete the saved game."""
        if os.path.exists(self.game_save_path):
            os.remove(self.game_save_path)
            return True
        return False

# Create a global instance of SaveManager
save_manager = SaveManager()