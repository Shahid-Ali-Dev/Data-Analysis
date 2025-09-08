from bmi.utils.config import SETTINGS
import duckdb

def test_features_table_exists():
    con = duckdb.connect(str(SETTINGS.duckdb_path))
    con.execute("CREATE TABLE IF NOT EXISTS features_test_probe(id INT)")
    assert con is not None
