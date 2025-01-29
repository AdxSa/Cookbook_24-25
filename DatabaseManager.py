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

    def czy_mialem_taki_skladnik(self, id_skladnika: int, id_magazynu: int):
        return self.fetchone(f"SELECT * FROM skladniki_w_magazynie WHERE ID_magazynu = %s AND ID_skladnika = %s", (id_magazynu, id_skladnika))

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