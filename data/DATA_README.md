# Data build: City of Sydney / Greater Sydney rent and international-student exposure

Run from `data/scripts` with the Python packages in `requirements.txt`. `<D>` = the `data/` folder.

| Step | Command | Writes |
|----|----|----|
| 1 | `python 01_crawl_bond.py <D>/raw/nsw_bond` | 62 xlsx files + `_manifest.json` (crawls the Fair Trading page for links) |
| 2 | `python 02_load_bond.py <D>/raw/nsw_bond <D>/processed` | `bond_lodgements_raw.parquet`, `bond_file_manifest.csv` |
| 3 | `python 03_parse_bp0015.py <unzipped pivotCache dir> <D>/processed/bp0015_granted_cube.parquet` | BP0015 cube (month x state x sector x onshore/offshore x applicant) |
| 4 | `python 04_poa_centroids.py <D>` | `poa_centroids_nsw.csv` |
| 5 | `python 05_build_exposure.py <D>` | `gs_geography.csv`, `he_campuses.csv`, `exposure_postcode.csv` |
| 6 | `python 06_build_panel.py <D>` | `analysis_bond_panel.parquet`, `analysis_pq_seg.parquet`, `postcode_baseline.csv` |

Raw inputs not produced by a script: 2018 bond CSV (`raw/nsw_bond_2018`, UAT mirror of data.nsw), CRICOS tables (`raw/cricos_full`), DoE SA4 xlsx (`raw/doe_sa4`), ABS correspondences (`raw/abs_corr`), ABS POA shapefile (`raw/abs_poa`), BP0015 xlsx (`raw/bp0015`).

## Key columns

-   `analysis_bond_panel.parquet`: one row per cleaned bond. `rent` (AUD/week), `seg` (f01 = flat \<=1 bed, f2, f3p, h34 = house/terrace 3-4 bed, other), `phase` (0_base2018, 1_closure, 2_recovery, 3_correction, 4_plateau_decline: the visa-grant definition), `sa4`, `city_of_sydney`, exposure columns. The project notebook re-derives its primary phases from students present (BP0019; 0_base2018, 1_closure, 2_recovery, 3_plateau, 4_decline) and keeps the stored visa-grant phases as the sensitivity check.
-   Exposure (`exposure_postcode.csv`): `E2_rows_l{1.5,3,5}` = sum over HE campus postcodes of (SA4 HE enrolments allocated by CRICOS HE course-location rows, in thousands) x exp(-distance/lambda km); `E2_equal_l*` = equal split across major campuses; `E3_dist_major_km` = distance from the postcode centroid to the nearest campus postcode centroid with \>=50 HE rows; `E1_share_*` = SA4 share.
-   `postcode_baseline.csv`: 2018 baseline per postcode, `flat_heavy`, `comparator_candidate`.

## Known limitations

-   Distances use postcode centroids (ABS POA), so resolution is about 1 km. UNSW (CRICOS 2052) is mapped to 2033 and Macquarie (2109) to 2113 because ABS has no POA for those institution postcodes.
-   Campus weights are an allocation assumption (SA4 enrolments split by CRICOS rows), not observed enrolments per campus. Weight variants correlate 0.99, so they do not test the assumption.
-   DoE SA4 data is one snapshot (YTD Dec 2025) and counts enrolments by place of study.
-   2018 comes from a UAT mirror (its medians match the official DCJ series); 2019-2020 not found at bond level. Phases are working labels: the primary definition uses the national stock of student visa holders (BP0019), the sensitivity definition uses NSW visa grants (BP0015).
-   Central Coast (10 POAs) is inside ABS Greater Sydney but excluded from the pool (`in_pool` = False).

## Extraction and overview notebook (balanced package)
`notebooks/00_data_extraction_overview.ipynb` (source: `00_data_extraction_overview.py`) downloads and parses the 8 sources of the balanced package
(bond lodgements, CRICOS, Dept of Education SA4 enrolments, ABS geography, DCJ rent tables 2018-2022, Census 2021 postcode tables, BP0019, City of Sydney
Housing Audit), explains every table, and writes tidy files to `processed/extracted/` with a `data_catalogue.csv`.
Set `RENT_DATA_ROOT` to run it in another folder; existing downloads in `raw/` are reused (`FORCE = True` re-downloads). A fresh run takes about 3 minutes
and downloads about 280 MB.

## Project notebook and appendix
`notebooks/sydney_student_rent_eda.ipynb` (source: `sydney_student_rent_eda.py`) reads `processed/` and the enrichment tables in `processed/extracted/`
(Census, BP0019, DCJ, Housing Audit), so run the overview notebook first on a fresh copy. It runs in about 2–3 minutes.
`notebooks/appendix_context_da_airbnb.ipynb` holds the development-application and Airbnb context checks (it needs `../inside_airbnb_data/`).
`EDA_IMPROVEMENT_VERIFICATION.md` records which suggested improvements were verified, adopted or changed, and why.
