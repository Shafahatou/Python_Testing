import json
from flask import Flask,render_template,request,redirect,flash,url_for


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

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)
    
    # Récupération des informations du formulaire
    placesRequired = int(request.form['places'])

    # Vérification si la compétition et le club existent
    if not competition or not club:
        flash("Erreur lors de la réservation, veuillez réessayer.")
        return redirect(url_for('index'))

      # Vérification du nombre de places (ne doit pas être négatif ou nul)
    if placesRequired <= 0:
        flash(f"Erreur : Le nombre de places doit être supérieur à 0.")
        return render_template('booking.html', club=club, competition=competition)

    # Limitation à un maximum de 12 places réservées par club
    if placesRequired > 12:
        flash("Erreur : Vous ne pouvez pas réserver plus de 12 places à la fois.")
        return render_template('booking.html', club=club, competition=competition)

    # Vérification des places disponibles dans la compétition
    if placesRequired > int(competition['numberOfPlaces']):
        flash(f"Erreur : Il n'y a pas assez de places disponibles pour la compétition {competition['name']}.")
        return render_template('booking.html', club=club, competition=competition)

    # Vérification si le club a assez de points pour réserver les places demandées
    if placesRequired > int(club['points']):
        flash(f"Erreur : Vous n'avez pas assez de points. Points disponibles : {club['points']}.")
        return render_template('booking.html', club=club, competition=competition)

    # Si tout est correct, mise à jour des points et des places
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    club['points'] = int(club['points']) - placesRequired

    flash('Réservation réussie !')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()


@app.route('/points')
def showPoints():
    return render_template('points.html', clubs=clubs)

