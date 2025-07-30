# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for compute SQL commands
"""
from datetime import datetime


def COMMAND_INSTALLATION_LOCATION_DETAIL(installation_list: list[str]):
    installation_ids_str = ', '.join(
        [f"'{id.lower()}'" for id in installation_list])

    query = f"""
    SELECT
        Installation.InstallationID,
        Installation.Country,
        Installation.StateName,
        CountryStates.CarbonCalculationRegionName
    FROM
        Installation
        INNER JOIN CountryStates ON Installation.StateName = CountryStates.StateName
    WHERE Installation.InstallationID IN ({installation_ids_str})
    """

    return query


def COMMAND_CARBON_CALCULATION_EXPRESSION(year_list: list[int], obj_prop_ids: list[str], country_names_list: list[str], state_names_list: list[str], region_names_list: list[str]):

    years_string = ', '.join([f"('{year}')" for year in year_list])
    obj_prop_ids_string = ', '.join([f"'{id.lower()}'" for id in obj_prop_ids])
    country_names_string = ', '.join(
        [f"'{country_name}'" for country_name in country_names_list])
    state_names_string = ', '.join(
        [f"'{state_name}'" for state_name in state_names_list])
    region_names_string = ', '.join(
        [f"'{region_name}'" for region_name in region_names_list])

    year_query = ''

    if year_list and len(year_list) > 0:
        year_query = f"""
        WITH YearList AS (
            SELECT Year
            FROM (VALUES {years_string}) AS YearTable(Year)
        )"""

    query = f"""
        {year_query}
        
        SELECT 
            ObjectProperties.ObjectPropertyID,
            CarbonCalculationRegions.CarbonCalculationRegionID, 
            CarbonCalculationRegions.ObjectPropertyTypeID, 
            CarbonCalculationRegions.RegionName,
            CarbonCalculationregionObjectPropertyTemplates.ObjectPropertyTemplateID,
            CarbonCalculations.CarbonExpression,
            CarbonCalculations.FromDate, 
            CarbonCalculations.ToDate,
            Country.CountryName,
            CountryStates.CarbonCalculationRegionName
        FROM 
        ObjectProperties
        INNER JOIN ObjectPropertyTemplates ON ObjectProperties.ObjectPropertyTemplateID = ObjectPropertyTemplates.ID
        INNER JOIN CarbonCalculationRegions ON ObjectPropertyTemplates.ObjectPropertyTypeID = CarbonCalculationRegions.ObjectPropertyTypeID
        LEFT OUTER JOIN CarbonCalculationregionObjectPropertyTemplates ON CarbonCalculationRegions.CarbonCalculationRegionID = CarbonCalculationRegionObjectPropertyTemplates.CarbonCalculationRegionID
        INNER JOIN CarbonCalculations ON CarbonCalculationRegions.CarbonCalculationRegionID = CarbonCalculations.CarbonCalculationRegionID
        INNER JOIN Country ON CarbonCalculationRegions.IntCountryCode = Country.IntCountryCode
        INNER JOIN CountryStates ON CarbonCalculationRegions.IntCountryCode = CountryStates.IntCountryCode
                AND Country.IntCountryCode = CountryStates.IntCountryCode 
                AND CarbonCalculationRegions.RegionName = CountryStates.CarbonCalculationRegionName
        INNER JOIN YearList ON YearList.Year BETWEEN YEAR(CarbonCalculations.FromDate) AND YEAR(CarbonCalculations.ToDate)
        WHERE
            ObjectProperties.ObjectPropertyID IN ({obj_prop_ids_string})
            AND LOWER(Country.CountryName) IN ({country_names_string})
            AND LOWER(CountryStates.StateName) IN ({state_names_string})
            AND LOWER(CarbonCalculationRegions.RegionName) IN ({region_names_string})
    GROUP BY
        ObjectProperties.ObjectPropertyID,
        CarbonCalculationRegions.CarbonCalculationRegionID, 
        CarbonCalculationRegions.ObjectPropertyTypeID, 
        CarbonCalculationRegions.RegionName,
        CarbonCalculationregionObjectPropertyTemplates.ObjectPropertyTemplateID,
        CarbonCalculations.CarbonExpression,
        CarbonCalculations.FromDate, 
        CarbonCalculations.ToDate,
        Country.CountryName,
        CountryStates.CarbonCalculationRegionName
        """

    return query
