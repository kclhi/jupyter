from pony import orm
from api.models.base import db

def db_imported():
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

def db_called():
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


