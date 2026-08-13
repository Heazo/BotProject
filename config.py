import logging
import os
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable is not set: {name}")
    return value


def _port() -> int:
    value = os.getenv("DB_PORT", "5432")
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError("DB_PORT must be an integer") from exc

@dataclass(frozen=True)
class Settings:
    telegram_token: str
    vk_token: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    log_level: int

class EmojisSetEnum(Enum):
    DEFAULT = "default"
    ALTERNATIVE = "alternative"
    HALLOWEEN = "halloween"
    NEW_YEAR = "new_year"

#TODO: Сделать словарь словарей эмоджи
@dataclass(frozen=True)
class Mess_Config:
    start_message: str = ("Привет!\n"
                          "Если Вы ещё не привязали группу, сделайте это с помощью команды /search <номер_группы>")
    find_group_description: str = "Привязать группу. Пример: /search 123456"
    start_menu_message: str = "Привет! Выберите день для просмотра расписания:"
    today_description: str = "Расписание на сегодня"
    tomorrow_description: str = "Расписание на завтра"
    week_description: str = "Выбрать неделю и день"
    choices_description: str = "Мои предметы по выбору"
    weekday_descriptions: tuple[str, ...] = (
        "Расписание на понедельник",
        "Расписание на вторник",
        "Расписание на среду",
        "Расписание на четверг",
        "Расписание на пятницу",
        "Расписание на субботу",
        "Расписание на воскресенье",
    )
    find_group_message: str = ("Пожалуйста, укажите номер группы.\n"
                               "Пример: /search 123456")
    group_linked_message: str = (
        "Группа {group_num} успешно привязана!\n\n"
        "Теперь Вы можете получать расписание:\n"
        "• /today - на сегодня\n"
        "• /tomorrow - на завтра\n"
        "• /week - на неделю"
    )
    group_linked_short_message: str = (
        "Группа {group_num} успешно привязана! \n"
        "Теперь Вы можете получать расписание"
    )
    group_link_error_message: str = (
        "Ошибка при привязке группы.\n"
        "Проверьте правильность номера группы.\n"
        "Если ошибка повторяется, обратитесь к администратору."
    )
    choose_week_message: str = "📅 Выберите неделю:"
    choose_day_message: str = "Выберите день:"
    choose_weekday_message: str = "Выберите день недели:"
    main_menu_message: str = "Главное меню:"
    back_to_weeks_message: str = "Назад к неделям"
    back_message: str = "Назад"
    no_choice_disciplines_message: str = "У вас пока нет добавленных предметов по выбору."
    my_choice_disciplines_message: str = "Мои предметы по выбору:"
    enter_choice_discipline_message: str = "Введите название предмета по выбору:"
    no_text_choice_discipline_error_message: str = "Пожалуйста, отправьте название предмета текстом."
    empty_text_choice_discipline_error_message: str = "Название предмета не может быть пустым."
    choice_discipline_not_found_message: str = (
        "❌ Не удалось найти подходящий предмет.\n"
        "Попробуйте написать название ещё раз."
    )
    choice_discipline_add_error_message: str = (
        "Не удалось добавить предмет. Попробуйте позже."
    )
    delete_choice_discipline_message: str = (
        "Выберите предмет, который хотите удалить:"
    )
    no_choice_disciplines_to_delete_message: str = (
        "У вас нет предметов для удаления."
    )
    choice_discipline_not_found_for_delete_message: str = (
        "Этот предмет отсутствует в вашем списке."
    )
    choice_discipline_delete_error_message: str = (
        "Не удалось удалить предмет."
    )
    choice_discipline_invalid_id_message: str = (
        "Некорректный идентификатор предмета."
    )


    num_emojis = {
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣"
        }
    
    default_emojis = {
        "discipline": "📖",
        "auditorium": "🏫",
        "no_classes": "🎉",
        "error": "⚠️",
        "time": "⏰",
        "calendar": "📅",
        "exam": "",
        "Lecture": "",
        "Practical": "",
        "Laboratory": "",
        "Consultation": "",
        "Zachet": "",
    }
    
    new_year_emojis = {
        "discipline": "🎁",
        "auditorium": "☃️",
        "no_classes": "🎉",
        "error": "⚠️",
        "time": "❄️",
        "calendar": "🎄",
        "exam": "",
        "Lecture": "🧦",
        "Practical": "",
        "Laboratory": "",
        "Consultation": "",
        "Zachet": "",
    }
    
    


def load_settings() -> Settings:
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, None)
    if not isinstance(log_level, int):
        raise RuntimeError("LOG_LEVEL must be a valid logging level")

    return Settings(
        telegram_token=_required("TELEGRAM_TOKEN"),
        vk_token=_required("VK_TOKEN"),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=_port(),
        db_name=os.getenv("DB_NAME", "studies_db"),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=_required("DB_PASSWORD"),
        log_level=log_level,
    )
