# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for compute.
"""

import json
import logging
import sys
import uuid
import pandas as pd
from typing import List
from datetime import datetime

from .._utils._utils import ApiInputs

from ._models import (CarbonCacheInfo, LocationInfo)
from ._iotservice import PlatformIOTService
from ._commands import (COMMAND_INSTALLATION_LOCATION_DETAIL,
                        COMMAND_CARBON_CALCULATION_EXPRESSION)
from ._utils import safe_uuid

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  %(name)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


class CostCarbonCalculation:
    """A class for computing Cost and Carbon - for now, only Carbon.
    Requires Dataframe in the constructor to prepare required data based on the passing Dataframes.
    """

    def __init__(self, api_inputs: ApiInputs, df: pd.DataFrame):
        self.api_inputs = api_inputs
        self.iot_service = None

        self.df = df
        self.installation_id_list = []
        self.objectproperty_id_list = []
        self.unique_years = []

        self.location_info = None
        self.country_state_holidays = []
        self.carbon_calculations_exp_df = pd.DataFrame()
        self.carbon_calculations_exp: list[CarbonCacheInfo] = []

        self.iot_service = PlatformIOTService()

        self.installation_id_list = self.df['InstallationId'].str.lower(
        ).unique().tolist()
        self.objectproperty_id_list = self.df['ObjectPropertyId'].str.lower(
        ).unique().tolist()
        self.unique_years = self.df['Timestamp'].dt.year.unique().tolist()

        if self.installation_id_list and len(self.installation_id_list) > 0:
            self.location_info = self._get_installation_location()

        # FOR COMPUTE CARBON
        if self.location_info is not None:
            self.carbon_calculations_exp_df = self._get_carbon_calculations_expression()

            if not self.carbon_calculations_exp_df.empty:
                for index, row in self.carbon_calculations_exp_df.iterrows():
                    self.carbon_calculations_exp.append(CarbonCacheInfo(
                        carbon_calculation_region_id=row.get(
                            "CarbonCalculationRegionID", 0),
                        from_date=datetime.strptime(
                            row.get("FromDate"), '%Y-%m-%dT%H:%M:%S'),
                        to_date=datetime.strptime(
                            row.get("ToDate"), '%Y-%m-%dT%H:%M:%S'),
                        country_name=row.get("CountryName", ""),
                        region_name=row.get("RegionName", ""),
                        object_property_id=safe_uuid(
                            row.get("ObjectPropertyID")),
                        object_property_type_id=safe_uuid(
                            row.get("ObjectPropertyTypeID")),
                        object_property_template_id=safe_uuid(
                            row.get("ObjectPropertyTemplateID")),
                        carbon_expression=row.get("CarbonExpression", "")
                    ))
            else:
                logger.info(
                    'There are no Carbon Calculation Expression retrieved.')

    def _get_installation_location(self):
        """Retrieves Installation location details for use in calculating Carbon.
        Returns
        -------
        LocationInfo
            Object containing consolidated installations' location info from the dataframe passed in the class.
        """
        location_info = None
        logger.info('Getting Installation location details.')

        query = COMMAND_INSTALLATION_LOCATION_DETAIL(
            installation_list=self.installation_id_list)
        df, error = self.iot_service.execute_reader(api_inputs=self.api_inputs,
                                                    command=query, nb_retry=3, parameters=[])

        if df is None or len(df) == 0:
            logger.info("No returned Installations' Location from SQL.")
            if error:
                logger.error(f'Error: {error}')
            return None

        if isinstance(df, pd.DataFrame) and not df.empty:
            countries = df['Country'].unique().tolist()
            state_names = df['StateName'].unique().tolist()
            region_names = df['CarbonCalculationRegionName'].unique().tolist()

            location_info = LocationInfo(
                country_list=countries, statename_list=state_names, carbon_calculation_region_name_list=region_names)

            logger.info(location_info)

        return location_info

    def _get_carbon_calculations_expression(self):
        """Retrieves the Carbon Calculation Expression for calculating Carbon.

        Returns
        -------
        Dataframe
            Dataframe containing sensor details including the carbon calculation expression.
        """
        carbon_calculations = pd.DataFrame()
        logger.info('Getting Installation location details.')

        query = COMMAND_CARBON_CALCULATION_EXPRESSION(country_names_list=self.location_info.countries,
                                                      state_names_list=self.location_info.state_names,
                                                      region_names_list=self.location_info.region_names,
                                                      year_list=self.unique_years,
                                                      obj_prop_ids=self.objectproperty_id_list)
        df, error = self.iot_service.execute_reader(api_inputs=self.api_inputs,
                                                    command=query, nb_retry=3, parameters=[])

        if df is None or len(df) == 0:
            logger.info("No returned Carbon Calculation Expressions from SQL.")
            if error:
                logger.error(f'Error: {error}')
            return pd.DataFrame()

        if isinstance(df, pd.DataFrame) and not df.empty:
            carbon_calculations = df

        return carbon_calculations

    def compute_carbon(self, sensor_id: str, value: float, date_time: datetime) -> float:
        """Computes the Carbon based on the Carbon Calculation Expression of sensors

        Parameters
        ----------
        sensor_id: str
            Sensor ID to calculate Carbon. Used as a reference to lookup Carbon Calculation Expression
            from the Carbon Calculation Epxression dataframe.
        value: float
            Value to compute Carbon
        date_time: datetime
            Datetime value of reading for calculating Carbon.

        Returns:
            float: Calculated Carbon
        """
        carbon_value = 0.0

        if not self.carbon_calculations_exp or len(self.carbon_calculations_exp) == 0:
            return carbon_value

        try:
            current_carbon_calc = next((
                item for item in self.carbon_calculations_exp
                if date_time >= item.from_date and
                date_time <= item.to_date and
                sensor_id.lower() == str(item.object_property_id).lower()
            ), None)

            if current_carbon_calc:
                current_carbon_calc_expression = current_carbon_calc.carbon_expression
                formula = current_carbon_calc_expression.replace(
                    '[Value]', str(value))
                carbon_value = round(eval(formula), 9)
        except Exception as ex:
            logger.error(f"Get Carbon Calculation Error: {str(ex)}")

        return carbon_value
