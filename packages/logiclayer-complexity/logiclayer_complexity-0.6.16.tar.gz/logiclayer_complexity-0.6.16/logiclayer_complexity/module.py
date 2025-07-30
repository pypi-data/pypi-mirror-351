"""Economic Complexity adapter for use in LogicLayer.

Contains a module to enable endpoints which return economic complexity
calculations, using a Tesseract OLAP server as data source.
"""

from typing import Any, Dict, Generator, List, Mapping, Optional, Tuple

import logiclayer as ll
import pandas as pd
import polars as pl
from fastapi import Depends, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from tesseract_olap import (
    DataRequest,
    OlapServer,
    TesseractCube,
    TesseractSchema,
)
from tesseract_olap.backend import Session
from tesseract_olap.exceptions.query import NotAuthorized
from tesseract_olap.query import DataQuery
from typing_extensions import Annotated

from . import __title__, __version__
from .complexity import (
    ComplexityParameters,
    ComplexitySubnationalParameters,
    prepare_complexity_params,
    prepare_complexity_subnational_params,
)
from .dependencies import auth_token, parse_alias, parse_filter, parse_topk
from .exceptions import ComplexityException
from .opportunity_gain import OpportunityGainParameters, prepare_opportunity_gain_params
from .pmi import (
    PEIIParameters,
    PGIParameters,
    prepare_peii_params,
    prepare_pgi_params,
)
from .rca import (
    RcaHistoricalParameters,
    RcaParameters,
    RcaSubnationalParameters,
    prepare_historicalrca_params,
    prepare_rca_params,
    prepare_subnatrca_params,
)
from .relatedness import (
    RelatednessParameters,
    RelatednessSubnationalParameters,
    RelativeRelatednessParameters,
    RelativeRelatednessSubnationalParameters,
    prepare_relatedness_params,
    prepare_relatedness_subnational_params,
    prepare_relative_relatedness_params,
    prepare_relative_relatedness_subnational_params,
)
from .response import ResponseFormat
from .structs import TopkIntent
from .wdi import WdiParameters, WdiReference, WdiReferenceSchema, parse_wdi


class EconomicComplexityModule(ll.LogicLayerModule):
    """Economic Complexity calculations module class for LogicLayer."""

    olap: "OlapServer"
    wdi: Optional["WdiReference"]

    def __init__(
        self,
        olap: "OlapServer",
        wdi: Optional["WdiReferenceSchema"] = None,
        **kwargs,
    ):
        """Setups the server for this instance."""
        super().__init__(**kwargs)

        if olap is None:
            msg = "EconomicComplexityModule requires a tesseract_olap.OlapServer instance"
            raise ValueError(msg)

        self.debug = kwargs.get("debug", False)
        self.olap = olap
        self.wdi = None if wdi is None else WdiReference(**wdi)

    def apply_threshold(
        self,
        session: Session,
        df: pl.DataFrame,
        *,
        rca: RcaParameters,
        wdi: List[WdiParameters] = [],
    ) -> pd.DataFrame:
        threshold_expr = [
            *_yield_threshold_expr(df, rca.measure, rca.threshold),
            *self._yield_wdi_threshold_expr(session, wdi),
        ]
        if len(threshold_expr) > 0:
            df = df.filter(threshold_expr)
        return df.to_pandas()

    def _yield_wdi_threshold_expr(
        self,
        session: Session,
        params: List[WdiParameters],
    ) -> Generator[pl.Expr, None, None]:
        if not self.wdi or len(params) == 0:
            return None

        for item in params:
            request = self.wdi.build_request(item)
            data = self.fetch_data(session, request)
            location = f"{self.wdi.get_level(item.location)} ID"
            yield pl.col(location).is_in(data[location])

    def fetch_data(self, session: Session, request: DataRequest) -> pl.DataFrame:
        """Retrieve the data from the backend, and handles related errors."""
        query = self.olap.build_query(request)
        result = session.fetch_dataframe(query)
        return result.data

    def resolve_drilldowns(self, request: DataRequest) -> List[str]:
        """Return the list of expected drilldown columns for the provided request."""
        query = self.olap.build_query(request)
        if not isinstance(query, DataQuery):
            return []
        locale = query.locale
        return [
            column[1] if isinstance(column, tuple) else column.alias
            for hiefi in query.fields_qualitative
            for lvlfi in hiefi.drilldown_levels
            for column in lvlfi.iter_columns(locale)
        ]

    @ll.route("GET", "/")
    def route_status(self) -> ll.ModuleStatus:
        """Retrieve the current status of the module."""
        return ll.ModuleStatus(
            module=__title__,
            version=__version__,
            debug=self.debug,
            status="ok" if self.olap.ping() else "error",
            wdi="disabled" if self.wdi is None else "enabled",
        )

    @ll.route("GET", "/cubes")
    def route_schema(
        self,
        locale: Optional[str] = None,
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> TesseractSchema:
        """Return the public schema, including all cubes."""
        roles = self.auth.get_roles(token)
        locale = self.olap.schema.default_locale if locale is None else locale
        return TesseractSchema.from_entity(self.olap.schema, locale=locale, roles=roles)

    @ll.route("GET", "/cubes/{cube_name}")
    def route_schema_cube(
        self,
        cube_name: str,
        locale: Optional[str] = None,
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> TesseractCube:
        """Return the public schema for a single cube."""
        roles = self.auth.get_roles(token)
        cube = self.olap.schema.get_cube(cube_name)
        if not cube.is_authorized(roles):
            raise NotAuthorized(f"Cube({cube.name})", roles)
        locale = self.olap.schema.default_locale if locale is None else locale
        return TesseractCube.from_entity(cube, locale=locale)

    @ll.route("GET", "/rca.{extension}")
    def route_rca(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RcaParameters = Depends(prepare_rca_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
        wdi: List[WdiParameters] = Depends(parse_wdi),
        topk: Optional[TopkIntent] = Depends(parse_topk),
    ) -> Response:
        """RCA calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if set(filters.keys()) - {params.location, params.activity}:
            params.parents = True

        request = params.build_request(roles)

        with self.olap.session() as session:
            df = self.fetch_data(session, request)
            df = self.apply_threshold(session, df, rca=params, wdi=wdi)

        df_rca = params.calculate(df)

        return extension.serialize(df_rca, aliases, filters, topk)

    @ll.route("GET", "/eci.{extension}")
    def route_eci(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: ComplexityParameters = Depends(prepare_complexity_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
        wdi: List[WdiParameters] = Depends(parse_wdi),
    ) -> Response:
        """ECI calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.rca_params.parents is True or set(filters.keys()) - {
            params.rca_params.location,
            params.rca_params.activity,
        }:
            # add parents only of the parameter required for the endpoint
            params.rca_params.parents = [params.rca_params.location]

        request = params.rca_params.build_request(roles)

        with self.olap.session() as session:
            df = self.fetch_data(session, request)
            df = self.apply_threshold(session, df, rca=params.rca_params, wdi=wdi)

        df_eci = params.calculate(df, "ECI")

        return extension.serialize(df_eci, aliases, filters)

    @ll.route("GET", "/pci.{extension}")
    def route_pci(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: ComplexityParameters = Depends(prepare_complexity_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
        wdi: List[WdiParameters] = Depends(parse_wdi),
    ) -> Response:
        """PCI calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.rca_params.parents is True or set(filters.keys()) - {
            params.rca_params.location,
            params.rca_params.activity,
        }:
            # add parents only for the required level
            params.rca_params.parents = [params.rca_params.activity]

        request = params.rca_params.build_request(roles)

        with self.olap.session() as session:
            df = self.fetch_data(session, request)
            df = self.apply_threshold(session, df, rca=params.rca_params, wdi=wdi)

        df_pci = params.calculate(df, "PCI")

        return extension.serialize(df_pci, aliases, filters)

    @ll.route("GET", "/relatedness.{extension}")
    def route_relatedness(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RelatednessParameters = Depends(prepare_relatedness_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
        topk: Optional[TopkIntent] = Depends(parse_topk),
    ) -> Response:
        """Relatedness calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.rca_params.parents or (
            set(filters.keys()) - {params.rca_params.location, params.rca_params.activity}
        ):
            params.rca_params.parents = True

            request_activity = params.build_request_activity(roles)
            request_location = params.build_request_location(roles)

            activity_columns = self.resolve_drilldowns(request_activity)
            location_columns = self.resolve_drilldowns(request_location)
        else:
            activity_columns = [params.rca_params.activity, params.rca_params.activity_id]
            location_columns = [params.rca_params.location, params.rca_params.location_id]

        request = params.rca_params.build_request(roles)

        with self.olap.session() as session:
            df = self.fetch_data(session, request)
            df_thresholded = self.apply_threshold(session, df, rca=params.rca_params)

        df = df.to_pandas()
        df_reltd = params.calculate(df, df_thresholded, activity_columns, location_columns)

        return extension.serialize(df_reltd, aliases, filters, topk)

    @ll.route("GET", "/relative_relatedness.{extension}")
    def route_relative_relatedness(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RelativeRelatednessParameters = Depends(
            prepare_relative_relatedness_params,
        ),
        token: Optional[ll.AuthToken] = Depends(auth_token),
        topk: Optional[TopkIntent] = Depends(parse_topk),
    ) -> Response:
        """Relative Relatedness calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.rca_params.parents or (
            set(filters.keys()) - {params.rca_params.location, params.rca_params.activity}
        ):
            params.rca_params.parents = True

            request_activity = params.build_request_activity(roles)
            request_location = params.build_request_location(roles)

            activity_columns = self.resolve_drilldowns(request_activity)
            location_columns = self.resolve_drilldowns(request_location)
        else:
            activity_columns = [params.rca_params.activity, params.rca_params.activity_id]
            location_columns = [params.rca_params.location, params.rca_params.location_id]

        request = params.rca_params.build_request(roles)

        with self.olap.session() as session:
            df = self.fetch_data(session, request)
            df_thresholded = self.apply_threshold(session, df, rca=params.rca_params)

        df = df.to_pandas()
        df_rel_reltd = params.calculate(df, df_thresholded, activity_columns, location_columns)

        return extension.serialize(df_rel_reltd, aliases, filters, topk)

    @ll.route("GET", "/opportunity_gain.{extension}")
    def route_opportunity_gain(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: OpportunityGainParameters = Depends(prepare_opportunity_gain_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
        topk: Optional[TopkIntent] = Depends(parse_topk),
    ) -> Response:
        """Opportunity Gain calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if set(filters.keys()) - {params.rca_params.location, params.rca_params.activity}:
            params.rca_params.parents = True

        request = params.rca_params.build_request(roles)

        with self.olap.session() as session:
            df = self.fetch_data(session, request)
            df = self.apply_threshold(session, df, rca=params.rca_params)

        df_opgain = params.calculate(df)

        return extension.serialize(df_opgain, aliases, filters, topk)

    @ll.route("GET", "/pgi.{extension}")
    def route_pgi(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: PGIParameters = Depends(prepare_pgi_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> Response:
        """PGI calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.rca_params.parents is True or set(filters.keys()) - {
            params.rca_params.location,
            params.rca_params.activity,
        }:
            # add parents only of the parameter required for the endpoint
            params.rca_params.parents = [params.rca_params.activity]

        request = params.rca_params.build_request(roles)
        request_gini = params.build_request(roles)

        with self.olap.session() as session:
            df = self.fetch_data(session, request)
            df = self.apply_threshold(session, df, rca=params.rca_params)
            df_gini = self.fetch_data(session, request_gini).to_pandas()

        df_pgi = params.calculate(df, df_gini)

        return extension.serialize(df_pgi, aliases, filters)

    @ll.route("GET", "/peii.{extension}")
    def route_peii(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: PEIIParameters = Depends(prepare_peii_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> Response:
        """PEII calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.rca_params.parents is True or set(filters.keys()) - {
            params.rca_params.location,
            params.rca_params.activity,
        }:
            # add parents only of the parameter required for the endpoint
            params.rca_params.parents = [params.rca_params.activity]

        request = params.rca_params.build_request(roles)
        request_emissions = params.build_request(roles)

        with self.olap.session() as session:
            df = self.fetch_data(session, request)
            df = self.apply_threshold(session, df, rca=params.rca_params)
            df_emissions = self.fetch_data(session, request_emissions).to_pandas()

        df_peii = params.calculate(df, df_emissions)

        return extension.serialize(df_peii, aliases, filters)

    @ll.route("GET", "/rca_subnational.{extension}")
    def route_rca_subnational(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RcaSubnationalParameters = Depends(prepare_subnatrca_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
        topk: Optional[TopkIntent] = Depends(parse_topk),
    ) -> Response:
        """Subnational RCA calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.subnat_params.parents is True or set(filters.keys()) - {
            params.subnat_params.location,
            params.subnat_params.activity,
        }:
            params.subnat_params.parents = True

        req_subnat = params.subnat_params.build_request(roles)
        req_global = params.global_params.build_request(roles)

        with self.olap.session() as session:
            df_subnat = self.fetch_data(session, req_subnat).to_pandas()
            df_global = self.fetch_data(session, req_global).to_pandas()

        df_rca = params.calculate(df_subnat, df_global)

        return extension.serialize(df_rca, aliases, filters, topk)

    @ll.route("GET", "/eci_subnational.{extension}")
    def route_eci_subnational(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: ComplexitySubnationalParameters = Depends(
            prepare_complexity_subnational_params,
        ),
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> Response:
        """Subnational ECI calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.rca_params.subnat_params.parents is True or set(filters.keys()) - {
            params.rca_params.subnat_params.location,
            params.rca_params.subnat_params.activity,
        }:
            # add parents only of the parameter required for the endpoint
            params.rca_params.subnat_params.parents = params.rca_params.subnat_params.location

        req_subnat = params.rca_params.subnat_params.build_request(roles)
        req_global = params.rca_params.global_params.build_request(roles)

        with self.olap.session() as session:
            df_subnat = self.fetch_data(session, req_subnat).to_pandas()
            df_global = self.fetch_data(session, req_global).to_pandas()

        df_eci = params.calculate(df_subnat, df_global, "ECI")

        return extension.serialize(df_eci, aliases, filters)

    @ll.route("GET", "/pci_subnational.{extension}")
    def route_pci_subnational(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: ComplexitySubnationalParameters = Depends(
            prepare_complexity_subnational_params,
        ),
        token: Optional[ll.AuthToken] = Depends(auth_token),
    ) -> Response:
        """Subnational PCI calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.rca_params.subnat_params.parents is True or set(filters.keys()) - {
            params.rca_params.subnat_params.location,
            params.rca_params.subnat_params.activity,
        }:
            # add parents only of the parameter required for the endpoint
            params.rca_params.subnat_params.parents = params.rca_params.subnat_params.activity

        req_subnat = params.rca_params.subnat_params.build_request(roles)
        req_global = params.rca_params.global_params.build_request(roles)

        with self.olap.session() as session:
            df_subnat = self.fetch_data(session, req_subnat).to_pandas()
            df_global = self.fetch_data(session, req_global).to_pandas()

        df_pci = params.calculate(df_subnat, df_global, "PCI")

        return extension.serialize(df_pci, aliases, filters)

    @ll.route("GET", "/relatedness_subnational.{extension}")
    def route_relatedness_subnational(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RelatednessSubnationalParameters = Depends(
            prepare_relatedness_subnational_params,
        ),
        token: Optional[ll.AuthToken] = Depends(auth_token),
        topk: Optional[TopkIntent] = Depends(parse_topk),
    ) -> Response:
        """Subnational Relatedness calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.rca_params.subnat_params.parents or (
            set(filters.keys())
            - {
                params.rca_params.subnat_params.location,
                params.rca_params.subnat_params.activity,
            }
        ):
            params.rca_params.subnat_params.parents = True

            request_activity = params.build_request_activity(roles)
            request_location = params.build_request_location(roles)

            activity_columns = self.resolve_drilldowns(request_activity)
            location_columns = self.resolve_drilldowns(request_location)
        else:
            activity_columns = [
                params.rca_params.subnat_params.activity,
                params.rca_params.subnat_params.activity_id,
            ]
            location_columns = [
                params.rca_params.subnat_params.location,
                params.rca_params.subnat_params.location_id,
            ]

        req_subnat = params.rca_params.subnat_params.build_request(roles)
        req_global = params.rca_params.global_params.build_request(roles)

        with self.olap.session() as session:
            df_subnat = self.fetch_data(session, req_subnat).to_pandas()
            df_global = self.fetch_data(session, req_global).to_pandas()

        df_reltd = params.calculate(
            df_subnat,
            df_global,
            activity_columns,
            location_columns,
        )

        return extension.serialize(df_reltd, aliases, filters, topk)

    @ll.route("GET", "/relative_relatedness_subnational.{extension}")
    def route_relative_relatedness_subnational(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RelativeRelatednessSubnationalParameters = Depends(
            prepare_relative_relatedness_subnational_params,
        ),
        token: Optional[ll.AuthToken] = Depends(auth_token),
        topk: Optional[TopkIntent] = Depends(parse_topk),
    ) -> Response:
        """Subnational Relative Relatedness calculation endpoint."""
        roles = self.auth.get_roles(token)

        # If there are filters other than location/activity, assume and activate parents
        if params.rca_params.subnat_params.parents or (
            set(filters.keys())
            - {
                params.rca_params.subnat_params.location,
                params.rca_params.subnat_params.activity,
            }
        ):
            params.rca_params.subnat_params.parents = True

            request_activity = params.build_request_activity(roles)
            request_location = params.build_request_location(roles)

            activity_columns = self.resolve_drilldowns(request_activity)
            location_columns = self.resolve_drilldowns(request_location)
        else:
            activity_columns = [
                params.rca_params.subnat_params.activity,
                params.rca_params.subnat_params.activity_id,
            ]
            location_columns = [
                params.rca_params.subnat_params.location,
                params.rca_params.subnat_params.location_id,
            ]

        req_subnat = params.rca_params.subnat_params.build_request(roles)
        req_global = params.rca_params.global_params.build_request(roles)

        with self.olap.session() as session:
            df_subnat = self.fetch_data(session, req_subnat).to_pandas()
            df_global = self.fetch_data(session, req_global).to_pandas()

        df_rel_reltd = params.calculate(
            df_subnat,
            df_global,
            activity_columns,
            location_columns,
        )

        return extension.serialize(df_rel_reltd, aliases, filters, topk)

    @ll.route("GET", "/rca_historical.{extension}")
    def route_rca_historical(
        self,
        extension: ResponseFormat,
        aliases: Dict[str, str] = Depends(parse_alias),
        filters: Dict[str, Tuple[str, ...]] = Depends(parse_filter),
        params: RcaHistoricalParameters = Depends(prepare_historicalrca_params),
        token: Optional[ll.AuthToken] = Depends(auth_token),
        topk: Optional[TopkIntent] = Depends(parse_topk),
    ) -> Response:
        """RCA Agg calculation endpoint."""
        roles = self.auth.get_roles(token)
        request_a = params.build_request_a(roles)
        request_b = params.build_request_b(roles)
        request_c = params.build_request_c(roles)
        request_d = params.build_request_d(roles)

        with self.olap.session() as session:
            df_a = self.fetch_data(session, request_a).to_pandas()
            df_b = self.fetch_data(session, request_b).to_pandas()
            df_c = self.fetch_data(session, request_c).to_pandas()
            df_d = self.fetch_data(session, request_d).to_pandas()

        df_rca = params.calculate(df_a, df_b, df_c, df_d)

        return extension.serialize(df_rca, aliases, filters, topk)

    @ll.route("GET", "/{endpoint}", response_class=RedirectResponse)
    def route_redirect(
        self,
        request: Request,
        endpoint: str,
        accept: Annotated[Optional[str], Header()] = None,
    ) -> str:
        """Redirect the user to the URL with the expected response format."""
        if not any(path.startswith("/" + endpoint + ".") for path in self.route_paths):
            raise HTTPException(404, "Not found")

        if accept is None or accept.startswith("*/*") or "text/csv" in accept:
            extension = ResponseFormat.csv
        elif "application/x-jsonarray" in accept:
            extension = ResponseFormat.jsonarrays
        elif "application/x-jsonrecords" in accept:
            extension = ResponseFormat.jsonrecords
        elif "text/tab-separated-values" in accept:
            extension = ResponseFormat.tsv
        else:
            message = (
                f"Requested invalid format: '{accept}'. "
                "Prefer an explicit format using a path with a filetype extension."
            )
            raise HTTPException(status_code=406, detail=message)

        url = request.url
        path, endpoint = url.path.rsplit("/", maxsplit=1)
        return f"{path}/{endpoint}.{extension}?{url.query}"

    @ll.exception_handler(ComplexityException)
    def complexity_exc_handler(self, request: Request, exc: ComplexityException) -> Response:
        """Return a meaningful error to the user in case the request couldn't be completed."""
        content: Dict[str, Any] = {"error": True, "detail": "Backend error"}

        if 399 < exc.code < 500:
            content["detail"] = exc.message

        return JSONResponse(content, status_code=exc.code)


def condition_expr(measure: str, operator: str, value: float) -> pl.Expr:
    """Generate a polars comparison expression between the provided parameters."""
    if operator == "lt":
        return pl.col(measure) < value
    if operator == "lte":
        return pl.col(measure) <= value
    if operator == "gt":
        return pl.col(measure) > value
    if operator == "gte":
        return pl.col(measure) >= value
    if operator == "eq":
        return pl.col(measure) == value
    return pl.col(measure) != value


def _yield_threshold_expr(
    df: pl.DataFrame,
    measure: str,
    threshold: Mapping[str, Tuple[str, float]],
):
    """Transform the provided threshold restrictions into polar expressions."""
    for level, (operator, value) in threshold.items():
        column = f"{level} ID"
        # Group rows by `column` and get the sum of `measure`, then
        # apply threshold condition and get `column` of rows that comply
        keepids = (
            df.lazy()
            .select(column, measure)
            .group_by(column)
            .agg(pl.col(measure).sum())
            .filter(condition_expr(measure, operator, value))
            .select(column)
            .collect()
        )
        # Yield Expr for this threshold instruction
        yield pl.col(column).is_in(keepids[column])
