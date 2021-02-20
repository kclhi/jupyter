import unittest, git, random, string
from pony import orm
from starlette.testclient import TestClient
from api import routes
from api.models.base import db
from tests.fixtures import db_fixtures

class BasicTestCall(unittest.TestCase):

  def setUp(self):
    db.provider = db.schema = None;
    db.bind(provider='sqlite', filename='../api/mappings.sqlite', create_db=True);
    db.generate_mapping(create_tables=True);
    db.drop_all_tables(with_all_data=True);
    db.create_tables();
    db_fixtures.db_called();

  def test_called(self):
    with orm.db_session: assert [sorted([tv.name for tv in row.template_variable]) for row in db.Expression.select()] == [['call', 'function'], ['object']];
  
  def test_add_calls(self):
    client = TestClient(routes.app);
    letters = string.ascii_lowercase;
    response = client.post('/add', json={
      'user': 'martin', 
      'code': '#!/usr/bin/env python\n# coding: utf-8\n\n# In[ ]:\n\n\n'+ (''.join(random.choice(letters) for i in range(10))) + '.' + (''.join(random.choice(letters) for i in range(10))) + '(y);\n\n\n# In[ ]:\n\n\n' + (''.join(random.choice(letters) for i in range(10))) + '.' + (''.join(random.choice(letters) for i in range(10))) + '(u);\n\n', 
      'notebook': {
        'name': 'NotebookB.ipynb', 
        'path': 'NotebookB.ipynb',
        'last_modified': '2021-02-11 19:01:40.820000+00:00', 
        'created': '2021-02-11 19:01:40.820000+00:00', 
        'content': None, 
        'format': None, 
        'mimetype': None, 
        'size': 716, 
        'writable': True, 
        'type': 'notebook'
      }
    });
    assert response.status_code == 200;

if __name__ == "__main__":
  unittest.main()
