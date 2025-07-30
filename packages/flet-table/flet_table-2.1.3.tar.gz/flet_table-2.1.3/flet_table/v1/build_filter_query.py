import flet as ft
from typing import Optional

def build_filtered_query(
    base_query: str,
    filters: dict[str, Optional[str]],
    sort_field: Optional[str] = None,
    sort_direction: Optional[str] = "ASC"
) -> tuple[str, list]:
    """
    Собирает SQL-запрос с фильтрами и сортировкой.
    filters — словарь вида {"field": value or None}
    """
    conditions = []
    params = []

    for field, value in filters.items():
        if value:  # если значение выбрано
            conditions.append(f"{field} = %s")
            params.append(value)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    if sort_field:
        base_query += f" ORDER BY {sort_field} {sort_direction}"

    return base_query, params

'''
def main(page: ft.Page):
    page.title = "Фильтрация и сортировка"
    page.scroll = True

    filters = {
        "status": None,
        "category": None
    }

    sort_field = "created_at"

    def on_filter_change(e):
        # Обновляем фильтры
        filters["status"] = status_dd.value
        filters["category"] = category_dd.value

        # Собираем запрос
        query, params = build_filtered_query(
            base_query="SELECT * FROM items",
            filters=filters,
            sort_field=sort_field,
            sort_direction="DESC"
        )

        print("Query:", query)
        print("Params:", params)

        # Пример:
        # cursor.execute(query, params)
        # results = cursor.fetchall()
        # render_table(results)

    status_dd = ft.Dropdown(
        label="Статус",
        options=[ft.dropdown.Option("new", "Новый"), ft.dropdown.Option("done", "Выполнен")],
        on_change=on_filter_change
    )

    category_dd = ft.Dropdown(
        label="Категория",
        options=[ft.dropdown.Option("1", "A"), ft.dropdown.Option("2", "B")],
        on_change=on_filter_change
    )

    page.add(ft.Row([status_dd, category_dd]))
'''