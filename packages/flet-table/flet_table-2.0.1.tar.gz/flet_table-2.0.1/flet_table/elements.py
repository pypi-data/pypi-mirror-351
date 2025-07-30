import flet as ft
from datetime import datetime, time
from typing import Union, Tuple, List, Optional, Callable


def radio_group(
    options: Union[List[Tuple[str, str]], Tuple[Tuple[str, str], ...]],
    label: Optional[str] = None,
    value: Optional[str] = None,
    on_change=None
) -> ft.Column:
    """Создает группу радио-кнопок"""
    radio_buttons = [ft.Radio(value=val, label=text) for val, text in options]
    return ft.Column(
        controls=[
            ft.Text(label) if label else None,
            ft.RadioGroup(
                content=ft.Column(radio_buttons),
                value=value,
                on_change=on_change
            )
        ],
        spacing=5
    )

def dropdown(
    options: Union[List[Tuple[str, str]], Tuple[Tuple[str, str], ...]],
    label: Optional[str] = None,
    value: Optional[str] = None,
    on_change=None
) -> ft.Column:
    """Создает выпадающий список"""
    return ft.Column(
        controls=[
            ft.Text(label) if label else None,
            ft.Dropdown(
                options=[ft.dropdown.Option(text=text, key=val) for val, text in options],
                value=value,
                on_change=on_change
            )
        ],
        spacing=5
    )

def datetime_input(
    label: Optional[str] = None,
    value: Optional[Union[datetime, str]] = None,
    mode: str = "datetime"  # "date", "time" или "datetime"
) -> ft.TextField:
    """Поле ввода даты/времени"""
    def parse_value(v):
        if v is None:
            return ""
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M:%S" if mode == "datetime" else 
                            "%Y-%m-%d" if mode == "date" else 
                            "%H:%M:%S")
        return str(v)
    
    return ft.TextField(
        label=label,
        value=parse_value(value),
        hint_text="YYYY-MM-DD HH:MM:SS" if mode == "datetime" else 
                 "YYYY-MM-DD" if mode == "date" else 
                 "HH:MM:SS",
        keyboard_type=ft.KeyboardType.TEXT
    )

def get_date_picker(page : ft.Page):
    return ft.ElevatedButton(
        "Pick date",
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda e: page.open(
            ft.DatePicker()
        ))

def get_time_picker(page : ft.Page):
    cupertino_date_picker = ft.CupertinoDatePicker(
    date_picker_mode=ft.CupertinoDatePickerMode.DATE_AND_TIME
    )
    return ft.CupertinoFilledButton(
            "Open CupertinoDatePicker",
            on_click=lambda e: page.open(
                ft.CupertinoBottomSheet(
                    cupertino_date_picker,
                    height=216,
                    padding=ft.padding.only(top=6),
                )
            ),
        )

def get_switch(for_label_text : str):
    return ft.Switch(label=for_label_text, value=False)


def search_bar_element(
    suggestions: List[str] = None,
    search_hint: str = "Search...",
    view_hint: str = "Select item",
    on_select: Optional[Callable[[str], None]] = None,
    on_search: Optional[Callable[[str], None]] = None
) -> ft.Column:
    """Создает готовый элемент SearchBar"""
    suggestions = suggestions or []
    
    def handle_select(e):
        search_bar.close_view(e.control.data)
        if on_select:
            on_select(e.control.data)
    
    def handle_search_change(e):
        if on_search:
            on_search(e.data)
    
    search_bar = ft.SearchBar(
        bar_hint_text=search_hint,
        view_hint_text=view_hint,
        on_change=handle_search_change,
        controls=[
            ft.ListTile(
                title=ft.Text(item),
                on_click=handle_select,
                data=item
            ) for item in suggestions
        ]
    )
    
    return ft.Column(
        controls=[
            ft.OutlinedButton(
                "Open Search",
                on_click=lambda _: search_bar.open_view(),
            ),
            search_bar
        ],
        spacing=10
    )

def time_range_input(
    label: Optional[str] = None,
    start_time: Optional[Union[time, str]] = None,
    end_time: Optional[Union[time, str]] = None
) -> ft.Column:
    """Два поля ввода для диапазона времени"""
    return ft.Column(
        controls=[
            ft.Text(label) if label else None,
            ft.Row(
                controls=[
                    datetime_input(
                        label="Начало",
                        value=start_time,
                        mode="time"
                    ),
                    datetime_input(
                        label="Конец",
                        value=end_time,
                        mode="time"
                    )
                ],
                spacing=20
            )
        ],
        spacing=5
    )

def get_alert_dialog(page):
    return ft.AlertDialog(
        title=ft.Text("Hi, this is a non-modal dialog!"),
        on_dismiss=lambda e: page.add(ft.Text("Non-modal dialog dismissed")),
    )

def log_page_alert_dialo(page):
    bs = ft.BottomSheet(
        content=ft.Container(
            padding=50,
            content=ft.Column(
                tight=True,
                controls=[
                    ft.Text("This is bottom sheet's content!"),
                    ft.ElevatedButton("Close bottom sheet", on_click=lambda _: page.close(bs)),
                ],
            ),
        ),
    )
    page.add(ft.ElevatedButton("Result", on_click=lambda _: page.open(bs)))


def get_error_banner(page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    action_button_style = ft.ButtonStyle(color=ft.Colors.BLUE)
    banner = ft.Banner(
        bgcolor=ft.Colors.AMBER_100,
        leading=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER, size=40),
        content=ft.Text(
            value="Ошибочка епта",
            color=ft.Colors.BLACK,
        ),
        actions=[
            ft.TextButton(text="Retry", style=action_button_style),
            ft.TextButton(text="Cancel", style=action_button_style)
        ],
    )

    page.add(ft.ElevatedButton("Show Banner", on_click=lambda e: page.open(banner)))


def get_tabs(tabs : List[ft.Tab]):
    'generate tabs'
    return ft.Tabs(
        selected_index=1,
        animation_duration=300,
        tabs=[tabs],
        expand=1,
    )

    
def main(page: ft.Page):
    # Радио-кнопки
    rg = radio_group(
        options=[("1", "Да"), ("2", "Нет")],
        label="Вы согласны?",
        value="1"
    )
    
    # Выпадающий список
    dd = dropdown(
        options=[("m", "Мужской"), ("f", "Женский")],
        label="Пол"
    )
    
    # Поле даты/времени
    dt = datetime_input(
        label="Дата встречи",
        mode="datetime"
    )
    
    # Диапазон времени
    tr = time_range_input(
        label="Время работы",
        start_time="09:00",
        end_time="18:00"
    )
    
    page.add(rg, dd, dt, tr)

if __name__ == '__main__':
    ft.app(target=main)
