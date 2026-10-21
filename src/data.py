"""Loading and preprocessing for the UNSW-NB15 dataset."""

import os

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
TARGET = 'attack_cat'
NOMINAL_COLS = ['proto', 'service', 'state']
KAGGLE_DATASET = 'dhoogla/unswnb15'


def load_unsw_nb15():
    """Download (cached) UNSW-NB15 from Kaggle and return the combined train+test records."""
    import kagglehub

    path = kagglehub.dataset_download(KAGGLE_DATASET)
    train_df = pd.read_parquet(os.path.join(path, 'UNSW_NB15_training-set.parquet'))
    test_df = pd.read_parquet(os.path.join(path, 'UNSW_NB15_testing-set.parquet'))

    df = pd.concat([train_df, test_df], ignore_index=True)
    df.columns = df.columns.str.strip().str.lower()
    df[TARGET] = df[TARGET].astype(str).str.strip().astype(object)
    return df


def numeric_feature_columns(df):
    return [
        c for c in df.columns
        if c not in NOMINAL_COLS + [TARGET, 'label', 'id']
        and pd.api.types.is_numeric_dtype(df[c])
    ]


def encode_features(df):
    """Impute missing values and one-hot encode the nominal columns.

    Returns the encoded feature matrix (float32 DataFrame) and the target Series.
    """
    drop_cols = [c for c in ['id', 'label', TARGET] if c in df.columns]
    X = df.drop(columns=drop_cols).copy()
    y = df[TARGET].astype(object).copy()

    for col in X.select_dtypes(include=[np.number]).columns:
        if X[col].isna().any():
            X[col] = X[col].fillna(X[col].median())

    ohe_cols = [c for c in NOMINAL_COLS if c in X.columns]
    for col in ohe_cols:
        X[col] = X[col].astype(str)
        if X[col].isna().any():
            X[col] = X[col].fillna(X[col].mode()[0])

    X = pd.get_dummies(X, columns=ohe_cols, drop_first=False)
    return X.astype(np.float32), y


def split_and_scale(X, y, test_size=0.2, random_state=RANDOM_STATE):
    """Stratified train/test split, then standardize with statistics from the training set only."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train).astype(np.float32)
    X_test_s = scaler.transform(X_test).astype(np.float32)
    return X_train_s, X_test_s, y_train.reset_index(drop=True), y_test.reset_index(drop=True), scaler
