from sklearn.model_selection import train_test_split, GroupShuffleSplit
import numpy as np
import pandas as pd

def test_split():
    X, y = np.arange(10).reshape((5, 2)), range(5)
    X = np.concatenate((X, X), axis=0)
    y = np.concatenate((y, y), axis=0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
    # CAUTION: LEAKAGE!
    print(X_train)
    print(X_test)

def test_gss():
    X, y = np.arange(10).reshape((5, 2)), range(5)
    X = np.concatenate((X, X), axis=0)
    y = np.concatenate((y, y), axis=0)
    df = pd.DataFrame(X)
    df['target'] = y

    # Create a group identifier for each unique feature combination
    df['group'] = df.drop('target', axis=1).apply(tuple, axis=1).astype(str)

    # Use GroupShuffleSplit to ensure samples with same features stay in same split
    gss = GroupShuffleSplit(n_splits=1, test_size=0.33, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups=df['group']))

    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = np.array(y)[train_idx], np.array(y)[test_idx]
    print(X_train)
    print(X_test)
    print(df['group'])