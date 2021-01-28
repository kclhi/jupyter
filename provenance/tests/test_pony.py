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
            m1 = db.Mapping(var="language", regex="(from\s+(\S)+\s+)?import\s+([^\s#\\\,]+)\s?", ivar=False);
            m2 = db.Mapping(var="language", regex="library\(('|\\\"\"|\\\\\")?([^\s,'\"\\\\)]+)", ivar=False);
            ma1 = db.MatchAction(action="text", value="Python", mapping=m1);
            ma2 = db.MatchAction(action="text", value="R", mapping=m2);
            m3 = db.Mapping(var="library", regex="(from\s+(\S)+\s+)?import\s+([^\s#\\\,]+)\s?", ivar=False);
            m4 = db.Mapping(var="library", regex="library\(('|\\\"\"|\\\\\")?([^\s,'\"\\\\)]+)", ivar=False);
            ma3 = db.MatchAction(action="extract", value="3", mapping=m3);
            ma4 = db.MatchAction(action="extract", value="2", mapping=m4);
            orm.commit();

            assert [row.var for row in db.Mapping.select()] == ['language', 'language', 'library', 'library'];

if __name__ == "__main__":
    unittest.main()
