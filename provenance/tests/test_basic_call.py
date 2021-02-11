import unittest, os, git, random, string
from pony import orm
from starlette.testclient import TestClient
from api import routes
from api.models.base import db

class BasicTestCall(unittest.TestCase):

    def setUp(self):
        db.provider = db.schema = None;
        db.bind(provider='sqlite', filename='../api/mappings.sqlite', create_db=True);
        db.generate_mapping(create_tables=True);
        db.drop_all_tables(with_all_data=True);
        db.create_tables();
        with orm.db_session:
            t = db.Template(name="called", path="templates/called.json");
            tv1 = db.TemplateVariable(name="call",template=t);
            tv2 = db.TemplateVariable(name="function", template=t);
            tv3 = db.TemplateVariable(name="object", template=t);
            e1 = db.Expression(regex="([^\.]+)\.([^\)]+)\([^\)]*\)", template_variable=(tv1, tv2));
            e2 = db.Expression(regex="([^\.]+)\.([^\)]+)\([^\)]*\)", template_variable=tv3);
            ma1 = db.MatchAction(action="extract", value="2", mapping=e1);
            ma2 = db.MatchAction(action="extract", value="1", mapping=e2);
            orm.commit();

    def test_called(self):
        with orm.db_session:
            assert [sorted([tv.name for tv in row.template_variable]) for row in db.Expression.select()] == [['call', 'function'], ['object']];
    
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
