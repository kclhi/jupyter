import configparser, os, uuid, json
from datetime import datetime
import pgt 

def get_variables(dictionary, variables={}): 
    for key, value in dictionary.items(): 
        if isinstance(value, dict): 
            get_variables(value, variables);
        else:
            variable = key if "var" in key else value;
            if "var:" in variable: variables[variable.split(":")[1]] = variable.split(":")[0];
    return variables

def is_ivar(template, variable):
    with open("templates/" + template + ".json") as template_file: return get_variables(json.load(template_file))[variable]=="var";

def complete_substitution(template, variables):
    with open("templates/" + template + ".json") as template_file:
        template_content = json.load(template_file);
        variables.sort();
        template_variables = list(get_variables(template_content, {}).keys());
        template_variables.sort();
        return variables == template_variables;

def get_zones(dictionary, zones={}, parent=None, parent_var=None):
    for key, value in dictionary.items(): 
        if isinstance(value, dict): 
            if "var:" in key: parent_var=key.split(":")[1];
            get_zones(value, zones, key, parent_var);
        else:
            if parent_var and parent=="zone:id" and key=="$": 
                zones[parent_var] = value;
                parent_var=None;

    return zones;

def get_zone(template, variable):
    with open("templates/" + template + ".json") as template_file:
        template_json = json.load(template_file);
        zones = get_zones(template_json);
        if is_ivar(template, variable): 
            return zones[variable] if variable in zones.keys() else None;
        else:
            # Return 'parent' ivar's zone
            vvar_ivar = get_vvar_ivar(template_json);
            return zones[vvar_ivar[variable]] if variable in vvar_ivar.keys() and vvar_ivar[variable] in zones.keys() else None;

def get_vvar_ivar(dictionary, relations={}, parent_var=None):
    for key, value in dictionary.items(): 
        if isinstance(value, dict): 
            if "var:" in key: parent_var=key.split(":")[1];
            get_vvar_ivar(value, relations, parent_var);
        else:
            if parent_var and "vvar:" in value: 
                relations[value.split(":")[1]] = parent_var;
                parent_var=None;
    return relations;

def is_part_of_zone(template, variable):
    with open("templates/" + template + ".json") as template_file:
        template_json = json.load(template_file);
        zones = get_zones(template_json);
        # if is ivar and in zone, or is in zone because variable of ivar.
        if is_ivar(template, variable): 
            return variable in zones.keys();
        else:
            return get_vvar_ivar(template_json)[variable] in zones.keys();

def create_substitutions(name, domain, fixed_values, variable_values):

    config = configparser.ConfigParser();

    if 'PY_ENV' in os.environ and os.environ['PY_ENV']=="production":
        config.read('config/config.prod.ini');
    else:
        config.read('config/config.dev.ini');

    client = pgt.RabbitClient(config.get('RABBIT', 'HOST', vars=os.environ), 5672, 'flopsy', 'password', 'pgt')

    template_substitutions = [];
    for template in set(list(fixed_values["templates"].keys()) + list(variable_values["templates"].keys())):
        fixed_variables = [variable["name"] for variable in fixed_values["templates"][template]] if template in fixed_values["templates"] else [];
        variable_variables = [variable["name"] for variable in variable_values["templates"][template][0]] if template in variable_values["templates"] else [];
        complete = complete_substitution(template, list(set(fixed_variables + variable_variables)));
        if complete: template_substitutions.append(template);

    for template in template_substitutions:

        # set up document
        with open("templates/" + template + ".json") as fh:
            t = fh.read()
        client.new_template(template, t)

        client.new(name, 'http://' + name + '.kcl.ac.uk')
        client.namespace(name, domain, 'http://' + name + '.kcl.ac.uk/' + domain)
        client.register_template(name, template)
        
        s = pgt.Substitution()

        if fixed_values["templates"][template]:
            # instantiate non-variable information
            for substitution_variable in fixed_values["templates"][template]:
                if template in variable_values["templates"].keys() and is_part_of_zone(template, substitution_variable["name"]):
                    # To add fixed zone information add to existing zone information derived from regex.
                    [substitution.append(substitution_variable) for substitution in variable_values["templates"][template]];
                    continue;
                s.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if is_ivar(template, substitution_variable['name']) else s.add_vvar(substitution_variable['name'], substitution_variable['value']);

        if template in variable_values["templates"].keys():
            # instantiate first new variable action
            for substitution_variable in variable_values["templates"][template][0]:
                s.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if is_ivar(template, substitution_variable['name']) else s.add_vvar(substitution_variable['name'], substitution_variable['value']);

        f_id = str(uuid.uuid1());
        client.geninit(name, template, f_id, s.to_json())

        if template in variable_values["templates"].keys():
            # instantiate remaining new substitutions as zones
            for substitution in variable_values["templates"][template][1:]:
                
                z = pgt.Substitution();
                # assume all variable values in a zone, and same zone
                zone_id = get_zone(template, substitution[0]['name']);
                for substitution_variable in substitution:
                    z.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if is_ivar(template, substitution_variable['name']) else z.add_vvar(substitution_variable['name'], substitution_variable['value']);

                client.genzone(name, template, f_id, zone_id, z.to_json())

        client.genfinal(name, template, f_id)
