from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Set

import economic_complexity as ec
import pandas as pd
from tesseract_olap import DataRequest, DataRequestParams

if TYPE_CHECKING:
    from logiclayer_complexity.rca import RcaParameters, RcaSubnationalParameters


@dataclass
class RelatednessParameters:
    rca_params: "RcaParameters"
    cutoff: float = 1
    iterations: int = 20
    rank: bool = False
    sort_ascending: Optional[bool] = None

    @property
    def column_name(self) -> str:
        return f"{self.rca_params.measure} Relatedness"

    # api call to know the hierarchy by location
    def build_request_location(self, roles: Set[str]) -> DataRequest:
        params: DataRequestParams = {
            "drilldowns": (self.rca_params.location,),
            "measures": (self.rca_params.measure,),
            "cuts_include": {**self.rca_params.cuts_include},
            "cuts_exclude": {**self.rca_params.cuts_exclude},
            "parents": self.rca_params.parents,
            "roles": roles,
            "pagination": (1, 0),
        }

        if self.rca_params.locale is not None:
            params["locale"] = self.rca_params.locale

        return DataRequest.new(self.rca_params.cube, params)

    # api call to know the hierarchy by activity
    def build_request_activity(self, roles: Set[str]) -> DataRequest:
        params: DataRequestParams = {
            "drilldowns": (self.rca_params.activity,),
            "measures": (self.rca_params.measure,),
            "cuts_include": {**self.rca_params.cuts_include},
            "cuts_exclude": {**self.rca_params.cuts_exclude},
            "parents": self.rca_params.parents,
            "roles": roles,
            "pagination": (1, 0),
        }

        if self.rca_params.locale is not None:
            params["locale"] = self.rca_params.locale

        return DataRequest.new(self.rca_params.cube, params)

    def _calculate(self, rca: pd.Series, rca_thresholded: pd.Series) -> pd.Series:
        df_rca = rca.unstack()
        df_rca_thresholded = rca_thresholded.unstack()

        # calculate proximity with the normalized matrix
        proximity = ec.proximity(df_rca_thresholded)

        # reindex df_rca to have the same activities that proximity
        df_rca = df_rca.reindex(columns=df_rca_thresholded.columns)

        # calculate relatedness with full matrix and normalized proximity
        df_relatd = ec.relatedness(df_rca, cutoff=self.cutoff, proximities=proximity)

        relatd = df_relatd.stack()
        if not isinstance(relatd, pd.Series):
            msg = "Calculation did not yield a pandas.Series"
            raise TypeError(msg)
        return relatd.rename(self.column_name)

    def calculate(
        self,
        df: pd.DataFrame,
        df_thresholded: pd.DataFrame,
        activity_columns: list[str],
        location_columns: list[str],
    ) -> pd.DataFrame:
        sort_ascending = self.sort_ascending
        name = self.column_name

        df_pivot_thresholded = self.rca_params.pivot(df_thresholded)
        df_pivot = self.rca_params.pivot(df)

        rca_thresholded = self.rca_params._calculate(df_pivot_thresholded)
        rca = self.rca_params._calculate(df_pivot)

        relatd = self._calculate(rca, rca_thresholded)

        ds = pd.concat([rca, relatd], axis=1).reset_index()

        if sort_ascending is not None:
            ds = ds.sort_values(by=name, ascending=sort_ascending)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = ds[name].rank(ascending=False, method="max").astype(int)

        df_index = df[location_columns].drop_duplicates()
        df_column = df[activity_columns].drop_duplicates()

        # add measure
        df_measure = df[
            [df_pivot.index.name, df_pivot.columns.name, self.rca_params.measure]
        ].merge(ds, how="right", on=[df_pivot.index.name, df_pivot.columns.name])

        # add complementary levels to df
        df_index = df_index.merge(df_measure, how="right", on=df_pivot.index.name)
        df_final = df_column.merge(df_index, how="right", on=df_pivot.columns.name)

        return df_final


@dataclass
class RelatednessSubnationalParameters:
    rca_params: "RcaSubnationalParameters"
    cutoff: float = 1
    rank: bool = False
    sort_ascending: Optional[bool] = None

    @property
    def column_name(self):
        return f"{self.rca_params.subnat_params.measure} Relatedness"

    # api call to know the hierarchy by location
    def build_request_location(self, roles: Set[str]) -> DataRequest:
        params: DataRequestParams = {
            "drilldowns": (self.rca_params.subnat_params.location,),
            "measures": (self.rca_params.subnat_params.measure,),
            "cuts_include": {**self.rca_params.subnat_params.cuts_include},
            "cuts_exclude": {**self.rca_params.subnat_params.cuts_exclude},
            "parents": self.rca_params.subnat_params.parents,
            "roles": roles,
            "pagination": (1, 0),
        }

        if self.rca_params.subnat_params.locale is not None:
            params["locale"] = self.rca_params.subnat_params.locale

        return DataRequest.new(self.rca_params.subnat_params.cube, params)

    # api call to know the hierarchy by activity
    def build_request_activity(self, roles: Set[str]) -> DataRequest:
        params: DataRequestParams = {
            "drilldowns": (self.rca_params.subnat_params.activity,),
            "measures": (self.rca_params.subnat_params.measure,),
            "cuts_include": {**self.rca_params.subnat_params.cuts_include},
            "cuts_exclude": {**self.rca_params.subnat_params.cuts_exclude},
            "parents": self.rca_params.subnat_params.parents,
            "roles": roles,
            "pagination": (1, 0),
        }

        if self.rca_params.subnat_params.locale is not None:
            params["locale"] = self.rca_params.subnat_params.locale

        return DataRequest.new(self.rca_params.subnat_params.cube, params)

    def _calculate(self, df_subnat: pd.DataFrame, df_global: pd.DataFrame):
        name = self.column_name
        params = self.rca_params.subnat_params

        location_id = params.location_id
        activity_id = params.activity_id

        df, tbl_global, tbl_rca_subnat = self.rca_params._calculate_subnat(
            df_subnat,
            df_global,
        )
        df_country = ec.rca(tbl_global)

        proximity = ec.proximity(df_country)
        output = ec.relatedness(
            tbl_rca_subnat.reindex(columns=list(proximity)).fillna(0),
            proximities=proximity,
        )

        # Keep the index names consistent, this is a subnat output
        output.index.name = location_id
        output.columns.name = activity_id

        output = pd.melt(output.reset_index(), id_vars=[location_id], value_name=name)
        output = output.merge(df, on=[location_id, activity_id], how="inner")

        return output

    def calculate(
        self,
        df_subnat: pd.DataFrame,
        df_global: pd.DataFrame,
        activity_columns: List[str],
        location_columns: List[str],
    ) -> pd.DataFrame:
        name = self.column_name
        sort_ascending = self.sort_ascending
        params = self.rca_params.subnat_params

        location_id = params.location_id
        activity_id = params.activity_id

        ds = self._calculate(df_subnat, df_global)

        if sort_ascending is not None:
            ds = ds.sort_values(by=name, ascending=sort_ascending)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = ds[name].rank(ascending=False, method="max").astype(int)

        # add measure
        df_measure = ds.merge(
            df_subnat[[location_id, activity_id, params.measure]],
            on=[location_id, activity_id],
            how="left",
        )

        # add complementary levels to df
        df_relatedness = df_measure.merge(
            df_subnat[activity_columns].drop_duplicates(),
            on=activity_id,
            how="left",
        )
        df_relatedness = df_relatedness.merge(
            df_subnat[location_columns].drop_duplicates(),
            on=location_id,
            how="left",
        )

        return df_relatedness


@dataclass
class RelativeRelatednessParameters:
    rca_params: "RcaParameters"
    cutoff: float = 1
    iterations: int = 20
    rank: bool = False
    sort_ascending: Optional[bool] = None

    @property
    def column_name(self):
        return f"{self.rca_params.measure} Relative Relatedness"

    # api call to know the hierarchy by location
    def build_request_location(self, roles: Set[str]) -> DataRequest:
        params: DataRequestParams = {
            "drilldowns": (self.rca_params.location,),
            "measures": (self.rca_params.measure,),
            "cuts_include": {**self.rca_params.cuts_include},
            "cuts_exclude": {**self.rca_params.cuts_exclude},
            "parents": self.rca_params.parents,
            "roles": roles,
            "pagination": (1, 0),
        }

        if self.rca_params.locale is not None:
            params["locale"] = self.rca_params.locale

        return DataRequest.new(self.rca_params.cube, params)

    # api call to know the hierarchy by activity
    def build_request_activity(self, roles: Set[str]) -> DataRequest:
        params: DataRequestParams = {
            "drilldowns": (self.rca_params.activity,),
            "measures": (self.rca_params.measure,),
            "cuts_include": {**self.rca_params.cuts_include},
            "cuts_exclude": {**self.rca_params.cuts_exclude},
            "parents": self.rca_params.parents,
            "roles": roles,
            "pagination": (1, 0),
        }

        if self.rca_params.locale is not None:
            params["locale"] = self.rca_params.locale

        return DataRequest.new(self.rca_params.cube, params)

    def _calculate(self, rca: pd.Series, rca_thresholded: pd.Series) -> pd.DataFrame:
        """Calculate the Relative Relatedness and returns it as a Series with (location, activity) MultiIndex."""
        colname_rca = f"{self.rca_params.measure} RCA"
        colname_relt = f"{self.rca_params.measure} Relatedness"
        colname_relrelt = f"{self.rca_params.measure} Relative Relatedness"

        location_id = self.rca_params.location_id
        activity_id = self.rca_params.activity_id

        df_rca = rca.unstack()
        df_rca_thresholded = rca_thresholded.unstack()

        # calculate proximity with the normalized matrix
        proximity = ec.proximity(df_rca_thresholded)

        # reindex df_rca to have the same activities that proximity
        df_rca = df_rca.reindex(columns=df_rca_thresholded.columns)

        df_relatedness = (
            ec.relatedness(df_rca, proximities=proximity)
            .reset_index()
            .melt(id_vars=[location_id], var_name=activity_id, value_name=colname_relt)
        )

        df_rca = df_rca.reset_index().melt(
            id_vars=[location_id],
            var_name=activity_id,
            value_name=colname_rca,
        )

        df = df_rca.merge(df_relatedness, on=[location_id, activity_id], how="right")

        # separate the data into possible entries (RCA <1) and possible exits (RCA >=1)
        # since relative relatedness is different for entries and exits
        entry_data = df[df[colname_rca] < self.cutoff].copy()
        exit_data = df[df[colname_rca] >= self.cutoff].copy()

        # calculate the relative relatedness as the z-score of the original relatedness
        # for each location or activity only for the subset of entry or exit data
        entry_data[colname_relrelt] = entry_data.groupby(location_id)[colname_relt].transform(
            lambda x: (x - x.mean()) / x.std(),
        )
        entry_data["Omega_cp_mean"] = entry_data.groupby(location_id)[colname_relt].transform(
            "mean",
        )
        entry_data["Omega_cp_std"] = entry_data.groupby(location_id)[colname_relt].transform("std")

        # compute sum and std from entry_data
        grouped_stats = (
            entry_data.groupby(location_id)[colname_relt]
            .agg(["mean", "std"])  # We rename them later
            .rename(columns={"mean": "Omega_cp_mean", "std": "Omega_cp_std"})
            .reset_index()
        )

        # merge (or map) these stats onto exit_data by 'country'
        exit_data = pd.merge(exit_data, grouped_stats, on=location_id, how="left")

        # compute the z-score for exit_data using *entry* sums/std
        exit_data[colname_relrelt] = (
            exit_data[colname_relt] - exit_data["Omega_cp_mean"]
        ) / exit_data["Omega_cp_std"]

        final_data = pd.concat([entry_data, exit_data], ignore_index=True)

        return final_data

    def calculate(
        self,
        df: pd.DataFrame,
        df_thresholded: pd.DataFrame,
        activity_columns: List[str],
        location_columns: List[str],
    ) -> pd.DataFrame:
        sort_ascending = self.sort_ascending
        name = self.column_name

        df_pivot = self.rca_params.pivot(df)
        df_pivot_thresholded = self.rca_params.pivot(df_thresholded)

        rca = self.rca_params._calculate(df_pivot)
        rca_thresholded = self.rca_params._calculate(df_pivot_thresholded)

        ds = self._calculate(rca, rca_thresholded)

        if sort_ascending is not None:
            ds = ds.sort_values(by=name, ascending=sort_ascending)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = ds[name].rank(ascending=False, method="max").astype(int)

        df_index = df[location_columns].drop_duplicates()
        df_column = df[activity_columns].drop_duplicates()

        # add measure
        df_measure = df[
            [df_pivot.index.name, df_pivot.columns.name, self.rca_params.measure]
        ].merge(ds, how="right", on=[df_pivot.index.name, df_pivot.columns.name])

        # add complementary levels to df
        df_index = df_index.merge(df_measure, how="right", on=df_pivot.index.name)
        df_final = df_column.merge(df_index, how="right", on=df_pivot.columns.name)

        return df_final


@dataclass
class RelativeRelatednessSubnationalParameters:
    rca_params: "RcaSubnationalParameters"
    cutoff: float = 1
    rank: bool = False
    sort_ascending: Optional[bool] = None

    @property
    def column_name(self):
        return f"{self.rca_params.subnat_params.measure} Relative Relatedness"

    # api call to know the hierarchy by location
    def build_request_location(self, roles: Set[str]) -> DataRequest:
        params: DataRequestParams = {
            "drilldowns": (self.rca_params.subnat_params.location,),
            "measures": (self.rca_params.subnat_params.measure,),
            "cuts_include": {**self.rca_params.subnat_params.cuts_include},
            "cuts_exclude": {**self.rca_params.subnat_params.cuts_exclude},
            "parents": self.rca_params.subnat_params.parents,
            "roles": roles,
            "pagination": (1, 0),
        }

        if self.rca_params.subnat_params.locale is not None:
            params["locale"] = self.rca_params.subnat_params.locale

        return DataRequest.new(self.rca_params.subnat_params.cube, params)

    # api call to know the hierarchy by activity
    def build_request_activity(self, roles: Set[str]) -> DataRequest:
        params: DataRequestParams = {
            "drilldowns": (self.rca_params.subnat_params.activity,),
            "measures": (self.rca_params.subnat_params.measure,),
            "cuts_include": {**self.rca_params.subnat_params.cuts_include},
            "cuts_exclude": {**self.rca_params.subnat_params.cuts_exclude},
            "parents": self.rca_params.subnat_params.parents,
            "roles": roles,
            "pagination": (1, 0),
        }

        if self.rca_params.subnat_params.locale is not None:
            params["locale"] = self.rca_params.subnat_params.locale

        return DataRequest.new(self.rca_params.subnat_params.cube, params)

    def _calculate(
        self,
        df_subnat: pd.DataFrame,
        df_global: pd.DataFrame,
    ):
        params = self.rca_params.subnat_params

        colname_rca = f"{params.measure} RCA"
        colname_relt = f"{params.measure} Relatedness"
        colname_relrelt = f"{params.measure} Relative Relatedness"

        location_id = params.location_id
        activity_id = params.activity_id

        df, tbl_global, tbl_rca_subnat = self.rca_params._calculate_subnat(
            df_subnat,
            df_global,
        )
        df_country = ec.rca(tbl_global)

        proximity = ec.proximity(df_country)

        relatedness = (
            ec.relatedness(
                tbl_rca_subnat.reindex(columns=list(proximity)).fillna(0),
                proximities=proximity,
            )
            .reset_index()
            .melt(
                id_vars=[location_id],
                var_name=activity_id,
                value_name=colname_relt,
            )
        )

        df_rca = tbl_rca_subnat.reset_index().melt(
            id_vars=[location_id],
            var_name=activity_id,
            value_name=colname_rca,
        )
        df = df_rca.merge(relatedness, on=[location_id, activity_id], how="right")

        # separate the data into possible entries (RCA <1) and possible exits (RCA >=1)
        # since relative relatedness is different for entries and exits
        entry_data = df[df[colname_rca] < self.cutoff].copy()
        exit_data = df[df[colname_rca] >= self.cutoff].copy()

        # calculate the relative relatedness as the z-score of the original relatedness
        # for each location or activity only for the subset of entry or exit data
        entry_data[colname_relrelt] = entry_data.groupby(location_id)[colname_relt].transform(
            lambda x: (x - x.mean()) / x.std(),
        )
        entry_data["Omega_cp_mean"] = entry_data.groupby(location_id)[colname_relt].transform(
            "mean",
        )
        entry_data["Omega_cp_std"] = entry_data.groupby(location_id)[colname_relt].transform("std")

        # compute sum and std from entry_data
        grouped_stats = (
            entry_data.groupby(location_id)[colname_relt]
            .agg(["mean", "std"])  # We rename them later
            .rename(columns={"mean": "Omega_cp_mean", "std": "Omega_cp_std"})
            .reset_index()
        )

        # merge (or map) these stats onto exit_data by 'country'
        exit_data = pd.merge(exit_data, grouped_stats, on=location_id, how="left")

        # compute the z-score for exit_data using *entry* sums/std
        exit_data[colname_relrelt] = (
            exit_data[colname_relt] - exit_data["Omega_cp_mean"]
        ) / exit_data["Omega_cp_std"]

        final_data = pd.concat([entry_data, exit_data], ignore_index=True)

        return final_data

    def calculate(
        self,
        df_subnat: pd.DataFrame,
        df_global: pd.DataFrame,
        activity_columns: list,
        location_columns: list,
    ) -> pd.DataFrame:
        name = self.column_name
        sort_ascending = self.sort_ascending
        params = self.rca_params.subnat_params

        location_id = params.location_id
        activity_id = params.activity_id

        ds = self._calculate(df_subnat, df_global)

        if sort_ascending is not None:
            ds = ds.sort_values(by=name, ascending=sort_ascending)

        if sort_ascending is not None or self.rank:
            ds[f"{name} Ranking"] = ds[name].rank(ascending=False, method="max").astype(int)

        # add measure
        df_measure = ds[ds[name].notna()].merge(
            df_subnat[[location_id, activity_id, params.measure]],
            on=[location_id, activity_id],
            how="left",
        )

        # add complementary levels to df
        df_relatedness = df_measure.merge(
            df_subnat[activity_columns].drop_duplicates(),
            on=activity_id,
            how="left",
        )
        df_relatedness = df_relatedness.merge(
            df_subnat[location_columns].drop_duplicates(),
            on=location_id,
            how="left",
        )

        return df_relatedness
