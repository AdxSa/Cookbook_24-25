import psycopg2
import decimal as dec
import PySimpleGUI as sg
from DatabaseManager import DatabaseManager

HOSTNAME = 'localhost'
DATABASE = 'cookbook'
USERNAME = 'cookbook'
PASSWORD = '2025'
OPTIONS = '-c search_path=public,dbo,drogeria'

def stworz_okno(tytul: str, layout: list) -> sg.Window:
    sg.theme('DarkRed')
    return sg.Window(tytul, layout)

def zaloguj():
    layout = [
        [sg.Text('Logowanie')],
        [sg.Text('Email', size =(15, 1)), sg.InputText()],
        [sg.Text('Hasło', size =(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Zaloguj'),  sg.Button(button_text='Stwórz konto')],
    ]
    window = stworz_okno('LOGOWANIE', layout)
    databaseManager = DatabaseManager(HOSTNAME, DATABASE, USERNAME, PASSWORD, OPTIONS)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            break
        if event == 'Zaloguj':
            user = databaseManager.znajdz_uzytkownika(values[0], values[1])
            if(user is None):
                sg.popup('Błędne dane logowania!')
            else:
                window.close()
                return show_menu(databaseManager, user)

        if event == "Stwórz konto":
            window.close()
            return otworz_okno_rejestracji(databaseManager)
def otworz_okno_rejestracji(databaseManager: DatabaseManager):
    layout = [
        [sg.Text('Podaj dane rejestracji')],
        [sg.Text('Imię', size=(15,1)), sg.InputText()],
        [sg.Text('Nazwisko', size=(15,1)), sg.InputText()],
        [sg.Text('Email', size=(15, 1)), sg.InputText()],
        [sg.Text('Hasło', size=(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Zarejestruj się')]
    ]
    window = stworz_okno('REJESTRACJA', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            break
        if event == "Zarejestruj się":
            if '' in values.values():
                sg.popup('Proszę wprowadzić pełne dane!')
            elif databaseManager.znajdz_uzytkownika(values[2], '%') is not None:
                sg.popup('Użytkownik o takim adresie Email już istnieje!')
            elif values[2].count('@') != 1:
                sg.popup('Proszę wprowadzić poprawny adres Email!')
            else:
                databaseManager.dodaj_uzytkownika(values[0], values[1], values[2], values[3])
                user = databaseManager.znajdz_uzytkownika(values[2], values[3])
                window.close()
                # tymczasowo, trzeba zmienić menu
                return show_menu(databaseManager, user)
def show_menu(databaseManager: DatabaseManager, user: tuple):
    layout = [
        [sg.Text('Wybierz operację')],
        [sg.Button('Otwórz magazyn')],
        [sg.Button('Kalkulator jednostek')],
        [sg.Button('Zobacz przepisy')],
        [sg.Button('Dodaj przepis')],
        # [sg.Button('Stwórz magazyn')],  # Przyciski do tworzenia magazynu
        # [sg.Button('Stwórz przepis')],  # Przycisk do tworzenia przepisu
        [sg.CloseButton(button_text='Wyjście')]
    ]
    if user[3] == 'kierownik':
        layout.append([sg.Button('Dodaj użytkownika')])

    window = stworz_okno('SMAKOSZE', layout)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break
        if event == 'Zobacz przepisy':
            Zobacz_przepisy(databaseManager, user)
        if event == 'Dodaj użytkownika':
            dodaj_uzytkownika(databaseManager)
        if event == 'Otwórz magazyn':
            przyjecie_dostawy(databaseManager, user)
        if event == 'Kalkulator jednostek':
            otworz_kalkulator(databaseManager)
        # if event == 'Stwórz magazyn':  # Obsługuje kliknięcie przycisku „Stwórz magazyn”
        #     stworz_magazyn(databaseManager, user[0])  # user[0] to ID użytkownika
        # if event == 'Stwórz przepis':  # Obsługuje kliknięcie przycisku „Stwórz przepis”
        #     stworz_przepis(databaseManager, user[0])  # user[0] to ID użytkownika
        if event == 'Dodaj przepis':
            dodaj_przepis(databaseManager, user)

    window.close()


# def przyjecie_dostawy(databaseManager, user):
#     magazyny = databaseManager.znajdz_moje_magazyny(user[0])  # Get user's warehouses
#
#     if not magazyny:
#         sg.popup("Nie masz żadnych magazynów!")
#         return
#
#     magazyny_lista = [str(magazyn[0]) for magazyn in magazyny]
#     layout = [
#         [sg.Text('Wybierz numer magazynu')],
#         [sg.Combo(magazyny_lista, key='MAGAZYN', readonly=True)],
#         [sg.Button('Wyślij'), sg.Button('Cofnij')]
#     ]
#
#     window = stworz_okno('DOSTAWA', layout)
#
#     while True:
#         event, values = window.read()
#
#         if event in (sg.WIN_CLOSED, 'Cofnij'):
#             break
#
#         if event == 'Wyślij':
#             if 'MAGAZYN' in values:
#                 id_magazynu = int(values['MAGAZYN'])
#                 obsluga_magazynu(databaseManager, id_magazynu, user)  # Handle warehouse operations
#             else:
#                 sg.popup("Wybierz numer magazynu!")
#
#     window.close()

# def obsluga_magazynu(databaseManager, id_magazynu, user):
#     skladniki = databaseManager.wypisz_skladniki(id_magazynu)
#     wszystkie_skladniki = databaseManager.wypisz_wszystkie_skladniki()
#
#     ilosc_skladnika = dict(skladniki)
#
#     layout = []
#
#     for id_skladnika, nazwa_skladnika in wszystkie_skladniki:
#         ilosc = ilosc_skladnika.get(id_skladnika, 0)
#         layout.append([
#             sg.Text(f'{nazwa_skladnika}', size=(20, 1)),
#             sg.Text(str(ilosc), size=(5, 1), key=f'ILOSC_{id_skladnika}'),
#             sg.Button('+', key=f'PLUS_{id_skladnika}'),
#             sg.Button('-', key=f'MINUS_{id_skladnika}')
#         ])
#
#     layout.append([sg.Button('Zamknij')])
#
#     window = sg.Window('Magazyn Składników', layout)
#
#     while True:
#         event, _ = window.read()
#
#         if event in (sg.WINDOW_CLOSED, 'Zamknij'):
#             break
#
#         for id_skladnika, _ in wszystkie_skladniki:
#             if event == f'PLUS_{id_skladnika}':
#                 # Handle adding stock
#                 pass
#             elif event == f'MINUS_{id_skladnika}':
#                 # Handle reducing stock
#                 pass
#
#     window.close()


# def stworz_magazyn(databaseManager, user_id):
#     # Pobierz magazyny użytkownika
#     magazyny = databaseManager.znajdz_moje_magazyny(user_id)
#
#     # Sprawdź, czy użytkownik nie ma już maksymalnej liczby magazynów (np. 5)
#     if len(magazyny) >= 5:
#         sg.popup("Nie możesz mieć więcej niż 5 magazynów!")
#         return
#
#     # Dodaj nowy magazyn
#     databaseManager.dodaj_magazyn(user_id)
#     sg.popup("Magazyn został pomyślnie utworzony!")

# def stworz_przepis(databaseManager, user_id):
#     # Zbieramy dane na temat przepisu
#     layout = [
#         [sg.Text('Podaj dane przepisu')],
#         [sg.Text('Nazwa przepisu', size=(15, 1)), sg.InputText(key='nazwa')],
#         [sg.Text('Opis', size=(15, 1)), sg.InputText(key='opis')],
#         [sg.Text('Czas przygotowania (w minutach)', size=(15, 1)), sg.InputText(key='czas')],
#         [sg.Text('ID składników (oddzielone przecinkami)', size=(15, 1)), sg.InputText(key='skladniki')],
#         [sg.Button('Stwórz przepis')]
#     ]
#     window = stworz_okno('Tworzenie przepisu', layout)
#
#     while True:
#         event, values = window.read()
#         if event == sg.WIN_CLOSED:
#             break
#         if event == 'Stwórz przepis':
#             nazwa = values['nazwa']
#             opis = values['opis']
#             czas = values['czas']
#             skladniki = values['skladniki'].split(',')
#
#             if not nazwa or not opis or not czas or not skladniki:
#                 sg.popup("Proszę wprowadzić wszystkie dane!")
#                 continue
#
#             try:
#                 # Dodaj przepis do bazy danych
#                 przepis_id = databaseManager.dodaj_przepis(nazwa, opis, czas, user_id)
#
#                 # Dodaj składniki do przepisu
#                 for skladnik_id in skladniki:
#                     databaseManager.dodaj_skladnik_do_przepisu(przepis_id, skladnik_id.strip())
#
#                 sg.popup(f"Przepis '{nazwa}' został pomyślnie dodany!")
#                 break
#             except Exception as e:
#                 sg.popup(f"Coś poszło nie tak: {str(e)}")
#                 continue
#
#     window.close()
def otworz_kalkulator(databaseManager: DatabaseManager):
    skladniki = databaseManager.wypisz_wszystkie_skladniki()
    print(skladniki)
    skladniki_dict = {str(id): nazwa for id, nazwa in skladniki}
    layout = [
        [sg.Text('Wybierz składnik'), sg.Combo(list(skladniki_dict.values()), key="SKŁADNIK", enable_events=True)],
        [sg.Text("Jednostka 1:"), sg.Combo([], key="JEDNOSTKA 1", enable_events=True)],
        [sg.Text("Jednostka 2:"), sg.Combo([], key="JEDNOSTKA 2", enable_events=True)],
        [sg.Text("Proporcja:"), sg.Text("", key="PROPORCJA", size=(50, 1))],
        [sg.Button("Oblicz"), sg.Button("Zamknij")]
              ]
    window = stworz_okno("Kalkulator przeliczania jednostek", layout)
    wybrany_skladnik_id = None

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Zamknij"):
            break

        # Gdy użytkownik wybierze składnik
        if event == "SKŁADNIK":
            wybrany_skladnik_nazwa = values["SKŁADNIK"]
            wybrany_skladnik_id = next(
                (id for id, name in skladniki_dict.items() if name == wybrany_skladnik_nazwa), None)

            if wybrany_skladnik_id:
                dostepne_jednostki = databaseManager.wypisz_jednostki_dla_skladnika(wybrany_skladnik_id)
                window["JEDNOSTKA 1"].update(values=dostepne_jednostki, value="")
                window["JEDNOSTKA 2"].update(values=dostepne_jednostki, value="")
                window["PROPORCJA"].update("")

        # Gdy użytkownik wybierze jednostki i kliknie "Oblicz"
        if event == "Oblicz":
            unit1 = values["JEDNOSTKA 1"]
            unit2 = values["JEDNOSTKA 2"]

            if wybrany_skladnik_id and unit1 and unit2:
                ratio = databaseManager.znajdz_przelicznik_jednostek(wybrany_skladnik_id, unit1, unit2)
                if ratio:
                    ratio = ratio[0]
                    window["PROPORCJA"].update(f"{round(float(ratio), 5)}")
                else:
                    ratio = databaseManager.znajdz_przelicznik_jednostek(wybrany_skladnik_id, unit2, unit1)
                    if ratio:
                        ratio = ratio[0]
                        window["PROPORCJA"].update(f"{round(float(1/ratio), 5)}")
                    else:
                        window["PROPORCJA"].update("Brak danych")

    window.close()



def Zobacz_przepisy(databaseManager: DatabaseManager, user):
    przepisy = databaseManager.get_all_recipes()
    dania_glowne = databaseManager.znajdz_przepisy_z_kategorii(1)
    desery = databaseManager.znajdz_przepisy_z_kategorii(2)
    zupy = databaseManager.znajdz_przepisy_z_kategorii(3)

    # Tworzenie layoutów dla każdej kategorii
    def generuj_layout(lista_przepisow):
        layout = []
        for recipe in lista_przepisow:
            if len(recipe) != 5:
                continue
            id_przepisu, nazwa, opis, czas, id_użytkownika = recipe
            layout.append([
                sg.Button(nazwa, key=str(id_przepisu), size=(20, 1)),  # Przycisk z nazwą przepisu
                sg.Text(f"{opis} | Czas: {czas} min", size=(100, 1))  # Opis + czas przygotowania
            ])
        return layout

    layout_wszystkie = generuj_layout(przepisy)
    layout_dania_glowne = generuj_layout(dania_glowne)
    layout_zupy = generuj_layout(zupy)
    layout_desery = generuj_layout(desery)

    # Tworzenie głównego layoutu z kategoriami
    kategorie_layout = [
        [sg.Text('Kategorie')],
        [sg.Button('Wszystkie'), sg.Button('Dania glowne'), sg.Button('Zupy'), sg.Button('Desery')],
    ]

    # Główne layouty jako ukryte kolumny
    layout = [
        kategorie_layout,
        [sg.Column(layout_wszystkie, key='-Wszystkie-'),
         sg.Column(layout_dania_glowne, visible=False, key='-Dania glowne-'),
         sg.Column(layout_zupy, visible=False, key='-Zupy-'),
         sg.Column(layout_desery, visible=False, key='-Desery-')],
        [sg.Button('Wyjście')]
    ]

    window = sg.Window('PRZEPISY', layout, finalize=True)

    aktualny = 'Wszystkie'  # Domyślna kategoria

    while True:
        event, _ = window.read()

        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break

        if event.isdigit():
            pokaz_kroki(databaseManager, event, user)

        if event in ['Wszystkie', 'Dania glowne', "Zupy", "Desery"]:
            window[f"-{aktualny}-"].update(visible=False)
            aktualny = event
            window[f"-{aktualny}-"].update(visible=True)

    window.close()


def pokaz_kroki(databaseManager: DatabaseManager, id_przepisu, user):
    kroki_przepisu = databaseManager.otrzymaj_kroki_przepisu(id_przepisu)
    skladniki = databaseManager.otrzymaj_skladniki_przepisu(id_przepisu)
    imie, nazwisko, email = databaseManager.dane_autora_przepisu(id_przepisu)
    layout = [[sg.Text(f"Przepis na pyszne jedzonko"), sg.Text("Autor:" + imie + " " + nazwisko), sg.Text("Email:" + " " + email)]]
    layout.append([sg.Text(f"Na wykonanie tego przepisu będziesz potrzebował:")])
    for skladnik in skladniki:
        nazwa_skladnika, ilosc, nazwa_jednostki = skladnik[2], skladnik[1], skladnik[3]
        layout.append([sg.Text(f"{ilosc} x {nazwa_skladnika} ({nazwa_jednostki})")])
    layout.append([sg.Text(f"\n Kroki wykonania przepisu:")])
    for krok in kroki_przepisu:
        kolejnosc, opis = krok
        layout.append([sg.Text(f"{kolejnosc} | {opis}", size=(100, 1))])
    layout.append([sg.CloseButton(button_text='Wyjście'), sg.CloseButton(button_text='Odejmij składniki')])
    window = stworz_okno(f"Przepis na pyszne jedzonko", layout)

    while True:
        event, _ = window.read()

        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break


        if event in (sg.WIN_CLOSED, 'Odejmij składniki'):
            str_list = []
            skladniki_list = [(int(skladnik[0]), float(skladnik[1])) for skladnik in skladniki]
            # dodać przeliczanie na jednostki domyślne
            print(skladniki_list)
            magazyny = databaseManager.znajdz_moje_magazyny(user[0])
            for magazyn in magazyny:
                stan_magazynu = databaseManager.wypisz_skladniki(magazyn[0])
                stan_magazynu = [(int(skladnik[0]), float(skladnik[1])) for skladnik in stan_magazynu]
                magazyn_dict = dict(stan_magazynu)

                czy_starczy = True

                for id_skladnika, ilosc_w_przepisie in skladniki_list:
                    ilosc_w_magazynie = magazyn_dict.get(id_skladnika, 0)  # Jeśli brak w magazynie, domyślnie 0

                    if ilosc_w_magazynie < ilosc_w_przepisie:
                        czy_starczy = False
                        str_list.append(str(f"Brak wystarczającej ilości składnika {str(databaseManager.dopasuj_skladnik_do_id(id_skladnika)[0])}: {ilosc_w_magazynie}/{ilosc_w_przepisie}n"))
                        sg.popup(f"Brak wystarczającej ilości składnika {str(databaseManager.dopasuj_skladnik_do_id(id_skladnika)[0])}: {ilosc_w_magazynie}/{ilosc_w_przepisie}")

                print("Stan magazynu przed:")
                print(databaseManager.wypisz_skladniki(magazyn[0]))
                for skladnik in skladniki_list:
                    databaseManager.zmien_ilosc_skladnika(magazyn[0], skladnik[0], skladnik[1], False)
                print("Stan magazynu po:")
                print(databaseManager.wypisz_skladniki(magazyn[0]))






    window.close()

def dodaj_przepis(databaseManager: DatabaseManager, user):
    layout = []
    skladniki = databaseManager.wypisz_wszystkie_skladniki()
    lista_skladnikow = dict()
    kategoria = 0
    kroki = []
    nazwa = ''
    opis = ''
    layout.append([sg.Text('Nazwa potrawy:', size=(15, 1)), sg.InputText(key='opis', size=(30, 1))])
    for id_skladnika, nazwa_skladnika in skladniki:
        lista_skladnikow[f'{id_skladnika}'] = 0
        layout.append([
            sg.Text(f'{nazwa_skladnika}: ', size=(20, 1)),
            sg.Text(str(0), size=(5, 1), key=f'ILOSC_{id_skladnika}'),
            sg.Button('+', key=f'PLUS_{id_skladnika}'),
            sg.Button('-', key=f'MINUS_{id_skladnika}')
        ])
    layout.append([sg.Text('Wybierz kategorię: ', size=(20, 1))])
    layout.append([sg.Button('Dania glowne'),
                   sg.Button('Zupy'),
                   sg.Button('Desery')])
    layout.append([sg.Text('Nie wybrano kategorii', size=(30, 1), key=f'kategoria')])
    layout.append([sg.Button('Dodaj opis i kroki'), sg.Button('Gotowe'), sg.Button('Anuluj')])

    window = sg.Window('Nowy przepis', layout)

    while True:
        event, _ = window.read()

        if event in (sg.WINDOW_CLOSED, 'Gotowe'):
            if nazwa == '':
                sg.popup("Przepis musi mieć nazwę")
                continue
            else:
                break

        if event in (sg.WINDOW_CLOSED, 'Anuluj'):
            break

        if event == 'Dania glowne':
            if kategoria == 1:
                window["kategoria"].update(f"Nie wybrano kategorii")
                kategoria = 0
            else:
                kategoria = 1
                window["kategoria"].update(f"Wybrano kategorię: {event}")

        if event == 'Desery':
            if kategoria == 2:
                window["kategoria"].update(f"Nie wybrano kategorii")
                kategoria = 0
            else:
                kategoria = 2
                window["kategoria"].update(f"Wybrano kategorię: {event}")

        if event == 'Zupy':
            if kategoria == 3:
                window["kategoria"].update(f"Nie wybrano kategorii")
                kategoria = 0
            else:
                kategoria = 3
                window["kategoria"].update(f"Wybrano kategorię: {event}")

        if event == 'Dodaj opis i kroki':
            layout_3 = [
        [sg.Button('Dodaj opis'),
        sg.Button('Dodaj krok'), sg.Button('Przejrzyj kroki')],
        [sg.Button('Zapisz i wróć')]
            ]

            new_window_2 = stworz_okno('Opis przepisu', layout_3)

            while True:
                event, values = new_window_2.read()

                if event in (sg.WINDOW_CLOSED, 'Zapisz i wróć'):
                    break

                if event == 'Dodaj opis':
                    layout_6 = [
    [sg.Text('Opis:', size=(15, 1))], [sg.InputText(key='opis', size=(30, 1))],
    [sg.Button('Dodaj'), sg.Button('Anuluj')]
        ]
                    new_window_6 = stworz_okno('Opis przepisu', layout_6)

                    while True:
                        event, values = new_window_6.read()

                        if event in (sg.WINDOW_CLOSED, 'Dodaj'):
                            opis = str(values['opis'])
                            break

                        if event in (sg.WINDOW_CLOSED, 'Anuluj'):
                            break
                    new_window_6.close()
                    continue

                if event == 'Dodaj krok':
                    layout_4 = [
    [sg.Text('Tekst kroku:', size=(15, 1))], [sg.InputText(key='krok', size=(30, 2))],
    [sg.Button('Dodaj'), sg.Button('Anuluj')]
        ]
                    new_window_4 = stworz_okno('Dodaj krok', layout_4)

                    while True:
                        event, values = new_window_4.read()

                        if event in (sg.WINDOW_CLOSED, 'Dodaj'):
                            kroki.append(values['krok'])
                            break
                        if event in (sg.WINDOW_CLOSED, 'Anuluj'):
                            break
                    new_window_4.close()
                    continue

                if event == 'Przejrzyj kroki':
                    if len(kroki) == 0:
                        continue
                    else:
                        layout_5 = []
                        layout_5.append([sg.Text(f"{opis}")])
                        for i in range(len(kroki)):
                            layout_5.append([sg.Text(f"{i + 1}. {kroki[i]}")])
                        layout_5.append([sg.Button('Wróć')])

                        new_window_5 = stworz_okno("Kroki", layout_5)

                        while True:
                            event, values = new_window_5.read()

                            if event in (sg.WINDOW_CLOSED, 'Wróć'):
                                break
                        new_window_5.close()
                        continue
            new_window_2.close()

        for id_skladnika, nazwa_skladnika in skladniki:
            if event == f'PLUS_{id_skladnika}':

                layout_2 = [
        [sg.Text('Ilość do dodania:', size=(15, 1)), sg.InputText(key='dodaj')],
        [sg.Button('Dodaj')]
    ]
                new_window = stworz_okno('Dodawanie składników', layout_2)
                while True:
                    event, values = new_window.read()

                    if event in (sg.WINDOW_CLOSED, 'Dodaj'):
                        values['dodaj'] = float(values['dodaj'])
                        if values['dodaj'] < 0:
                            sg.popup(f'Jesteś w oknie dodawania produktów')
                            break
                        # można wywoływać jakieś exception itd
                        lista_skladnikow[f'{id_skladnika}'] += values['dodaj']
                        break
                new_window.close()

            elif event == f'MINUS_{id_skladnika}':
                layout_2 = [
            [sg.Text('Ilość do odjęcia:', size=(15, 1)), sg.InputText(key='dodaj')],
            [sg.Button('Odejmij')]
        ]
                new_window = stworz_okno('Odejmowanie składników', layout_2)
                while True:
                    event, values = new_window.read()

                    if event in (sg.WINDOW_CLOSED, 'Odejmij'):
                        values['dodaj'] = float(values['dodaj'])
                        if values['dodaj'] < 0:
                            sg.popup(f'Jesteś w oknie odejmowania produktów, podaj liczbę dodatnią')
                            break
                        # można wywoływać jakieś exception itd
                        aktualna_ilosc = lista_skladnikow[f'{id_skladnika}']
                    if aktualna_ilosc + values['dodaj'] < 0:
                        lista_skladnikow[f'{id_skladnika}'] = 0
                    else:
                        lista_skladnikow[f'{id_skladnika}'] -= values['dodaj']
                    break
                new_window.close()

            window[f'ILOSC_{id_skladnika}'].update(str(lista_skladnikow[f'{id_skladnika}']))

    window.close()

def dodaj_uzytkownika(databaseManager: DatabaseManager):
    layout = [
        [sg.Text('Dodaj użytkownika')],
        [sg.Text('Login:', size =(15, 1)), sg.InputText()],
        [sg.Text('Hasło:', size =(15, 1)), sg.InputText()],
        [sg.Text('Stanowisko:', size =(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Wyślij'), sg.CloseButton(button_text='Wyjście')]
    ]
    window = stworz_okno('NOWY UŻYTKOWNIK', layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break
        if values[0] != "" and values[1] != "" and values[2] != "":
            try:
                databaseManager.dodaj_uzytkownika(values[0], values[1], values[2])
                sg.popup(f'Dodałem nowego użytkownika')
            except (psycopg2.errors.UniqueViolation) as blad:
                sg.popup("Użytkownik o tym loginie już istnieje!", blad)
            except (psycopg2.errors.RaiseException) as blad:
                sg.popup('Wystąpił błąd!', blad)

    window.close()

def obsluga_magazynu(databaseManager, id_magazynu, user):
    skladniki = databaseManager.wypisz_skladniki(id_magazynu)
    wszystkie_skladniki = databaseManager.wypisz_wszystkie_skladniki()

    ilosc_skladnika = dict(skladniki)

    layout = []

    for id_skladnika, nazwa_skladnika in wszystkie_skladniki:
        ilosc = ilosc_skladnika.get(id_skladnika, 0)

        layout.append([
            sg.Text(f'{nazwa_skladnika}', size=(20, 1)),
            sg.Text(str(ilosc), size=(5, 1), key=f'ILOSC_{id_skladnika}'),
            sg.Button('+', key=f'PLUS_{id_skladnika}'),
            sg.Button('-', key=f'MINUS_{id_skladnika}')
        ])

    layout.append([sg.Button('Zamknij')])

    window = sg.Window('Magazyn Składników', layout)

    while True:
        event, _ = window.read()

        if event in (sg.WINDOW_CLOSED, 'Zamknij'):
            break

        for id_skladnika, _ in wszystkie_skladniki:
            if event == f'PLUS_{id_skladnika}':
                if databaseManager.czy_mialem_taki_skladnik(id_skladnika, id_magazynu) == None:
                    databaseManager.dodaj_skladnik_do_magazynu(id_magazynu, id_skladnika)

                layout_2 = [
        [sg.Text('Ilość do dodania:', size=(15, 1)), sg.InputText(key='dodaj')],
        [sg.Button('Dodaj')]
    ]
                new_window = stworz_okno('Dodawanie składników', layout_2)
                while True:
                    event, values = new_window.read()

                    if event in (sg.WINDOW_CLOSED, 'Dodaj'):
                        values['dodaj'] = float(values['dodaj'])
                        if values['dodaj'] < 0:
                            sg.popup(f'Jesteś w oknie dodawania produktów')
                            break
                        # można wywoływać jakieś exception itd
                        databaseManager.zmien_ilosc_skladnika(id_magazynu, id_skladnika, values['dodaj'], True)
                        break
                new_window.close()

            elif event == f'MINUS_{id_skladnika}':
                if databaseManager.czy_mialem_taki_skladnik(id_skladnika, id_magazynu) == None:
                    databaseManager.dodaj_skladnik_do_magazynu(id_magazynu, id_skladnika)
                layout_2 = [
            [sg.Text('Ilość do odjęcia:', size=(15, 1)), sg.InputText(key='dodaj')],
            [sg.Button('Odejmij')]
        ]
                new_window = stworz_okno('Odejmowanie składników', layout_2)
                while True:
                    event, values = new_window.read()

                    if event in (sg.WINDOW_CLOSED, 'Odejmij'):
                        values['dodaj'] = float(values['dodaj'])
                        if values['dodaj'] < 0:
                            sg.popup(f'Jesteś w oknie odejmowania produktów')
                            break
                        # można wywoływać jakieś exception itd
                        aktualna_ilosc = float(databaseManager.podaj_ilosc_skladnikow(id_magazynu, id_skladnika)[0])
                    if aktualna_ilosc + values['dodaj'] < 0:
                        sg.popup(f'Jest tylko {aktualna_ilosc} tego produktu')
                        continue
                    databaseManager.zmien_ilosc_skladnika(id_magazynu, id_skladnika, values['dodaj'], False)
                    break
                new_window.close()

            ilosc_skladnika = databaseManager.podaj_ilosc_skladnikow(id_magazynu, id_skladnika)

            if ilosc_skladnika is None:
                nowa_ilosc = 0
            else:
                nowa_ilosc = float(ilosc_skladnika[0])

            window[f'ILOSC_{id_skladnika}'].update(str(nowa_ilosc))

    window.close()

### DODAWANIE MAGAZYNU, SPRAWDŹ
def stworz_magazyn(databaseManager, user_id):
    # Pobierz magazyny użytkownika
    magazyny = databaseManager.znajdz_moje_magazyny(user_id)

    # Sprawdź, czy użytkownik nie ma już maksymalnej liczby magazynów (np. 5)
    if len(magazyny) >= 5:
        sg.popup("Nie możesz mieć więcej niż 5 magazynów!")
        return

    # Dodaj nowy magazyn
    databaseManager.dodaj_magazyn(user_id)
    sg.popup("Magazyn został pomyślnie utworzony!")

### DODAWANIE PRZEPISU, ALTERNATYWA DO MOJEGO
def stworz_przepis(databaseManager, user_id):
    # Zbieramy dane na temat przepisu
    layout = [
        [sg.Text('Podaj dane przepisu')],
        [sg.Text('Nazwa przepisu', size=(15, 1)), sg.InputText(key='nazwa')],
        [sg.Text('Opis', size=(15, 1)), sg.InputText(key='opis')],
        [sg.Text('Czas przygotowania (w minutach)', size=(15, 1)), sg.InputText(key='czas')],
        [sg.Text('ID składników (oddzielone przecinkami)', size=(15, 1)), sg.InputText(key='skladniki')],
        [sg.Button('Stwórz przepis')]
    ]
    window = stworz_okno('Tworzenie przepisu', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Stwórz przepis':
            nazwa = values['nazwa']
            opis = values['opis']
            czas = values['czas']
            skladniki = values['skladniki'].split(',')

            if not nazwa or not opis or not czas or not skladniki:
                sg.popup("Proszę wprowadzić wszystkie dane!")
                continue
            
            try:
                # Dodaj przepis do bazy danych
                przepis_id = databaseManager.dodaj_przepis(nazwa, opis, czas, user_id)

                # Dodaj składniki do przepisu
                for skladnik_id in skladniki:
                    databaseManager.dodaj_skladnik_do_przepisu(przepis_id, skladnik_id.strip())

                sg.popup(f"Przepis '{nazwa}' został pomyślnie dodany!")
                break
            except Exception as e:
                sg.popup(f"Coś poszło nie tak: {str(e)}")
                continue

    window.close()


###

def przyjecie_dostawy(databaseManager, user):
    # moje_magazyny = databaseManager.znajdz_moje_magazyny(user[0])
    # print(moje_magazyny)
    layout = [
        # [sg.Text('Moje magazyny: ', size=(15, 1)), sg.Text(f"{moje_magazyny}"), sg.Button('Dodaj magazyn')],
        [sg.Text('Numer magazynu:', size=(15, 1)), sg.InputText(key='MAGAZYN')],
        [sg.Button('Wyślij'), sg.Button('Cofnij')]
    ]
    window = stworz_okno('DOSTAWA', layout)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Cofnij'):
            break

        # if event == 'Dodaj magazyn':
        #     if len(moje_magazyny) < 5:
        #         databaseManager.dodaj_magazyn(user[0])
        #     else:
        #         sg.popup("Masz już maksymalną możliwą liczbę magazynów")

        if event == 'Wyślij':
            obsluga_magazynu(databaseManager, int(values['MAGAZYN']), user)

    window.close()



def sprzedaz(databaseManager: DatabaseManager, user_id: int):
    layout = [
        [sg.Text('Kod kreskowy:', size =(15, 1)), sg.InputText()],
        [sg.Text('Ilość:', size =(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Dodaj'), sg.Submit(button_text='Zakończ sprzedaż'), sg.CloseButton(button_text='Anuluj sprzedaż')],
    ]
    window = stworz_okno('SKANOWANIE', layout)

    sprzedaz_id = databaseManager.rozpoczecie_sprzedazy(user_id)
    while True:
        event, values = window.read()
        if event == 'Dodaj':
            produkt = databaseManager.znajdz_produkt(values[0])
            if(produkt is None):
                sg.popup('Produkt nie istnieje!')
            else:
                try:
                    databaseManager.skanowanie_produktu(produkt[0], values[1], produkt[1], sprzedaz_id)
                    sg.popup('Dodałem produkt')
                except (psycopg2.errors.UniqueViolation) as blad:
                    sg.popup("Produkt już został zeskanowany!")
        if event in (sg.WIN_CLOSED, 'Anuluj sprzedaż'):
            databaseManager.anulowanie_sprzedazy(sprzedaz_id)
            sg.popup('Anulowałem sprzedaz')
            break
        if event == 'Zakończ sprzedaż':
            databaseManager.zakonczenie_sprzedazy(sprzedaz_id)
            sg.popup('Zakonczylem sprzedaz')
            break

    window.close()

if __name__ == "__main__":
    zaloguj()
