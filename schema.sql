CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    balance REAL NOT NULL,
    email TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE Games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    seats INTEGER NOT NULL
);

CREATE TABLE UserGames (
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, game_id),
    FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES Games (id) ON DELETE CASCADE
);

CREATE TABLE TransactionsHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    payer_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    payment_amount INTEGER NOT NULL,
    FOREIGN KEY (payer_id) REFERENCES Users (id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES Users (id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES Games (id) ON DELETE CASCADE
);


CREATE OR REPLACE TRIGGER check_seats_available
BEFORE INSERT ON UserGames
    BEGIN
        SELECT
        CASE
        WHEN (SELECT COUNT(*) FROM UserGames WHERE game_id = NEW.game_id) >= (SELECT seats FROM Games WHERE id = NEW.game_id)
        THEN RAISE(ABORT, 'All seats are occupied')
    END;
END;
