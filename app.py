#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import logging
from logging import Formatter, FileHandler
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import Form
from sqlalchemy.orm import aliased
from forms import ShowForm, ArtistForm, VenueForm
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres: @localhost:5432/fyyur1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# connect to a local postgresql database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id                  = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String, nullable=False)
    city                = db.Column(db.String(120), nullable=False)
    state               = db.Column(db.String(120), nullable=False)
    address             = db.Column(db.String(120))
    phone               = db.Column(db.String(120))
    image_link          = db.Column(db.String(500))
    facebook_link       = db.Column(db.String(120))
    genres              = db.Column(db.String(120), nullable=False)
    website             = db.Column(db.String(120))
    seeking_talent      = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    Show = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f"<Venue {self.name}>"

    # implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id                  = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String, nullable=False)
    city                = db.Column(db.String(120), nullable=False)
    state               = db.Column(db.String(120), nullable=False)
    phone               = db.Column(db.String(120))
    genres              = db.Column(db.String(120), nullable=False)
    image_link          = db.Column(db.String(500))
    website             = db.Column(db.String(120))
    facebook_link       = db.Column(db.String(120))
    seeking_venue       = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    Show = db.relationship('Show', backref='artist', lazy=True)

    # implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

def get_dict_list_from_result(result):
    list_dict = []
    for i in result:
        i_dict = i._asdict()
        list_dict.append(i_dict)
    return list_dict

@app.route('/venues')
def venues():
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data1 = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state)
    data2 = get_dict_list_from_result(data1)
    for row in data2:
        data3 = db.session.query(Venue.id, Venue.name).group_by(Venue.id, Venue.name).filter(Venue.city==row['city'], Venue.state==row['state'])
        data4 = get_dict_list_from_result(data3)
        row['venues']=data4
    return render_template('pages/venues.html', areas=data2)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term=request.form.get('search_term', '')
    data1 = db.session.query(Venue).filter(Venue.name.ilike('%'+str(search_term)+'%')).all()
    response={'count':'','data':''}
    response['count']=len(data1)
    response['data']=data1

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    data1 = db.session.query(Venue).filter(Venue.id==venue_id).first()
    return render_template('pages/show_venue.html', venue=data1)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm(request.form)
    try:
        venue = Venue()
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
        error = True
        print(e)
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        abort (400)
    else:
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        db.session.query(Venue).filter(Venue.id==venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return None    

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data1 = db.session.query(Artist.id, Artist.name).group_by(Artist.id, Artist.name)
    return render_template('pages/artists.html', artists=data1)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term=request.form.get('search_term', '')
    data1 = db.session.query(Artist).filter(Artist.name.ilike('%'+str(search_term)+'%')).all()
    response={'count':'','data':''}
    response['count']=len(data1)
    response['data']=data1    
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    data1 = db.session.query(Artist).filter(Artist.id==artist_id).first()
    return render_template('pages/show_artist.html', artist=data1)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = db.session.query(Artist).get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    try:
        data = request.form
        artist = db.session.query(Artist).get(artist_id)
        form.populate_obj(artist)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = db.session.query(Venue).get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    try:
        data = request.form
        venue = db.session.query(Venue).get(venue_id)
        form.populate_obj(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()    
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    form = ArtistForm(request.form)
    try:
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
        error = True
        print(e)
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        abort (400)
    else:
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.
    #artist_name = aliased(name)
    data = db.session.query(Show.venue_id, Show.artist_id, Show.start_time, Artist.image_link.label("artist_image_link"), Artist.name.label("artist_name"), Venue.name.label("venue_name")).join(Artist).join(Venue).group_by(Show.venue_id, Show.artist_id, Show.start_time, Artist.id, Venue.id)
    data1 = get_dict_list_from_result(data)
    return render_template('pages/shows.html', shows=data1)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # insert form data as a new Show record in the db, instead
    error = False
    form = ShowForm(request.form)
    try:
        show = Show()
        form.populate_obj(show)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        error = True
        db.session.rollback()
        # on unsuccessful db insert, flash an error.
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    if error:
        abort (400)
    else:
        return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger().setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger().addHandler(file_handler)
    app.logger().info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
