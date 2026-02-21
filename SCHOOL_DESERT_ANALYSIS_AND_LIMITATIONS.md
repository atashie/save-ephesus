# School Desert Analysis: Methodology and Limitations

## Overview

The school desert analysis (`src/school_desert.py`) quantifies how school closures affect travel times across the Chapel Hill-Carrboro City Schools (CHCCS) district. For every 100-meter grid cell in the district, it computes the minimum travel time to the nearest open elementary school under seven scenarios: baseline (all 11 schools open) and six closure scenarios. The output is an interactive heatmap (`assets/maps/school_desert_map.html`) with scenario/mode switching and hover tooltips.

---

## Pipeline Steps

### Step 1: Load School Locations

**Source:** NCES EDGE Public School Locations 2023-24 (LEAID 3700720), cached at `data/cache/nces_school_locations.csv`.

Loads the 11 CHCCS elementary schools with their official NCES coordinates (lat/lon in WGS84). These coordinates represent the school building locations as reported by the National Center for Education Statistics.

### Step 2: Load District Boundary

**Source:** U.S. Census Bureau TIGER/Line Unified School District boundaries (2023), GEOID `3700720`.

Downloads the official CHCCS district polygon from Census TIGER/Line shapefiles and caches it as a GeoPackage (`data/cache/chccs_district_boundary.gpkg`). If the download fails, a fallback boundary is created from the convex hull of all 11 school locations with a 3 km buffer — this is less accurate but ensures the analysis can still run.

### Step 3: Download Road Networks

**Source:** OpenStreetMap via the OSMnx library.

Three separate road network graphs are downloaded, one per travel mode:

| Mode | OSMnx network_type | Description |
|------|-------------------|-------------|
| Drive | `drive` | Roads accessible to motor vehicles |
| Bike | `bike` | Roads and paths accessible to cyclists (falls back to `all` if the bike-specific network fails) |
| Walk | `walk` | All pedestrian-accessible paths including sidewalks, trails, footways |

Each network is downloaded for the district polygon plus a 500-meter buffer (in UTM) to capture roads that cross the district boundary. Networks are cached as GraphML files in `data/cache/`.

**Edge weights (travel_time in seconds)** are computed per edge from `edge length / speed`:

- **Walk:** 2.5 mph (1.12 m/s) — mid-range for K-5 children. Based on MUTCD Section 4E.06 design speed of 3.5 ft/s and Fitzpatrick et al. (2006, FHWA-HRT-06-042) measurements of 3.7–4.2 ft/s for school-age children.
- **Bike:** 12 mph (5.36 m/s) — flat constant.
- **Drive:** Variable by OSM `highway` tag, using effective speeds that account for signals, stop signs, and school-hour traffic. Derived from posted speed limits reduced by empirical ratios from HCM6 Chapter 16 and FHWA Urban Arterial Speed Studies:

| Road type | Posted (mph) | Effective (mph) | Ratio |
|-----------|-------------|-----------------|-------|
| Motorway | 65 | 60 | 92% |
| Trunk | 55 | 40 | 73% |
| Primary | 45 | 30 | 67% |
| Secondary | 35 | 25 | 71% |
| Tertiary | 30 | 22 | 73% |
| Residential | 25 | 18 | 72% |
| Living street | 15 | 10 | 67% |
| Service | 15 | 10 | 67% |

Edges with unrecognized highway types default to 18 mph effective speed.

### Step 4: Compute School-Outward Travel Times (Dijkstra)

For each school, Dijkstra's single-source shortest-path algorithm is run outward across the entire network graph with no distance cutoff. This produces a lookup table of `{node_id: travel_time_seconds}` for every reachable node.

**Key design choice — graph reversal for drive mode:** Drive networks are directional (one-way streets). The question we want to answer is "how long does it take a resident at grid point X to drive to the nearest school?" This is a grid→school query. But Dijkstra runs outward from the source, computing school→grid times. For walk and bike networks (which are effectively undirected), these are equivalent. For the drive network, the graph is **reversed** before running Dijkstra so that the outward traversal follows roads in the direction a resident would actually drive toward the school.

This yields 33 Dijkstra runs total (11 schools × 3 modes). Travel times are cached in memory — they do not change across scenarios.

### Step 5: Create Analysis Grid

A regular point grid is generated in UTM (EPSG:32617) at 100-meter spacing. Only points whose UTM coordinates fall inside the district polygon (via `shapely.contains()`) are retained. The grid is then reprojected to WGS84 (EPSG:4326) for all subsequent steps.

This produces approximately 16,164 grid points covering the district interior.

### Step 6: Compute Desert Scores

For each combination of (grid point × travel mode × scenario):

1. The grid point is snapped to the nearest network node using a cKDTree spatial index. Longitudes are scaled by `cos(latitude)` before building the tree so that Euclidean distances in the tree approximate true metric distances.
2. For each open school in the scenario, the pre-computed Dijkstra travel time from that school to the snapped node is looked up.
3. The minimum travel time across all open schools is recorded, along with the identity of the nearest school.
4. If no school's Dijkstra tree reaches the snapped node, the travel time is recorded as NaN.

**Scenarios evaluated:**

| Scenario | Schools closed | Schools open |
|----------|---------------|-------------|
| Baseline | None | All 11 |
| Close Ephesus | Ephesus Elementary | 10 |
| Close Glenwood | Glenwood Elementary | 10 |
| Close FPG | Frank Porter Graham Bilingüe | 10 |
| Close Estes Hills | Estes Hills Elementary | 10 |
| Close Seawell | Seawell Elementary | 10 |
| Close Ephesus + Glenwood | Ephesus + Glenwood | 9 |

### Step 7: Compute Deltas

For each non-baseline scenario, the delta (change from baseline) is computed:

```
delta = closure_scenario_time - baseline_time
```

A positive delta means the closure increased travel time at that grid point. Zero delta means the grid point's nearest school was unaffected by the closure.

### Step 8: Rasterize to Heatmap Images

Grid points (irregularly spaced in WGS84 due to UTM→WGS84 reprojection) are binned into a regular lat/lon pixel grid:

1. **Cell size** is computed from the 100m resolution: `dlat = 100 / 111320` degrees, `dlon = 100 / (111320 × cos(center_lat))` degrees. This ensures pixels are approximately 100m × 100m at the center of the district.
2. Each grid point is assigned to its containing pixel via integer index arithmetic.
3. **Gap filling:** NaN pixels surrounded by valid data (caused by UTM→WGS84 coordinate rotation and network routing failures) are filled using 3 iterations of mean-of-neighbors smoothing with a 3×3 window (`scipy.ndimage.uniform_filter`). Each iteration fills NaN cells that border at least one valid cell with the mean of their valid neighbors.
4. **District boundary masking:** After gap filling, every pixel center is tested for containment within the CHCCS district polygon. Pixels outside the polygon are set back to NaN. This prevents the gap fill from bleeding color outside the district boundary.
5. **Colorization:** The value raster is mapped to RGBA using matplotlib colormaps. NaN cells become fully transparent (alpha=0); data cells get alpha=210/255. Absolute time layers use `RdYlGn_r` (green=close, red=far). Delta layers use `Oranges` (white=no change, dark orange=large increase).
6. **Encoding:** The RGBA image is saved as a base64 PNG for embedding in the HTML map. The raw float32 values are also base64-encoded for the hover tooltip lookup.

GeoTIFFs are saved to `data/cache/school_desert_tiffs/` for archival.

### Step 9: Interactive Map

A Folium map is generated with:
- CartoDB Positron base tiles
- The district boundary as a dashed polygon overlay
- School locations as circle markers (blue=open, red with ×=closed, per scenario)
- All heatmap layers pre-loaded as Leaflet `L.imageOverlay` objects (toggled via opacity)
- Radio button controls for scenario, travel mode, and layer type (absolute time vs. delta)
- A hover tooltip that decodes the base64 float32 grid in JavaScript and reports the value at the cursor position using linear WGS84 coordinate interpolation

---

## Data Sources

| Data | Source | Vintage | Access |
|------|--------|---------|--------|
| School locations | NCES EDGE Public School Locations | 2023-24 | Public download, LEAID 3700720 |
| District boundary | U.S. Census TIGER/Line Unified School Districts | 2023 | Public download, GEOID 3700720 |
| Road networks | OpenStreetMap via OSMnx | Fetched at analysis time | Overpass API |
| Walk speed | MUTCD 4E.06, Fitzpatrick et al. 2006 (FHWA-HRT-06-042) | 2006 | Published research |
| Drive speed adjustments | HCM6 Ch.16, FHWA Urban Arterial Speed Studies | 2016 | Published standards |

---

## Known Limitations

### 1. Speed Model Simplifications

**Walk speed is a single constant (2.5 mph).** In reality, walking speed varies with:
- Age (kindergartners walk slower than 5th graders)
- Terrain and elevation (Chapel Hill has hills; the model treats all paths as flat)
- Sidewalk availability (the OSM walk network includes paths that exist in the data, but not all streets have sidewalks — a path's presence in OSM does not mean a safe, paved sidewalk exists)
- Weather and season
- Whether the child is accompanied by an adult

**Bike speed is a single constant (12 mph).** No adjustment for hills, road surface, or rider age.

**Drive effective speeds are static estimates per road class.** They do not account for:
- Time-of-day variation (school drop-off congestion vs. midday)
- Intersection-specific signal timing
- Seasonal variation or construction
- Left-turn delays at specific intersections
- School zone speed reductions (20 mph zones active during arrival/dismissal)

### 2. Network Completeness and Accuracy

**OpenStreetMap data is community-maintained and may be incomplete.** Specific risks:
- Missing sidewalks, cut-throughs, or pedestrian paths
- Incorrect or outdated one-way street designations
- Missing or incorrect `highway` tags (affecting drive speed assignment)
- New developments or road changes not yet mapped

**The bike network may use a fallback.** If OSMnx fails to download a bike-specific network, the code falls back to `network_type="all"`, which includes roads not suitable for cycling.

**Network edges are simplified by OSMnx.** Intermediate nodes on straight road segments are removed. This reduces computational cost but means the network cannot represent mid-block access points.

### 3. Grid Snapping Approximation

Each grid point is snapped to the **single nearest network node** using Euclidean distance (with longitude scaling). This means:
- The grid point's travel time is actually the travel time from/to that node, not from the grid point's exact location
- For grid points far from any road (e.g., in parks or undeveloped areas), the snap distance could be 200m+, adding unmeasured walking time to reach the road
- Two adjacent grid points may snap to the same node and receive identical travel times, masking local variation

### 4. Dijkstra Routing Gaps

Some grid points receive NaN travel times because the network node they snapped to is unreachable from all schools. This happens primarily in the **reversed drive network** (16 NaN points per drive scenario, 6 per bike, 0 for walk) where isolated one-way road segments have no inbound path from any school. These NaN gaps are filled by the mean-of-neighbors interpolation during rasterization, but the interpolated values are estimates, not routed travel times.

### 5. UTM-to-WGS84 Grid Rotation

The analysis grid is generated in UTM (EPSG:32617) for uniform metric spacing, then reprojected to WGS84 for display. Because UTM grid lines are not perfectly aligned with latitude/longitude lines, the reprojected points do not fall on a perfectly regular lat/lon grid. When these points are binned into the raster's regular lat/lon pixel grid, some pixels receive no data point. These 1-pixel gaps are filled by the same mean-of-neighbors interpolation described above.

### 6. District Boundary Precision

The Census TIGER/Line district boundary is a cartographic generalization. It may not match the actual school attendance boundary to the parcel level. If the TIGER download fails, the fallback boundary (convex hull of school locations + 3 km buffer) is significantly less accurate and will include areas outside the actual district.

### 7. "Nearest School" Is Not "Assigned School"

The analysis computes travel time to the **geographically nearest** school. CHCCS assigns students to schools based on attendance zones, not pure proximity. A student's assigned school may not be the closest one. This analysis shows geographic access patterns, not actual assignment impacts.

### 8. No Capacity Constraints

The model treats all open schools as equally available regardless of capacity. In a real closure scenario, students would be redistributed according to capacity and policy, and some schools might become overcrowded. This analysis does not model redistribution — it only measures raw geographic access.

### 9. Mode-Specific Limitations

**Drive mode** uses the reversed graph to model grid→school travel. This correctly accounts for one-way streets but assumes the driver follows the shortest-time route. It does not model:
- Parking and walking from a parking lot to the school entrance
- Drop-off line queuing time
- Route choice preferences (parents may avoid certain roads)

**Walk mode** does not account for:
- Road crossing safety (no intersection danger weighting)
- Sidewalk connectivity gaps
- Safe Routes to School infrastructure (or lack thereof)
- Whether a route is suitable for an unaccompanied child

**Bike mode** does not account for:
- Whether bike infrastructure exists on the route
- Road safety for child cyclists
- Bike parking availability at schools

### 10. Raster Resolution vs. Display Resolution

The 100-meter grid resolution means each pixel represents a 100m × 100m area. Travel time is assigned to the entire pixel based on a single point at (or near) its center. Sub-pixel variation is lost. The `image-rendering: pixelated` CSS directive preserves crisp pixel boundaries when the map is zoomed in, but this makes the blocky resolution visually obvious.

### 11. Color Scale Clamping

Travel times are mapped to fixed color ranges per mode:
- Drive: 0–15 min (absolute), 0–10 min (delta)
- Bike: 0–30 min (absolute), 0–15 min (delta)
- Walk: 0–60 min (absolute), 0–30 min (delta)

Values exceeding the maximum are clamped to the darkest color. This means a 20-minute drive and a 40-minute drive both appear as the same dark red. The hover tooltip shows the actual value, but the visual impression can be misleading at extremes.

### 12. Static Network Snapshot

The OSM road network is downloaded once and cached. It represents road infrastructure at the time of download. New roads, closed roads, or construction are not reflected unless the cache is cleared and the network re-downloaded.

### 13. No Elevation or Terrain Model

All travel time calculations are based on 2D network distance. Hill gradients, which meaningfully affect walk and bike speeds in Chapel Hill's terrain, are not modeled. Routes through hilly areas will underestimate actual travel times for walk and bike modes.

---

## Output Files

| File | Description |
|------|-------------|
| `assets/maps/school_desert_map.html` | Interactive map with all scenarios, modes, and layers |
| `data/processed/school_desert_grid.csv` | Raw data: 339,444 rows (16,164 grid points × 7 scenarios × 3 modes) |
| `data/cache/school_desert_tiffs/*.tif` | GeoTIFF rasters (WGS84) for each scenario/mode/layer combination |
| `data/cache/nces_school_locations.csv` | School coordinates (input) |
| `data/cache/chccs_district_boundary.gpkg` | District polygon (input) |
| `data/cache/network_{drive,bike,walk}.graphml` | Cached road network graphs (input) |

---

## Reproducibility

To regenerate the analysis from scratch:

```bash
# Delete cached networks to force fresh download from OSM
rm data/cache/network_*.graphml

# Run the analysis
python src/school_desert.py
```

School locations and the district boundary are stable (NCES 2023-24 and Census 2023). Road networks may change between OSM downloads. All random seeds are deterministic (Dijkstra is deterministic given the same graph).
