# Oklahoma Railroad Crossing Roughness

This project examines whether roadway pavement is rougher at public at-grade railroad crossings in Oklahoma than on the pavement segments immediately before and after each crossing.

It uses **Python, ArcPy, and ArcGIS Pro** to combine Oklahoma Department of Transportation pavement roughness data with a national railroad crossing inventory and automate the full analysis workflow.

## Research Question

**Are roadway International Roughness Index (IRI) values higher on pavement segments associated with public at-grade railroad crossings than on the immediately adjacent pavement segments?**

The project is designed to identify a repeatable spatial pattern, not to establish that railroad crossings directly cause higher pavement roughness.

## Data

The analysis uses two public vector datasets:

- **ODOT Pavement_IRI** — statewide Oklahoma pavement segments containing IRI values, route identifiers, direction, and roadway measures.
- **U.S. DOT Railroad Grade Crossings** — a national inventory of railroad crossing locations.

The railroad inventory was filtered to include only Oklahoma crossings that were:

- Public
- At grade
- Highway crossings

This produced **3,632 Oklahoma public highway at-grade railroad crossings**.

## Workflow

1. Filter the national railroad crossing dataset to Oklahoma public highway at-grade crossings.
2. Create a user-defined geodesic buffer around each crossing.
3. Spatially join the crossing buffers to ODOT pavement IRI segments.
4. Group pavement records by **ROUTE_ID** and **DIRECTION**.
5. Sort each route-direction group by roadway measure.
6. Identify the pavement segment immediately before and after each crossing segment.
7. Retain zero-value IRI records while establishing roadway sequence, then remove them before statistical analysis.
8. Calculate count, mean, minimum, maximum, and standard deviation of IRI for crossing and neighboring segments.

A **10-foot geodesic buffer** was used for the final analysis. A preliminary 20-foot run produced a similar overall pattern, but the narrower distance reduced the chance of selecting pavement that was nearby rather than directly associated with the crossing.

## Results

| Segment Type | Count | Mean IRI | Min | Max | Std. Dev. |
|---|---:|---:|---:|---:|---:|
| Railroad Crossing | 165 | 235.49 | 64 | 488 | 80.05 |
| Before Crossing | 148 | 164.66 | 48 | 509 | 86.34 |
| After Crossing | 145 | 146.94 | 44 | 444 | 75.83 |

The average of the before- and after-crossing means was **155.80**. The crossing mean was **79.69 IRI units higher**, or approximately **51% higher** than the neighboring pavement average.

The results show a clear association between public at-grade railroad crossing locations and higher roadway roughness in the matched ODOT pavement data.

## Requirements

The project was developed using:

- Python 3
- ArcPy
- ArcGIS Pro
- pathlib
- GeoPackage output

Because ArcPy is used throughout the workflow, the code is intended to run in an ArcGIS Pro Python environment.

## Data Availability

The source datasets are not included in this repository. They are available from the original public data providers:

- [Federal Railroad Administration Crossing Inventory](https://railroads.dot.gov/railroad-safety/divisions/crossing-safety-and-trespass-prevention/crossing-inventory)
- [ODOT Pavement IRI Feature Service](https://services6.arcgis.com/RBtoEUQ2lmN0K3GY/arcgis/rest/services/Pavement_IRI/FeatureServer)
- [U.S. DOT / BTS Railroad Grade Crossings Feature Service](https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_Railroad_Grade_Crossings/FeatureServer)
