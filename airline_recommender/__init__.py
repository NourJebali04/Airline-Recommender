from flask import Flask, render_template, redirect, url_for, request
from neo4j import GraphDatabase

from .utils import db

conn = db.DBConnect("neo4j://localhost:7687", "neo4j", "1234")

application = Flask(__name__)

@application.route('/home')
def index():
    return render_template('index.html')

@application.route('/airlines')
def airlines():
        return (render_template('airlines.html'))

@application.route('/test')
def test():
        print('hello')
        return (redirect(url_for('airlines')))


@application.route('/', methods=[ 'GET', 'POST'])
def index2():
    try:
        if request.method == 'POST':
            source = request.form['to']
            destination = request.form['from']
            try:
                airlines = conn.find_airline_to_go_to_from(source, destination)
                k = (list(airlines))
                print(source, destination, k)

                #return render_template('airlines.html', airlines=k, source=source, destination=destination)
                return render_template('airlines.html',  source=source, destination=destination, airlines=k)
                #return redirect(url_for('test'))

            except Exception as e:
                print(e)
        else:
            print("we're here!")
            return render_template('index.html')
    except:
        print("oops!")
    #return render_template('index.html')

@application.route('/bestairlines')
def bestairlines():
    best = conn.find_best_airline()
    return render_template('bestairlines.html', best=best)

@application.route('/destinations')
def bestdest():
    bestdest = conn.find_best_airlines_destination()
    return render_template('destinations.html', bestdest=bestdest)

