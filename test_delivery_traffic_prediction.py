import unittest
import delivery_traffic_prediction

class TestDeliveryTrafficPrediction(unittest.TestCase):
    def test_on_message(self):
        # Test the on_message function
        client = delivery_traffic_prediction.mqtt.Client()
        msg = {
            'vehicle_id': 'vehicle1',
            'location': 'location1',
            'speed': 60,
            'route': 'route1',
            'weather': 'weather1'
        }
        client.on_message(None, None, msg)
        
        # Verify if the data was stored in the object storage
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket='bucket_name', Key='vehicle_data/vehicle1')
        # Verify if the data was stored in the object storage
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket='bucket_name', Key='vehicle_data/vehicle1')
        data = json.loads(obj['Body'].read().decode('utf-8'))
        self.assertEqual(data['vehicle_id'], 'vehicle1')
        self.assertEqual(data['location'], 'location1')
        self.assertEqual(data['speed'], 60)
        self.assertEqual(data['route'], 'route1')
        self.assertEqual(data['weather'], 'weather1')

        # Verify if the data was inserted into the database
        conn = mysql.connector.connect(user='user', password='password', host='host', database='database')
        cursor = conn.cursor()
        query = "SELECT * FROM delivery_data WHERE vehicle_id = %s"
        cursor.execute(query, ('vehicle1',))
        delivery_data = cursor.fetchone()
        self.assertEqual(delivery_data[0], 'vehicle1')
        self.assertEqual(delivery_data[1], 'location1')
        self.assertEqual(delivery_data[2], 60)
        self.assertEqual(delivery_data[3], 'route1')
        self.assertEqual(delivery_data[4], 'weather1')

if __name__ == '__main__':
    unittest.main()

