import sqlite3


def join_game(user_id, game_id):
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    # jeszcze potem dodam tu że wyrzuca bład jak dołączamy do gry w której jesteśmy,
    # teraz nic się nie dzieje złego w bazie, ale nie ma błędu

    try:
        cur.execute('SELECT EXISTS(SELECT 1 FROM UserGames WHERE user_id = ? AND game_id = ?)', (user_id, game_id))
        row_exists = cur.fetchone()[0]
        if not row_exists:
            cur.execute('INSERT INTO UserGames (user_id, game_id, active) VALUES (?, ?, ?)', (user_id, game_id, True))
        else:
            cur.execute('UPDATE UserGames SET active = ? WHERE user_id = ? AND game_id = ? AND active = ?',
                        (True, user_id, game_id, False))
        conn.commit()
        print(f'User with ID {user_id} joined game with ID {game_id}')
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Error while joining game: {e}')
    finally:
        conn.close()

def leave_game(user_id, game_id):
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()

    try:
        cur.execute('UPDATE UserGames SET active = ? WHERE user_id = ? AND game_id = ? AND active = ?',
                    (False, user_id, game_id, True))
        conn.commit()
        print(f'User with ID {user_id} left game with ID {game_id}')
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Error while leaving game: {e} (User ID: {user_id})')
    finally:
        conn.close()


join_game(4, 1)
leave_game(6, 1)
join_game(4, 1)
join_game(6, 1)

# conn = sqlite3.connect('PokerDatabase')
# with open('schema.sql') as f:
#     conn.executescript(f.read())
# conn.close()