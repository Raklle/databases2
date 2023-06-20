from flask import Flask, render_template, request, redirect, url_for
import models
import bcrypt

app = Flask(__name__)

user_id = None
game_id = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global user_id, game_id
    if user_id is not None:
        return render_template('index.html', show_user_profile = "True")
    return render_template('index.html')

@app.route('/logout')
def logout():
    global user_id, game_id 
    user_id = None
    game_id = None 
    return redirect('/')

@app.route('/user-profile', methods=['GET', 'POST'])
def user_profile():
    global user_id, game_id

    if user_id is None: 
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if "firstname" in request.form: 
            first_name = request.form['firstname']
            last_name = request.form['lastname']
            email = request.form['email']
            country = request.form['country']
            password = bcrypt.hashpw(request.form['password'].encode("utf-8"), bcrypt.gensalt())
            models.update_data(user_id, first_name, last_name, email, country, password)
    
    return render_template('user-profile.html', user_data = user_id, data=models.get_user_data(user_id)[0])

@app.route('/lobbies', methods=['GET', 'POST'])
def lobbies():
    global user_id, game_id
    if user_id is None: 
        return redirect(url_for('index'))
 
    if request.method == 'POST' or request.method == 'GET':
        if "leave_room" in request.form:
            models.leave_game(user_id, game_id)
            return render_template('lobbies.html', data=models.get_filtered_games(True), actual_button = 'True', min_players = '0', max_players = '6')
        
        if "test" in request.form:
            game_id = request.form.get('test')[1]
            return render_template('room.html', data=models.get_players(request.form.get('test')[1]))
     
        if "actual" in request.form or "minimal_no_players" in request.form or "maximum_no_players" in request.form:

            min_players = 0 if request.form["minimal_no_players"] == '' else request.form["minimal_no_players"]
            max_players = 6 if request.form["maximum_no_players"] == '' else request.form["maximum_no_players"]

            if "actual" in request.form:
                show_actual = (request.form["actual"] == "on")
            else:
                show_actual = False

            return render_template('lobbies.html', data=models.get_filtered_games(show_actual, min_players, max_players),  actual_button = show_actual, min_players = str(min_players), max_players = str(max_players))

    return render_template('lobbies.html', data=models.get_filtered_games(True), actual_button = 'True',  min_players = '0', max_players ='6')

@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    global user_id, game_id
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
    
        data = models.logger(email)
        print(email, data)

        if not data: 
            error = "Failed to log in!"
            return render_template('sign-in.html', error=error)

        tmp_user_id = data[0][0]

        if bcrypt.checkpw(password.encode("utf-8"), data[0][1]):
            globals()['user_id'] = tmp_user_id
            return render_template('index.html', show_user_profile=True)
        else:
            error = "Failed to log in!"
            globals()['user_id'] = None
            return render_template('sign-in.html', error=error)

    return render_template('sign-in.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ""
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        country = request.form['country']
        password = request.form['password']

        password_hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        models.add_user(first_name, last_name, email, country, password_hashed)
        return redirect(url_for('index'))
    
    return render_template('register.html', message=error)

@app.route("/room", methods = ["post"])
def room():
    global user_id, game_id

    if user_id is None: 
        return redirect(url_for('index'))
    
    game_id = request.form.get('test')[1]
    models.join_game(user_id, game_id)
    return render_template('room.html', data=models.get_players(game_id))

@app.route("/history", methods=['GET', 'POST'])
def history():
    global user_id

    if user_id is None: 
        return redirect(url_for('index'))
    
    if request.method == 'POST' and "show_players_info" in request.form:
        return render_template('history.html', game_info=models.get_players(request.form['show_players_info']))

    return render_template('history.html', data=models.get_player_games_history(user_id))


# Run the application
app.run(debug=True)