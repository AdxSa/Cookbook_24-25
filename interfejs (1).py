import psycopg2
import decimal as dec
from tkinter import N
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
                sg.popup('Błedne dane logowania!')
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
        [sg.Button('Przyjmij dostawę')],
        [sg.Button('Sprzedaż')],
        [sg.Button('Zobacz przepisy')],
        [sg.CloseButton(button_text='Wyjście')]
    ]
    if user[3] == 'kierownik':
        layout.append([sg.Button('Dodaj użytkownika')])

    window = stworz_okno('DROGERIA', layout)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break
        if event == 'Zobacz przepisy':
            Zobacz_przepisy(databaseManager)
        if event == 'Dodaj użytkownika':
            dodaj_uzytkownika(databaseManager)
        if event == 'Przyjmij dostawę':
            przyjecie_dostawy(databaseManager)
        if event == 'Sprzedaż':
            sprzedaz(databaseManager, user[0])

    window.close()
    
def Zobacz_przepisy(databaseManager: DatabaseManager):
    przepisy = databaseManager.get_all_recipes()
    layout = [[sg.Text('Kategorie')], [sg.Button('Wszystkie'), sg.Button('Dania glowne'), sg.Button('Zupy'), sg.Button('Desery')]]
    for recipe in przepisy:
        id_przepisu, nazwa, opis, czas, id_użytkownika = recipe
        layout.append([
            sg.Button(nazwa, key=str(id_przepisu), size=(20, 1)),  # Przycisk z nazwą przepisu
            sg.Text(f"{opis} | Czas: {czas} min", size=(100, 1))  # Opis + czas przygotowania
        ])


    layout.append([sg.CloseButton(button_text='Wyjście')])
    window = stworz_okno('PRZEPISY', layout)

    while True:
        event, _ = window.read()

        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break

        if event.isdigit():
            pokaz_kroki(databaseManager, event)


    window.close()

def pokaz_kroki(databaseManager: DatabaseManager, id_przepisu):
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
    layout.append([sg.CloseButton(button_text='Wyjście')])
    window = stworz_okno(f"Przepis na pyszne jedzonko", layout)

    while True:
        event, _ = window.read()

        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break

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

def przyjecie_dostawy(databaseManager: DatabaseManager):
    layout = [
        [sg.Text('Kod kreskowy:', size =(15, 1)), sg.InputText()],
        [sg.Text('Ilość: ', size =(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Wyślij'), sg.CloseButton(button_text='Wyjście')]
    ]
    window = stworz_okno('DOSTAWA', layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break
        if values[0] != "" and values[1] != "":
            produkt = databaseManager.znajdz_produkt(values[0])
            if produkt is None:
               sg.popup('Produkt nie istnieje!')
            else: 
                databaseManager.przyjmij_dostawe(produkt[0], values[1])
                ilosc = values[1]
                sg.popup(f'Dodałem {ilosc} sztuk')

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