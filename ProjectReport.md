# Identifying Roadway Roughness Segments Near At-Grade Railroad Crossings in Oklahoma

**Jeff Smith**  

## Abstract

This project used Python and ArcPy to identify roadway roughness patterns near public at-grade railroad crossings in Oklahoma. The analysis combined the Oklahoma Department of Transportation (ODOT) Pavement_IRI roadway layer with a national railroad grade crossing dataset.

The railroad crossing inventory was filtered to Oklahoma public highway crossings located at grade, producing **3,632 crossing points**. A user-entered geodesic buffer was created around each crossing. A **10-foot buffer** was used for the final analysis after visual review showed that a wider preliminary buffer could include pavement segments that were close to a crossing but not directly associated with it.

A spatial join identified pavement segments related to the crossing buffers. Pavement records were then grouped by `ROUTE_ID` and `DIRECTION` and ordered by roadway measure so that the segment immediately before and after each crossing segment could be identified without mixing travel directions.

Records with `IRI_AVG` equal to zero were retained while roadway sequence was established, but were removed before summary statistics were calculated. Mean IRI at railroad crossing segments was **235.49**, compared with **164.66** before crossings and **146.94** after crossings. The average of the two neighboring means was **155.80**, making the crossing mean **79.69 IRI units higher**, or approximately **51% higher**.

The results show a clear association between public at-grade railroad crossing locations and higher roadway roughness, although the analysis does not establish that the crossing itself caused the increase.

**Keywords:** at-grade railroad crossings, roadway roughness, International Roughness Index, transportation GIS, Python geoprocessing

## Introduction

Pavement roughness is commonly used to evaluate roadway condition and support pavement management decisions. The **International Roughness Index (IRI)** provides a standardized measure of roadway smoothness.

Railroad crossings are locations where roadway pavement, rail infrastructure, and crossing materials meet, making them reasonable locations to examine for localized changes in pavement roughness. The purpose of this project was to use GIS and Python to determine whether roadway segments associated with public at-grade railroad crossings in Oklahoma show higher IRI values than the pavement immediately before and after the crossing.

The project used the ODOT `Pavement_IRI` feature layer for roadway roughness and the U.S. Department of Transportation railroad grade crossing inventory for crossing locations. The ODOT layer contains statewide pavement segments and attributes including `IRI_AVG`, `ROUTE_ID`, `DIRECTION`, and roadway measures. The railroad inventory contains crossing locations across the United States, so the workflow first reduced the national dataset to the Oklahoma crossings relevant to the study.

### Research Question

**Are roadway IRI values higher on pavement segments associated with public at-grade railroad crossings than on the immediately adjacent pavement segments?**

The goal was not to prove that railroad crossings cause higher roughness. Instead, the analysis provides a screening method that can identify a repeatable spatial pattern and provide additional context when pavement condition data is reviewed.

Python makes this workflow repeatable because the analysis can be rerun with updated datasets or a different buffer distance without manually repeating each GIS operation.

## Materials and Methods

### Input Data

The analysis used two vector datasets.

The first was the **ODOT Pavement_IRI** line layer, containing **156,932 roadway records** in the downloaded shapefile. Important fields included:

- `IRI_AVG`
- `ROUTE_ID`
- `DIRECTION`
- `FROMMEASUR`
- `TOMEASURE`

The second dataset was the national railroad grade crossing point layer, containing **242,108 records**. Important fields included:

- `StateAbbre`
- `CrossingTy`
- `CrossingPo`
- `CrossingPu`
- `CrossingID`

Both source datasets were stored in **GCS_WGS_1984**. Original shapefiles were kept unchanged, while processed layers and tables were written to a GeoPackage named `RailRoughnessAnalysis.gpkg`.

### Filtering Railroad Crossings

ArcPy Select was used to filter the national railroad crossing inventory using four conditions:

- `StateAbbre = 'OK'`
- `CrossingTy = 'Public'`
- `CrossingPo = 'At Grade'`
- `CrossingPu = 'Highway'`

The Highway condition excluded pedestrian and station crossings because the pavement dataset represents roadway travel lanes.

The filtered dataset contained **3,632 Oklahoma public highway at-grade crossings**.

### Crossing Buffers

The program asks the user to enter the railroad crossing analysis distance in feet.

The final analysis used a **10-foot buffer**. A preliminary 20-foot run produced a similar overall pattern, but visual review showed that the larger buffer could select nearby pavement segments that were not the best representation of the crossing segment.

Because the source data remained in GCS_WGS_1984, ArcPy created the crossing buffers using the **GEODESIC** method so the distance could be applied in feet without treating geographic coordinates as planar units.

### Identifying Crossing Pavement Segments

A Spatial Join was used to identify ODOT pavement segments intersecting the railroad crossing buffers.

The pavement layer was used as the target so the full pavement segment geometry and original attributes were retained. `JOIN_ONE_TO_MANY` was used because a pavement segment can be related to more than one crossing.

### Identifying Before and After Segments

The most important custom processing step was identifying the pavement segment immediately before and immediately after each crossing segment.

Direction had to be preserved. Pavement records were grouped using the combination of `ROUTE_ID` and `DIRECTION`. Each route-direction group was sorted by `FROMMEASUR`.

For every pavement segment identified by the spatial join:

- `RailFlag = 1` identified the railroad crossing segment.
- `RailFlag = 2` identified the previous segment.
- `RailFlag = 3` identified the next segment.

This approach prevented pavement in the opposite travel direction from being treated as a neighboring segment.

### Handling Zero IRI Values

The pavement data contained `IRI_AVG` values equal to zero.

These records were not removed before the neighboring-segment logic was run because removing them early could alter roadway sequence and cause the program to skip the true adjacent record.

After crossing, before, and after relationships were established, records with `IRI_AVG = 0` were removed from the statistical comparison.

### Summary Statistics

ArcPy Summary Statistics calculated the following for each `RailFlag` group:

- Count
- Mean IRI
- Minimum IRI
- Maximum IRI
- Standard deviation

The analysis was organized between `smit2788_main.ipynb` and `smit2788_module.py`. The notebook defines project paths, checks inputs, receives the user-entered buffer distance, calls the processing functions, and displays final results. Reusable ArcPy functions are stored in the Python module.

## Processing Workflow

```text
Raw pavement and crossing data
        |
        v
Filter Oklahoma public at-grade highway crossings
        |
        v
Enter buffer distance
        |
        v
Create geodesic crossing buffers
        |
        v
Spatial Join to pavement IRI
        |
        v
Group by ROUTE_ID and DIRECTION
        |
        v
Sort by FROMMEASUR
        |
        v
Flag before / crossing / after segments
        |
        v
Remove IRI_AVG = 0 from statistics
        |
        v
Calculate summary statistics
```

## Results

After zero-value IRI records were removed, the final comparison contained:

- **165** railroad crossing segments with valid IRI values
- **148** valid segments immediately before crossings
- **145** valid segments immediately after crossings

The different counts are expected because some neighboring records contained `IRI_AVG = 0`, and some crossing locations did not have a valid adjacent record at the edge of a route or direction sequence.

| Segment Type | Count | Mean IRI | Min | Max | Std. Dev. |
|---|---:|---:|---:|---:|---:|
| Railroad Crossing | 165 | 235.49 | 64 | 488 | 80.05 |
| Before Crossing | 148 | 164.66 | 48 | 509 | 86.34 |
| After Crossing | 145 | 146.94 | 44 | 444 | 75.83 |

The railroad crossing group had the highest mean IRI at **235.49**. The segment immediately before the crossing had a mean of **164.66**, while the segment immediately after the crossing had a mean of **146.94**.

Averaging the before and after means produced a neighboring pavement mean of **155.80**. The crossing mean was therefore **79.69 IRI units higher**, approximately **51% higher** than the neighboring pavement average.

The higher crossing mean was present when the crossing group was compared separately with both the before and after groups.

Standard deviations ranged from **75.83 to 86.34**, showing substantial variation in roughness across individual locations even though the statewide average pattern remained clear.

### Buffer Sensitivity Check

The preliminary 20-foot run produced:

- Crossing mean IRI: **230.17**
- Average neighboring IRI: **154.05**
- Difference: **76.12**

The final 10-foot analysis reduced the number of matched pavement records but produced the same overall pattern, with a slightly larger difference of **79.69**. This supported use of the more restrictive buffer in the final reported results.

## Discussion and Conclusions

The results support the research question. In the final statewide analysis, pavement segments associated with public at-grade railroad crossings had higher average IRI values than the immediately neighboring pavement segments on the same route and in the same direction.

Several methodological decisions were important:

- The 10-foot buffer reduced the chance of selecting pavement merely close to a crossing.
- Grouping records by both `ROUTE_ID` and `DIRECTION` prevented opposite travel directions from being treated as sequential neighbors.
- Retaining zero-value IRI records until after the before-and-after relationships were established preserved roadway sequence.

The analysis has limitations. It identifies a **spatial association** and does not prove that railroad crossings caused the higher IRI values. Roughness at individual locations can be influenced by pavement condition, crossing surface materials, roadway geometry, maintenance history, traffic, data collection conditions, and other factors.

Not every Oklahoma public at-grade crossing had an ODOT IRI segment within the final 10-foot buffer, so the reported statistics represent the subset of crossing locations that could be matched to the pavement dataset.

The project demonstrates that Python can automate a practical transportation GIS workflow using public data. The same workflow can be rerun with updated pavement or crossing data or with a different user-entered buffer distance.

Potential future work could:

- Compare each crossing segment directly with its own neighboring segments.
- Examine other pavement condition measures such as rutting or cracking.
- Include railroad and traffic characteristics to help explain why some crossings show larger roughness differences.

For the current project, the workflow provides a simple and repeatable method for identifying railroad crossing locations where pavement roughness may deserve additional context or review.

## References

- Esri. *Python and geoprocessing*. ArcGIS Pro documentation.  
  https://pro.arcgis.com/en/pro-app/latest/help/analysis/geoprocessing/basics/python-and-geoprocessing.htm

- Federal Railroad Administration. (2025, April 4). *Crossing inventory*. U.S. Department of Transportation.  
  https://railroads.dot.gov/railroad-safety/divisions/crossing-safety-and-trespass-prevention/crossing-inventory

- Oklahoma Department of Transportation GIS Management Branch, & ODOT Pavement Management Branch. *Pavement_IRI* [Feature service].  
  https://services6.arcgis.com/RBtoEUQ2lmN0K3GY/arcgis/rest/services/Pavement_IRI/FeatureServer

- U.S. Department of Transportation, Bureau of Transportation Statistics. (2026). *Railroad grade crossings* [Feature service].  
  https://services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_Railroad_Grade_Crossings/FeatureServer
