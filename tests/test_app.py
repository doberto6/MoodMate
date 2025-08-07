import unittest
from app import app, db
from models import Entry
import json

class MoodMateTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()

    def test_save_entry(self):
        response = self.app.post('/api/entries',
            data=json.dumps({
                'mood': 4,
                'content': 'Feeling great today!'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()
