#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
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

    def __init__(self, name, city, state, address, phone, image_link, facebook_link, genres, website, seeking_talent, seeking_description):
        self.name                = name
        self.city                = city
        self.state               = state
        self.address             = address
        self.phone               = phone
        self.image_link          = image_link
        self.facebook_link       = facebook_link
        self.genres              = genres
        self.website             = website
        self.seeking_talent      = seeking_talent
        self.seeking_description = seeking_description
    
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
