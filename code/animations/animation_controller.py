from config import *
from animations.animation_base import Animation, EasingFunctions
from animations.specific_animations import *
    

class AnimationController:
    """Manages all animations in the game."""

    def __init__(self, playing_state):
        """Initialise with a reference to the playing state."""
        self.playing_state = playing_state

    @property
    def session(self):
        """Quick access to game session."""
        return self.playing_state.session

    def animate_card_to_discard(self, card):
        """Animate a card being destroyed and appearing in the discard pile."""

        if card.type == "monster":
            effect_type = "slash"
        elif card.type == "weapon":
            effect_type = "shatter"
        elif card.type == "potion":
            effect_type = "burn"
        else:
            effect_type = random.choice(["slash", "burn", "shatter"])

        destroy_anim = DestructionAnimation(
            card,
            effect_type,
            duration=0.5,
            on_complete=lambda: self.materialise_card_at_discard(card)
        )

        self.playing_state.animation_manager.add_animation(destroy_anim)

    def materialise_card_at_discard(self, card):
        """Materialise the card at the discard pile position."""

        card.update_position(self.session.discard_pile.position)

        materialise_anim = MaterialiseAnimation(
            card,
            self.session.discard_pile.position,
            effect_type="sparkle",
            duration=0.3,
            on_complete=lambda: self.playing_state.room_manager.remove_and_discard(card)
        )

        self.playing_state.animation_manager.add_animation(materialise_anim)

    def animate_card_movement(self, card, target_pos, duration=0.3, easing=None,
        on_complete=None):
        """Create a simple, direct animation for card movement with optional callback."""
        if easing is None:
            easing = EasingFunctions.ease_out_quad

        animation = MoveAnimation(
            card,
            card.rect.topleft,
            target_pos,
            duration,
            easing,
            on_complete
        )

        self.playing_state.animation_manager.add_animation(animation)

    def position_monster_stack(self, preserve_positions=False):
        """Position defeated monsters in a stack."""
        if not self.session.defeated_monsters or not self.session.equipped_weapon:
            return

        weapon_card = self.session.equipped_weapon
        is_default_weapon_position = (weapon_card.rect.x == WEAPON_POSITION[0] and weapon_card.rect.y == WEAPON_POSITION[1])

        start_x = weapon_card.rect.x + MONSTER_START_OFFSET[0]

        for i, monster in enumerate(self.session.defeated_monsters):

            has_valid_position = hasattr(monster, 'rect') and monster.rect.x > 0 and monster.rect.y > 0

            new_stack_position = (
                start_x + i * MONSTER_STACK_OFFSET[0],
                weapon_card.rect.y + MONSTER_STACK_OFFSET[1] * i
            )

            if not has_valid_position or not preserve_positions:
                self.animate_card_movement(monster, new_stack_position)

        if is_default_weapon_position:
            new_weapon_position = (
                weapon_card.rect.x - MONSTER_STACK_OFFSET[1]*2,
                weapon_card.rect.y
            )
            self.animate_card_movement(weapon_card, new_weapon_position)

    def schedule_delayed_animation(self, delay, callback):
        """Schedule an animation to start after a delay."""

        timer = Animation(delay, on_complete=callback)
        self.playing_state.animation_manager.add_animation(timer)

    def start_card_flip(self, card):
        """Start the flip animation for a card."""
        card.start_flip()

    def animate_health_change(self, is_damage, amount):
        """Create animation for health change."""

        health_display_x = self.session.deck.rect.x + 100
        health_display_y = SCREEN_HEIGHT - self.session.deck.rect.y - 30

        health_anim = HealthChangeAnimation(
            is_damage,
            amount,
            (health_display_x, health_display_y),
            self.playing_state.body_font
        )

        self.playing_state.animation_manager.add_animation(health_anim)

    def animate_card_to_inventory(self, card):
        """Animate a card moving to its position in the inventory."""

        inv_width = INVENTORY_PANEL_WIDTH
        inv_height = INVENTORY_PANEL_HEIGHT
        inv_x = INVENTORY_PANEL_X
        inv_y = INVENTORY_PANEL_Y

        card_scale = 1.0

        card.update_scale(card_scale)

        card.in_inventory = True

        scaled_card_width = int(CARD_WIDTH * card_scale)
        scaled_card_height = int(CARD_HEIGHT * card_scale)

        inventory_x = inv_x + (inv_width // 2) - (scaled_card_width // 2)

        num_cards = len(self.session.inventory)

        if num_cards == 1:

            inventory_y = inv_y + (inv_height // 2) - (scaled_card_height // 2)
        elif num_cards == 2:

            existing_card = self.session.inventory[0]
            top_y = inv_y + (inv_height // 4) - (scaled_card_height // 2)

            if existing_card.rect.y != top_y:
                self.animate_card_movement(existing_card, (inventory_x, top_y))

            inventory_y = inv_y + (3 * inv_height // 4) - (scaled_card_height // 2)

        inventory_pos = (inventory_x, inventory_y)

        self.animate_card_movement(card, inventory_pos, on_complete=lambda: self.playing_state.inventory_manager.position_inventory_cards())

