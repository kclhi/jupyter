import unittest
from pony import orm
from api.models.base import db

class PonyTests(unittest.TestCase):

    def test_pony(self):
        
        db.bind(provider='sqlite', filename='../api/mappings.sqlite', create_db=True);
        db.generate_mapping(create_tables=True);
        db.drop_all_tables(with_all_data=True);
        db.create_tables();

        with orm.db_session:
            t = db.Template(name="import", path="templates/import.json");
            tv1 = db.TemplateVariable(name="language", ivar=False, template=t);
            e1 = db.Expression(regex="(from\s+(\S)+\s+)?import\s+([^\s#\\\,]+)\s?", template_variable=tv1);
            e2 = db.Expression(regex="library\(('|\\\"\"|\\\\\")?([^\s,'\"\\\\)]+)", template_variable=tv1);
            ma1 = db.MatchAction(action="text", value="Python", mapping=e1);
            ma2 = db.MatchAction(action="text", value="R", mapping=e2);
            tv2 = db.TemplateVariable(name="library", ivar=True, template=t);
            tv3 = db.TemplateVariable(name="libraryName", ivar=False, template=t);
            e3 = db.Expression(regex="(from\s+(\S)+\s+)?import\s+([^\s#\\\,]+)\s?", template_variable=(tv2, tv3));
            e4 = db.Expression(regex="library\(('|\\\"\"|\\\\\")?([^\s,'\"\\\\)]+)", template_variable=(tv2, tv3));
            ma3 = db.MatchAction(action="extract", value="3", mapping=e3);
            ma4 = db.MatchAction(action="extract", value="2", mapping=e4);
            orm.commit();

            assert [[tv.name for tv in row.template_variable] for row in db.Expression.select()] == [['language'], ['language'], ['libraryName', 'library'], ['libraryName', 'library']];

if __name__ == "__main__":
    unittest.main()
