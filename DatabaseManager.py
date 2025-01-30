import psycopg2

class DatabaseManager:
    def __init__(self, hostname, database, username, password, options):
        self.credentials = {"host": hostname, "dbname": database, "user": username, "password": password, "options":options}

    def fetchone(self, query: str, arguments: tuple):
        with psycopg2.connect(**self.credentials) as con:
            with con.cursor() as curs:
                curs.execute(query, arguments)
                return curs.fetchone()
    
    def fetchall(self, query: str, arguments: tuple):
        with psycopg2.connect(**self.credentials) as con:
            with con.cursor() as curs:
                curs.execute(query, arguments)
                return curs.fetchall()
    
    def wykonaj_query(self, query: str, arguments: tuple):
        with psycopg2.connect(**self.credentials) as con:
            with con.cursor() as curs:
                curs.execute(query, arguments)

    # def znajdz_uzytkownika(self, login: str, haslo: str):
    #     return self.fetchone(f"SELECT * FROM uzytkownicy WHERE login=%s AND haslo=%s;", (login, haslo))
    def znajdz_uzytkownika(self, email: str, haslo: str):
        return self.fetchone(f"SELECT * FROM uzytkownicy WHERE email=%s AND haslo LIKE %s;", (email, haslo))

    def ilosc_produktu(self, id_produktu: int)-> int:
        aktualny_stan = 0
        stan_magazynowy = self.fetchall(f'SELECT SUM(ilosc) AS sprzedane, typ FROM stan_magazynowy WHERE id_produktu=%s GROUP BY typ;', (id_produktu,))
        for wpis in stan_magazynowy:
            if(wpis[1] == 'przyjecie'):
                aktualny_stan = aktualny_stan + wpis[0]
            else:
                aktualny_stan = aktualny_stan - wpis[0]

        return aktualny_stan
    
    def dodaj_uzytkownika(self, imie: str, nazwisko: str, email: str, haslo: str):
        self.wykonaj_query(f"INSERT INTO uzytkownicy(imie, nazwisko, haslo, email) VALUES (%s, %s, %s, %s);", (imie, nazwisko ,haslo, email))

    def przyjmij_dostawe(self, id_produktu: int, ilosc: int):
        self.wykonaj_query(f"INSERT INTO stan_magazynowy (ilosc, typ, id_produktu) VALUES (%s, %s, %s);", (ilosc, "przyjecie", id_produktu))

    def wypisz_wszystkie_skladniki(self):
        return self.fetchall(f"SELECT ID_skladnika, nazwa_skladnika FROM skladniki;", 1)

    def wypisz_skladniki(self, id_magazynu):
        return self.fetchall(f"SELECT ID_skladnika, ILOSC FROM skladniki_w_magazynie WHERE ID_magazynu = %s;", (id_magazynu,))

    def podaj_ilosc_skladnikow(self, id_magazynu: int, id_skladnika: int):
        return self.fetchone(f"SELECT ILOSC FROM skladniki_w_magazynie WHERE ID_magazynu = %s AND ID_skladnika = %s;", (id_magazynu, id_skladnika))

    def zmien_ilosc_skladnika(self, id_magazynu: int, id_skladnika: int, ilosc_do_dodania: float, dodaj: bool):
        quantity = self.fetchone(f"SELECT ILOSC FROM skladniki_w_magazynie WHERE ID_magazynu = %s AND ID_skladnika = %s;", (id_magazynu, id_skladnika))
        quantity = float(quantity[0])
        if dodaj == True:
            quantity += ilosc_do_dodania
            self.wykonaj_query(f"UPDATE skladniki_w_magazynie SET ILOSC = %s WHERE ID_magazynu = %s AND ID_skladnika = %s;", (quantity, id_magazynu, id_skladnika))
        elif quantity - ilosc_do_dodania >= 0:
            quantity -= ilosc_do_dodania
            self.wykonaj_query(f"UPDATE skladniki_w_magazynie SET ILOSC = %s WHERE ID_magazynu = %s AND ID_skladnika = %s;", (quantity, id_magazynu, id_skladnika))

    def dodaj_skladnik_do_magazynu(self, id_magazynu: int, id_skladnika: int):
        self.wykonaj_query(f"INSERT INTO skladniki_w_magazynie (ID_magazynu, ID_skladnika, Ilosc) VALUES (%s, %s, 0);", (id_magazynu, id_skladnika))

    def dodaj_magazyn(self, id_uzytkownika: int):
        self.wykonaj_query(f"INSERT INTO Magazyn (ID_uzytkownika) VALUES (%s);", (id_uzytkownika, ))

    def dodaj_przepis(self, nazwa, opis, czas, id_uzytkownika):
        self.wykonaj_query(f"INSERT INTO Przepisy (Nazwa_przepisu, Opis, Czas_przygotowania, ID_uzytkownika) VALUES VALUES (%s, %s, %s, %s);", (nazwa, opis, czas, id_uzytkownika, ))

    def czy_mialem_taki_skladnik(self, id_skladnika: int, id_magazynu: int):
        return self.fetchone(f"SELECT * FROM skladniki_w_magazynie WHERE ID_magazynu = %s AND ID_skladnika = %s", (id_magazynu, id_skladnika))

    def znajdz_moje_magazyny(self, id_uzytkownika: int):
        return self.fetchall(f"SELECT ID_magazynu FROM magazyn WHERE ID_uzytkownika = %s", (id_uzytkownika, ))

    def dopasuj_skladnik_do_id(self, id_skladnika: int):
        return self.fetchone(f"SELECT nazwa_skladnika FROM SKLADNIKI WHERE ID_skladnika = %s", (id_skladnika, ))

    def rozpoczecie_sprzedazy(self, id_uzytkownika: int)-> int:
        sprzedaz = self.fetchone(f"INSERT INTO sprzedaz (data, status, id_uzytkownika) VALUES (current_timestamp, 'w trakcie', %s) RETURNING id_sprzedazy", (id_uzytkownika,))
        return sprzedaz[0]

    def znajdz_produkt(self, kod_kreskowy: str):
        return self.fetchone(f"SELECT id_produktu, cena FROM produkty WHERE kod_kreskowy=%s;", (kod_kreskowy,))

    def skanowanie_produktu(self, id_produktu: int, ilosc: int, cena: int, id_sprzedazy: int):
        self.wykonaj_query(f"INSERT INTO sprzedaz_produktu (id_produktu, id_sprzedazy, cena, ilosc) VALUES (%s, %s, %s, %s)", (id_produktu, id_sprzedazy, cena, ilosc))
    
    def anulowanie_sprzedazy(self, sprzedaz_id: int):
        self.wykonaj_query(f"UPDATE sprzedaz SET status = 'anulowana' WHERE id_sprzedazy = %s;", (sprzedaz_id,))
    
    def zakonczenie_sprzedazy(self, sprzedaz_id: int):
        self.wykonaj_query(f"UPDATE sprzedaz SET status = 'ukonczona' WHERE id_sprzedazy = %s;", (sprzedaz_id,))
        self.wykonaj_query(f"INSERT INTO stan_magazynowy (ilosc, id_produktu) SELECT ilosc, id_produktu FROM sprzedaz_produktu WHERE id_sprzedazy = %s;", (sprzedaz_id,))

    def znajdz_przepisy_z_kategorii(self, id_kategorii: int):
        return self.fetchall(f"SELECT Przepisy.ID_przepisu, Przepisy.Nazwa_przepisu, Przepisy.Opis, "
                         f"Przepisy.Czas_przygotowania, Przepisy.ID_uzytkownika FROM Kategorie_przepisow "
                         f"JOIN Przepisy_kategorie ON Kategorie_przepisow.ID_kategorii = Przepisy_kategorie.ID_kategorii "
                         f"JOIN Przepisy ON Przepisy_kategorie.ID_przepisu = Przepisy.ID_przepisu "
                         f"WHERE Kategorie_przepisow.ID_kategorii = %s", (id_kategorii,))

    def get_all_recipes(self):
        return self.fetchall(f"SELECT * FROM przepisy", 1)

    def otrzymaj_kroki_przepisu(self, id_przepisu: int):
        return self.fetchall(f"SELECT kolejnosc, tresc_kroku FROM kroki_przepisu WHERE id_przepisu = %s;", (id_przepisu, ))

    def otrzymaj_skladniki_przepisu(self, id_przepisu: int):
        return self.fetchall(f"SELECT ls.id_skladnika, ls.ilosc, s.nazwa_skladnika, nazwa_jednostki FROM lista_skladnikow ls JOIN skladniki s ON (ls.id_skladnika = s.id_skladnika) JOIN jednostki_miary jm USING (id_jednostki) WHERE ls.id_przepisu = %s", (id_przepisu, ))

    def dane_autora_przepisu(self, id_przepisu: int):
        return self.fetchone(f"SELECT imie, nazwisko, email FROM uzytkownicy u JOIN przepisy p ON (u.id_uzytkownika=p.id_uzytkownika) WHERE p.id_przepisu = %s;", (id_przepisu, ))


    def wypisz_jednostki_dla_skladnika(self, id_skladnika:int):
        t1 = self.fetchall(f"SELECT u1.nazwa_jednostki, u2.nazwa_jednostki FROM przelicznik_miary p "
                           f"JOIN jednostki_miary u1 ON p.id_jednostki_1 = u1.id_jednostki "
                           f"JOIN jednostki_miary u2 ON p.id_jednostki_2 = u2.id_jednostki "
                           f"WHERE p.id_skladnika = %s;", (id_skladnika, ))
        jednostki = set()
        for i, j in t1:
            jednostki.add(i)
            jednostki.add(j)
        return list(jednostki)
    def znajdz_przelicznik_jednostek(self, id_skladnika:int, nazwa1 :int, nazwa2:int):
        return self.fetchone(f"SELECT proporcja FROM przelicznik_miary p "
                             f"JOIN jednostki_miary u1 ON p.id_jednostki_1 = u1.id_jednostki "
                             f"JOIN jednostki_miary u2 ON p.id_jednostki_2 = u2.id_jednostki "
                             f"WHERE p.id_skladnika = %s AND "
                             f"(u1.nazwa_jednostki = %s AND u2.nazwa_jednostki = %s);", (id_skladnika, nazwa1, nazwa2))
