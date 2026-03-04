import pandas as pd
import re

EXPECTED_COLUMNS = [
    "№ п/п",
    "Наименование",
    "Значение автомобильной дороги",
    "Категория",
    "Протяженность, км",
]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.replace("\u00A0", " ", regex=False)   # неразрывные пробелы
        .str.replace("\n", " ", regex=False)       # переносы строк
        .str.replace(r"\s+", " ", regex=True)      # множественные пробелы
        .str.strip()
    )
    return df


def read_and_validate_excel(file_obj) -> pd.DataFrame:
    """
    Читает Excel из загруженного файла Django (InMemoryUploadedFile/TemporaryUploadedFile),
    нормализует заголовки и проверяет структуру (названия + порядок).
    Возвращает DataFrame или кидает ValueError с понятным сообщением.
    """
    df = pd.read_excel(file_obj)
    df = normalize_columns(df)

    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            "Неверная структура файла. Проверьте порядок и названия колонок: "
            + ", ".join(EXPECTED_COLUMNS)
        )

    return df



def calculate_total_length(df: pd.DataFrame) -> float:
    df = df.copy()

    def clean_number(value):
        if pd.isna(value):
            return 0

        value = str(value)
        value = value.replace("\u00A0", "")
        value = value.replace(" ", "")
        value = value.replace(",", ".")

        # удаляем всё кроме цифр и точки
        value = re.sub(r"[^0-9.]", "", value)

        try:
            return float(value)
        except ValueError:
            return 0

    df["Протяженность, км"] = df["Протяженность, км"].apply(clean_number)

    return df["Протяженность, км"].sum()