import pandas as pd
from sqlalchemy import create_engine


class Load:
    """ Save data to csv"""
    @staticmethod
    def to_csv(df, file_path):
        df.to_csv(file_path, index=False)

    """ Save data to excel"""
    @staticmethod
    def to_excel(df, file_path):
        df.to_excel(file_path, index=False)

    
    """ Load data to postgresql"""
    @staticmethod
    def to_postgres(df, table_name):
        
        try:
            engine = create_engine(f"postgresql://user:password@host:port/database")
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Data was successfully loaded to the db under table with the name {table_name}")
        except Exception as error:
            print("Couldn't load data to DB due to error: ", type(error).__name__, "-", error)
            

