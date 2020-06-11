import unittest
from starlette.testclient import TestClient
from api import routes

class BasicTests(unittest.TestCase):
    def test_add(self):
        client = TestClient(routes.app)
        response = client.post('/add');
        assert response.status_code == 200

if __name__ == "__main__":
    unittest.main()
