"""
Author: Jeff Smith

Purpose:
Contains reusable functions for analyzing roadway roughness near
public at-grade railroad crossings in Oklahoma.
"""

import arcpy

def filter_crossings(inputCrossings, outputCrossings):
    """
    Filters the national railroad crossing dataset to public
    highway at-grade crossings located in Oklahoma.
    """

    whereClause = (
        "StateAbbre = 'OK' AND "
        "CrossingTy = 'Public' AND "
        "CrossingPo = 'At Grade' AND "
        "CrossingPu = 'Highway'"
    )

    if arcpy.Exists(str(outputCrossings)):
        arcpy.management.Delete(str(outputCrossings))

    arcpy.analysis.Select(
        str(inputCrossings),
        str(outputCrossings),
        whereClause
    )

    print("Oklahoma public at-grade railroad crossings created.")


def buffer_crossings(inputCrossings, outputBuffer, bufferDistance):
    """
    Creates a geodesic buffer around the filtered railroad crossings
    using a user-defined distance in feet.
    """

    bufferValue = f"{bufferDistance} Feet"

    if arcpy.Exists(str(outputBuffer)):
        arcpy.management.Delete(str(outputBuffer))

    arcpy.analysis.Buffer(
        str(inputCrossings),
        str(outputBuffer),
        bufferValue,
        method="GEODESIC"
    )

    print(f"Railroad crossings buffered by {bufferDistance} feet.")


def identify_crossing_segments(pavementIRI, crossingBuffers, outputSegments):
    """
    Identifies pavement IRI segments that intersect railroad crossing
    buffers while retaining the complete pavement segment geometry.
    """

    if arcpy.Exists(str(outputSegments)):
        arcpy.management.Delete(str(outputSegments))

    arcpy.analysis.SpatialJoin(
        target_features=str(pavementIRI),
        join_features=str(crossingBuffers),
        out_feature_class=str(outputSegments),
        join_operation="JOIN_ONE_TO_MANY",
        join_type="KEEP_COMMON",
        match_option="INTERSECT"
    )

    print("Pavement segments near railroad crossings identified.")


def flag_neighbor_segments(pavementIRI, crossingSegments, outputSegments):
    """
    Identifies railroad crossing pavement segments and the segments
    immediately before and after them on the same route and direction.

    RailFlag values:
        1 = railroad crossing segment
        2 = segment before railroad crossing
        3 = segment after railroad crossing
    """

    # Delete the output if it already exists
    if arcpy.Exists(str(outputSegments)):
        arcpy.management.Delete(str(outputSegments))

    # Get the original pavement feature IDs identified by the spatial join
    crossingOids = set()

    with arcpy.da.SearchCursor(
        str(crossingSegments),
        ["TARGET_FID"]
    ) as cursor:
        for row in cursor:
            crossingOids.add(row[0])

    # Group pavement segments by route and direction
    routeGroups = {}

    with arcpy.da.SearchCursor(
        str(pavementIRI),
        ["OID@", "ROUTE_ID", "DIRECTION", "FROMMEASUR"]
    ) as cursor:
        for oid, routeId, direction, fromMeasure in cursor:

            groupKey = (routeId, direction)

            if groupKey not in routeGroups:
                routeGroups[groupKey] = []

            routeGroups[groupKey].append((oid, fromMeasure))

    # Store the RailFlag value for each selected pavement segment
    segmentFlags = {}

    for segments in routeGroups.values():

        # Sort segments by roadway measure
        segments.sort(key=lambda x: x[1])

        for i in range(len(segments)):

            currentOid = segments[i][0]

            if currentOid in crossingOids:

                # Flag the railroad crossing segment
                segmentFlags[currentOid] = 1

                # Flag the previous segment on the same route and direction
                if i > 0:
                    previousOid = segments[i - 1][0]

                    if previousOid not in crossingOids:
                        segmentFlags.setdefault(previousOid, 2)

                # Flag the next segment on the same route and direction
                if i < len(segments) - 1:
                    nextOid = segments[i + 1][0]

                    if nextOid not in crossingOids:
                        segmentFlags.setdefault(nextOid, 3)

    # Delete the temporary feature layer if it already exists
    if arcpy.Exists("pavementLayer"):
        arcpy.management.Delete("pavementLayer")

    # Create a temporary pavement feature layer
    pavementLayer = arcpy.management.MakeFeatureLayer(
        str(pavementIRI),
        "pavementLayer"
    ).getOutput(0)

    # Select the crossing, before, and after pavement segments
    oidField = arcpy.Describe(str(pavementIRI)).OIDFieldName
    selectedOids = list(segmentFlags.keys())

    whereClause = f"{oidField} IN ({','.join(map(str, selectedOids))})"

    arcpy.management.SelectLayerByAttribute(
        pavementLayer,
        "NEW_SELECTION",
        whereClause
    )

    # Copy the selected pavement segments to the GeoPackage
    arcpy.management.CopyFeatures(
        pavementLayer,
        str(outputSegments)
    )

    # Add the RailFlag field
    arcpy.management.AddField(
        str(outputSegments),
        "RailFlag",
        "SHORT"
    )

    # Create a lookup for assigning RailFlag values to the output
    flagLookup = {}

    with arcpy.da.SearchCursor(
        str(pavementIRI),
        ["OID@", "ROUTE_ID", "DIRECTION", "FROMMEASUR", "TOMEASURE"]
    ) as cursor:
        for oid, routeId, direction, fromMeasure, toMeasure in cursor:

            if oid in segmentFlags:
                key = (
                    routeId,
                    direction,
                    fromMeasure,
                    toMeasure
                )

                flagLookup[key] = segmentFlags[oid]

    # Write the RailFlag values to the output layer
    with arcpy.da.UpdateCursor(
        str(outputSegments),
        ["ROUTE_ID", "DIRECTION", "FROMMEASUR", "TOMEASURE", "RailFlag"]
    ) as cursor:
        for row in cursor:

            key = (
                row[0],
                row[1],
                row[2],
                row[3]
            )

            if key in flagLookup:
                row[4] = flagLookup[key]
                cursor.updateRow(row)

    # Remove the temporary feature layer
    arcpy.management.Delete(pavementLayer)

    print("Crossing, before, and after pavement segments identified.")


def filter_valid_iri(inputSegments, outputSegments):
    """
    Removes pavement segments with an IRI_AVG value of zero
    before summary statistics are calculated.
    """

    if arcpy.Exists(str(outputSegments)):
        arcpy.management.Delete(str(outputSegments))

    whereClause = "IRI_AVG > 0"

    arcpy.analysis.Select(
        str(inputSegments),
        str(outputSegments),
        whereClause
    )

    print("Pavement segments with valid IRI values selected.")
    

def summarize_iri(inputSegments, outputTable):
    """
    Calculates summary statistics for IRI values grouped by RailFlag.
    """

    if arcpy.Exists(str(outputTable)):
        arcpy.management.Delete(str(outputTable))

    arcpy.analysis.Statistics(
        str(inputSegments),
        str(outputTable),
        [["IRI_AVG", "MEAN"],
         ["IRI_AVG", "MIN"],
         ["IRI_AVG", "MAX"],
         ["IRI_AVG", "STD"],
         ["IRI_AVG", "COUNT"]],
        "RailFlag"
    )

    print("IRI summary statistics calculated.")