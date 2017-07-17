import os
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template


app = Flask(__name__)


@app.route('/')
def home():
	return render_template('base.html')