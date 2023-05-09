import sqlite3


def join_game(user_id, game_id):
    conn = sqlite3.connect('PokerDatabase')

    with open('schema.sql') as f:
        conn.executescript(f.read())

    cur = conn.cursor()

    try:
        cur.execute('INSERT INTO UserGames (user_id, game_id) VALUES (?, ?)', (user_id, game_id))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Error while joining game: {e}')
    finally:
        conn.close()



join_game(4, 1)

