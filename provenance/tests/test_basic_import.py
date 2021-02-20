import unittest, git, random, string
from pony import orm
from api.models.base import db
from starlette.testclient import TestClient
from api import routes
from tests.fixtures import db_fixtures

class BasicTestImport(unittest.TestCase):

  def setUp(self):
    db.provider = db.schema = None;
    db.bind(provider='sqlite', filename='../api/mappings.sqlite', create_db=True);
    db.generate_mapping(create_tables=True);
    db.drop_all_tables(with_all_data=True);
    db.create_tables();
    db_fixtures.db_imported();
      
  def test_db(self):
    with orm.db_session: assert [sorted([tv.name for tv in row.template_variable]) for row in db.Expression.select()] == [['language'], ['language'], ['library', 'libraryName'], ['library', 'libraryName']];
          
  def test_add_imports(self):
    client = TestClient(routes.app);
    letters = string.ascii_lowercase;
    response = client.post('/add', json={
      'user': 'martin', 
      'code': '#!/usr/bin/env python\n# coding: utf-8\n\n# In[1]:\n\n\nimport ' + (''.join(random.choice(letters) for i in range(10))) + '\n\n\n# In[ ]:\n\n\nimport ' + (''.join(random.choice(letters) for i in range(10))) + '\n\n', 
      'notebook': {
        'name': 'NotebookA.ipynb', 
        'path': 'NotebookA.ipynb', 
        'last_modified': '2021-01-28 16:32:39.320000+00:00', 
        'created': '2021-01-28 16:32:39.320000+00:00', 
        'content': None, 
        'format': None, 
        'mimetype': None, 
        'size': 715, 
        'writable': True, 
        'type': 'notebook'
      }
    });
    assert response.status_code == 200;

if __name__ == "__main__":
  unittest.main();
