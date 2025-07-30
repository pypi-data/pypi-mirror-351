import pandas as pd 
import simpledt
import flet as ft 
from pathlib import Path
from typing import Tuple, List
import os

def create_flet_table(database_output : tuple[tuple], columns_names : list[str]) -> simpledt.DataFrame:
    df = pd.DataFrame(list(database_output), columns=columns_names)
    generate_object = simpledt.DataFrame(df)
    return generate_object.datatable

def create_image_table(data: Tuple[Tuple], columns_names: List[str], assets_dir: str = "assets") -> ft.DataTable:
    """
    Создает таблицу Flet с изображениями в первой колонке.
    
    Args:
        data: Кортеж с данными (первый элемент каждой строки - путь к изображению)
        columns_names: Список названий колонок
        assets_dir: Папка с изображениями (по умолчанию 'assets')
        
    Returns:
        Готовый DataTable для отображения
    """
    def get_asset_path(img_path: str) -> str:
        """Проверяет и возвращает корректный путь к изображению"""
        # Если путь абсолютный - используем как есть
        if os.path.isabs(img_path):
            return img_path if os.path.exists(img_path) else None
        
        # Пробуем найти относительно assets_dir
        asset_path = os.path.join(assets_dir, img_path)
        if os.path.exists(asset_path):
            return asset_path
        
        # Пробуем найти относительно текущей директории
        if os.path.exists(img_path):
            return img_path
        
        return None

    # Создаем колонки
    datacolumns = [ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD)) for col in columns_names]
    
    # Создаем строки
    datarows = []
    for row in data:
        if not row:  # Пропускаем пустые строки
            continue
            
        cells = []
        for i, cell in enumerate(row):
            # Первая колонка - проверяем на изображение
            if i == 0 and isinstance(cell, str):
                img_path = get_asset_path(cell)
                print(img_path)
                if img_path and Path(img_path).suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    print('ok')
                    img = ft.Image(
                        src=img_path,
                        width=100,
                        height=100,
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=ft.border_radius.all(5),
                    )
                    cells.append(ft.DataCell(img))
                else:
                    cells.append(ft.DataCell(
                        ft.Text(f"Файл не найден: {cell}", color=ft.colors.RED)
                    ))
            else:
                # Все остальные ячейки
                cells.append(ft.DataCell(
                    ft.Text(str(cell), max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
                ))
        
        datarows.append(ft.DataRow(cells=cells))
    
    return ft.DataTable(
        columns=datacolumns,
        rows=datarows,
        vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
    )

if __name__ == '__main__':
    tuple_example = (('test', 'test1'), ('test2', 'test2')) 
    print(type(create_flet_table((('test', 'test1'), ('test2', 'test2')), columns_names=['test', 'test2'])))


