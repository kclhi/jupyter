import configparser, os, uuid, unittest, random, string
from datetime import datetime
import pgt 

class TemplateTests(unittest.TestCase):

    def test_template(self):

        letters = string.ascii_lowercase;

        config = configparser.ConfigParser();

        if 'PY_ENV' in os.environ and os.environ['PY_ENV']=="production":
            config.read('config/config.prod.ini');
        else:
            config.read('config/config.dev.ini');

        client = pgt.RabbitClient(config.get('RABBIT', 'HOST', vars=os.environ), 5672, 'flopsy', 'password', 'pgt')

        # set up document
        with open("templates/import.json") as fh:
            t = fh.read()
        client.new_template('imported', t)

        client.new('covid', 'http://covid.kcl.ac.uk')
        client.namespace('covid', 'pandas', 'http://covid.kcl.ac.uk/pandas')
        client.register_template('covid', 'imported')

        language = (''.join(random.choice(letters) for i in range(10)));
        library = (''.join(random.choice(letters) for i in range(10)));
        filename = "Notebook.pynb";
        author = "martin"; 
        time = "2021-02-01T02:07:41.969622";
        sha = "DEF";
        previous_sha = "ABC";

        s = pgt.Substitution()

        nb_id1 = filename + "_" + previous_sha

        s.add_ivar('notebookBefore', pgt.QualifiedName('', nb_id1))

        nb_id2 = filename + '_' + sha
        s.add_ivar('notebookAfter', pgt.QualifiedName('', nb_id2))
        s.add_vvar('filename', filename)
        s.add_vvar('commit', sha)

        a_id = filename + '_' + str(uuid.uuid1())
        s.add_ivar('imported', pgt.QualifiedName('', a_id))
        s.add_vvar('time', datetime.fromisoformat(time))

        s.add_ivar('author', pgt.QualifiedName('', author))

        s.add_ivar('library', pgt.QualifiedName('', library))
        s.add_vvar('libraryName', library)
        s.add_vvar('language', language)

        f_id = filename + '_' + sha
        client.geninit('covid', 'imported', f_id, s.to_json())

        language = (''.join(random.choice(letters) for i in range(10)));
        library = (''.join(random.choice(letters) for i in range(10)));

        z = pgt.Substitution()

        a_id = filename + '_' + str(uuid.uuid1())
        z.add_ivar('imported', pgt.QualifiedName('', a_id))
        z.add_vvar('time', datetime.fromisoformat(time))

        z.add_ivar('library', pgt.QualifiedName('', library))
        z.add_vvar('libraryName', library)
        z.add_vvar('language', language)

        client.genzone('covid', 'imported', f_id, 'import', z.to_json())

        client.genfinal('covid', 'imported', f_id)

if __name__ == "__main__":
    unittest.main();