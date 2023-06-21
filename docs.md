# Dokumentacja bazy danych

![Schemat bazy](https://github.com/Raklle/databases2/blob/main/schema.png)

## Tabele:
## Users

Ta tabela przechowuje informacje o użytkownikach w systemie.

### Kolumny:
- id: INTEGER (Primary Key)
- first_name: TEXT (Required)
- last_name: TEXT (Required)
- balance: REAL (Required)
- email: TEXT (Required)
- country: TEXT (Required) FOREIGN KEY

## Country

Ta tabela przechowuje informacje o krajach.

### Kolumny:
- CountryName: TEXT (Primary Key)


## Games

Ta tabela przechowuje informacje o grach.

### Kolumny:
- id: INTEGER (Primary Key)
- start_date: TIMESTAMP (Required, Default: CURRENT_TIMESTAMP)
- end_date: TIMESTAMP
- seats: INTEGER (Required)

## UserGames

Ta tabela reprezentuje relację między użytkownikami a grami.

### Kolumny:
- user_id: INTEGER (Required)
- game_id: INTEGER (Required)
- active: INTEGER (Default: TRUE)

## TransactionsHistory

Ta tabela rejestruje historię transakcji między użytkownikami dla konkretnych gier.

### Kolumny:
- id: INTEGER (Primary Key)
- date: TIMESTAMP (Required, Default: CURRENT_TIMESTAMP)
- payer_id: INTEGER
- receiver_id: INTEGER
- game_id: INTEGER
- payment_amount: INTEGER (Required)

## Triggery:
### check_seats_available (BEFORE INSERT ON UserGames)

Ten trigger sprawdza, czy są dostępne miejsca przed wstawieniem nowego rekordu do tabeli UserGames.
```
CREATE TRIGGER check_seats_available
BEFORE INSERT ON UserGames
BEGIN
    SELECT
    CASE
        WHEN (SELECT COUNT(*) FROM UserGames
        WHERE game_id = NEW.game_id AND active = TRUE) >= (SELECT seats FROM Games WHERE id = NEW.game_id)
        THEN RAISE(ABORT, 'All seats are occupied')
    END;
END;
```
### check_seats_available_update (BEFORE UPDATE ON UserGames)

Ten trigger sprawdza, czy są dostępne miejsca przed aktualizacją rekordu w tabeli UserGames.
```
    CREATE TRIGGER check_seats_available_update
    BEFORE UPDATE ON UserGames
              FOR EACH ROW
        WHEN OLD.active = false AND NEW.active = true
        BEGIN
            SELECT
            CASE
            WHEN (SELECT COUNT(*) FROM UserGames WHERE 
            game_id = NEW.game_id AND active = TRUE) >= (SELECT seats FROM Games WHERE id = NEW.game_id)
            THEN RAISE(ABORT, 'All seats are occupied')
            END;
        END;
```
### PreventNegativeBalance (BEFORE UPDATE ON Users)

Ten trigger zapobiega ujemnemu saldu użytkownika podczas aktualizacji.
```
CREATE TRIGGER PreventNegativeBalance
BEFORE UPDATE ON Users
FOR EACH ROW
WHEN NEW.balance < 0
BEGIN
    SELECT RAISE(ABORT, 'Balance cannot be negative');
END;
```

### PreventJoiningFinishedGames 

Ten trigger zapobiega dołączeniu do zakończonej gry.
```
CREATE TRIGGER PreventJoiningFinishedGames
BEFORE INSERT ON UserGames
FOR EACH ROW
WHEN EXISTS (SELECT 1 FROM Games WHERE id = NEW.game_id AND end_date IS NOT NULL)
BEGIN
    SELECT RAISE(ABORT, 'Game already ended');
END;
```

## Widok: GamesView

Ten widok zapewnia podsumowanie gier, w tym liczbę miejsc i liczbę aktywnych graczy dla każdej gry.
```
CREATE VIEW GamesView AS SELECT id, seats, (SELECT COUNT(*) FROM UserGames WHERE game_id =g.id AND active = 1 ) active_players 
                         FROM Games AS g;
```
