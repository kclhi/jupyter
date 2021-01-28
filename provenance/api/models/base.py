from pony import orm

db = orm.Database();

class Mapping(db.Entity):
    var = orm.Required(str);
    regex = orm.Required(str);
    ivar = orm.Required(bool);
    match_action = orm.Optional("MatchAction");

class MatchAction(db.Entity):
    action = orm.Required(str);
    value = orm.Required(str);
    mapping = orm.Required("Mapping");