from typing import List, Tuple, Type
import numpy as np
import time
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from pamly import Stain
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import pandas as pd


from bellameta.utils import sqlite_connection
from bellameta.types import Task, Cohort, BellametaType

from bellasplit.types import Mode, Splitname
from bellasplit.filter import Filter
from bellasplit.database import Db
from bellasplit.utils import validate_table_names


@dataclass
class DataItem:
    '''
    Class holding source data for split for a single case
    '''

    hash: str
    patient: str
    label: str

@dataclass
class DataItems:
    '''
    Collection of DataItem
    '''

    items: List[DataItem]
    hashes: List[str] = field(init=False)
    patients: List[str] = field(init=False)
    labels: List[str] = field(init=False)

    def __post_init__(self):
        self.hashes = self.get_hashes()
        self.patients = self.get_patients()
        self.labels = self.get_labels()
    
    def __iter__(self):
        for item in self.items:
            yield item
    
    def __len__(self):
        return len(self.items)
    
    def __str__(self):
        df = self.to_df()
        return df.to_string(index=False)
    
    def to_df(self):
        triples = self.to_list()
        df = pd.DataFrame(triples, columns=['hash', 'patient', 'label'])
        return df

    def to_list(self):
        return [(item.hash, item.patient, item.label) for item in self.items]
    
    @classmethod
    def from_numpy(cls, array: np.ndarray):
        l = array.tolist()
        items = []
        for item in l:
            items.append(DataItem(hash=item[0], patient=item[1], label=item[2]))
        return DataItems(items=items)


    def get_hashes(self):
        return [item.hash for item in self.items]
    def get_patients(self):
        return [item.patient for item in self.items]
    def get_labels(self):
        return [item.label for item in self.items]



class DataSource(ABC):
    '''
    Interface for fetching data to be split

    Attributes
    ----------
    db: Db
        Database holding scans and metadata
    task: Type[Task]
       A digital pathology task like e.g. subtyping, for available tasks see Task.list() or .yaml config

    Methods
    -------
    get_data:
        The main function that needs to be implemented by a child class in order to compose splits

    '''

    def __init__(self,
                 db: Db,
                 task: Type[Task]): 
        self.db = db
        self.sqlite_path = self.db.sqlite_path
        self.task = task
        self.label_table = task.to_label_table_name()
    
    @abstractmethod
    def get_data(self) -> DataItems:
        '''
        The main function that needs to be implemented by a child class in order to compose splits.

        Returns
        ------
        DataItems
            The fetched data
        '''
        pass

    @sqlite_connection
    def filter(self, cursor, **kwargs) -> DataItems:
        '''
        Filter the database for matching metadata values.

        The user can specify any valid table name as **kwargs in order to filter for matching entries.
        
        Parameters
        -----------
        **kwargs : 
            A valid table name, i.e. in bellameta.constants.METADATA_TABLES or the kwarg `class`
            which provides class lables to be filtered by.
            The values can be lists or single elements.
        
        Returns
        --------
        DataItems
            A collection of DataItem satisfying the conditions specified via **kwargs
        '''

        # add task to the kwargs in order to be filtered
        kwargs['task'] = self.task

        base_statement = f"SELECT storage.hash, patient.value, {self.label_table}.value FROM storage "
        
        # dynamically concatenate the sqlite statement based on **kwargs
        join_statements = []
        where_statements = []
        constraints = []
        if 'class' in kwargs.keys():
            # rename class key to the correct label table name
            kwargs[self.label_table] = kwargs.pop('class')
        else:
            join_statements.append(
                f"INNER JOIN {self.label_table} ON storage.hash = {self.label_table}.hash "   
            )
        for key, value in kwargs.items():
            fl = Filter(key, value)
            join_statements.append(
                f"INNER JOIN {fl.table} ON storage.hash = {fl.table}.hash "
            )            
            where_statements.append(
                f"{fl.table}.value IN ({fl.placeholder}) "
            )
            constraints.extend(fl.values)
        join_statements.append(
            f"INNER JOIN patient ON storage.hash = patient.hash "
        )
        where_statement = "AND ".join(where_statements)
        join_statement = " ".join(join_statements)
        final_statement = base_statement + join_statement + "WHERE " + where_statement
        cursor.execute(
            final_statement, constraints
        )
        result = cursor.fetchall()
        data_items = []
        for r in result:
            data_items.append(DataItem(r[0], r[1], r[2]))
        data_items = DataItems(data_items)
        return data_items

@dataclass
class Split:
    '''
    Class holding the split.

    Attributes
    ----------
    source_data: DataSource
        Class implementing the get_data method for fetching the source data
    splitname: Type[Splitname]
        A unique name for the split serving as an identifier in the database
    test_size: float
        Fraction of test split with respect to the whole dataset
    val_size: float
        Fraction of validation split with respect to the training dataset
    train: List[str]
        The training split as list of hashes
    val: List[str]
        The validation split as list of hashes
    test: List[str]
        The test split as list of hashes
    '''
        
    source_data: DataItems
    splitname: Type[Splitname]
    test_size: float
    val_size: float
    train: DataItems = field(init=False)
    val: DataItems = field(init=False)
    test: DataItems = field(init=False)

    def __post_init__(self):
        (x_train, x_val, x_test) = self.get_split()
        self.train = x_train
        self.val = x_val
        self.test = x_test

    
    def get_split(self) -> tuple[DataItems, DataItems, DataItems]:
        '''
        A wrapper around `sklearn.model_selection.train_test_split` in order to split labeled data.

        Returns
        -----------
        tuple[DataItems, DataItems, DataItems]
            Train, val and test split as DataItems
        '''
        df = self.source_data.to_df()
        gss = GroupShuffleSplit(n_splits=1, test_size=self.test_size, random_state=42)
        X = np.array(self.source_data.to_list())
        y = np.array(self.source_data.labels)
        train_idx, test_idx = next(gss.split(X, y, groups=df['patient']))
        X_train, X_test = X[train_idx], X[test_idx]
        y_train = y[train_idx]
        groups_train_val = df['patient'].iloc[train_idx]
        train_idx, val_idx = next(gss.split(X_train, y_train, groups=groups_train_val))
        X_train, X_val = X_train[train_idx], X_train[val_idx]

        return (DataItems.from_numpy(X_train), DataItems.from_numpy(X_val), DataItems.from_numpy(X_test))

class SplitWriter:
    '''
    Class to insert split into database

    Attributes
    ----------
        db: Db
            Database connection
        split: Split
            Split holding train, validation and test set
    
    Methods
    -------
        write:
            Writes split to database
    '''

    def __init__(self,
                 db: Db, 
                 split: Split): 
        
        self.db = db
        self.sqlite_path = self.db.sqlite_path
        self.split = split

    @sqlite_connection
    def write(self, cursor, verbose=False):
        '''
        Writes the split to the database
        '''

        data = self._prepare_insert()
        # check that only valid data is inserted
        filtered_data = [(hash, value, split) for (hash, value, split) in data if value is not None]
        mode_data = [(data[0], data[1], data[2]) for data in filtered_data]
        split_data = [(data[0], data[2]) for data in filtered_data]
        cursor.executemany(
            f"INSERT OR IGNORE INTO mode (hash, value, split) VALUES (?, ?, ?)",
            mode_data
        )
        cursor.executemany(
            f"INSERT OR IGNORE INTO split (hash, value) VALUES (?, ?)",
            split_data
        )
        if verbose:
            print(f'Inserted to {self.sqlite_path}:')
            print('Mode Table:')
            print(pd.DataFrame(mode_data, columns=['Hash', 'Value', 'Split']).to_string(index=False))
            print('Split Table:')
            print(pd.DataFrame(split_data, columns=['Hash', 'Value']).to_string(index=False))


    def _prepare_insert(self):
        '''
        Helper method to prepare data for insertion into the databse.
        Only hashes are written.
        '''

        unix_time = int(time.time())
        data = np.concatenate((
            np.stack((
                self.split.train.hashes,
                np.full(len(self.split.train.hashes), Mode.Train.to_string()),
                np.full(len(self.split.train.hashes), self.split.splitname.to_string())),
            axis = 1),
            np.stack((
                self.split.val.hashes,
                np.full(len(self.split.val.hashes), Mode.Val.to_string()),
                np.full(len(self.split.val.hashes), self.split.splitname.to_string())),
            axis = 1),
            np.stack((
                self.split.test.hashes,
                np.full(len(self.split.test.hashes), Mode.Test.to_string()),
                np.full(len(self.split.test.hashes), self.split.splitname.to_string())),
            axis = 1)
            ))
        return data
    
    @sqlite_connection
    def _drop(self, cursor):
        '''
        Just for development purposes.
        '''
        
        cursor.execute(f"""
            DROP TABLE mode
        """)
        cursor.execute(f"""
            DROP TABLE split
        """)