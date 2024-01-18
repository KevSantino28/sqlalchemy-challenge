# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from flask import Flask, jsonify
import datetime as dt
import pandas as pd

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Station = Base.classes.station
Measurements = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

##Creating a reference for date
def date_prev_year():
    most_recent_date = session.query(func.max(Measurements.date)).first()[0]
    first_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return(
        f"Welcome to the Hawaii climate API:<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    start_date = '2016-08-23'
    sel = [Measurements.date, func.sum(Measurements.prcp)]
    precipitation = session.query(*sel).\
    filter(Measurements.date >= start_date).\
    group_by(Measurements.date).\
    order_by(Measurements.date).all()
    session.close()
    
    precipitation_dates = []
    precipitation_totals = []

    for date, dailytotal in precipitation:
        precipitation_dates.append(date)
        precipitation_totals.append(dailytotal)

    precipitation_dict = dict(zip(precipitation_dates, precipitation_totals))

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement,stations_query.session.bind)
    return jsonify(stations.to_dict())
    
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    start_date = '2016-08-23'
    sel = [Measurements.date, Measurements.tobs]
    station_temps = session.query(*sel).\
    filter(Measurements.date >= start_date, Measurements.station == 'USC00519281').\
    group_by(Measurements.date).\
    order_by(Measurements.date).all()
    session.close()

    observ_dates = []
    temp_observations = []

    for date, observation in station_temps:
        observ_dates.append(date)
        temp_observations.append(observation)
    most_active_tobs = dict(zip(observ_dates, temp_observations))

    return jsonify(most_active_tobs)

@app.route("/api/v1.0/<start_date>")
def trip (start_date, end_date='2017-08-23'):
    session = Session(engine)
    query_result = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
    filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    if trip_dict['Min']:
        return jsonify(trip_stats)
    else:
        return jsonify({"Error": f"Date {start_date} not found or formatted incorrectly (YYYY-MM-DD)"})

@app.route("/api/v1.0/<start_date>/<end_date>")
def trip2 (start_date, end_date):
    session=Session(engine)
    query_result = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
    filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        trip_dict = {}
        trip_dict["Min"] = min
        trip_dict["Average"] = avg
        trip_dict["Max"] = max
        trip_stats.append(trip_dict)

    if trip_dict['Min']:
        return jsonify(trip_stats)
    else:
        return jsonify({"Error": f"Date(s) not found or formatted incorrectly (YYYY-MM-DD)"})


if __name__ == "__main__":
    app.run()