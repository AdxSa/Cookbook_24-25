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

    def rozpoczecie_sprzedazy(self, id_uzytkownika: int)-> int:
        sprzedaz = self.fetchone(f"INSERT INTO sprzedaz (data, status, id_uzytkownika) VALUES (current_timestamp, 'w trakcie', %s) RETURNING id_sprzedazy;", (id_uzytkownika,))
        return sprzedaz[0]

    def znajdz_produkt(self, kod_kreskowy: str):
        return self.fetchone(f"SELECT id_produktu, cena FROM produkty WHERE kod_kreskowy=%s;", (kod_kreskowy,))

    def skanowanie_produktu(self, id_produktu: int, ilosc: int, cena: int, id_sprzedazy: int):
        self.wykonaj_query(f"INSERT INTO sprzedaz_produktu (id_produktu, id_sprzedazy, cena, ilosc) VALUES (%s, %s, %s, %s);", (id_produktu, id_sprzedazy, cena, ilosc))
    
    def anulowanie_sprzedazy(self, sprzedaz_id: int):
        self.wykonaj_query(f"UPDATE sprzedaz SET status = 'anulowana' WHERE id_sprzedazy = %s;", (sprzedaz_id,))
    
    def zakonczenie_sprzedazy(self, sprzedaz_id: int):
        self.wykonaj_query(f"UPDATE sprzedaz SET status = 'ukonczona' WHERE id_sprzedazy = %s;", (sprzedaz_id,))
        self.wykonaj_query(f"INSERT INTO stan_magazynowy (ilosc, id_produktu) SELECT ilosc, id_produktu FROM sprzedaz_produktu WHERE id_sprzedazy = %s;", (sprzedaz_id,))

    def get_all_recipes(self):
        return self.fetchall(f"SELECT * FROM przepisy", 1)

    def otrzymaj_kroki_przepisu(self, id_przepisu: int):
        return self.fetchall(f"SELECT kolejnosc, tresc_kroku FROM kroki_przepisu WHERE id_przepisu = %s;", (id_przepisu, ))

    def otrzymaj_skladniki_przepisu(self, id_przepisu: int):
        return self.fetchall(f"SELECT ls.id_skladnika, ls.ilosc, s.nazwa_skladnika, nazwa_jednostki FROM lista_skladnikow ls JOIN skladniki s ON (ls.id_skladnika = s.id_skladnika) JOIN jednostki_miary jm USING (id_jednostki) WHERE ls.id_przepisu = %s", (id_przepisu, ))
    def dane_autora_przepisu(self, id_przepisu: int):
        return self.fetchone(f"SELECT imie, nazwisko, email FROM uzytkownicy u JOIN przepisy p ON (u.id_uzytkownika=p.id_uzytkownika) WHERE p.id_przepisu = %s;", (id_przepisu, ))