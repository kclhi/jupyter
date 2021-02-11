import unittest, os, git, random, string
from pony import orm
from api.models.base import db
from starlette.testclient import TestClient
from api import routes

class BasicTestImport(unittest.TestCase):

    def setUp(self):
        db.provider = db.schema = None;
        db.bind(provider='sqlite', filename='../api/mappings.sqlite', create_db=True);
        db.generate_mapping(create_tables=True);
        db.drop_all_tables(with_all_data=True);
        db.create_tables();
        with orm.db_session:
            t = db.Template(name="imported2", path="templates/imported2.json");
            tv1 = db.TemplateVariable(name="language", template=t);
            e1 = db.Expression(regex="(from\s+(\S)+\s+)?import\s+([^\s#\\\,]+)\s?", template_variable=tv1);
            e2 = db.Expression(regex="library\(('|\\\"\"|\\\\\")?([^\s,'\"\\\\)]+)", template_variable=tv1);
            ma1 = db.MatchAction(action="text", value="Python", mapping=e1);
            ma2 = db.MatchAction(action="text", value="R", mapping=e2);
            tv2 = db.TemplateVariable(name="library", template=t);
            tv3 = db.TemplateVariable(name="libraryName", template=t);
            e3 = db.Expression(regex="(from\s+(\S)+\s+)?import\s+([^\s#\\\,]+)\s?", template_variable=(tv2, tv3));
            e4 = db.Expression(regex="library\(('|\\\"\"|\\\\\")?([^\s,'\"\\\\)]+)", template_variable=(tv2, tv3));
            ma3 = db.MatchAction(action="extract", value="3", mapping=e3);
            ma4 = db.MatchAction(action="extract", value="2", mapping=e4);
            orm.commit();
        
    def test_db(self):
        with orm.db_session:
            assert [sorted([tv.name for tv in row.template_variable]) for row in db.Expression.select()] == [['language'], ['language'], ['libraryName', 'library'], ['libraryName', 'library']];
            
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
