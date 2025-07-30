import flet as ft
from typing import Union, Tuple, List, Optional


def radio_group(
    options: Union[List[Tuple[str, str]], Tuple[Tuple[str, str], ...]],
    label: Optional[str] = None,
    value: Optional[str] = None,
    on_change=None
) -> Tuple[ft.Column, ft.RadioGroup]:
    """Создает группу радио-кнопок и возвращает (контейнер, сам контрол)"""
    radio_buttons = [ft.Radio(value=val, label=text) for val, text in options]
    group = ft.RadioGroup(
        content=ft.Column(radio_buttons),
        value=value,
        on_change=on_change
    )
    return ft.Column(
        controls=[ft.Text(label) if label else None, group],
        spacing=5
    ), group

def dropdown(
    options: Union[List[Tuple[str, str]], Tuple[Tuple[str, str], ...]],
    label: Optional[str] = None,
    value: Optional[str] = None,
    on_change=None
) -> Tuple[ft.Column, ft.Dropdown]:
    """Создает выпадающий список и возвращает (контейнер, сам контрол)"""
    dd = ft.Dropdown(
        options=[ft.dropdown.Option(text=text, key=val) for val, text in options],
        value=value,
        on_change=on_change
    )
    return ft.Column(
        controls=[ft.Text(label) if label else None, dd],
        spacing=5
    ), dd
