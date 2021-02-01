import configparser, os, uuid
from datetime import datetime
import pgt 

def create_substitutions(name, domain, fixed_values, variable_values):

    config = configparser.ConfigParser();

    if 'PY_ENV' in os.environ and os.environ['PY_ENV']=="production":
        config.read('config/config.prod.ini');
    else:
        config.read('config/config.dev.ini');

    client = pgt.RabbitClient(config.get('RABBIT', 'HOST', vars=os.environ), 5672, 'flopsy', 'password', 'pgt')

    for template in variable_values["templates"]:

        # set up document
        with open("templates/" + template + ".json") as fh:
            t = fh.read()
        client.new_template(template, t)

        client.new(name, 'http://' + name + '.kcl.ac.uk')
        client.namespace(name, domain, 'http://' + name + '.kcl.ac.uk/' + domain)
        client.register_template(name, template)

        # instantiate non-variable information
        s = pgt.Substitution()

        for substitution_variable in fixed_values[template]:
            if substitution_variable["zone"]:
                # To add fixed zone information add to existing zone information derived from regex.
                [substitution.append(substitution_variable) for substitution in variable_values["templates"][template]];
                continue;
            s.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if substitution_variable['ivar'] else s.add_vvar(substitution_variable['name'], substitution_variable['value']);

        # instantiate first new variable action
        for substitution_variable in variable_values["templates"][template][0]:
            s.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if substitution_variable['ivar'] else s.add_vvar(substitution_variable['name'], substitution_variable['value']);

        f_id = str(uuid.uuid1());
        client.geninit(name, template, f_id, s.to_json())

        # instantiate remaining new substitutions as zones
        for substitution in  variable_values["templates"][template][1:]:
            
            z = pgt.Substitution()

            for substitution_variable in substitution:
                z.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if substitution_variable['ivar'] else z.add_vvar(substitution_variable['name'], substitution_variable['value']);

            client.genzone(name, template, f_id, 'import', z.to_json())

        client.genfinal(name, template, f_id)
