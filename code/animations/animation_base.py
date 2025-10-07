class Animation:
    """Base class for animations."""

    def __init__(self, duration, on_complete=None):
        self.duration = duration
        self.elapsed_time = 0
        self.is_completed = False
        self.on_complete = on_complete

    def update(self, delta_time):
        if self.is_completed:
            return True

        self.elapsed_time += delta_time
        if self.elapsed_time >= self.duration:
            self.elapsed_time = self.duration
            self.is_completed = True
            if self.on_complete:
                self.on_complete()
            return True

        return False

    def reset(self):
        self.elapsed_time = 0
        self.is_completed = False

    def get_progress(self):
        return min(1.0, self.elapsed_time / self.duration)


class EasingFunctions:
    """Static class containing various easing functions."""

    @staticmethod
    def linear(progress):
        return progress

    @staticmethod
    def ease_in_quad(progress):
        return progress * progress

    @staticmethod
    def ease_out_quad(progress):
        return 1 - (1 - progress) * (1 - progress)

    @staticmethod
    def ease_in_out_quad(progress):
        if progress < 0.5:
            return 2 * progress * progress
        else:
            return 1 - pow(-2 * progress + 2, 2) / 2