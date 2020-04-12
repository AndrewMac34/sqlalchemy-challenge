import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
from datetime import datetime, timedelta
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()
#inspector = inspect(engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    obj = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date=obj[0]
    date_object = datetime.strptime(date, '%Y-%m-%d').date()
    query_date = dt.date(date_object.year,date_object.month,date_object.day)- dt.timedelta(days=365)
    ha=session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= query_date).order_by(Measurement.date).all()

    session.close()

    prec = []
    for date, prcp in ha:
        raw_prec = {}
        raw_prec["Date"] = date
        raw_prec["Precipitation"] = prcp
        prec.append(raw_prec)
     
    

    return jsonify(prec)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    obj = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date=obj[0]
    date_object = datetime.strptime(date, '%Y-%m-%d').date()
    query_date = dt.date(date_object.year,date_object.month,date_object.day)- dt.timedelta(days=365)
    active=session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    session.close()
    return jsonify(active)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    obj = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date=obj[0]
    date_object = datetime.strptime(date, '%Y-%m-%d').date()
    query_date = dt.date(date_object.year,date_object.month,date_object.day)- dt.timedelta(days=365)
    most_active=session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).limit(1)[0][0]

    temperature=session.query(Measurement.tobs).\
    filter(Measurement.date >= query_date).\
    filter(Measurement.station==most_active).order_by(Measurement.date).all()
    session.close()
    return jsonify(temperature)

@app.route("/api/v1.0/start")
def calc_temps():
    
    session=Session(engine)
    obj = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date=obj[0]
    date_object = datetime.strptime(date, '%Y-%m-%d').date()
    start_date = '2017-02-28'
    query_date = dt.date(date_object.year,date_object.month,date_object.day)- dt.timedelta(days=365)
    start_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    # function usage example
    #print(calc_temps('2012-02-28', '2012-03-05'))
    session.close()
    return jsonify(start_temp)

@app.route("/api/v1.0/start/end")
def calc_temps_start_end():
   
    session=Session(engine)
    obj = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date=obj[0]
    date_object = datetime.strptime(date, '%Y-%m-%d').date()
    start_date = '2017-02-28'
    end_date = '2017-03-05'
    query_date = dt.date(date_object.year,date_object.month,date_object.day)- dt.timedelta(days=365)
    start_end_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # function usage example
    #print(calc_temps('2017-02-28', '2017-03-05'))
    session.close()
    return jsonify(start_end_temp)

if __name__ == "__main__":
    app.run(debug =  True)