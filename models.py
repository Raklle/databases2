import sqlite3

class AlreadyInGameException(Exception):
    pass

def join_game(user_id, game_id):
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()

    try:
        cur.execute('SELECT EXISTS(SELECT 1 FROM UserGames WHERE user_id = ? AND game_id = ?)', (user_id, game_id))
        row_exists = cur.fetchone()[0]

        if not row_exists:
            cur.execute('INSERT INTO UserGames (user_id, game_id, active) VALUES (?, ?, ?)', (user_id, game_id, True))
        else:
            cur.execute('SELECT active FROM UserGames WHERE user_id = ? AND game_id = ?', (user_id, game_id))
            active_status = cur.fetchone()[0]

            if active_status:
                raise AlreadyInGameException

            cur.execute('UPDATE UserGames SET active = ? WHERE user_id = ? AND game_id = ? AND active = ?',
                        (True, user_id, game_id, False))

        conn.commit()
        print(f'User with ID {user_id} joined game with ID {game_id}')

    except sqlite3.Error as e:
        conn.rollback()
        print(f'Error while joining game: {e}')
    except AlreadyInGameException as e:
        print(str(f"User with ID {user_id} is already active in game with ID {game_id}"))
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

# Podstawowe zapytania do testu
def get_active_games():
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()

    cur.execute("SELECT * FROM GamesView")
    return cur.fetchall()

def get_players(game_id):
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    cur.execute("SELECT * FROM UserGames where game_id =" + str(game_id))
    return cur.fetchall()

# Koniec zmian

def is_in_game(user_id, game_id):
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    cur.execute('SELECT EXISTS(SELECT 1 FROM UserGames WHERE user_id = ? AND game_id = ?)', (user_id, game_id))
    row_exists = cur.fetchone()[0]
    conn.close()
    if not row_exists:
       return True
    else:
        return False

def get_user_game_history(user_id):
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()

    try:
        cur.execute('''SELECT g.id, g.start_date, g.end_date, g.seats 
                        FROM Games AS g 
                        WHERE g.id IN (SELECT game_id FROM UserGames WHERE user_id = ?)''',
                    (user_id,))
        result = cur.fetchall()
        return result

    except sqlite3.Error as e:
        print(f'Error while retrieving user game history: {e}')

    finally:
        conn.close()

def get_active_players(game_id):
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()

    try:
        cur.execute('''SELECT u.first_name, u.last_name, u.email, u.country
                       FROM UserGames AS ug
                       JOIN Users AS u ON ug.user_id = u.id
                       WHERE ug.game_id = ? AND ug.active = 1''', (game_id,))
        result = cur.fetchall()
        active_players = [f"{row[0]} {row[1]}" for row in result]
        return active_players

    except sqlite3.Error as e:
        print(f'Error while retrieving active players: {e}')

    finally:
        conn.close()

def transfer(payer_id, receiver_id,game_id, money):
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    try:
        # Remove money from payer's account
        # Preventing negative balance is handled by a trigger
        cur.execute('SELECT balance FROM Users WHERE id = ?', (payer_id,))
        current_balance = cur.fetchone()[0]
        cur.execute('UPDATE Users SET balance = ? WHERE id = ?',
                    (current_balance - money, payer_id))

        # Add money to receiver's account
        cur.execute('SELECT balance FROM Users WHERE id = ?', (receiver_id,))
        current_balance = cur.fetchone()[0]
        cur.execute('UPDATE Users SET balance = ? WHERE id = ?',
                    (current_balance + money, receiver_id))

        cur.execute('INSERT INTO TransactionsHistory (payer_id, receiver_id, game_id, payment_amount) VALUES (?, ?, ?, ?)', (payer_id,receiver_id,game_id, money))
        conn.commit()
        return

    except sqlite3.Error as e:
        print(f'Error while processing money transfer: {e}')
    finally:
        conn.close()

def deposit(user_id, money):
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    try:
        # Add money to user's account
        cur.execute('SELECT balance FROM Users WHERE id = ?', (user_id,))
        current_balance = cur.fetchone()[0]
        cur.execute('UPDATE Users SET balance = ? WHERE id = ?',
                    (current_balance + money, user_id))

        cur.execute('INSERT INTO TransactionsHistory (payer_id, receiver_id, game_id, payment_amount) VALUES (?, ?, ?, ?)', (user_id,None,None, money))
        conn.commit()
        return


    except sqlite3.Error as e:
        print(f'Error while processing money deposit: {e}')
    finally:
        conn.close()

def withdraw(user_id, money):
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    try:
        # Remove money from user's account
        # Preventing negative balance is handled by a trigger
        cur.execute('SELECT balance FROM Users WHERE id = ?', (user_id,))
        current_balance = cur.fetchone()[0]
        cur.execute('UPDATE Users SET balance = ? WHERE id = ?',
                    (current_balance - money, user_id))

        cur.execute('INSERT INTO TransactionsHistory (payer_id, receiver_id, game_id, payment_amount) VALUES (?, ?, ?, ?)', (None,user_id,None, money))
        conn.commit()
        return
    except sqlite3.Error as e:
        print(f'Error while processing money withdrawal: {e}')
    finally:
        conn.close()

withdraw(2, 1000)

# conn = sqlite3.connect('PokerDatabase')
# with open('schema.sql') as f:
#     conn.executescript(f.read())
# conn.close()
