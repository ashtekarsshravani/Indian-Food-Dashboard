import pandas as pd
import numpy as np

def _clean_name(name):
    ''' A helper function to clean the name of the food
    Args:
        name (str): The name of the food
    Returns:
        str: The cleaned name of the food'''

    name = name.lower()
    name = name.strip()
    return name

def _clean_ingeredient(ingredient):
    ''' A helper function to clean the ingredient of the food
    Args:
        ingredient (str): The ingredient of the food
    Returns:
        set: The cleaned set of ingredients of the food'''

    ingredient = ingredient.lower()
    ingredient = ingredient.split(', ')
    return set(ingredient)

def clean_df(df):
    ''' A function to clean the food dataframe
    Args:
        df (DataFrame): The dataframe to be cleaned
    Returns:
        DataFrame: The cleaned dataframe'''

    df['name'] = df['name'].apply(_clean_name)
    df['ingredients'] = df['ingredients'].apply(_clean_ingeredient)
    df.replace('-1', np.nan , inplace=True)
    df.replace(-1, np.nan, inplace=True)
    df.dropna(inplace=True)
    return df
