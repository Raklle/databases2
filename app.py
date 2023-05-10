from flask import Flask, render_template, request, redirect, url_for
import models

app = Flask(__name__)
app.config['SECRET_KEY'] = 'our very hard to guess secretfir'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lobbies')
def lobbies():
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
    return render_template('room.html')


# Run the application
app.run(debug=True)