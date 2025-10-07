from ..managers.floor_manager import FloorManager

from states.title_state import TitleState
from states.rules_state import RulesState
from states.playing_state import PlayingState
from states.game_over_state import GameOverState
from states.tutorial_state import TutorialState

class GameManager:
    """Manager for game states with roguelike elements."""

    def __init__(self):

        self.floor_manager = FloorManager(self)

        self.states = {
            "title": TitleState(self),
            "rules": RulesState(self),
            "playing": PlayingState(self),
            "game_over": GameOverState(self),
            "tutorial": TutorialState(self),
            "tutorial_watch": TutorialState(self, watch=True),
        }

        self.current_state = None
        self.game_data = {
            "life_points": STARTING_ATTRIBUTES["life_points"],
            "max_life": STARTING_ATTRIBUTES["max_life"],
            "victory": False,
            "run_complete": False
        }

        self.equipped_weapon = {}
        self.defeated_monsters = []
        self.last_card_data = None

        self.fade_alpha = 0
        self.fade_direction = 0
        self.fade_speed = 255 / 0.5
        self.pending_state = None
        self.fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fade_surface.fill(BLACK)
        
        self.fade_surface = self.fade_surface.convert_alpha()

        self.change_state("title")

    def change_state(self, state_name, fade_duration=0.5):
        if self.current_state is None:
            self.current_state = self.states[state_name]
            self.current_state.enter()
            return

        if self.fade_direction != 0:
            return
            
        if self.current_state == self.states[state_name]:
            return
        
        self.fade_speed = 255 / fade_duration
        
        self.pending_state = state_name
        self.fade_direction = 1
        self.fade_alpha = 0

    def _execute_state_transition(self):
        if self.current_state:
            if type(self.current_state) == TutorialState:
                self.has_shown_tutorial = True
            self.current_state.exit()

        if self.pending_state == "title" and not self.floor_manager.floors:
            self.floor_manager.initialise_run()

        self.current_state = self.states[self.pending_state]
        self.current_state.enter()
        self.pending_state = None

    def change_state_instant(self, state_name):
        if self.current_state and self.current_state == self.states[state_name]:
            return

        if self.current_state:
            self.current_state.exit()

        if state_name == "title" and not self.floor_manager.floors:
            self.floor_manager.initialise_run()

        self.current_state = self.states[state_name]
        self.current_state.enter()

    def handle_event(self, event):
        if self.fade_direction != 0 and event.type == MOUSEBUTTONDOWN:
            return
            
        if self.current_state:
            self.current_state.handle_event(event)

    def update(self, delta_time):
        if self.fade_direction != 0:
            self.fade_alpha += self.fade_direction * self.fade_speed * delta_time
            
            if self.fade_direction == 1:
                if self.fade_alpha >= 255:
                    self.fade_alpha = 255
                    self._execute_state_transition()
                    self.fade_direction = -1
            else:
                if self.fade_alpha <= 0:
                    self.fade_alpha = 0
                    self.fade_direction = 0
        
        if self.current_state and not (self.fade_direction == 1):
            self.current_state.update(delta_time)

    def draw(self, surface):
        if self.current_state:
            self.current_state.draw(surface)
        
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(int(self.fade_alpha))
            surface.blit(self.fade_surface, (0, 0))

    def start_new_run(self):
        """Initialise a new roguelike run."""

        self.game_data["life_points"] = STARTING_ATTRIBUTES["life_points"]
        self.game_data["max_life"] = STARTING_ATTRIBUTES["max_life"]
        self.game_data["victory"] = False
        self.game_data["run_complete"] = False

        self.floor_manager.initialise_run()

        self.is_new_run = True

        self.change_state("playing")

    def advance_to_next_room(self):
        """Advance to the next room in the current floor."""
        room_info = self.floor_manager.advance_room()

        if "run_complete" in room_info and room_info["run_complete"]:

            self.game_data["victory"] = True
            self.game_data["run_complete"] = True
            return

        if "is_floor_start" in room_info and room_info["is_floor_start"]:
            return

    def check_game_over(self):
        """Check if the game is over."""
        if self.game_data["life_points"] <= 0:
            self.game_data["victory"] = False

            self.change_state("game_over")
            return True
        return False

    def heal_player(self, amount=5):
        """Heal the player by the specified amount."""
        self.game_data["life_points"] = min(
            self.game_data["life_points"] + amount,
            self.game_data["max_life"]
        )

    def increase_max_health(self, amount=5):
        """Increase the player's maximum health."""
        self.game_data["max_life"] += amount
        self.game_data["life_points"] += amount