import pandas as pd

class Transformer:
    """
    data transformation by dropping nulls, dropping unnecessary columns, renaming columns
    and converting to the right data type
    """
    
    """drop rows with null values"""
    @staticmethod
    def drop_nulls(df):
        return df.dropna()

    """drop specific columns"""
    @staticmethod
    def drop_columns(df, columns_to_drop):
        return df.drop(columns=columns_to_drop)
        
    """rename columns"""
    @staticmethod
    def rename_columns(df, rename_columns):
        return df.rename(columns=rename_columns)
    
    """fill null values"""
    @staticmethod
    def fill_nulls(df, value):
        return df.fillna(value)
    
    """change to a specific data type"""
    @staticmethod
    def to_data_type(df, column_dtype):
        return df.astype(column_dtype)
    