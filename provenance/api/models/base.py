from pony import orm

db = orm.Database();

class Template(db.Entity):
  name = orm.Required(str);
  path = orm.Required(str);
  template_variable = orm.Set("TemplateVariable");

class TemplateVariable(db.Entity):
  name = orm.Required(str);
  template = orm.Required("Template");
  expression = orm.Set("Expression");

class Expression(db.Entity):
  regex = orm.Required(str);
  template_variable = orm.Set("TemplateVariable");    
  match_action = orm.Optional("MatchAction");

class MatchAction(db.Entity):
  action = orm.Required(str);
  value = orm.Required(str);
  mapping = orm.Required("Expression");