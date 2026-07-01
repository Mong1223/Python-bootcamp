import random
import time
from typing import List, Optional


class Student:
    def __init__(self, name: str, gender: str):
        self.name = name
        self.gender = gender

        self.status: str = "Очередь"
        self.time: Optional[float] = None
        self.passed: Optional[bool] = None


class Examiner:
    def __init__(self, name: str, gender: str):
        self.name = name
        self.gender = gender

        self.current_student: Optional[str] = None
        self.total_students: int = 0
        self.failed_students: int = 0
        self.end_time: Optional[float] = (
            None  # время окончания работы (от начала экзамена)
        )

        self._lunch_taken: bool = False
        self.lunch_duration: float = 0

    def maybe_take_lunch(self, exam_start: float) -> None:
        """
        Экзаменатор идёт на обед один раз после 30 секунд
        (можно заменить константу для теста).
        Пауза 12–18 секунд.
        """
        if self._lunch_taken:
            return

        elapsed = time.time() - exam_start
        if elapsed >= 3.0:
            self.lunch_duration = random.uniform(12.0, 18.0)
            time.sleep(self.lunch_duration)
            self._lunch_taken = True

    @property
    def exam_duration(self) -> float:
        """
        Длительность экзамена — случайное число
        от len(name)-1 до len(name)+1.
        """
        L = len(self.name)
        return random.uniform(L - 1, L + 1)

    def pass_or_no(self, correct: int, incorrect: int) -> bool:
        """
        Модель настроения:
        - 1/8 плохое → провалил
        - 1/4 хорошее → сдал
        - 5/8 нейтральное:
          объективная оценка по количеству верных/неверных.
        """
        mood = random.choices(
            ["Fail", "Pass", "Neutral"],
            weights=[1 / 8, 1 / 4, 5 / 8],
            k=1,
        )[0]

        if mood == "Fail":
            return False
        if mood == "Pass":
            return True
        return correct > incorrect


class Question:
    GOLDEN_RATIO = (1 + 5**0.5) / 2  # φ ≈ 1.618...

    def __init__(self, id: int, text: str):
        self.id = id
        self.text = text.strip()

    @property
    def words(self) -> List[str]:
        return self.text.split()

    @classmethod
    def _golden_probs(cls, n: int) -> List[float]:
        remaining = 1.0
        probs: List[float] = []

        for _ in range(n - 1):
            p = remaining / cls.GOLDEN_RATIO
            probs.append(p)
            remaining -= p

        probs.append(remaining)
        return probs

    def _pick_index(self, gender: str) -> int:
        """
        Выбор индекса слова по золотому сечению.
        Для 'M' — веса ближе к началу,
        для 'F' — зеркально к концу.
        """
        words = self.words
        n = len(words)
        base = self._golden_probs(n)

        if gender == "M":
            weights = base
        else:
            weights = list(reversed(base))

        indices = list(range(n))
        return random.choices(indices, weights=weights, k=1)[0]

    def student_choice(self, gender: str) -> int:
        """
        Индекс слова, выбранный студентом данного пола.
        """
        return self._pick_index(gender)

    def examiner_choice(self, examiner_gender: str) -> List[int]:
        """
        Экзаменатор выбирает 1 слово, затем с вероятностью 1/3 ещё одно,
        и так до тех пор, пока не выберет все или случай не остановит.
        """
        chosen = set()
        words = self.words
        n = len(words)

        while True:
            idx = self._pick_index(examiner_gender)
            chosen.add(idx)
            if len(chosen) == n:
                break
            if random.random() > (1.0 / 3.0):
                break

        return list(chosen)
