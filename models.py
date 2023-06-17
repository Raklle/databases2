import sqlite3

class AlreadyInGameException(Exception):
    pass

def join_game(user_id, game_id):
    """
    This function allows a user to join a game by inserting a new record into the UserGames table.

    Parameters:
    - user_id: ID of the user
    - game_id: ID of the game
    """
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
    """
    This function allows a user to leave a game by updating the active status in the UserGames table.

    Parameters:
    - user_id: ID of the user
    - game_id: ID of the game
    """
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

def get_active_games():
    """
    This function retrieves a list of active games.

    Returns:
    - A list of active games
    """
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()

    cur.execute("SELECT * FROM GamesView")
    return cur.fetchall()

def get_players(game_id):
    """
    This function retrieves a list of players for a specific game.

    Parameters:
    - game_id: ID of the game

    Returns:
    - A list of players for the given game
    """
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    cur.execute("SELECT * FROM UserGames where game_id =" + str(game_id))
    return cur.fetchall()


def is_in_game(user_id, game_id):
    """
    This function checks if a user is already in a game.

    Parameters:
    - user_id: ID of the user
    - game_id: ID of the game

    Returns:
    - True if the user is  in the game, otherwise False
    """
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
    """
    This function retrieves the game history of a user.

    Parameters:
    - user_id: ID of the user

    Returns:
    - User's game history
    """
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
    """
    This function retrieves the list of active players in a game.

    Parameters:
    - game_id: ID of the game

    Returns:
    - A list of active players in the game
    """
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

def transfer(payer_id, receiver_id, game_id, money):
    """
    This function transfers money from the payer's account to the receiver's account.

    Parameters:
    - payer_id: ID of the payer
    - receiver_id: ID of the receiver
    - game_id: ID of the game
    - money: Amount of money to transfer
    """
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
    """
    This function deposits money into a user's account.

    Parameters:
    - user_id: ID of the user
    - money: Amount of money to deposit
    """
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
        print(f'Error while retrieving user game history: {e}')

    finally:
        conn.close()

def withdraw(user_id, money):
    """
    This function withdraws money from a user's account.

    Parameters:
    - user_id: ID of the user
    - money: Amount of money to withdraw
    """
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

# conn = sqlite3.connect('PokerDatabase')
# with open('schema.sql') as f:
#     conn.executescript(f.read())
# conn.close()
