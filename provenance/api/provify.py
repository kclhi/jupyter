import configparser, os, uuid, json
import pgt 

class Provify:

    def __init__(self):
        self.__use_cache = True;
        self.__template_json = {};
        self.__template_vars = {};
        self.__template_zones = {};
        self.__template_vvar_ivar = {};
        
    def get_variables(self, dictionary, variables={}): 
        for key, value in dictionary.items(): 
            if isinstance(value, dict): 
                self.get_variables(value, variables);
            else:
                variable = key if "var" in key else value;
                if "var:" in variable: variables[variable.split(":")[1]] = variable.split(":")[0];
        return variables

    def template_json_cache(self, template):
        if self.__use_cache and template in self.__template_json.keys():
            return self.__template_json[template];
        else:
            with open("templates/" + template + ".json") as template_file:
                template_json = json.load(template_file);
                self.__template_json[template] = template_json;
                return template_json;

    def var_cache(self, template):
        if self.__use_cache and template in self.__template_vars:
            return self.__template_vars[template];
        else:
            variables = self.get_variables(self.template_json_cache(template), {});
            self.__template_vars[template] = variables;
            return variables;

    def is_ivar(self, template, variable):
         return self.var_cache(template)[variable]=="var";

    def complete_substitution(self, template, variables):
        variables.sort();
        template_variables = list(self.var_cache(template).keys());
        template_variables.sort();
        return variables == template_variables;

    def get_vvar_ivar(self, dictionary, relations={}, parent_var=None):
        for key, value in dictionary.items(): 
            if isinstance(value, dict): 
                if "var:" in key: parent_var=key.split(":")[1];
                self.get_vvar_ivar(value, relations, parent_var);
            else:
                if parent_var and "vvar:" in value: 
                    relations[value.split(":")[1]] = parent_var;
                    parent_var=None;
        return relations;

    def vvar_ivar_cache(self, template):
        if self.__use_cache and template in self.__template_vvar_ivar:
            return self.__template_vvar_ivar[template];
        else:
            vvar_ivar = self.get_vvar_ivar(self.template_json_cache(template));
            self.__template_vvar_ivar[template] = vvar_ivar;
            return vvar_ivar;

    def get_zones(self, dictionary, zones={}, parent=None, parent_var=None):
        for key, value in dictionary.items(): 
            if isinstance(value, dict): 
                if "var:" in key: parent_var=key.split(":")[1];
                self.get_zones(value, zones, key, parent_var);
            else:
                if parent_var and parent=="zone:id" and key=="$": 
                    zones[parent_var] = value;
                    parent_var=None;
        return zones;

    def zone_cache(self, template):
        if self.__use_cache and template in self.__template_zones.keys():
            return self.__template_zones[template];
        else:
            zones = self.get_zones(self.template_json_cache(template));
            self.__template_zones[template] = zones;
            return zones;

    def get_zone(self, template, variable):
        zones = self.zone_cache(template);
        if self.is_ivar(template, variable): 
            return zones[variable] if variable in zones.keys() else None;
        else:
            # Return 'parent' ivar's zone
            vvar_ivar = self.vvar_ivar_cache(template);
            return zones[vvar_ivar[variable]] if variable in vvar_ivar.keys() and vvar_ivar[variable] in zones.keys() else None;

    def is_part_of_zone(self, template, variable):
            zones = self.zone_cache(template);
            # if is ivar and in zone, or is in zone because variable of ivar in zone.
            if self.is_ivar(template, variable): 
                return variable in zones.keys();
            else:
                return self.vvar_ivar_cache(template)[variable] in zones.keys();

    def create_substitutions(self, name, domain, fixed_values, variable_values):
        config = configparser.ConfigParser();

        if 'PY_ENV' in os.environ and os.environ['PY_ENV']=="production": config.read('config/config.prod.ini');
        else: config.read('config/config.dev.ini');

        client = pgt.RabbitClient(config.get('RABBIT', 'HOST', vars=os.environ), 5672, 'flopsy', 'password', 'pgt')

        template_substitutions = [];
        for template in set(list(fixed_values["templates"].keys()) + list(variable_values["templates"].keys())):
            fixed_names = [variable["name"] for variable in fixed_values["templates"][template]] if template in fixed_values["templates"] else [];
            variable_names = [variable["name"] for variable in variable_values["templates"][template][0]] if template in variable_values["templates"] else [];
            complete = self.complete_substitution(template, list(set(fixed_names + variable_names)));
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
                    if template in variable_values["templates"].keys() and self.is_part_of_zone(template, substitution_variable["name"]):
                        # To add fixed zone information add to existing zone information derived from regex.
                        [substitution.append(substitution_variable) for substitution in variable_values["templates"][template]];
                        continue;
                    s.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if self.is_ivar(template, substitution_variable['name']) else s.add_vvar(substitution_variable['name'], substitution_variable['value']);

            if template in variable_values["templates"].keys():
                # instantiate first new variable action
                for substitution_variable in variable_values["templates"][template][0]:
                    s.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if self.is_ivar(template, substitution_variable['name']) else s.add_vvar(substitution_variable['name'], substitution_variable['value']);

            f_id = str(uuid.uuid1());
            client.geninit(name, template, f_id, s.to_json())

            if template in variable_values["templates"].keys():
                # instantiate remaining new substitutions as zones
                for substitution in variable_values["templates"][template][1:]:
                    
                    z = pgt.Substitution();
                    # assume all variable values in a zone, and same zone
                    zone_id = self.get_zone(template, substitution[0]['name']);
                    for substitution_variable in substitution:
                        z.add_ivar(substitution_variable['name'], pgt.QualifiedName('', substitution_variable['value'])) if self.is_ivar(template, substitution_variable['name']) else z.add_vvar(substitution_variable['name'], substitution_variable['value']);

                    client.genzone(name, template, f_id, zone_id, z.to_json())
                   
            client.genfinal(name, template, f_id)
