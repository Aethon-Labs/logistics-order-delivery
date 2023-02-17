import paho.mqtt.client as mqtt
import json
import boto3
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# MQTT callback function to handle incoming data
def on_message(client, userdata, msg):
    # Decode the incoming data as a JSON object
    data = json.loads(msg.payload.decode())

    # Store the data in the object storage
    s3 = boto3.client('s3')
    s3.put_object(Bucket='bucket_name', Key='vehicle_data/' + data['vehicle_id'], Body=json.dumps(data))

    # Connect to the MySQL database
    conn = mysql.connector.connect(user='user', password='password', host='host', database='database')
    cursor = conn.cursor()

    # Insert the data into the database
    query = "INSERT INTO delivery_data (vehicle_id, location, speed, route, weather) VALUES (%s, %s, %s, %s, %s)"
    values = (data['vehicle_id'], data['location'], data['speed'], data['route'], data['weather'])
    cursor.execute(query, values)
    conn.commit()

    # Retrieve the delivery data from the database
    query = "SELECT * FROM delivery_data"
    cursor.execute(query)
    delivery_data = cursor.fetchall()

    # Convert the delivery data into a Pandas DataFrame
    delivery_data = pd.DataFrame(delivery_data, columns=['vehicle_id', 'location', 'speed', 'route', 'weather'])

    # Preprocess the delivery data
    delivery_data = delivery_data.replace(-999, np.NaN)
    delivery_data.dropna(inplace=True)
    le = LabelEncoder()
    delivery_data['location'] = le.fit_transform(delivery_data['location'])
    delivery_data['route'] = le.fit_transform(delivery_data['route'])
    delivery_data['weather'] = le.fit_transform(delivery_data['weather'])

    # Split the delivery data into training and test sets
    X = delivery_data.drop('speed', axis=1)
    y = delivery_data['speed']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Train a Random Forest Regressor model
    regressor = RandomForestRegressor(n_estimators=100, random_state=0)
    regressor.fit(X_train, y_train)

    # Predict the delivery traffic
    y_pred = regressor.predict(X_test)

    # Evaluate the model using metrics such as mean absolute error and root mean squared error
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print("Mean Absolute Error:", mae)
    print("Root Mean Squared Error:", rmse)

    # Close the database connection
    cursor.close()
    conn.close()

# MQTT client configuration
client = mqtt.Client()
client.on_message = on_message
client.connect('broker_host', 1883, 60)
client.subscribe('vehicle_data')

# Start the MQTT client loop
client.loop_forever()

