import unittest, os, git, random, string
from starlette.testclient import TestClient
from api import routes

class BasicTests(unittest.TestCase):

    def test_add(self):
        client = TestClient(routes.app);
        letters = string.ascii_lowercase;
        response = client.post('/add', json={'user': 'martin', 'code': '#!/usr/bin/env python\n# coding: utf-8\n\n# In[1]:\n\n\nimport ' + (''.join(random.choice(letters) for i in range(10))) + '\n\n\n# In[ ]:\n\n\nimport ' + (''.join(random.choice(letters) for i in range(10))) + '\n\n', 'notebook': {'name': 'Untitled.ipynb', 'path': 'Untitled.ipynb', 'last_modified': '2021-01-28 16:32:39.320000+00:00', 'created': '2021-01-28 16:32:39.320000+00:00', 'content': None, 'format': None, 'mimetype': None, 'size': 715, 'writable': True, 'type': 'notebook'}});
        assert response.status_code == 200;

if __name__ == "__main__":
    unittest.main();
