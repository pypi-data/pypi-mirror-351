
from .base import validate_dataframe_columns

import pandas as pd
import typing as t
import time

from ..pandas_columns import *
from ..constants import FlagLevels

import logging
logger = logging.getLogger(__name__)


#################################### checkers ####################################################
def check_company_inputs(name: str, dataset_type: str, description: str, min_date: pd.Timestamp, max_date: pd.Timestamp) -> None:

    if not isinstance(name, str):
        raise ValueError("Company name must be a string.")
    if not isinstance(dataset_type, str):
        raise ValueError("Dataset type must be a string.")
    if not isinstance(description, str):
        raise ValueError("Description must be a string.")
    if not isinstance(min_date, pd.Timestamp):
        raise ValueError("Min date must be a pandas Timestamp.")
    if not isinstance(max_date, pd.Timestamp):
        raise ValueError("Max date must be a pandas Timestamp.")
    
def clean_and_check_store_region_map(store_region_map: pd.DataFrame, copy: bool = False) -> pd.DataFrame:

    if copy:
        store_region_map = store_region_map.copy()

    expected_base_columns = [
        StoresColumns.STORE.value,
        StoresColumns.COUNTRY.value,
    ]

    num_columns = len(store_region_map.columns)
    if num_columns == 2:
        expected_types = StoresColumns._TYPES.value[:2]
        store_region_map = validate_dataframe_columns(store_region_map, expected_base_columns, expected_types, "Store Region Map")

    elif num_columns == 3:
        for column in store_region_map.columns:
            if column in ["store", "country"]:
                continue
            else:
                region_type = column
                break
                # check that the region type is supported
        if region_type not in StoresColumns.ADDITIONAL_COLUMNS.value:
            raise ValueError(f"Region type {region_type} is not supported. Supported types are: {StoresColumns.ADDITIONAL_COLUMNS.value}")
        expected_columns = expected_base_columns + [region_type]
        expected_types = StoresColumns._TYPES.value[:3]
        store_region_map = validate_dataframe_columns(store_region_map, expected_columns, expected_types, "Store Region Map")
    
    else:
        raise ValueError(f"Expected 2 or 3 columns for store-region map, found {num_columns} columns: {store_region_map.columns}")

    return store_region_map



def clean_and_check_categories_level_description(categories_level_description: pd.DataFrame, copy: bool = False) -> pd.DataFrame:
    if copy:
        categories_level_description = categories_level_description.copy()
    
    expected_columns = [col.value for col in list(CategoriesLevelColumns)[:-1]]
    expected_types = CategoriesLevelColumns._TYPES.value
    categories_level_description = validate_dataframe_columns(categories_level_description, expected_columns, expected_types, "Category level descriptions")

    # convert level to int
    categories_level_description[CategoriesLevelColumns.LEVEL.value] = categories_level_description[CategoriesLevelColumns.LEVEL.value].astype(int)
    
    return categories_level_description


def clean_and_check_categories_dict(categories_dict: t.Dict, copy=False) -> t.Dict:

    if copy:
        categories_dict = categories_dict.copy()

    categories_dict = {int(key): value for key, value in categories_dict.items()}

    # Check if the keys are a range from 0 to n-1 without gaps
    if set(categories_dict.keys()) != set(range(0, len(categories_dict))):
        keys = sorted(categories_dict.keys())
        raise ValueError("The keys of the categories dictionary must be a range from 0 to n-1 without gaps, got: {}".format(keys))

    return categories_dict

def clean_and_check_products(products: pd.DataFrame, copy: bool = False) -> pd.DataFrame:

    if copy:
        products = products.copy()

    expected_columns = [col.value for col in list(ProductsColumns)[:-1]]
    expected_types = ProductsColumns._TYPES.value
    products = validate_dataframe_columns(products, expected_columns, expected_types, "Products")

    return products

def clean_and_check_flags(flags: pd.DataFrame, copy: bool = False) -> pd.DataFrame:
    if copy:
        flags = flags.copy()

    expected_columns = [col.value for col in list(FlagsColumns)[:-1]]
    expected_types = FlagsColumns._TYPES.value
    flags = validate_dataframe_columns(flags, expected_columns, expected_types, "Flags")

    allowed_flag_levels = [level.value for level in FlagLevels]

    invalid_flags = flags[~flags["flag"].isin(allowed_flag_levels)]

    if not invalid_flags.empty:
        raise ValueError(
            f"Invalid flag_level(s) found: {invalid_flags['flag'].unique().tolist()}. "
            f"Allowed values are: {allowed_flag_levels}"
        )

    return flags

def clean_and_check_time_sku_feature_description_map(time_sku_feature_description_map: pd.DataFrame, copy: bool = False) -> pd.DataFrame:

    if copy:
        time_sku_feature_description_map = time_sku_feature_description_map.copy()

    if not time_sku_feature_description_map["name"].str.islower().all():
        invalid_names = time_sku_feature_description_map.loc[
            ~time_sku_feature_description_map["name"].str.islower(), "name"
        ]
        raise ValueError(f"All entries in column 'name' must be lowercase, got: {invalid_names.tolist()}")

    expected_columns = [col.value for col in list(FeatureDescriptionsColumns)[:-1]]
    expected_types = FeatureDescriptionsColumns._TYPES.value

    time_sku_feature_description_map = validate_dataframe_columns(time_sku_feature_description_map, expected_columns, expected_types, "Time SKU Feature Description Map")
    
    return time_sku_feature_description_map

def clean_and_check_time_sku_data(time_sku_data: pd.DataFrame, copy: bool = False) -> pd.DataFrame:

    if copy:
        time_sku_data = time_sku_data.copy()

    expected_columns = [col.value for col in list(TimeSkuColumns)[:-1]]
    expected_types = TimeSkuColumns._TYPES.value
    time_sku_data = validate_dataframe_columns(time_sku_data, expected_columns, expected_types, "Time SKU Data", allow_additional=True)

    return time_sku_data

def validate_feature_mapping(feature_description_map: pd.DataFrame, feature_data: pd.DataFrame):
    # Check if all features in df2 exist in df1
    features_in_data = set(feature_data['feature'].unique())
    features_in_description = set(feature_description_map['name'].unique())

    # Check for undefined features
    undefined_features = features_in_data - features_in_description
    if undefined_features:
        raise ValueError(f"The following features are not defined in feature_description_map: {', '.join(undefined_features)}")

    # Check for features with no data
    unused_features = features_in_description - features_in_data
    for feature in unused_features:
        logger.warning(f"Feature '{feature}' is defined under feature descriptions, but no data provided in feature_data.")

def clean_and_check_feature_description_map(feature_description_map: pd.DataFrame, feature_data: pd.DataFrame, copy: bool = False) -> pd.DataFrame:

    if copy:
        feature_description_map = feature_description_map.copy()

    validate_feature_mapping(feature_description_map, feature_data)
    
    expected_columns = [col.value for col in list(FeatureDescriptionsColumns)[:-1]]
    expected_types = FeatureDescriptionsColumns._TYPES.value

    feature_description_map = validate_dataframe_columns(feature_description_map, expected_columns, expected_types, "Feature Description Map")
    
    return feature_description_map

def clean_and_check_store_feature_data(store_feature_data: pd.DataFrame, copy: bool = False) -> pd.DataFrame:
    
    if copy:
        store_feature_data = store_feature_data.copy()

    expected_columns = [col.value for col in list(StoreFeatureColumns)[:-1]]
    expected_types = StoreFeatureColumns._TYPES.value

    store_feature_data = validate_dataframe_columns(store_feature_data, expected_columns, expected_types, "Store Feature Data")

    return store_feature_data

def clean_and_check_sku_feature_data(sku_feature_data: pd.DataFrame, copy: bool = False) -> pd.DataFrame:
    
    if copy:
        sku_feature_data = sku_feature_data.copy()

    expected_columns = [col.value for col in list(SKUFeatureColumns)[:-1]]
    expected_types = SKUFeatureColumns._TYPES.value

    sku_feature_data = validate_dataframe_columns(sku_feature_data, expected_columns, expected_types, "SKU Feature Data")

    return sku_feature_data

def clean_and_check_product_feature_data(product_feature_data: pd.DataFrame, copy: bool = False) -> pd.DataFrame:

    if copy:
        product_feature_data = product_feature_data.copy()

    expected_columns = [col.value for col in list(ProductFeatureColumns)[:-1]]
    expected_types = ProductFeatureColumns._TYPES.value

    product_feature_data = validate_dataframe_columns(product_feature_data, expected_columns, expected_types, "Product Feature Data")

    return product_feature_data

def clean_and_check_time_product_feature_data(time_product_feature_data: pd.DataFrame, copy: bool = False) -> pd.DataFrame:
        
    if copy:
        time_product_feature_data = time_product_feature_data.copy()

    expected_columns = [col.value for col in list(TimeProductFeatureColumns)[:-1]]
    expected_types = TimeProductFeatureColumns._TYPES.value

    time_product_feature_data = validate_dataframe_columns(time_product_feature_data, expected_columns, expected_types, "Time Product Feature Data")

    return time_product_feature_data


def clean_and_check_time_region_feature_data(time_region_feature_data: pd.DataFrame, copy: bool = False) -> pd.DataFrame:

    if copy:
        time_region_feature_data = time_region_feature_data.copy()
    
    expected_base_columns = [
        TimeRegionFeatureColumns.DATE.value,
        TimeRegionFeatureColumns.COUNTRY.value,
        TimeRegionFeatureColumns.FEATURE.value,
        TimeRegionFeatureColumns.VALUE.value
    ]

    num_columns = len(time_region_feature_data.columns)
    if num_columns == 4:
        expected_types = TimeRegionFeatureColumns._TYPES.value[:4]
        time_region_feature_data = validate_dataframe_columns(time_region_feature_data, expected_base_columns, expected_types, "Time Region Feature Data")
    elif num_columns == 5:
        for column in time_region_feature_data.columns:
            if column in ["date", "country", "feature", "value"]:
                continue
            else:
                region_type = column
                break
                # check that the region type is supported
        if region_type not in TimeRegionFeatureColumns.ADDITIONAL_COLUMNS.value:
            raise ValueError(f"Region type {region_type} is not supported. Supported types are: {TimeRegionFeatureColumns.ADDITIONAL_COLUMNS.value}")
        expected_columns = expected_base_columns + [region_type]
        expected_types = TimeRegionFeatureColumns._TYPES.value[:5]
        time_region_feature_data = validate_dataframe_columns(time_region_feature_data, expected_columns, expected_types, "Time Region Feature Data", allow_additional=True)

    else:
        raise ValueError(f"Expected 4 or 5 columns for time region feature data, found {num_columns} columns: {time_region_feature_data.columns}")

    return time_region_feature_data


def clean_and_check_time_store_feature_data(time_store_feature_data: pd.DataFrame, copy: bool = False) -> pd.DataFrame:

    if copy:
        time_store_feature_data = time_store_feature_data.copy()

    expected_columns = [col.value for col in list(TimeStoreFeatureColumns)[:-1]]
    expected_types = TimeStoreFeatureColumns._TYPES.value

    time_store_feature_data = validate_dataframe_columns(time_store_feature_data, expected_columns, expected_types, "Time Store Feature Data")

    return time_store_feature_data