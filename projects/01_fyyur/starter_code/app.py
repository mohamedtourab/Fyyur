# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import logging
from logging import Formatter, FileHandler
import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from forms import *
import datetime
from sqlalchemy import exc

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, s_format='medium'):
    date = dateutil.parser.parse(value)
    if s_format == 'full':
        s_format = "EEEE MMMM, d, y 'at' h:mma"
    elif s_format == 'medium':
        s_format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, s_format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    all_venues = Venue.query.all()
    obj = {}
    for venue in all_venues:
        obj[venue.state + '&' + venue.city] = []

    for venue in all_venues:
        num_upcoming_shows = len(
            Show.query.filter(Show.start_time > datetime.datetime.now(), Show.venue_id == venue.id).all())
        obj[venue.state + '&' + venue.city].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows,
        })
    data = []
    for key, value in obj.items():
        data.append({
            "city": key.split("&")[1],
            "state": key.split("&")[0],
            "venues": value
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    all_venues = Venue.query.all()
    response = {
        "count": 0,
        "data": []
    }
    for venue in all_venues:
        num_upcoming_shows = len(
            Show.query.filter(Show.start_time > datetime.datetime.now(), Show.venue_id == venue.id).all())
        if search_term.lower() in venue.name.lower():
            response["data"].append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": num_upcoming_shows,
            })
    response["count"] = len(response["data"])
    return render_template('pages/search_venues.html', results=response,
                           search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.get(venue_id)
    past_shows = Show.query.filter(Show.start_time <= datetime.datetime.now(), Show.venue_id == venue_id).all()
    future_shows = Show.query.filter(Show.start_time > datetime.datetime.now(), Show.venue_id == venue_id).all()
    venue_copy = {
        "id": venue.id,
        "name": venue.name,
        "genres": [venue.genres],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(future_shows),
    }
    for past_show in past_shows:
        venue_copy['past_shows'].append({
            "artist_id": past_show.artist.id,
            "artist_name": past_show.artist.name,
            "artist_image_link": past_show.artist.image_link,
            "start_time": str(past_show.start_time)
        })
    for future_show in future_shows:
        venue_copy['upcoming_shows'].append({
            "artist_id": future_show.artist.id,
            "artist_name": future_show.artist.name,
            "artist_image_link": future_show.artist.image_link,
            "start_time": str(future_show.start_time)
        })
    return render_template('pages/show_venue.html', venue=venue_copy)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    my_venue = {}
    form = request.form
    try:
        my_venue = Venue(name=form['name'], city=form['city'], state=form['state'], address=form['address'],
                         phone=form['phone'], facebook_link=form['facebook_link'],
                         image_link="https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
                         seeking_talent=True, genres=",".join(request.form.getlist('genres')))
        # on successful db insert, flash success
        db.session.add(my_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred. Venue ' + form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = []
    all_artists = Artist.query.all()
    for artist in all_artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    all_artists = Artist.query.all()
    response = {
        "count": 0,
        "data": []
    }
    for artist in all_artists:
        num_upcoming_shows = len(
            Show.query.filter(Show.start_time > datetime.datetime.now(), Show.artist_id == artist.id).all())
        if search_term.lower() in artist.name.lower():
            response["data"].append({
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": num_upcoming_shows,
            })
    response["count"] = len(response["data"])
    return render_template('pages/search_artists.html', results=response,
                           search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    desired_artist = Artist.query.get(artist_id)
    past_shows = Show.query.filter(Show.start_time <= datetime.datetime.now(), Show.artist_id == artist_id).all()
    future_shows = Show.query.filter(Show.start_time > datetime.datetime.now(), Show.artist_id == artist_id).all()
    artist_copy = {
        "id": desired_artist.id,
        "name": desired_artist.name,
        "genres": [desired_artist.genres],
        "city": desired_artist.city,
        "state": desired_artist.state,
        "phone": desired_artist.phone,
        "website": desired_artist.website,
        "facebook_link": desired_artist.facebook_link,
        "seeking_venue": desired_artist.seeking_venue,
        "seeking_description": desired_artist.seeking_description,
        "image_link": desired_artist.image_link,
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(future_shows),
    }
    for past_show in past_shows:
        artist_copy['past_shows'].append({
            "venue_id": past_show.venue.id,
            "venue_name": past_show.venue.name,
            "venue_image_link": past_show.venue.image_link,
            "start_time": str(past_show.start_time)
        })
    for future_show in future_shows:
        artist_copy['upcoming_shows'].append({
            "venue_id": future_show.venue.id,
            "venue_name": future_show.venue.name,
            "venue_image_link": future_show.venue.image_link,
            "start_time": str(future_show.start_time)
        })
    return render_template('pages/show_artist.html', artist=artist_copy)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    desired_artist = Artist.query.get(artist_id)
    artist = {
        "id": desired_artist.id,
        "name": desired_artist.name,
        "genres": [desired_artist.genres],
        "city": desired_artist.city,
        "state": desired_artist.state,
        "phone": desired_artist.phone,
        "website": desired_artist.website,
        "facebook_link": desired_artist.facebook_link,
        "seeking_venue": desired_artist.seeking_venue,
        "seeking_description": desired_artist.seeking_description,
        "image_link": desired_artist.image_link,
    }
    form.name.data = artist['name']
    form.genres.data = [(genre, genre) for genre in artist["genres"][0].split(",")]
    form.city.data = artist['city']
    form.state.data = artist['state']
    form.phone.data = artist['phone']
    form.facebook_link.data = artist['facebook_link']
    form.image_link.data = artist['image_link']

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # artist record with ID <artist_id> using the new attributes
    my_artist = Artist.query.get(artist_id)
    artist = {
        "id": my_artist.id,
        "name": my_artist.name,
        "genres": [my_artist.genres],
        "city": my_artist.city,
        "state": my_artist.state,
        "phone": my_artist.phone,
        "website": my_artist.website,
        "facebook_link": my_artist.facebook_link,
        "seeking_venue": my_artist.seeking_venue,
        "seeking_description": my_artist.seeking_description,
        "image_link": my_artist.image_link,
    }
    form = request.form
    try:
        my_artist.name = form['name']
        my_artist.city = form['city']
        my_artist.state = form['state']
        my_artist.phone = form['phone']
        my_artist.facebook_link = form['facebook_link']
        my_artist.genres = ",".join(request.form.getlist('genres'))
        db.session.add(my_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred. Artist ' + form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    desired_venue = Venue.query.get(venue_id)
    venue = {
        "id": desired_venue.id,
        "name": desired_venue.name,
        "genres": [desired_venue.genres],
        "address": desired_venue.address,
        "city": desired_venue.city,
        "state": desired_venue.state,
        "phone": desired_venue.phone,
        "website": desired_venue.website,
        "facebook_link": desired_venue.facebook_link,
        "seeking_talent": desired_venue.seeking_talent,
        "seeking_description": desired_venue.seeking_description,
        "image_link": desired_venue.image_link
    }
    form.address.data = venue["address"]
    form.name.data = venue['name']
    form.genres.data = [(genre, genre) for genre in venue["genres"][0].split(",")]
    form.city.data = venue['city']
    form.state.data = venue['state']
    form.phone.data = venue['phone']
    form.facebook_link.data = venue['facebook_link']
    form.image_link.data = venue['image_link']
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # venue record with ID <venue_id> using the new attributes
    my_venue = Venue.query.get(venue_id)
    try:
        form = request.form
        my_venue.name = form['name']
        my_venue.city = form['city']
        my_venue.state = form['state']
        my_venue.address = form['address']
        my_venue.phone = form['phone']
        my_venue.facebook_link = form['facebook_link']
        my_venue.genres = ",".join(request.form.getlist('genres'))
        db.session.add(my_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred. Venue ' + my_venue.name + ' could not be listed.')
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
    # called upon submitting the new artist listing form
    my_artist = {}
    form = request.form
    try:
        my_artist = Artist(name=form['name'], city=form['city'], state=form['state'],
                           phone=form['phone'], facebook_link=form['facebook_link'],
                           image_link="https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
                           seeking_venue=True, genres=",".join(request.form.getlist('genres')))
        # on successful db insert, flash success
        db.session.add(my_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except SQLAlchemy.exce:
        db.session.rollback()
        flash('An error occurred. Artist ' + form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    all_shows = Show.query.all()
    data = []
    for show in all_shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    try:
        form = request.form
        artist = Artist.query.get(form['artist_id'])
        venue = Venue.query.get(form['venue_id'])
        show = Show(start_time=form['start_time'])
        show.artist = artist
        show.venue = venue
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except exc.SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
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
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
