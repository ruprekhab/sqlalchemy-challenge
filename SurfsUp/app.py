# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()


# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

###############################################################
#Calculate latest date and date a year before
###############################################################

# Query to find the most recent date in dataset
date_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

# Calculate the date one year from the last date in data set.
last_year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Define the routes
@app.route("/")
def welcome():
    """List all the available api routes."""
    return(
        f"Avaialble Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br>"           
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
        # Perform a query to retrieve the date and precipitation scores of last 12 months from the most recent date      
        prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year_date).all()
        # Convert query result to a dictionary
        prcp_list = {date:prcp for date, prcp in prcp_data}
        # Return JSON representation of dictionary.
        return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    # Perform a query to get station names from the dataset
    stations_data = session.query(Measurement.station).distinct().all()
    # Convert list of tuples into a normal list
    stations_list =list(np.ravel(stations_data))
    # Return a JSON list of stations.
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
        # Perform query to get the most active station
        active_stations = session.query(Measurement.station, func.count(Measurement.station))\
                   .group_by(Measurement.station).order_by(func.count(Measurement.station)\
                                                                  .desc()).first()
        
        # Query the temperature observations of the most-active station for the 12 months of data from the most recent date
        temp_data = session.query(Measurement).filter(Measurement.tobs).\
                filter(Measurement.date >= last_year_date).filter(Measurement.station == active_stations.station) 
        # Extracts and stores temperature in a list
        temp = [t.tobs for t in temp_data]
        # Return a JSON list of temperature observations for the previous year
        return jsonify(temp)


@app.route("/api/v1.0/<start>")
def temp_stats(start):
    #   Query to  calculate MIN, AVG, and MAX for all the dates greater than or equal to the specified start date.
      temp_stats = session.query(func.min(Measurement.tobs),
                           func.avg(Measurement.tobs),
                           func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()
      # Convert list of tuples into a normal list
      response = list(np.ravel(temp_stats))
      # Return a JSON list of temperature statistics.  
      return jsonify(response) 

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    # Query to calculate TMIN, TAVG, and TMAX for all dates between the specified start and end date.
    temp_range = session.query(func.min(Measurement.tobs),
                                func.avg(Measurement.tobs),
                                func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()

    # Convert list of tuples into a normal list
    response = list(np.ravel(temp_range))
    
    # Return a JSON list of temperature statistics
    return jsonify(response) 


# Close session
session.close()
# Define the main behavior
if __name__ == '__main__':
      app.run(debug=True)