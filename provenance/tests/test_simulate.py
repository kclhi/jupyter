import os, unittest, git, json, configparser
from pony import orm
from api.models.base import db
from starlette.testclient import TestClient
from api import routes
from tests.fixtures import db_fixtures
import settings

class SimulationTest(unittest.TestCase):

    def setUp(self):
        db.provider = db.schema = None;
        db.bind(provider='sqlite', filename='../api/mappings.sqlite', create_db=True);
        db.generate_mapping(create_tables=True);
        db.drop_all_tables(with_all_data=True);
        db.create_tables();
        db_fixtures.db_imported();
        db_fixtures.db_called();

    def test_simulation(self):
        repo = "/home/martin/covid-1";
        repository = git.Repo(repo);
        repository.remotes.cleaned.pull();
        commits = len(list(repository.iter_commits("HEAD")));
        config = configparser.ConfigParser();
        
        if 'PY_ENV' in os.environ and os.environ['PY_ENV']=="production": config.read('config/config.prod.ini');
        else: config.read('config/config.dev.ini');

        dir_of_interest = config.get('SIMULATION', 'RESEARCHERS', vars=os.environ).split(",");
        client = TestClient(routes.app);

        for commit in range(commits-1, 1, -1):
            print(str(commit))
            repository.remotes.cleaned.pull();
            repository.head.reset('HEAD~' + str(commit), index=True, working_tree=True);
            for dir in dir_of_interest:
                for file in os.listdir(repo + "/" + dir):
                    if file.endswith(".ipynb"):
                        with open(os.path.join(repo + "/" + dir, file)) as ipynb:
                            response = client.post('/add', json={
                                'user': dir, 
                                'code': '\n'.join([''.join(cell["source"]) for cell in json.load(ipynb)["cells"]]),
                                'notebook': {
                                    'name': file, 
                                    'path': file, 
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