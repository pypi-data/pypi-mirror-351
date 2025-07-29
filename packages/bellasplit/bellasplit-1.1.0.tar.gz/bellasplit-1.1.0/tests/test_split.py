import sqlite3

from bellameta import types as t

from bellasplit.types import Splitname
from bellasplit.base_split import Split, SplitWriter, DataItem, DataItems

def test_data_source(data):
    assert set(data.labels).issubset(set([t.Subtype.DLBCL.to_string(), t.Subtype.FL.to_string()]))

def test_split():
    patient_1 = [DataItem(c, '1', 'DLBCL') for c in ['A', 'B', 'C', 'D']]
    patient_2 = [DataItem(c, '2', 'DLBCL') for c in ['E', 'F', 'G', 'H']]
    patient_3 = [DataItem(c, '3', 'FL') for c in ['I', 'J', 'K', 'L']]
    source_data = DataItems(patient_1 + patient_2 + patient_3)
    split = Split(source_data, Splitname.from_int(0), test_size = 0.3, val_size=0.5)
    assert set(split.test.patients).isdisjoint(set(split.val.patients))
    assert set(split.test.patients).isdisjoint(set(split.train.patients))
    assert set(split.train.patients).isdisjoint(set(split.val.patients))

def test_write(db, split):
    writer = SplitWriter(db=db, split=split)
    writer.write(verbose=True)
    assert set(split.source_data.hashes) == set(check_entries(db))


def check_entries(db):
    with sqlite3.connect(db.sqlite_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM split")
        data = cursor.fetchall()
        data = [d[0] for d in data]
    return data
