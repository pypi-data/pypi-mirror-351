import flet as ft

class EditableTable:
    def __init__(
        self,
        cursor,
        table_name: str,
        field_mapping: dict,
        width: int = 800,
        height: int = 400
    ):
        self.cursor = cursor
        self.table_name = table_name
        self.field_mapping = field_mapping
        self.width = width
        self.height = height
        self.dropdown_options = self._generate_dropdown_options()

    def _generate_dropdown_options(self):
        options = {}
        for field in self.field_mapping:
            if field.endswith("_id") and field != f"{self.table_name}_id":
                ref_table = field.replace("_id", "")
                try:
                    self.cursor.execute(f"SELECT {field}, {ref_table} FROM {ref_table}")
                    results = self.cursor.fetchall()
                    options[field] = [(str(row[0]), str(row[1])) for row in results]
                except Exception as e:
                    print(f"[WARN] Не удалось загрузить dropdown для {field}: {e}")
        return options

    def create_add_form(self):
        new_fields = {}
        input_controls = []

        for field in list(self.field_mapping.keys())[1:]:  # Пропускаем ID
            if field in self.dropdown_options:
                ctrl = ft.Dropdown(
                    options=[ft.dropdown.Option(key=str(k), text=str(v)) for k, v in self.dropdown_options[field]],
                    value=None,
                    expand=True
                )
            else:
                ctrl = ft.TextField(label=self.field_mapping[field], expand=True)

            new_fields[field] = ctrl
            input_controls.append(ctrl)

        def handle_add():
            try:
                fields = ", ".join(new_fields.keys())
                placeholders = ", ".join(["%s"] * len(new_fields))
                values = [ctrl.value for ctrl in new_fields.values()]
                insert_query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
                self.cursor.execute(insert_query, values)
                self.cursor.connection.commit()
                print("[INFO] Запись добавлена:", values)
                return True, "Успешно добавлено"
            except Exception as ex:
                print("[ERROR] Ошибка добавления:", str(ex))
                return False, f"Ошибка: {str(ex)}"

        form_row = ft.Row(input_controls)
        return form_row, handle_add


    def create_table(self):
        db_fields = list(self.field_mapping.keys())
        query = f"SELECT {', '.join(db_fields)} FROM {self.table_name}"
        self.cursor.execute(query)
        data = self.cursor.fetchall()

        rows = []
        for row in data:
            record_id = row[0]
            cells = []
            field_controls = {}

            for field, value in zip(db_fields, row):
                if field == db_fields[0]:
                    cells.append(ft.DataCell(ft.Text(str(value))))
                    continue

                if field in self.dropdown_options:
                    ctrl = ft.Container(
                        content=ft.Dropdown(
                            options=[ft.dropdown.Option(key=str(k), text=v) for k, v in self.dropdown_options[field]],
                            value=str(value),
                            expand=True
                        ),
                        padding=5,
                        expand=True
                    )
                else:
                    ctrl = ft.Container(
                        content=ft.TextField(
                            value=str(value),
                            border=ft.InputBorder.NONE,
                            expand=True
                        ),
                        padding=5,
                        expand=True
                    )

                field_controls[field] = ctrl.content
                cells.append(ft.DataCell(ctrl))

            def make_save_callback(record_id, controls):
                def save(e):
                    try:
                        update_fields = ", ".join(f"{field} = %s" for field in controls.keys())
                        values = [c.value for c in controls.values()]
                        update_query = f"UPDATE {self.table_name} SET {update_fields} WHERE {db_fields[0]} = %s"
                        self.cursor.execute(update_query, (*values, record_id))
                        self.cursor.connection.commit()
                        e.page.snack_bar = ft.SnackBar(ft.Text("Изменения сохранены"))
                        e.page.snack_bar.open = True
                        print(f"[LOG] Updated record {record_id} with values {values}")
                    except Exception as ex:
                        e.page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {str(ex)}"))
                        e.page.snack_bar.open = True
                    e.page.update()
                return save

            save_button = ft.IconButton(icon=ft.icons.SAVE, tooltip="Сохранить", on_click=make_save_callback(record_id, field_controls))
            delete_button = ft.IconButton(icon=ft.icons.DELETE, tooltip="Удалить", on_click=self._handle_delete(record_id))
            cells.append(ft.DataCell(ft.Row([save_button, delete_button], spacing=0)))

            rows.append(ft.DataRow(cells=cells))

        column_headers = [self.field_mapping[field] for field in db_fields] + ["Действия"]
        return ft.DataTable(
            columns=[ft.DataColumn(ft.Text(col)) for col in column_headers],
            rows=rows,
            width=self.width - 20
        )

    def _handle_delete(self, record_id: int):
        def callback(e):
            try:
                delete_query = f"DELETE FROM {self.table_name} WHERE {list(self.field_mapping.keys())[0]} = %s"
                self.cursor.execute(delete_query, (record_id,))
                self.cursor.connection.commit()
                e.page.snack_bar = ft.SnackBar(ft.Text("Запись удалена!"))
                e.page.snack_bar.open = True
                e.page.update()
            except Exception as ex:
                e.page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {str(ex)}"))
                e.page.snack_bar.open = True
                e.page.update()
        return callback

'''
def main(page: ft.Page):
    # Установка базовых свойств страницы
    page.title = 'Панель администратора'
    page.scroll = True  # Включаем прокрутку
    page.snack_bar = ft.SnackBar(ft.Text(""))  # Подготовка всплывающего уведомления (Snackbar)

    # Заголовок страницы
    page.add(ft.Text("Панель администратора", size=20, weight="bold"))

    # Сопоставление названий полей БД с заголовками таблицы
    field_mapping = {
        "material_and_place_id": "ID",        # первичный ключ
        "material_id": "Материал",            # внешний ключ → таблица material
        "place_id": "Место",                  # внешний ключ → таблица place
        "counted": "Кол-во"                   # обычное числовое поле
    }

    # Создание экземпляра редактируемой таблицы
    # dropdown_options не указывается — подбираются автоматически по *_id
    editable_table = EditableTable(
        cursor=cursor,                          # курсор подключения к БД
        table_name="material_and_place",        # целевая таблица
        field_mapping=field_mapping             # отображаемые поля
    )

    # Контейнер, в который будет загружена таблица (перерисовывается при добавлении/удалении)
    table_container = ft.Column()

    # Функция перерисовки таблицы (вызывается после добавления новой записи)
    def reload_table():
        table_container.controls.clear()                           # очистка старой таблицы
        table_container.controls.append(editable_table.create_table())  # добавление обновлённой таблицы
        page.update()                                              # обновление интерфейса

    # Создание формы добавления новой записи
    # При добавлении вызывается reload_table, чтобы таблица обновилась
    form = editable_table.create_add_form(page, on_added=reload_table)

    # Добавляем форму и таблицу на страницу
    page.add(form)
    page.add(table_container)

    # Первичная загрузка таблицы
    reload_table()

    
    ДОБАВЛЕНИЕ ЗАПИСИ UI И НЕ ТОЛЬКО 
    def on_add_click(e):
    success, msg = handle_add()
    page.snack_bar = ft.SnackBar(ft.Text(msg))
    page.snack_bar.open = True
        page.update()
        add_button = ft.ElevatedButton("Добавить", on_click=on_add_click)
        page.add(add_button)
        form_ui, handle_add = MyTable.create_add_form()
        page.add(form_ui)

# Точка входа в приложение Flet
if __name__ == '__main__':
    ft.app(main)
'''