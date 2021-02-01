import configparser, os, uuid
from datetime import datetime
import pgt 

def create_substitution(variable_substitutions):

    config = configparser.ConfigParser();

    if 'PY_ENV' in os.environ and os.environ['PY_ENV']=="production":
        config.read('config/config.prod.ini');
    else:
        config.read('config/config.dev.ini');

    client = pgt.RabbitClient(config.get('RABBIT', 'HOST', vars=os.environ), 5672, 'flopsy', 'password', 'pgt')

    templates, filename, author, time, sha, previous_sha = variable_substitutions.values()

    for template in templates:

        # set up document
        with open("templates/" + template + ".json") as fh:
            t = fh.read()
        client.new_template(template, t)

        client.new('covid', 'http://covid.kcl.ac.uk')
        client.namespace('covid', 'pandas', 'http://covid.kcl.ac.uk/pandas')
        client.register_template('covid', template)

        # instantiate non-variable information
        s = pgt.Substitution()

        nb_id1 = filename + "_" + previous_sha

        s.add_ivar('notebookBefore', pgt.QualifiedName('', nb_id1))

        nb_id2 = filename + '_' + sha
        s.add_ivar('notebookAfter', pgt.QualifiedName('', nb_id2))
        s.add_vvar('filename', filename)
        s.add_vvar('commit', sha)

        s.add_vvar('time', datetime.fromisoformat(time))

        s.add_ivar('author', pgt.QualifiedName('', author))

        a_id = filename + '_' + str(uuid.uuid1())
        s.add_ivar('imported', pgt.QualifiedName('', a_id))

        # instantiate first new variable action
        for substitution_variable in templates[template][0]:
            s.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if substitution_variable['ivar'] else s.add_vvar(substitution_variable['name'], substitution_variable['value']);

        f_id = filename + '_' + sha
        client.geninit('covid', template, f_id, s.to_json())

        # instantiate remaining new imports
        for substitution in templates[template][1:]:
            
            z = pgt.Substitution()

            a_id = filename + '_' + str(uuid.uuid1())
            z.add_ivar('imported', pgt.QualifiedName('', a_id))
            z.add_vvar('time', datetime.fromisoformat(time))

            for substitution_variable in substitution:
                z.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if substitution_variable['ivar'] else z.add_vvar(substitution_variable['name'], substitution_variable['value']);

            client.genzone('covid', template, f_id, 'import', z.to_json())

        client.genfinal('covid', template, f_id)
