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

def update_data(user_id, first_name, last_name, email, country, password):
    """
    This function is to update user's data.
    """
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    data = (first_name, last_name, email, country, password, user_id)

    try:
        cur.execute(f"UPDATE Users SET first_name = ?, last_name = ?, email = ?, country = ?, password = ? where id = ?", data)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f'Error while modifiying data: {e}')
    finally:
        conn.close()

def get_user_data(user_id):
    """
    This function retrives user data.
    """
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM Users where id = {user_id}")
    return cur.fetchall()

def get_games():
    """
    This function retrieves a list of active games.

    Returns:
    - A list of active games
    """
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()

    cur.execute("SELECT * FROM GamesView")
    return cur.fetchall()

def get_player_games_history(user_id):
    """
    This function retrieves a history of games for user with user_id.

    Returns:
    - A list of games
    """
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()

    cur.execute(f"SELECT * from Games g INNER JOIN UserGames UG on g.id = UG.game_id where UG.user_id = {user_id} and g.end_date is not NULL")
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
    cur.execute("SELECT UserGames.user_id, Users.first_name || ' ' || Users.last_name as name FROM UserGames inner join Users on UserGames.user_id = Users.id where game_id = " + str(game_id))
    return cur.fetchall()


def get_filtered_games(show_active = False, min_players = -9223372036854775808, max_players = 9223372036854775807):
    """
    This function retrieves a list of players for a specific game.

    Parameters:
    - game_id: ID of the game

    Returns:
    - A list of players for the given game
    """

    print(show_active, min_players, max_players)
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()

    if show_active is True: 
        cur.execute('''SELECT id, seats, (SELECT COUNT(*) FROM UserGames 
                        WHERE game_id =g.id AND active = 1 ) active_players 
                        FROM Games AS g 
                        WHERE g.end_date is NULL and active_players between ? and ? ;''', (int(min_players), int(max_players)))    
    else:
        cur.execute('''SELECT id, seats, (SELECT COUNT(*) FROM UserGames 
                        WHERE game_id =g.id AND active = 1 ) active_players 
                        FROM Games AS g 
                        WHERE active_players between ? and ? ;''', (int(min_players), int(max_players)))    

    # cur.execute("SELECT id, seats, (SELECT COUNT(*) FROM UserGames WHERE game_id =g.id AND active = 1 ) active_players FROM Games AS g where g.end_date is NULL ;")
    return cur.fetchall()

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

def add_user(first_name, last_name, email, country, password):
    """
    This function adds a user to the Users table. New country is added to Country table, if given doesn't exist.

    Parameters:
    - first_name: first name of the user
    - last_name: last name of the game
    - email: email of the user
    - country: country ot the user
    - password: users_password
    """
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    data = (first_name, last_name, 0, email, country, password)

    try:
        cur.execute("INSERT INTO USERS (first_name, last_name, balance, email, country, password) VALUES (?,?,?,?,?,?)", data)
        conn.commit()
        print("New user added")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error while adding new user to database!")
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

def get_user_transaction_history(user_id):
    """
    This function retrieves the transaction history of a user.

    Parameters:
    - user_id: ID of the user

    Returns:
    - User's transaction history
    """
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()
    try:
        cur.execute('''SELECT g.id, g.payer_id, g.receiver_id, g.payment_amount 
                        FROM TransactionsHistory AS g 
                        WHERE ? = payer_id OR ? = receiver_id''',
                    (user_id, user_id))
        result = cur.fetchall()
        return result
    except sqlite3.Error as e:
        print(f'Error while retrieving user transaction history: {e}')

    finally:
        conn.close()

def logger(email):
    """
    This function is to authenticate users data.

    Parameters:
    - email

    Returns:
    - password to validate
    """
    conn = sqlite3.connect('PokerDatabase')
    cur = conn.cursor()

    cur.execute(f"SELECT id, password FROM Users where email = ?", (email, ))
    return cur.fetchall()


# conn = sqlite3.connect('PokerDatabase')
# with open('schema.sql') as f:
#     conn.executescript(f.read())
# conn.close()