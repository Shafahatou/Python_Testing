import json
from flask import Flask,render_template,request,redirect,flash,url_for,session


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    club = next((club for club in clubs if club['email'] == request.form['email']), None)
    if not club:
        flash("Email non trouvé.")
        return redirect(url_for('index'))
    return render_template('welcome.html', club=club, competitions=competitions)



@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)



@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
   
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)

   
    placesRequired = int(request.form['places'])

   
    if not competition or not club:
        flash("Erreur lors de la réservation, veuillez réessayer.")
        return redirect(url_for('index'))

    
    if placesRequired <= 0:
        flash("Erreur : Le nombre de places doit être supérieur à 0.")
        return render_template('booking.html', club=club, competition=competition)

   
    if placesRequired > 12:
        flash("Erreur : Vous ne pouvez pas réserver plus de 12 places à la fois.")
        return render_template('booking.html', club=club, competition=competition)

    
    if placesRequired > int(competition['numberOfPlaces']):
        flash(f"Erreur : Il n'y a pas assez de places disponibles pour la compétition {competition['name']}.")
        return render_template('booking.html', club=club, competition=competition)

    
    if placesRequired > int(club['points']):
        flash(f"Erreur : Vous n'avez pas assez de points. Points disponibles : {club['points']}.")
        return render_template('booking.html', club=club, competition=competition)

    
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    club['points'] = int(club['points']) - placesRequired

    flash('Réservation réussie ! Vous avez utilisé {} points pour {} places.'.format(placesRequired, placesRequired))
    return render_template('welcome.html', club=club, competitions=competitions)



@app.route('/points')
def showPoints():
    return render_template('points.html', clubs=clubs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        
        club = next((club for club in clubs if club['email'] == email), None)
        
        if club:
            
            session['club'] = club  
            flash(f"Bienvenue {club['name']}!", "success")
            return redirect(url_for('showSummary'))
        else:
            flash("Adresse email invalide. Veuillez réessayer.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('club', None)  # Supprime la session
    flash("Vous vous êtes déconnecté.", "success")
    return redirect(url_for('index'))

@app.route('/competitions')
def competitions_list():
    return render_template('competitions.html', competitions=competitions)

@app.route('/selectCompetition/<club_name>', methods=['GET', 'POST'])
def select_competition(club_name):
    club = next((c for c in clubs if c['name'] == club_name), None)
    if request.method == 'POST':
        competition_name = request.form['competition']
        return redirect(url_for('book', competition=competition_name, club=club_name))

    return render_template('select_competition.html', club=club, competitions=competitions)



# TODO: Add route for points display

# main driver function
if __name__ == '__main__':
    app.run(debug=True)



