#!/usr/bin/env python
# -- coding: utf-8 --

import re
import sys
import os
from os.path import sep, expanduser, isdir, dirname
import platform

# Import in this case needed for setting config
# variables before others import. If we put
# this code below others import, we can't guarantee
# his work on 100%
from kivy import config
import gtk

screen_size = gtk.gdk.screen_get_default()

config.Config.set('graphics', 'resizable', 0)
config.Config.set('graphics', 'height', screen_size.get_height()/2)
config.Config.set('graphics', 'width', screen_size.get_width()/3)

# Модули для создания UI
import kivy.app as app
import kivy.uix.button as btn
import kivy.uix.floatlayout as fl
import kivy.uix.label as label
import kivy.uix.popup as pu
import kivy.uix.textinput as ti
import kivy.core.window as wi
import kivy.uix.filebrowser as fb
import kivy.uix.modalview as mv
import kivy.uix.dropdown as dd # import dropdown for district, square, rooms, year
import kivy.uix.checkbox as check # import checkbox for infra and remonta
# Импортируем модуль, в котором создается сеть
import neural
import dataset_factor

class FieldRules(ti.TextInput):

    pattern = re.compile(r'[ A-Za-z!?=*+\\,]')

    def insert_text(self, substring, from_undo=False):
        search = re.sub(self.pattern, '', substring)
        return super(FieldRules, self).insert_text(search, from_undo=from_undo)


class NeuralNetworkApp(app.App):

    platform = platform.system().lower()

    @staticmethod
    def autosize_font(perc):
        """
        Функция для автоматического ресайза шрифтов (на любой размер экрана)
        :param perc: Процент на который надо умножить
        :return: Размер шрифта
        """
        return perc * wi.Window.height

    def create_browser(self):
        if platform == 'win':
            user_path = dirname(expanduser('~')) + sep + 'Documents'
        else:
            user_path = expanduser('~') + sep + 'Documents'
        browser = fb.FileBrowser(select_string='Select',
                                 favorites=[(user_path, 'Documents')])
        browser.bind(
                    on_success=self._fbrowser_success,
                    on_canceled=self._fbrowser_canceled)
        return browser

    def _fbrowser_canceled(self, instance):
        self.view.dismiss()

    def _fbrowser_success(self, instance):
        try:
            self.file = instance.selection[0]
        except IndexError:
            pass
        else:
            self.load_configuration(self.file)
            self.view.dismiss()

    def calculate(self):
        """
        Функция для рассчета результата сети
        :return:
        """
        try:
            # Пробуем удалить label.
            self.grid.remove_widget(self.label)
        except AttributeError:
            # Если его нет - ничего страшного, создадим потом, и
            # будем удалять каждый раз, как вызовем self.calculate()
            pass

        fake_fake_input_value = []
        fake_input_value = []
        input_value = []
        try:
            input_value.append(neural.district_map[str(self.district_btn.text)])
            input_value.append(neural.square_map[str(self.square_btn.text)])
            input_value.append(neural.room_map[str(self.room_btn.text)])
            input_value.append(neural.infra_map[self.infra_check.active])
            input_value.append(neural.year_map[str(self.year_btn.text)])
            input_value.append(neural.remont_map[self.remont_check.active])
            fake_input_value.append(input_value)
            fake_fake_input_value.append(fake_input_value)
        except KeyError:
            raise SystemExit("One or more maps has no some attributes! Please check all points in menu! Thanks!")

        print 'RAION: '+str(neural.district_map[str(self.district_btn.text)])
        print 'PLOSHAD: '+str(neural.square_map[str(self.square_btn.text)])
        print 'KOMNATA: '+str(neural.room_map[str(self.room_btn.text)])
        print 'INFRA: '+str(neural.infra_map[self.infra_check.active])
        print 'GOD: '+str(neural.year_map[str(self.year_btn.text)])
        print 'REMONT: '+str(neural.remont_map[self.remont_check.active])

        try:
            self.price_value_label = label.Label(text=str(int(self.network.test(fake_fake_input_value)*10000000)) + " rub",
                                                 size_hint=(.33, .10),
                                                font_size=self.autosize_font(0.038),
                                                pos_hint={'x': .30, 'y': .30})

        except AttributeError:
            content = btn.Button(text='Сеть не обучена,\n либо не загружена из файла!')

            self.error_popup = pu.Popup(title='Error!',
                              content=content,
                              size_hint=(None, None), size=(300, 300),
                              auto_dismiss=False)

            content.bind(on_press=self.error_popup.dismiss)
            self.error_popup.open()
        else:
            self.grid.add_widget(self.price_label)
            self.grid.add_widget(self.price_value_label)

    def clean_all(self):
        try:
            self.grid.remove_widget(self.district_dd)
            self.grid.remove_widget(self.district_label)
            self.grid.remove_widget(self.district_btn)
            self.grid.remove_widget(self.square_label)
            self.grid.remove_widget(self.square_btn)
            self.grid.remove_widget(self.square_dd)
            self.grid.remove_widget(self.room_label)
            self.grid.remove_widget(self.room_btn)
            self.grid.remove_widget(self.room_dd)
            self.grid.remove_widget(self.year_btn)
            self.grid.remove_widget(self.year_dd)
            self.grid.remove_widget(self.year_label)
            self.grid.remove_widget(self.infra_check)
            self.grid.remove_widget(self.infra_label)
            self.grid.remove_widget(self.remont_check)
            self.grid.remove_widget(self.remont_label)
            self.grid.remove_widget(self.price_label)
            self.grid.remove_widget(self.price_value_label)
        except AttributeError:
            pass
        self.create_env()

    def start_browsing(self):
        self.view = mv.ModalView(size_hint=(None, None),
                                 size=(screen_size.get_width()/3-50, screen_size.get_height()/2-50),
                                 auto_dismiss=False)
        self.view.add_widget(self.create_browser())
        self.view.open()

    def create_env(self):

        ###############################################################################################################
        # Ярлык с надписью район
        self.district_label = label.Label(text='Район:',
                                          size_hint=(.33, .10),
                                          font_size=self.autosize_font(0.038),
                                          pos_hint={'x': .0, 'y': .90})

        # выпадающее меню для выбора района
        self.district_dd = dd.DropDown()
        for index in ['Центр', 'Спальный', 'Окраина']:
            butn = btn.Button(text='{0}'.format(index),
                              size_hint_y=None,
                              height=44,
                              on_release=lambda butn: self.district_dd.select(butn.text))

            self.district_dd.add_widget(butn)
        self.district_btn = btn.Button(text='Выберите район..',  size_hint=(.33, .10), pos_hint={'x': .30, 'y': .90})
        self.district_btn.bind(on_release=self.district_dd.open)
        self.district_dd.bind(on_select=lambda instance, x: setattr(self.district_btn, 'text', x))

        self.grid.add_widget(self.district_label)

        self.grid.add_widget(self.district_btn)

        ###############################################################################################################

        # Ярлык с надписью площадь
        self.square_label = label.Label(text='Площадь:',
                                        size_hint=(.33, .10),
                                        font_size=self.autosize_font(0.038),
                                        pos_hint={'x': .0, 'y': .80})

        # выпадающее меню для выбора площади дома
        self.square_dd = dd.DropDown()
        for index in ['< 50 м2', '50-100 м2', '100-150 м2', '150-200 м2', '200-250 м2', '> 250 м2']:
            butn = btn.Button(text='{0}'.format(index),
                              size_hint_y=None,
                              height=44,
                              on_release=lambda butn: self.square_dd.select(butn.text))

            self.square_dd.add_widget(butn)
        self.square_btn = btn.Button(text='Выберите площадь..',  size_hint=(.33, .10), pos_hint={'x': .30, 'y': .80})
        self.square_btn.bind(on_release=self.square_dd.open)
        self.square_dd.bind(on_select=lambda instance, x: setattr(self.square_btn, 'text', x))

        self.grid.add_widget(self.square_label)

        self.grid.add_widget(self.square_btn)

        ###############################################################################################################

        # Ярлык с надписью количества комнат
        self.room_label = label.Label(text='Кол-во комнат:',
                                          size_hint=(.33, .10),
                                          font_size=self.autosize_font(0.038),
                                          pos_hint={'x': .0, 'y': .70})

        # выпадающее меню для выбора количества комнат
        self.room_dd = dd.DropDown()
        for index in ['1', '2', '3', '4', '5']:
            butn = btn.Button(text='{0}'.format(index),
                              size_hint_y=None,
                              height=44,
                              on_release=lambda butn: self.room_dd.select(butn.text))

            self.room_dd.add_widget(butn)
        self.room_btn = btn.Button(text='Выберите кол-во команат',  size_hint=(.33, .10), pos_hint={'x': .30, 'y': .70})
        self.room_btn.bind(on_release=self.room_dd.open)
        self.room_dd.bind(on_select=lambda instance, x: setattr(self.room_btn, 'text', x))
        self.grid.add_widget(self.room_label)
        self.grid.add_widget(self.room_btn)

        ###############################################################################################################

        # Ярлык с надписью Год
        self.year_label = label.Label(text='Год:',
                                          size_hint=(.33, .10),
                                          font_size=self.autosize_font(0.038),
                                          pos_hint={'x': .0, 'y': .50})

        # выпадающее меню для выбора Года
        self.year_dd = dd.DropDown()
        for index in ['70е', '80е', '90е', '00е', '10е']:
            butn = btn.Button(text='{0}'.format(index),
                              size_hint_y=None,
                              height=44,
                              on_release=lambda butn: self.year_dd.select(butn.text))

            self.year_dd.add_widget(butn)
        self.year_btn = btn.Button(text='Выберите год.',  size_hint=(.33, .10), pos_hint={'x': .30, 'y': .50})
        self.year_btn.bind(on_release=self.year_dd.open)
        self.year_dd.bind(on_select=lambda instance, x: setattr(self.year_btn, 'text', x))
        self.grid.add_widget(self.year_label)
        self.grid.add_widget(self.year_btn)

        ###############################################################################################################

        # Ярлык с надписью Год
        self.infra_label = label.Label(text='Инфраструктура:',
                                          size_hint=(.33, .10),
                                          font_size=self.autosize_font(0.038),
                                          pos_hint={'x': .0, 'y': .60})

        self.infra_check = check.CheckBox(size_hint=(.33, .10), pos_hint={'x': .30, 'y': .60})
        self.grid.add_widget(self.infra_label)
        self.grid.add_widget(self.infra_check)

        ###############################################################################################################

        # Ярлык с надписью Год
        self.remont_label = label.Label(text='Ремонт:',
                                          size_hint=(.33, .10),
                                          font_size=self.autosize_font(0.038),
                                          pos_hint={'x': .0, 'y': .40})

        self.remont_check = check.CheckBox(size_hint=(.33, .10), pos_hint={'x': .30, 'y': .40})
        self.grid.add_widget(self.remont_label)
        self.grid.add_widget(self.remont_check)

        ###############################################################################################################

        self.price_label = label.Label(text='Цена на квартиру:',
                                       size_hint=(.33, .10),
                                       font_size=self.autosize_font(0.038),
                                       pos_hint={'x': .0, 'y': .30})

    def load_configuration(self, file_name):
        self.network = neural.NN(6, 2, 1)
        self.network.load(file_name)

    def learn_network(self):
        self.network = neural.NN(6, 2, 1)
        self.popup.open()
        self.target = dataset_factor.dataset_fabric()
        self.network.train(self.target)
        self.popup.dismiss()

    def build(self):

        # Сетка для размещения элементов внутри окна.
        self.grid = fl.FloatLayout(size=(200, 200))

        self.create_env()

        self.learn_button = btn.Button(text='Обучить сеть',
                                size_hint=(.33, .10),
                                font_size=self.autosize_font(0.038),
                                pos_hint={'x': .68, 'y': .24},
                                on_press=lambda f: self.learn_network())

        self.browse_button = btn.Button(text='Загрузить сеть',
                                size_hint=(.33, .10),
                                font_size=self.autosize_font(0.038),
                                pos_hint={'x': .68, 'y': .12},
                                on_press=lambda f: self.start_browsing())

        # Кнопки "Рассчитать", "Очистить" и "Выход"
        self.calculate_button = btn.Button(text='Рассчитать',
                                           size_hint=(.33, .10),
                                           font_size=self.autosize_font(0.038),
                                           pos_hint={'x': .0, 'y': .0},
                                           on_press=lambda f: self.calculate())
        self.clear_button = btn.Button(text='Очистить все',
                                       font_size=self.autosize_font(0.038),
                                       size_hint=(.33, .10),
                                       pos_hint={'x': .34, 'y': .0},
                                       on_press=lambda f: self.clean_all())
        self.exit_button = btn.Button(text='Выход',
                                      size_hint=(.33, .10),
                                      font_size=self.autosize_font(0.038),
                                      pos_hint={'x': .68, 'y': .0},
                                      on_press=lambda f: sys.exit())

        # Всплывающее окно, взывающее пользователя проявить терпение.
        # Пока сеть маленькая, может и не особо надо. В дальнейшем,
        # я чувствую, точно пригодится
        self.popup = pu.Popup(title='Loading',
                              content=label.Label(text='Please, wait...'),
                              size_hint=(None, None), size=(200, 200),
                              auto_dismiss=False)
        # Добавляем кнопки на форму
        self.grid.add_widget(self.learn_button)
        self.grid.add_widget(self.browse_button)
        self.grid.add_widget(self.calculate_button)
        self.grid.add_widget(self.clear_button)
        self.grid.add_widget(self.exit_button)
        return self.grid

if __name__ == '__main__':
    NeuralNetworkApp().run()
