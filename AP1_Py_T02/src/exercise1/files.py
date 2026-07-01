from typing import List
from classes import Student, Examiner, Question


def read_students(file_path: str) -> List[Student]:
    """
    Читает данные студентов из файла и возвращает список объектов Student.
    Формат строк: "Имя Пол"
    """
    students: List[Student] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            name, gender = line.split()
            students.append(Student(name, gender))
    return students


def read_examiners(file_path: str) -> List[Examiner]:
    """
    Читает данные экзаменаторов из файла и возвращает список объектов Examiner.
    Формат строк: "Имя Пол"
    """
    examiners: List[Examiner] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            name, gender = line.split()
            examiners.append(Examiner(name, gender))
    return examiners


def read_questions(path: str) -> List[Question]:
    """
    Читает список вопросов и возвращает список объектов Question.
    Каждая непустая строка — отдельный вопрос.
    """
    questions: List[Question] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            questions.append(Question(i, line))
    return questions
