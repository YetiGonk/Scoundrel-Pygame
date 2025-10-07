from config import FLOOR_NAMES, FLOOR_TOTAL
import random

class FloorManager:
    """Manages the different floors in a run."""

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.floors = [f"{random.choice(FLOOR_NAMES['first'])} {random.choice(FLOOR_NAMES['second'])}" for _ in range(FLOOR_TOTAL)]
        self.current_floor_index = 0
        self.current_room = 1
        self.total_floors = FLOOR_TOTAL

    def initialise_run(self):
        """Initialise a new run with randomised floor order."""
        self.current_floor_index = 0

        self.current_room = 1
        return self.get_current_floor()

    def get_current_floor(self):
        """Get the current floor type."""
        if not self.floors or self.current_floor_index >= len(self.floors):

            if not self.floors:
                self.initialise_run()

            if not self.floors or self.current_floor_index >= len(self.floors):
                return "dungeon"

        return self.floors[self.current_floor_index]

    def advance_room(self):
        """Move to the next room in the current floor."""
        old_room = self.current_room
        self.current_room += 1

        if self.current_room > FLOOR_TOTAL:
            return self.advance_floor()

        return {
            "floor": self.get_current_floor(),
            "room": self.current_room
        }

    def advance_floor(self):
        """Move to the next floor."""
        self.current_floor_index += 1

        self.current_room = 1

        if self.current_floor_index >= len(self.floors):
            return {"run_complete": True}

        if hasattr(self.game_manager, 'states') and 'playing' in self.game_manager.states:
            playing_state = self.game_manager.states["playing"]
            if hasattr(playing_state, 'completed_rooms'):
                playing_state.completed_rooms = 0

        return {
            "floor": self.get_current_floor(),
            "room": self.current_room,
            "is_floor_start": True
        }