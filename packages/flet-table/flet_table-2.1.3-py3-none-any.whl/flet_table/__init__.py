from .v1.elements import radio_group as v1_radio_group
from .v1.elements import dropdown as v1_dropdown 
from .editable_table import EditableTable
from .elements import radio_group, dropdown, get_error_banner, get_alert_dialog, get_date_picker, get_switch, get_tabs, get_time_picker
from .hash_pass_functools import get_password_hash, validate_password
from .table import create_flet_table, create_image_table

'''
# ──────────────────────────────────────────────────────
# 🧭 Краткий гайд по выравниванию и стилизации в Flet
# ──────────────────────────────────────────────────────

# 📦 Основные параметры выравнивания страницы:
page.horizontal_alignment = ft.MainAxisAlignment.CENTER   # по горизонтали: START, CENTER, END, SPACE_BETWEEN и др.
page.vertical_alignment = ft.CrossAxisAlignment.CENTER     # по вертикали: START, CENTER, END

# 📐 Контейнер с отступами и выравниванием:
ft.Container(
    content=...,
    padding=20,                       # отступы внутри (int или EdgeInsets)
    margin=ft.Margin(10, 10, 0, 0),   # внешние отступы: слева, сверху, справа, снизу
    alignment=ft.alignment.center,    # выравнивание контента в контейнере
    bgcolor=ft.Colors.AMBER_100       # цвет фона
)

# 🎯 Центрирование текста:
ft.Text("Центр", text_align=ft.TextAlign.CENTER)

# 📏 Управление размерами:
ft.Container(width=400, height=100)
ft.TextField(width=300)

# 🧱 Row и Column — выравнивание дочерних элементов:
ft.Row(
    controls=[...],
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # или CENTER, START, END
    vertical_alignment=ft.CrossAxisAlignment.CENTER
)

# 🌐 Заполнение доступного пространства:
ft.Expanded(ft.Text("Растягивается по ширине"))

# 🧊 Card или Elevated Container:
ft.Card(
    content=ft.Container(
        content=ft.Text("Внутри карточки"),
        padding=10
    )
)

# 📌 Подсказка: используйте page.update() после изменения элементов

# ──────────────────────────────────────────────────────
'''

'''
# ──────────────────────────────────────────────────────
# 🎨 Гайд по цветам и иконкам в Flet
# ──────────────────────────────────────────────────────

# 📦 Цвет текста, фона, кнопок
ft.Text("Красный текст", color=ft.colors.RED)

ft.Container(
    content=ft.Text("Синий фон"),
    bgcolor=ft.colors.BLUE_200,
    padding=10
)

ft.ElevatedButton("Кнопка", bgcolor=ft.colors.GREEN_500, color=ft.colors.WHITE)

# ✏️ Цвет рамки и курсора в поле ввода
ft.TextField(
    label="Имя",
    border_color=ft.colors.PURPLE,
    cursor_color=ft.colors.PINK
)

# ✅ Новый стиль через Colors (вместо устаревшего colors)
from flet import Colors
ft.Text("Современный стиль", color=Colors.TEAL)

# ⭐ Добавление иконок
# Просто иконка
ft.Icon(name=ft.icons.STAR, color=ft.colors.YELLOW)

# Кнопка с иконкой
ft.ElevatedButton(text="Сохранить", icon=ft.icons.SAVE)

# Иконка-кнопка (без текста)
ft.IconButton(icon=ft.icons.DELETE, tooltip="Удалить", icon_color=ft.colors.RED)

# В таблице (рядом с текстом)
ft.DataCell(
    ft.Row([
        ft.Text("Готово"),
        ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.colors.GREEN)
    ])
)

# 🧪 Мини-комбинация:
ft.Row([
    ft.Icon(ft.icons.LIGHT_MODE, color=ft.colors.YELLOW_600),
    ft.Text("Светлая тема", color=ft.colors.BLACK87)
])

# ──────────────────────────────────────────────────────
'''