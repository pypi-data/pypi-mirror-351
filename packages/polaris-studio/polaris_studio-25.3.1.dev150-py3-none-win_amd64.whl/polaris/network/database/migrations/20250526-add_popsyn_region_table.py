# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import warnings

from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import has_table, rename_column, without_triggers
from polaris.utils.database.standard_database import DatabaseType, StandardDatabase
from polaris.network.create.triggers import create_triggers
from polaris.utils.database.db_utils import has_column


def migrate(conn):
    db = StandardDatabase.for_type(DatabaseType.Supply)
    if not has_table(conn, "popsyn_region"):
        db.add_table(conn, "popsyn_region", get_srid(conn=conn), add_defaults=False)

    # Return if popsyn_region is already there
    if has_column(conn, "Location", "popsyn_region"):
        return

    triggers = [
        "polaris_location_populates_fields_on_new_record",
        "polaris_location_on_geo_change",
        "polaris_location_on_popsyn_region_change",
        "polaris_popsyn_region_populates_fields_on_new_record",
        "polaris_popsyn_region_on_geo_change",
        "polaris_popsyn_region_on_delete_record",
        "ISO_metadata_reference_row_id_value_update",
        "ISO_metadata_reference_row_id_value_insert",
    ]

    with without_triggers(conn, triggers):
        rename_column(conn, "Location", "census_zone", "popsyn_region")

    # Create any new triggers that have been added
    create_triggers(StandardDatabase.for_type(DatabaseType.Supply), conn)

    warnings.warn(
        "Empty PopSyn_Region table has been added. Please populate table and run geo-consistency checks to update the network"
    )
