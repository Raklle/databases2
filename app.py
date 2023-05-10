from flask import Flask, render_template, request, redirect, url_for
import models

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lobbies', methods=['GET', 'POST'])
def lobbies():
    if request.method == 'POST':
        print(request.values)
        return render_template('room.html', data=request.values)

    print(models.get_games())
    return render_template('lobbies.html', data=models.get_games())

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    error = ""
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']

        return redirect(url_for('lobbies'))
    return render_template('sign-up.html', message=error)

@app.route("/room", methods = ["post"])
def printer():
    # print(request.form.get('test')[1])
    models.join_game("10", request.form.get('test')[1])
    # print(models.get_players(request.form.get('test')[1]))
    return render_template('room.html', data=models.get_players(request.form.get('test')[1]))


# Run the application
app.run(debug=True)