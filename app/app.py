import client.utils as utils

from datetime import datetime, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from database import Database
from client.methods import export_to_csv, export_to_json
from client.utils import Customer


class DefaultScreen(Screen):
    def __init__(self, db: Database, **kwargs):
        super().__init__(**kwargs)

        self.db = db
        self.root = BoxLayout(orientation="vertical", padding=20, spacing=20)
        self.add_widget(self.root)

        self.alert = Label(
            text="",
            size_hint_y=None,
            height=0,
            color=(1, 1, 1, 1)
        )

        self.root.add_widget(self.alert)

    def go(self, name):
        self.manager.current = name

    def show_alert(self, text, success=True, duration=2):
        self.alert.text = text
        self.alert.color = (0, 0.6, 0, 1) if success else (0.8, 0, 0, 1)
        self.alert.height = 40
        Clock.unschedule(self._hide_alert)
        Clock.schedule_once(self._hide_alert, duration)

    def _hide_alert(self, *_):
        self.alert.text = ""
        self.alert.height = 0


class HomeScreen(DefaultScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        logo_container = AnchorLayout(
            anchor_x="center",
            anchor_y="top",
            size_hint=(1, None),
            height=220
        )

        logo = Image(
            source="assets/logo.png",
            size_hint=(None, None),
            size=(180, 180),
            allow_stretch=True,
            keep_ratio=True
        )
        logo_container.add_widget(logo)

        button_layout = BoxLayout(
            orientation="vertical",
            spacing=15,
            size_hint=(0.6, None)
        )
        button_layout.bind(minimum_height=button_layout.setter("height"))

        buttons = [
            ("Zarezerwuj kort", "reservation"),
            ("Wyświetl grafik", "schedule"),
        ]

        for text, go_to in buttons:
            btn = Button(
                text=text,
                font_size=18,
                size_hint_y=None,
                height=50,
                background_normal="",
                background_down="",
                background_color=(0.373, 0.596, 0.172, 1),
                color=(1, 1, 1, 1),
                on_press=lambda _, screen=go_to: self.go(screen)
            )
            button_layout.add_widget(btn)

        buttons_center = AnchorLayout(
            anchor_x="center",
            size_hint=(1, None)
        )
        buttons_center.height = button_layout.height
        button_layout.bind(
            minimum_height=lambda instance, value: setattr(buttons_center, "height", value)
        )
        buttons_center.add_widget(button_layout)

        self.root.add_widget(logo_container)
        self.root.add_widget(buttons_center)
        self.root.add_widget(BoxLayout())


class ReservationScreen(DefaultScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        form = BoxLayout(
            orientation="vertical",
            spacing=15,
            size_hint=(1, 0.8)
        )

        self.first_name = TextInput(hint_text="Imię", multiline=False)
        self.last_name = TextInput(hint_text="Nazwisko", multiline=False)

        today = datetime.today().date()
        dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(14)]

        self.date_spinner = Spinner(text=dates[0], values=dates)
        self.start_time = TextInput(hint_text="Godzina start (HH:MM)", multiline=False)
        self.duration = Spinner(
            text="60 minut",
            values=["30 minut", "60 minut", "90 minut"]
        )

        submit = Button(text="Zarezerwuj", size_hint_y=None, height=50)
        submit.bind(on_press=self.submit)

        for w in (
                self.first_name,
                self.last_name,
                self.date_spinner,
                self.start_time,
                self.duration,
        ):
            w.size_hint_y = None
            w.height = 45
            form.add_widget(w)

        form.add_widget(submit)

        back = Button(
            text="Wróć",
            size_hint_y=None,
            height=50,
            on_press=lambda _: self.go("home")
        )

        self.root.add_widget(Label(text="Rezerwacja", font_size=22, size_hint_y=None, height=40))
        self.root.add_widget(form)
        self.root.add_widget(back)

    def submit(self, *_):
        try:
            customer_first_name = self.first_name.text.strip()
            customer_last_name = self.last_name.text.strip()

            if not customer_first_name or not customer_last_name:
                self.show_alert("Uzupełnij imię i nazwisko", success=False)
                return

            reservation_start = datetime.strptime(
                f"{self.date_spinner.text} {self.start_time.text}",
                "%Y-%m-%d %H:%M"
            )
            if utils.is_datetime_less_than_hour_from_now(reservation_start):
                self.show_alert("Rezerwacja nie może zaczynać się szybciej niż godzina od teraz", success=False)
                return

            duration_minutes = int(self.duration.text.split()[0])

            customer = Customer(customer_first_name, customer_last_name)
            customer_id = self.db.get_customer_id(customer)

            if not customer_id:
                self.db.insert_customer(customer)
                customer_id = self.db.get_customer_id(customer)
            elif not self.db.is_customer_has_less_than_two_reservations_this_week(customer_id, reservation_start):
                self.show_alert("Masz już dwie aktywne rezerwacje w tym tygodniu.", success=False)
                return


            if not self.db.is_reservation_available_to_set(reservation_start, duration_minutes):
                msg = "Termin jest niedostępny."

                suggested_date = self.db.get_suggestion_available_time(reservation_start, duration_minutes)
                if suggested_date:
                    suggested_dt = datetime.strptime(suggested_date[0], "%Y-%m-%d %H:%M")
                    msg += f' Dostępna godzina {suggested_dt.strftime("%H:%M")}'

                self.show_alert(msg, success=False)
                return

            self.db.set_reservation(customer_id, reservation_start, duration_minutes)

            self.go("home")
            self.manager.get_screen("home").show_alert("Rezerwacja utworzona", success=True)
        except ValueError:
            self.show_alert("Błędna data lub godzina", success=False)

    def on_pre_enter(self, *args):
        self.first_name.text = ""
        self.last_name.text = ""
        self.start_time.text = ""
        self.duration.text = "60 minut"
        self.date_spinner.text = self.date_spinner.values[0]


class ScheduleScreen(DefaultScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        today = datetime.today().date()
        dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(14)]

        filters = BoxLayout(
            size_hint_y=None,
            height=50,
            spacing=10
        )

        self.date_from = Spinner(text=dates[0], values=dates)
        self.date_to = Spinner(text=dates[-1], values=dates)

        filters.add_widget(self.date_from)
        filters.add_widget(self.date_to)
        filters.add_widget(
            Button(text="Filtruj", on_press=self.load_data)
        )

        self.root.add_widget(filters)

        exports = BoxLayout(
            size_hint_y=None,
            height=45,
            spacing=10
        )

        export_csv = Button(
            text="Eksport CSV",
            size_hint_x=0.5,
            on_press=lambda _: self.export("csv")
        )

        export_json = Button(
            text="Eksport JSON",
            size_hint_x=0.5,
            on_press=lambda _: self.export("json")
        )

        exports.add_widget(export_csv)
        exports.add_widget(export_json)

        self.root.add_widget(exports)

        scroll = ScrollView()

        self.table = GridLayout(
            cols=4,
            spacing=5,
            size_hint_y=None,
            row_default_height=40,
            row_force_default=True
        )
        self.table.bind(minimum_height=self.table.setter("height"))

        scroll.add_widget(self.table)
        self.root.add_widget(scroll)

        self.root.add_widget(
            Button(
                text="Wróć",
                size_hint_y=None,
                height=50,
                on_press=lambda _: self.go("home")
            )
        )

    def load_data(self, *_):
        self.table.clear_widgets()

        dates = utils.get_dates_from_range(
            datetime.strptime(self.date_from.text, '%Y-%m-%d').date(),
            datetime.strptime(self.date_to.text, '%Y-%m-%d').date()
        )

        for date_x in dates:
            reservations = self.db.get_reservations_for_this_date(date_x)
            if not reservations:
                continue

            for first_name, last_name, start, end in reservations:
                customer = Customer(first_name, last_name)
                customer_id = self.db.get_customer_id(customer)
                res_id = self.db.get_reservation_id(
                    customer_id,
                    datetime.strptime(start, '%Y-%m-%d %H:%M')
                )
                widgets = []

                widgets.extend(
                    [
                        self.cell(f"{first_name} {last_name}"),
                        self.cell(start),
                        self.cell(end),
                        self.action_button(res_id, widgets)
                    ]
                )

                for widget in widgets:
                    self.table.add_widget(widget)

    def cell(self, text):
        return Label(
            text=text,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle"
        )

    def action_button(self, res_id, widgets):
        return Button(
            text="X",
            size_hint_x=None,
            width=40,
            size_hint_y=None,
            height=40,
            on_press=lambda _: self.cancel_reservation(res_id, widgets)
        )

    def cancel_reservation(self, res_id, widgets):
        self.db.cancel_reservation(res_id)
        for widget in widgets:
            self.table.remove_widget(widget)

    def on_pre_enter(self, *args):
        self.load_data()

    def export(self, file_type):
        date_from = datetime.strptime(self.date_from.text, '%Y-%m-%d').date()
        date_to = datetime.strptime(self.date_to.text, '%Y-%m-%d').date()
        match file_type:
            case "csv":
                export_to_csv(date_from, date_to)
                self.show_alert('Wyeksportowano do pliku CSV')
            case "json":
                export_to_json(date_from, date_to)
                self.show_alert('Wyeksportowano do pliku JSON')
            case _: pass


class MyApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        db = Database(db_name="schedule")
        db.create_tables()

        screen_manager = ScreenManager()
        screen_manager.add_widget(HomeScreen(name="home", db=db))
        screen_manager.add_widget(ReservationScreen(name="reservation", db=db))
        screen_manager.add_widget(ScheduleScreen(name="schedule", db=db))

        return screen_manager
