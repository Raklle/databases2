-- CREATE TABLE Users (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     first_name TEXT NOT NULL,
--     last_name TEXT NOT NULL,
--     balance REAL NOT NULL,
--     email TEXT NOT NULL,
--     country TEXT NOT NULL,
--     password TEXT NOT NULL
-- );

-- CREATE TABLE Games (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     end_date TIMESTAMP,
--     seats INTEGER NOT NULL
-- );

-- CREATE TABLE UserGames (
--     user_id INTEGER NOT NULL,
--     game_id INTEGER NOT NULL,
--     active INTEGER DEFAULT TRUE,
--     PRIMARY KEY (user_id, game_id),
--     FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE,
--     FOREIGN KEY (game_id) REFERENCES Games (id) ON DELETE CASCADE
-- );


-- CREATE TABLE TransactionsHistory (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--     payer_id INTEGER,
--     receiver_id INTEGER,
--     game_id INTEGER,
--     payment_amount INTEGER NOT NULL,
--     FOREIGN KEY (payer_id) REFERENCES Users (id) ON DELETE CASCADE,
--     FOREIGN KEY (receiver_id) REFERENCES Users (id) ON DELETE CASCADE,
--     FOREIGN KEY (game_id) REFERENCES Games (id) ON DELETE CASCADE
-- );


-- DROP TRIGGER IF EXISTS check_seats_available;

-- CREATE TRIGGER check_seats_available
-- BEFORE INSERT ON UserGames
--     BEGIN
--         SELECT
--         CASE
--             WHEN (SELECT COUNT(*) FROM UserGames WHERE game_id = NEW.game_id AND active = TRUE) >= (SELECT seats FROM Games WHERE id = NEW.game_id)
--             THEN RAISE(ABORT, 'All seats are occupied')
--         END;
--     END;

-- DROP TRIGGER IF EXISTS check_seats_available_update;

-- CREATE TRIGGER check_seats_available_update
-- BEFORE UPDATE ON UserGames
--     FOR EACH ROW
--     WHEN OLD.active = false AND NEW.active = true
--     BEGIN
--         SELECT
--         CASE
--         WHEN (SELECT COUNT(*) FROM UserGames WHERE game_id = NEW.game_id AND active = TRUE) >= (SELECT seats FROM Games WHERE id = NEW.game_id)
--         THEN RAISE(ABORT, 'All seats are occupied')
--         END;
--     END;


-- CREATE VIEW GamesView AS SELECT id, seats, (SELECT COUNT(*) FROM UserGames WHERE game_id =g.id AND active = 1 ) active_players FROM Games AS g;
--

-- CREATE TRIGGER PreventNegativeBalance
-- BEFORE UPDATE ON Users
-- FOR EACH ROW
-- WHEN NEW.balance < 0
-- BEGIN
--     SELECT RAISE(ABORT, 'Balance cannot be negative');
-- END;

-- CREATE TRIGGER PreventJoiningFinishedGames
-- BEFORE INSERT ON UserGames
-- FOR EACH ROW
-- WHEN EXISTS (SELECT 1 FROM Games WHERE id = NEW.game_id AND end_date IS NOT NULL)
-- BEGIN
--     SELECT RAISE(ABORT, 'Game already ended');
-- END;
