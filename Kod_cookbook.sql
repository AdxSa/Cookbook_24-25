-- Tworzenie tabeli użytkowników
CREATE TABLE Uzytkownicy (
    ID_uzytkownika INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Imie VARCHAR(100) NOT NULL,
    Nazwisko VARCHAR(100) NOT NULL,
    Haslo VARCHAR(100) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE
);

-- Tworzenie tabeli przepisów
CREATE TABLE Przepisy (
    ID_przepisu INTEGER PRIMARY KEY,
    Nazwa_przepisu VARCHAR(255) NOT NULL UNIQUE,
    Opis TEXT,
    Czas_przygotowania INTEGER,
    ID_uzytkownika INTEGER NOT NULL,
    FOREIGN KEY (ID_uzytkownika) REFERENCES Uzytkownicy(ID_uzytkownika)
);

-- Tworzenie tabeli składników
CREATE TABLE Skladniki (
    ID_skladnika INTEGER PRIMARY KEY,
    Nazwa_skladnika VARCHAR(255) NOT NULL,
    Typ VARCHAR(100) NOT NULL,
    Opis_skladnika TEXT
);

-- Tworzenie tabeli magazynów
CREATE TABLE Magazyn (
    ID_magazynu INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ID_uzytkownika INTEGER NOT NULL,
    FOREIGN KEY (ID_uzytkownika) REFERENCES Uzytkownicy(ID_uzytkownika)
);

-- Tworzenie tabeli składników w magazynie
CREATE TABLE Skladniki_w_magazynie (
    ID_magazynu INTEGER NOT NULL,
    ID_skladnika INTEGER NOT NULL,
    Ilosc DECIMAL(10, 2),
    PRIMARY KEY (ID_magazynu, ID_skladnika),
    FOREIGN KEY (ID_magazynu) REFERENCES Magazyn(ID_magazynu),
    FOREIGN KEY (ID_skladnika) REFERENCES Skladniki(ID_skladnika)
);

-- Tworzenie tabeli listy składników
CREATE TABLE lista_skladnikow (
    ID_przepisu INTEGER NOT NULL,
    ID_skladnika INTEGER NOT NULL,
    Ilosc DECIMAL(10, 2) NOT NULL,
    ID_jednostki INTEGER NOT NULL,
    PRIMARY KEY (ID_przepisu, ID_skladnika),
    FOREIGN KEY (ID_przepisu) REFERENCES Przepisy(ID_przepisu),
    FOREIGN KEY (ID_skladnika) REFERENCES Skladniki(ID_skladnika)
);

-- Tworzenie tabeli kategorii przepisów
CREATE TABLE Kategorie_przepisow (
    ID_kategorii INTEGER PRIMARY KEY,
    Nazwa_kategorii VARCHAR(100) NOT NULL
);

-- Tworzenie tabeli przypisania przepisów do kategorii
CREATE TABLE Przepisy_kategorie (
    ID_przepisu INTEGER NOT NULL,
    ID_kategorii INTEGER NOT NULL,
    PRIMARY KEY (ID_przepisu, ID_kategorii),
    FOREIGN KEY (ID_przepisu) REFERENCES Przepisy(ID_przepisu),
    FOREIGN KEY (ID_kategorii) REFERENCES Kategorie_przepisow(ID_kategorii)
);

-- Tworzenie tabeli kroków przepisu
CREATE TABLE Kroki_przepisu (
    ID_kroku INTEGER PRIMARY KEY,
    ID_przepisu INTEGER NOT NULL,
    Tresc_kroku TEXT NOT NULL,
    Kolejnosc INTEGER NOT NULL,
    UNIQUE (ID_przepisu, Kolejnosc),
    FOREIGN KEY (ID_przepisu) REFERENCES Przepisy(ID_przepisu)
);

-- Tworzenie tabeli jednostek miary
CREATE TABLE Jednostki_miary (
    ID_jednostki INTEGER PRIMARY KEY,
    Nazwa_jednostki VARCHAR(50) NOT NULL
);

-- Tworzenie tabeli przelicznika jednostek miary
CREATE TABLE Przelicznik_miary (
    ID_skladnika INTEGER NOT NULL,
    ID_jednostki_1 INTEGER NOT NULL,
    ID_jednostki_2 INTEGER NOT NULL,
    Proporcja DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (ID_skladnika, ID_jednostki_1, ID_jednostki_2),
    FOREIGN KEY (ID_skladnika) REFERENCES Skladniki(ID_skladnika),
    FOREIGN KEY (ID_jednostki_1) REFERENCES Jednostki_miary(ID_jednostki),
    FOREIGN KEY (ID_jednostki_2) REFERENCES Jednostki_miary(ID_jednostki)
);

-- Uzytkownicy
INSERT INTO Uzytkownicy (Imie, Nazwisko, Haslo, Email) VALUES
('Anna', 'Kowalska', 'haslo123', 'anna.kowalska@example.com'),
('Jan', 'Nowak', 'bezpieczneHaslo', 'jan.nowak@example.com'),
('Piotr', 'Wisniewski', 'mojeHaslo', 'piotr.wisniewski@example.com');

-- Przepisy
INSERT INTO Przepisy (ID_przepisu, Nazwa_przepisu, Opis, Czas_przygotowania, ID_uzytkownika) VALUES
(1, 'Spaghetti Carbonara', 'Tradycyjne wloskie danie z makaronem i sosem jajecznym.', 20, 1),
(2, 'Tiramisu', 'Deser na bazie mascarpone, biszkoptow i kawy.', 30, 2),
(3, 'Zupa pomidorowa', 'Klasyczna zupa na bazie pomidorow i warzyw.', 15, 3);

-- Skladniki
INSERT INTO Skladniki (ID_skladnika, Nazwa_skladnika, Typ, Opis_skladnika) VALUES
(1, 'Makaron', 'Weglowodany', 'Podstawowy skladnik wielu dan makaronowych.'),
(2, 'Ser Parmezan', 'Nabial', 'Twardy ser o wyrazistym smaku.'),
(3, 'Jajka', 'Bialko', 'Uniwersalny skladnik uzywany do ciast i sosow.'),
(4, 'Pomidor', 'Warzywo', 'Podstawowy skladnik wielu zup i salatek.');

-- Magazyn
INSERT INTO Magazyn (ID_uzytkownika) VALUES
(1),
(2),
(3);

-- Skladniki w magazynie
INSERT INTO Skladniki_w_magazynie (ID_magazynu, ID_skladnika, Ilosc) VALUES
(1, 1, 2.5),
(1, 2, 0.3),
(2, 3, 6.0),
(3, 4, 10.0);

-- Lista skladnikow
INSERT INTO lista_skladnikow (ID_przepisu, ID_skladnika, Ilosc, ID_jednostki) VALUES
(1, 1, 200, 1),
(1, 2, 50, 1),
(1, 3, 2, 2),
(3, 4, 3, 2);

-- Kategorie przepisow
INSERT INTO Kategorie_przepisow (ID_kategorii, Nazwa_kategorii) VALUES
(1, 'Dania glowne'),
(2, 'Desery'),
(3, 'Zupy');

-- Przepisy kategorie
INSERT INTO Przepisy_kategorie (ID_przepisu, ID_kategorii) VALUES
(1, 1),
(2, 2), 
(3, 3); 

-- Kroki przepisu
INSERT INTO Kroki_przepisu (ID_kroku, ID_przepisu, Tresc_kroku, Kolejnosc) VALUES
(1, 1, 'Ugotuj makaron al dente.', 1),
(2, 1, 'Wymieszaj jajka z serem Parmezan.', 2),
(3, 1, 'Polacz makaron z sosem jajecznym.', 3),
(4, 3, 'Pokroj pomidory.', 1),
(5, 3, 'Podsmaz pomidory na oliwie.', 2),
(6, 3, 'Zalej woda i gotuj przez 10 minut.', 3);

-- Jednostki miary
INSERT INTO Jednostki_miary (ID_jednostki, Nazwa_jednostki) VALUES
(1, 'gram'),
(2, 'sztuka'),
(3, 'mililitr');

-- Przelicznik miary
INSERT INTO Przelicznik_miary (ID_skladnika, ID_jednostki_1, ID_jednostki_2, Proporcja) VALUES
(1, 1, 3, 1.0), 
(3, 2, 1, 50.0); 
