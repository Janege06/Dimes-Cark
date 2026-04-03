from question_manager import Category, Question


class GameState:
    TOTAL_ROUNDS = 8
    Q_TIME = 20

    def __init__(self):
        self.current_question = None
        self.current_category = None
        self.score = 0
        self.lives = 3
        self.streak = 0
        self.max_streak = 0
        self.round = 0
        self.correct_answers = 0
        self.bonus_points = 0
        self.spinning = False
        self.answering = False
        self.question_timer = None
        self.time_left = GameState.Q_TIME
        self.round_results = [] # 'ok'|'bad' per round
        self.used_questions: dict[str, list[int]] = {
            Category.SURDURULEBILIRLIK.value: [],
            Category.URUNLER.value: [],
            Category.GENEL_KULTUR.value: [],
            Category.BONUS.value: []
        }
        self.screen = 'start' # 'start', 'main', 'pause', 'end'