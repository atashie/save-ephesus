"""
School Desert Analysis for CHCCS Elementary Schools

Quantifies the geographic impact of school closures by computing travel times
(drive, bike, walk) from every point in the school district to the nearest
elementary school under multiple closure scenarios.

Methodology:
- Inverts the problem: runs Dijkstra OUTWARD from each school (33 total runs)
  rather than from every grid point (thousands of runs)
- For closure scenarios, simply excludes removed school(s) and re-takes the
  minimum travel time — no recomputation needed
- Travel speeds: walk 2.5 mph (K-5 children), bike 12 mph,
  drive by road type using effective speeds (10-60 mph)
- Grid resolution: 100m over the entire CHCCS district

Speed model sources:
- Walk: MUTCD Section 4E.06 design walk speed (3.5 ft/s = 2.4 mph).
  Fitzpatrick et al. (2006, FHWA-HRT-06-042) measured 3.7-4.2 ft/s for
  school-age children. We use 2.5 mph (3.67 ft/s) — mid-range for K-5.
- Drive: Posted limits reduced to effective speeds per HCM6 Ch.16 (Urban
  Street Facilities) and FHWA Urban Arterial Speed Studies. Effective/posted
  ratios: ~65% residential, ~71% secondary, ~73% primary/trunk, ~92% motorway.
  Accounts for intersection delays, stop signs, signals, school-hour traffic.
- Node snapping: longitudes scaled by cos(latitude) for metric-approximate
  nearest-neighbor queries in WGS84 coordinate space.

Data sources:
- Road networks: OpenStreetMap via OSMnx
- School locations: NCES EDGE Public School Locations 2023-24
- District boundary: Census TIGER/Line Unified School Districts 2023

Outputs:
- assets/maps/school_desert_map.html (interactive map with scenario switching)
- data/processed/school_desert_grid.csv (raw grid travel time data)
"""

import base64
import io
import json
import sys
import warnings
from pathlib import Path

import folium
import geopandas as gpd
import matplotlib
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

warnings.filterwarnings("ignore", category=FutureWarning)
matplotlib.use("Agg")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_CACHE = PROJECT_ROOT / "data" / "cache"
ASSETS_MAPS = PROJECT_ROOT / "assets" / "maps"

SCHOOL_CSV = DATA_CACHE / "nces_school_locations.csv"
DISTRICT_CACHE = DATA_CACHE / "chccs_district_boundary.gpkg"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Travel speeds
WALK_SPEED_MPS = 1.12   # 2.5 mph — K-5 children (MUTCD 4E.06 / FHWA-HRT-06-042)
BIKE_SPEED_MPS = 5.36   # 12 mph

# Posted speed limits (kept for documentation only)
DRIVE_POSTED_SPEEDS_MPH = {
    "motorway": 65, "motorway_link": 55,
    "trunk": 55, "trunk_link": 45,
    "primary": 45, "primary_link": 35,
    "secondary": 35, "secondary_link": 30,
    "tertiary": 30, "tertiary_link": 25,
    "residential": 25, "living_street": 15,
    "service": 15, "unclassified": 25,
}

# Effective speeds accounting for signals, stops, and school-hour traffic
# Sources: HCM6 Ch.16 Urban Street Facilities, FHWA Urban Arterial Speed Studies
# Ratios vs posted: ~92% motorway, ~73% trunk/primary, ~71% secondary, ~65% residential
DRIVE_EFFECTIVE_SPEEDS_MPH = {
    "motorway": 60, "motorway_link": 50,
    "trunk": 40, "trunk_link": 35,
    "primary": 30, "primary_link": 25,
    "secondary": 25, "secondary_link": 22,
    "tertiary": 22, "tertiary_link": 18,
    "residential": 18, "living_street": 10,
    "service": 10, "unclassified": 18,
}
DEFAULT_DRIVE_EFFECTIVE_MPH = 18

# Grid
GRID_RESOLUTION_M = 100

# CRS
CRS_WGS84 = "EPSG:4326"
CRS_UTM17N = "EPSG:32617"

# Map center
CHAPEL_HILL_CENTER = [35.9132, -79.0558]

# Color scale ranges (minutes)
MODE_RANGES = {
    "drive": {"abs": (0, 15), "delta": (0, 10)},
    "bike":  {"abs": (0, 30), "delta": (0, 15)},
    "walk":  {"abs": (0, 60), "delta": (0, 30)},
}

# Closure scenarios
SCENARIOS = {
    "baseline": [],
    "no_ephesus": ["Ephesus Elementary"],
    "no_glenwood": ["Glenwood Elementary"],
    "no_fpg": ["Frank Porter Graham Bilingue"],
    "no_estes": ["Estes Hills Elementary"],
    "no_seawell": ["Seawell Elementary"],
    "no_ephesus_glenwood": ["Ephesus Elementary", "Glenwood Elementary"],
}

SCENARIO_LABELS = {
    "baseline": "Baseline (All 11 Schools)",
    "no_ephesus": "Close Ephesus",
    "no_glenwood": "Close Glenwood",
    "no_fpg": "Close FPG Bilingüe",
    "no_estes": "Close Estes Hills",
    "no_seawell": "Close Seawell",
    "no_ephesus_glenwood": "Close Ephesus + Glenwood",
}

MODE_LABELS = {"drive": "Drive", "bike": "Bike", "walk": "Walk"}

# Styling
EPHESUS_COLOR = "#e6031b"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _progress(msg: str):
    print(f"  ... {msg}")


def ensure_directories():
    for d in [DATA_PROCESSED, DATA_CACHE, ASSETS_MAPS]:
        d.mkdir(parents=True, exist_ok=True)


def _build_node_index(G: nx.MultiDiGraph):
    """Build a cKDTree spatial index for graph nodes.

    Scales longitudes by cos(mean_latitude) so Euclidean distance in the
    tree approximates true metric distance. At 35.9°N, cos(lat) ≈ 0.81.

    Returns (node_ids, tree, cos_lat).
    """
    node_ids = list(G.nodes())
    raw_coords = np.array([(G.nodes[n]["x"], G.nodes[n]["y"]) for n in node_ids])
    mean_lat = raw_coords[:, 1].mean()
    cos_lat = np.cos(np.radians(mean_lat))
    scaled_coords = np.column_stack([raw_coords[:, 0] * cos_lat, raw_coords[:, 1]])
    tree = cKDTree(scaled_coords)
    return node_ids, tree, cos_lat


def _nearest_node(node_ids, tree, lon, lat, cos_lat):
    """Find the nearest graph node to a (lon, lat) point."""
    _, idx = tree.query([lon * cos_lat, lat])
    return node_ids[idx]


def _nearest_nodes_batch(node_ids, tree, lons, lats, cos_lat):
    """Find nearest graph nodes for arrays of (lon, lat) points."""
    coords = np.column_stack([lons * cos_lat, lats])
    _, indices = tree.query(coords)
    return [node_ids[i] for i in indices]


# ---------------------------------------------------------------------------
# 1. Load school locations
# ---------------------------------------------------------------------------
def load_schools() -> gpd.GeoDataFrame:
    """Load NCES school locations from cache."""
    if not SCHOOL_CSV.exists():
        raise FileNotFoundError(
            f"School locations not found at {SCHOOL_CSV}. "
            "Run road_pollution.py first to download them."
        )
    df = pd.read_csv(SCHOOL_CSV)
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=CRS_WGS84
    )
    _progress(f"Loaded {len(gdf)} schools from {SCHOOL_CSV}")
    return gdf


# ---------------------------------------------------------------------------
# 2. Download district boundary
# ---------------------------------------------------------------------------
def download_district_boundary(schools: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Download CHCCS unified school district polygon from Census TIGER/Line.

    Uses GEOID 3700720 (Chapel Hill-Carrboro City Schools).
    Falls back to convex hull around schools with buffer if download fails.
    """
    if DISTRICT_CACHE.exists():
        _progress(f"Loading cached district boundary from {DISTRICT_CACHE}")
        return gpd.read_file(DISTRICT_CACHE)

    _progress("Downloading CHCCS district boundary from Census TIGER/Line ...")
    import requests
    import zipfile
    import tempfile

    url = "https://www2.census.gov/geo/tiger/TIGER2023/UNSD/tl_2023_37_unsd.zip"
    try:
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "unsd.zip"
            zip_path.write_bytes(resp.content)

            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(tmpdir)

            # Find the shapefile
            shp_files = list(Path(tmpdir).glob("*.shp"))
            if not shp_files:
                raise FileNotFoundError("No .shp found in TIGER/Line zip")

            gdf = gpd.read_file(shp_files[0])
            district = gdf[gdf["GEOID"] == "3700720"].copy()

            if len(district) == 0:
                raise ValueError("GEOID 3700720 not found in TIGER/Line data")

            district = district.to_crs(CRS_WGS84)
            district.to_file(DISTRICT_CACHE, driver="GPKG")
            _progress(f"Cached district boundary to {DISTRICT_CACHE}")
            return district

    except Exception as e:
        _progress(f"WARNING: District download failed ({e}), using convex hull fallback")
        return _fallback_district_boundary(schools)


def _fallback_district_boundary(schools: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Create fallback district boundary from convex hull of schools + 3km buffer."""
    schools_utm = schools.to_crs(CRS_UTM17N)
    hull = schools_utm.union_all().convex_hull
    buffered = hull.buffer(3000)  # 3km buffer
    gdf = gpd.GeoDataFrame(geometry=[buffered], crs=CRS_UTM17N).to_crs(CRS_WGS84)
    gdf.to_file(DISTRICT_CACHE, driver="GPKG")
    _progress("Created fallback district boundary (convex hull + 3km buffer)")
    return gdf


# ---------------------------------------------------------------------------
# 3. Download and prepare road networks
# ---------------------------------------------------------------------------
def _get_network_cache_path(mode: str) -> Path:
    return DATA_CACHE / f"network_{mode}.graphml"


def _add_travel_time_weights(G: nx.MultiDiGraph, mode: str) -> nx.MultiDiGraph:
    """Add travel_time (seconds) edge weights based on mode."""
    for u, v, key, data in G.edges(keys=True, data=True):
        length_m = data.get("length", 0)

        if mode == "walk":
            data["travel_time"] = length_m / WALK_SPEED_MPS
        elif mode == "bike":
            data["travel_time"] = length_m / BIKE_SPEED_MPS
        elif mode == "drive":
            highway = data.get("highway", "residential")
            if isinstance(highway, list):
                highway = highway[0]
            speed_mph = DRIVE_EFFECTIVE_SPEEDS_MPH.get(highway, DEFAULT_DRIVE_EFFECTIVE_MPH)
            speed_mps = speed_mph * 0.44704  # mph to m/s
            data["travel_time"] = length_m / speed_mps if speed_mps > 0 else 9999
    return G


def download_network(district_polygon, mode: str) -> nx.MultiDiGraph:
    """Download OSM road network for the district area.

    Args:
        district_polygon: Shapely polygon of the district (WGS84)
        mode: 'walk', 'bike', or 'drive'
    Returns:
        NetworkX graph with travel_time edge weights (seconds)
    """
    cache_path = _get_network_cache_path(mode)

    if cache_path.exists():
        _progress(f"Loading cached {mode} network from {cache_path}")
        G = ox.load_graphml(cache_path)
        # Re-add travel_time weights (graphml stores as strings)
        _add_travel_time_weights(G, mode)
        return G

    _progress(f"Downloading {mode} road network from OSM (this may take a few minutes) ...")

    ox.settings.use_cache = True
    ox.settings.requests_timeout = 300

    # Buffer the polygon slightly for edge accuracy
    district_gdf = gpd.GeoDataFrame(geometry=[district_polygon], crs=CRS_WGS84)
    district_utm = district_gdf.to_crs(CRS_UTM17N)
    buffered_utm = district_utm.geometry.iloc[0].buffer(500)
    buffered_wgs = gpd.GeoDataFrame(
        geometry=[buffered_utm], crs=CRS_UTM17N
    ).to_crs(CRS_WGS84).geometry.iloc[0]

    # Map mode to OSMnx network_type
    osmnx_type = {"walk": "walk", "bike": "bike", "drive": "drive"}[mode]

    try:
        G = ox.graph_from_polygon(buffered_wgs, network_type=osmnx_type, simplify=True)
    except Exception as e:
        if mode == "bike":
            _progress(f"Bike network failed ({e}), falling back to 'all' network")
            G = ox.graph_from_polygon(buffered_wgs, network_type="all", simplify=True)
        else:
            raise

    G = _add_travel_time_weights(G, mode)

    ox.save_graphml(G, cache_path)
    _progress(f"Cached {mode} network ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges) to {cache_path}")
    return G


# ---------------------------------------------------------------------------
# 4. Compute school-outward travel times
# ---------------------------------------------------------------------------
def compute_school_travel_times(
    G: nx.MultiDiGraph,
    schools: gpd.GeoDataFrame,
    reverse: bool = False,
) -> dict:
    """Run Dijkstra from each school outward (no cutoff — explores entire graph).

    Args:
        reverse: If True, reverse the graph before running Dijkstra.
            Use for drive mode so Dijkstra computes gridpoint->school
            (resident reaching school) instead of school->gridpoint.

    Returns:
        {school_name: {node_id: travel_time_seconds, ...}, ...}
    """
    G_search = G.reverse(copy=True) if reverse else G
    node_ids, tree, cos_lat = _build_node_index(G)
    travel_times = {}
    for _, row in schools.iterrows():
        name = row["school"]
        nearest_node = _nearest_node(node_ids, tree, row.geometry.x, row.geometry.y, cos_lat)
        times = nx.single_source_dijkstra_path_length(
            G_search, nearest_node, weight="travel_time"
        )
        travel_times[name] = dict(times)
        _progress(f"  {name}: reached {len(times)} nodes (full graph)")

    return travel_times


# ---------------------------------------------------------------------------
# 5. Create analysis grid
# ---------------------------------------------------------------------------
def create_grid(district_polygon, resolution_m: int = GRID_RESOLUTION_M) -> gpd.GeoDataFrame:
    """Create a regular point grid over the district at given resolution."""
    # Project to UTM for meter-based grid
    district_gdf = gpd.GeoDataFrame(geometry=[district_polygon], crs=CRS_WGS84)
    district_utm = district_gdf.to_crs(CRS_UTM17N).geometry.iloc[0]

    minx, miny, maxx, maxy = district_utm.bounds
    xs = np.arange(minx, maxx, resolution_m)
    ys = np.arange(miny, maxy, resolution_m)

    points = []
    grid_ids = []
    idx = 0
    for x in xs:
        for y in ys:
            pt = Point(x, y)
            if district_utm.contains(pt):
                points.append(pt)
                grid_ids.append(idx)
                idx += 1

    _progress(f"Created grid with {len(points)} points at {resolution_m}m resolution")

    gdf = gpd.GeoDataFrame(
        {"grid_id": grid_ids},
        geometry=points,
        crs=CRS_UTM17N,
    ).to_crs(CRS_WGS84)

    gdf["lat"] = gdf.geometry.y
    gdf["lon"] = gdf.geometry.x

    return gdf


# ---------------------------------------------------------------------------
# 6. Compute desert scores
# ---------------------------------------------------------------------------
def compute_desert_scores(
    grid: gpd.GeoDataFrame,
    travel_times_by_mode: dict,
    graphs: dict,
    scenarios: dict,
) -> pd.DataFrame:
    """For each grid point, scenario, and mode, compute min travel time.

    Args:
        grid: GeoDataFrame of grid points
        travel_times_by_mode: {mode: {school_name: {node_id: seconds}}}
        graphs: {mode: nx.MultiDiGraph}
        scenarios: {scenario_name: [closed_schools]}

    Returns:
        DataFrame with columns:
            grid_id, lat, lon, mode, scenario, min_time_seconds, nearest_school
    """
    all_schools = list(next(iter(travel_times_by_mode.values())).keys())

    results = []
    grid_ids = grid["grid_id"].values
    grid_lats = grid["lat"].values
    grid_lons = grid["lon"].values
    n_points = len(grid)

    for mode, travel_times in travel_times_by_mode.items():
        G = graphs[mode]

        # Snap grid points to nearest network nodes (once per mode)
        _progress(f"Snapping grid points to {mode} network ...")
        node_ids, tree, cos_lat = _build_node_index(G)
        nearest_nodes = _nearest_nodes_batch(node_ids, tree, grid_lons, grid_lats, cos_lat)

        for scenario_name, closed_schools in scenarios.items():
            open_schools = [s for s in all_schools if s not in closed_schools]

            _progress(f"  Computing {mode} / {scenario_name} ({len(open_schools)} open schools) ...")

            for i in range(n_points):
                node = nearest_nodes[i]
                best_time = np.inf
                best_school = None

                for school_name in open_schools:
                    t = travel_times[school_name].get(node, np.inf)
                    if t < best_time:
                        best_time = t
                        best_school = school_name

                results.append({
                    "grid_id": grid_ids[i],
                    "lat": grid_lats[i],
                    "lon": grid_lons[i],
                    "mode": mode,
                    "scenario": scenario_name,
                    "min_time_seconds": best_time if best_time < np.inf else np.nan,
                    "nearest_school": best_school,
                })

    df = pd.DataFrame(results)
    _progress(f"Computed {len(df)} desert scores")
    return df


# ---------------------------------------------------------------------------
# 7. Rasterize grid → GeoTIFF → colorized PNG overlay
# ---------------------------------------------------------------------------
TIFF_DIR = DATA_CACHE / "school_desert_tiffs"


def rasterize_grid(
    grid_df: pd.DataFrame,
    value_column: str,
    resolution_m: int = GRID_RESOLUTION_M,
    district_polygon=None,
) -> tuple:
    """Convert grid points to a 2D value raster in WGS84 space.

    Builds the pixel grid directly in lat/lon so rows align with latitude
    lines, matching Leaflet's axis-aligned image overlay display.

    Args:
        district_polygon: Optional Shapely polygon (WGS84) used to mask
            pixels outside the district after gap filling.

    Returns:
        (values_2d, grid_meta, bounds) or (None, None, None) if no valid data.
        values_2d: np.float32 array (nRows×nCols), NaN for empty cells
        grid_meta: dict with WGS84 bounds, cell size, dimensions
        bounds: [[south, west], [north, east]] for Leaflet
    """
    valid = grid_df.dropna(subset=[value_column])
    if len(valid) == 0:
        return None, None, None

    lats = valid["lat"].values
    lons = valid["lon"].values
    vals = valid[value_column].values

    # Cell size in degrees, approximating resolution_m at center latitude
    center_lat = lats.mean()
    dlat = resolution_m / 111_320.0
    dlon = resolution_m / (111_320.0 * np.cos(np.radians(center_lat)))

    # Raster bounds with half-cell padding
    minlon = lons.min() - dlon / 2
    maxlon = lons.max() + dlon / 2
    minlat = lats.min() - dlat / 2
    maxlat = lats.max() + dlat / 2

    ncols = int(np.ceil((maxlon - minlon) / dlon))
    nrows = int(np.ceil((maxlat - minlat) / dlat))

    values_2d = np.full((nrows, ncols), np.nan, dtype=np.float32)
    col_indices = np.clip(((lons - minlon) / dlon).astype(int), 0, ncols - 1)
    row_indices = np.clip(((maxlat - lats) / dlat).astype(int), 0, nrows - 1)
    values_2d[row_indices, col_indices] = vals

    # Fill NaN gaps from grid rotation + network routing failures.
    # Iteratively replace each NaN that borders valid data with the
    # mean of its non-NaN neighbors (3×3 window).  Three passes cover
    # gaps up to ~6 px wide (filling inward from both sides).
    from scipy.ndimage import uniform_filter
    for _ in range(3):
        mask = np.isnan(values_2d)
        if not mask.any():
            break
        # mean of non-NaN values in 3×3 window
        filled = np.where(mask, 0.0, values_2d)
        counts = uniform_filter((~mask).astype(np.float64), size=3, mode='constant', cval=0.0)
        smoothed = uniform_filter(filled.astype(np.float64), size=3, mode='constant', cval=0.0)
        has_neighbor = counts > 0
        fillable = mask & has_neighbor
        values_2d[fillable] = (smoothed[fillable] / counts[fillable]).astype(np.float32)

    # Mask out pixels whose centers fall outside the district polygon
    # so the gap fill doesn't bleed past the boundary.
    if district_polygon is not None:
        from shapely.prepared import prep
        prepared = prep(district_polygon)
        col_centers = minlon + (np.arange(ncols) + 0.5) * dlon
        row_centers = maxlat - (np.arange(nrows) + 0.5) * dlat
        cc, rr = np.meshgrid(col_centers, row_centers)
        pixel_points = [Point(lon, lat) for lon, lat in zip(cc.ravel(), rr.ravel())]
        inside = np.array([prepared.contains(p) for p in pixel_points]).reshape(nrows, ncols)
        values_2d[~inside] = np.nan

    bounds = [[minlat, minlon], [maxlat, maxlon]]

    grid_meta = {
        "lonMin": float(minlon), "latMin": float(minlat),
        "lonMax": float(maxlon), "latMax": float(maxlat),
        "cellSize": resolution_m, "nRows": nrows, "nCols": ncols,
    }
    return values_2d, grid_meta, bounds


def save_geotiff(values_2d: np.ndarray, grid_meta: dict, path: Path):
    """Save a value raster as a GeoTIFF with WGS84 CRS."""
    import rasterio
    from rasterio.transform import from_bounds

    nrows, ncols = values_2d.shape
    transform = from_bounds(
        grid_meta["lonMin"], grid_meta["latMin"],
        grid_meta["lonMax"], grid_meta["latMax"],
        ncols, nrows,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        str(path), "w", driver="GTiff",
        height=nrows, width=ncols, count=1,
        dtype="float32", crs=CRS_WGS84,
        transform=transform, nodata=float("nan"),
        compress="deflate",
    ) as dst:
        dst.write(values_2d, 1)


def colorize_raster(
    values_2d: np.ndarray,
    vmin: float, vmax: float,
    cmap_name: str,
) -> str:
    """Apply a colormap to a 2D value raster and return a base64 PNG.

    Cells with NaN are fully transparent; data cells are opaque (alpha=210).
    """
    if values_2d is None:
        return None

    cmap = plt.get_cmap(cmap_name)
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    has_data = ~np.isnan(values_2d)
    normed = norm(np.where(has_data, values_2d, 0))
    rgba = (cmap(normed) * 255).astype(np.uint8)
    rgba[..., 3] = np.where(has_data, 210, 0)

    buf = io.BytesIO()
    plt.imsave(buf, rgba, format="png")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def encode_value_grid(values_2d: np.ndarray) -> str:
    """Encode a 2D float32 array as base64 for JS hover lookup."""
    return base64.b64encode(values_2d.astype(np.float32).tobytes()).decode("utf-8")


# ---------------------------------------------------------------------------
# 8. Create interactive map
# ---------------------------------------------------------------------------
def create_map(
    heatmap_data: dict,
    schools: gpd.GeoDataFrame,
    district_gdf: gpd.GeoDataFrame,
    bounds: list,
    hover_grids: dict = None,
    grid_meta: dict = None,
) -> folium.Map:
    """Create interactive Folium map with scenario/mode switching.

    Args:
        heatmap_data: {(scenario, mode, layer_type): (base64_png, bounds)}
        schools: GeoDataFrame of school locations
        district_gdf: District boundary GeoDataFrame
        bounds: [[south, west], [north, east]] for overlay positioning
        hover_grids: {"scenario|mode|type": base64_float32_grid}
        grid_meta: dict with UTM/WGS84 bounds and grid dimensions
    """
    m = folium.Map(
        location=CHAPEL_HILL_CENTER,
        zoom_start=12,
        tiles="cartodbpositron",
        control_scale=True,
    )

    # Add district boundary
    folium.GeoJson(
        district_gdf.__geo_interface__,
        name="District Boundary",
        style_function=lambda x: {
            "fillColor": "transparent",
            "color": "#333333",
            "weight": 2,
            "dashArray": "5,5",
        },
    ).add_to(m)

    # School data for JS
    school_data = []
    for _, row in schools.iterrows():
        school_data.append({
            "name": row["school"],
            "lat": row["lat"],
            "lon": row["lon"],
            "address": row.get("address", ""),
        })

    # Build the custom HTML/JS control with overlay data embedded
    control_html = _build_control_html(
        heatmap_data, school_data, hover_grids or {}, grid_meta,
    )
    m.get_root().html.add_child(folium.Element(control_html))

    return m


def _build_control_html(
    heatmap_data: dict, schools: list,
    hover_grids: dict, grid_meta: dict,
) -> str:
    """Build HTML/CSS/JS for scenario/mode/layer switching controls.

    Creates L.imageOverlay instances directly in JS (bypassing Folium)
    and stores them in a dictionary for direct access by updateDesertMap().
    Includes hover tooltip that reads values from embedded Float32 grids.
    """

    # Build overlay data for JS — keyed by "scenario|mode|type"
    overlays_data = {}
    for (scenario, mode, layer_type), (b64, img_bounds) in heatmap_data.items():
        if b64 is None:
            continue
        key = f"{scenario}|{mode}|{layer_type}"
        overlays_data[key] = {
            "url": f"data:image/png;base64,{b64}",
            "bounds": img_bounds,
        }

    overlays_data_json = json.dumps(overlays_data)
    scenarios_json = json.dumps(SCENARIOS)
    scenario_labels_json = json.dumps(SCENARIO_LABELS)
    mode_labels_json = json.dumps(MODE_LABELS)
    mode_ranges_json = json.dumps(MODE_RANGES)
    schools_json = json.dumps(schools)
    hover_grids_json = json.dumps(hover_grids)
    grid_meta_json = json.dumps(grid_meta) if grid_meta else "null"

    return f"""
<style>
/* Force crisp pixel rendering on all Leaflet image overlays */
.leaflet-image-layer {{
    image-rendering: pixelated;
    image-rendering: -moz-crisp-edges;
    image-rendering: crisp-edges;
}}
#desert-controls {{
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 1000;
    background: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    font-family: 'Segoe UI', Tahoma, sans-serif;
    font-size: 13px;
    max-width: 260px;
    max-height: 90vh;
    overflow-y: auto;
}}
#desert-controls h3 {{
    margin: 0 0 10px 0;
    font-size: 15px;
    color: #333;
    border-bottom: 2px solid {EPHESUS_COLOR};
    padding-bottom: 5px;
}}
#desert-controls label {{
    display: block;
    margin: 3px 0;
    cursor: pointer;
    padding: 2px 4px;
    border-radius: 3px;
}}
#desert-controls label:hover {{
    background: #f0f0f0;
}}
#desert-controls .section-title {{
    font-weight: bold;
    margin: 10px 0 5px 0;
    color: #555;
    font-size: 12px;
    text-transform: uppercase;
}}
#desert-legend {{
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid #ddd;
}}
#desert-legend .gradient-bar {{
    height: 12px;
    border-radius: 3px;
    margin: 4px 0;
}}
#desert-legend .range-labels {{
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #666;
}}
.school-marker-info {{
    font-size: 12px;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #ddd;
    color: #666;
}}
.school-marker-info .closed {{
    color: {EPHESUS_COLOR};
    font-weight: bold;
}}
#desert-tooltip {{
    position: fixed;
    z-index: 2000;
    background: rgba(0,0,0,0.8);
    color: #fff;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    pointer-events: none;
    display: none;
    white-space: nowrap;
}}
</style>

<div id="desert-controls">
    <h3>School Desert Analysis</h3>

    <div class="section-title">Scenario</div>
    <div id="scenario-options"></div>

    <div class="section-title">Travel Mode</div>
    <div id="mode-options"></div>

    <div class="section-title">Layer</div>
    <label><input type="radio" name="layer_type" value="abs" checked onchange="window.updateDesertMap()"> Travel Time</label>
    <label><input type="radio" name="layer_type" value="delta" onchange="window.updateDesertMap()"> Change from Baseline</label>

    <div id="desert-legend">
        <div class="section-title">Legend</div>
        <div id="legend-label"></div>
        <div class="gradient-bar" id="legend-bar"></div>
        <div class="range-labels">
            <span id="legend-min"></span>
            <span id="legend-max"></span>
        </div>
    </div>

    <div class="school-marker-info" id="school-info"></div>
</div>
<div id="desert-tooltip"></div>

<script>
(function() {{
    var SCENARIOS = {scenarios_json};
    var SCENARIO_LABELS = {scenario_labels_json};
    var MODE_LABELS = {mode_labels_json};
    var MODE_RANGES = {mode_ranges_json};
    var OVERLAYS_DATA = {overlays_data_json};
    var SCHOOLS = {schools_json};
    var HOVER_GRIDS_B64 = {hover_grids_json};
    var GRID_META = {grid_meta_json};

    var overlayLayers = {{}};
    var schoolMarkers = [];
    var currentOverlayKey = null;
    var tooltip = document.getElementById('desert-tooltip');

    // --- Hover grid decoding ---
    var decodedGrids = {{}};
    function decodeGrid(key) {{
        if (decodedGrids[key]) return decodedGrids[key];
        var b64 = HOVER_GRIDS_B64[key];
        if (!b64) return null;
        var raw = atob(b64);
        var buf = new ArrayBuffer(raw.length);
        var u8 = new Uint8Array(buf);
        for (var i = 0; i < raw.length; i++) u8[i] = raw.charCodeAt(i);
        decodedGrids[key] = new Float32Array(buf);
        return decodedGrids[key];
    }}

    function getGridValue(lat, lon) {{
        if (!currentOverlayKey || !GRID_META) return null;
        var grid = decodeGrid(currentOverlayKey);
        if (!grid) return null;
        // Linear WGS84 → fractional grid coords (accurate for small areas)
        var fracX = (lon - GRID_META.lonMin) / (GRID_META.lonMax - GRID_META.lonMin);
        var fracY = (lat - GRID_META.latMin) / (GRID_META.latMax - GRID_META.latMin);
        var col = Math.floor(fracX * GRID_META.nCols);
        var row = Math.floor((1 - fracY) * GRID_META.nRows);
        if (row < 0 || row >= GRID_META.nRows || col < 0 || col >= GRID_META.nCols) return null;
        var val = grid[row * GRID_META.nCols + col];
        return isNaN(val) ? null : val;
    }}

    function getSelectedValue(name) {{
        var radios = document.querySelectorAll('input[name="' + name + '"]');
        for (var i = 0; i < radios.length; i++) {{
            if (radios[i].checked) return radios[i].value;
        }}
        return null;
    }}

    function getMap() {{
        for (var key in window) {{
            try {{
                if (window[key] && window[key]._leaflet_id && window[key].getZoom) {{
                    return window[key];
                }}
            }} catch(e) {{}}
        }}
        return null;
    }}

    function initOverlays(map) {{
        for (var key in OVERLAYS_DATA) {{
            var d = OVERLAYS_DATA[key];
            overlayLayers[key] = L.imageOverlay(d.url, d.bounds, {{opacity: 0}}).addTo(map);
        }}
        // Attach hover handler once
        map.on('mousemove', function(e) {{
            var val = getGridValue(e.latlng.lat, e.latlng.lng);
            if (val !== null) {{
                var layerType = getSelectedValue('layer_type');
                var label = (layerType === 'delta') ? '+' + val.toFixed(1) + ' min' : val.toFixed(1) + ' min';
                tooltip.textContent = label;
                tooltip.style.left = (e.originalEvent.pageX + 15) + 'px';
                tooltip.style.top = (e.originalEvent.pageY - 10) + 'px';
                tooltip.style.display = 'block';
            }} else {{
                tooltip.style.display = 'none';
            }}
        }});
        map.on('mouseout', function() {{ tooltip.style.display = 'none'; }});
    }}

    function updateSchoolMarkers(map, scenario) {{
        schoolMarkers.forEach(function(m) {{ map.removeLayer(m); }});
        schoolMarkers = [];

        var closedSchools = SCENARIOS[scenario] || [];

        SCHOOLS.forEach(function(school) {{
            var isClosed = closedSchools.indexOf(school.name) !== -1;
            var marker = L.circleMarker([school.lat, school.lon], {{
                radius: isClosed ? 8 : 7,
                fillColor: isClosed ? '#dc3545' : '#0d6efd',
                color: isClosed ? '#dc3545' : '#0a58ca',
                weight: 2,
                opacity: 1,
                fillOpacity: isClosed ? 0.3 : 0.8,
                dashArray: isClosed ? '4,4' : null,
            }});

            var status = isClosed ? '<span style="color:#dc3545;font-weight:bold">CLOSED</span>' : '<span style="color:#198754">Open</span>';
            marker.bindPopup(
                '<b>' + school.name + '</b><br>' +
                school.address + '<br>' +
                status
            );

            if (isClosed) {{
                var xIcon = L.divIcon({{
                    html: '<span style="color:#dc3545;font-size:18px;font-weight:bold;">&times;</span>',
                    className: 'closed-school-x',
                    iconSize: [20, 20],
                    iconAnchor: [10, 10],
                }});
                var xMarker = L.marker([school.lat, school.lon], {{icon: xIcon}});
                xMarker.addTo(map);
                schoolMarkers.push(xMarker);
            }}

            marker.addTo(map);
            schoolMarkers.push(marker);
        }});
    }}

    // Define updateDesertMap BEFORE radio buttons are created
    window.updateDesertMap = function() {{
        var scenario = getSelectedValue('scenario');
        var mode = getSelectedValue('mode');
        var layerType = getSelectedValue('layer_type');

        if (!scenario || !mode || !layerType) return;

        var map = getMap();
        if (!map) return;

        if (Object.keys(overlayLayers).length === 0) {{
            initOverlays(map);
        }}

        // Disable "Change from Baseline" for baseline scenario
        var deltaRadio = document.querySelector('input[name="layer_type"][value="delta"]');
        if (scenario === 'baseline') {{
            if (layerType === 'delta') {{
                document.querySelector('input[name="layer_type"][value="abs"]').checked = true;
                layerType = 'abs';
            }}
            deltaRadio.disabled = true;
            deltaRadio.parentElement.style.opacity = '0.4';
        }} else {{
            deltaRadio.disabled = false;
            deltaRadio.parentElement.style.opacity = '1';
        }}

        // Hide all overlays, show selected
        for (var key in overlayLayers) {{
            overlayLayers[key].setOpacity(0);
        }}
        var overlayKey = scenario + '|' + mode + '|' + layerType;
        if (overlayLayers[overlayKey]) {{
            overlayLayers[overlayKey].setOpacity(0.7);
        }}
        currentOverlayKey = overlayKey;

        updateSchoolMarkers(map, scenario);

        // Update legend
        var ranges = MODE_RANGES[mode];
        var range = layerType === 'abs' ? ranges['abs'] : ranges['delta'];
        var legendLabel = document.getElementById('legend-label');
        var legendBar = document.getElementById('legend-bar');
        var legendMin = document.getElementById('legend-min');
        var legendMax = document.getElementById('legend-max');

        if (layerType === 'abs') {{
            legendLabel.textContent = 'Minutes to nearest school';
            legendBar.style.background = 'linear-gradient(to right, #1a9850, #a6d96a, #ffffbf, #fdae61, #d73027)';
        }} else {{
            legendLabel.textContent = 'Added minutes (vs baseline)';
            legendBar.style.background = 'linear-gradient(to right, #fff5eb, #fdbe85, #fd8d3c, #e6550d, #a63603)';
        }}
        legendMin.textContent = range[0] + ' min';
        legendMax.textContent = range[1] + ' min';

        // Update school info
        var closedSchools = SCENARIOS[scenario] || [];
        var infoDiv = document.getElementById('school-info');
        if (closedSchools.length > 0) {{
            infoDiv.innerHTML = '<span class="closed">Closed:</span> ' + closedSchools.join(', ');
        }} else {{
            infoDiv.innerHTML = 'All 11 schools open';
        }}
    }};

    // Populate scenario radio buttons
    var scenarioDiv = document.getElementById('scenario-options');
    var first = true;
    for (var key in SCENARIO_LABELS) {{
        var label = document.createElement('label');
        var radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'scenario';
        radio.value = key;
        radio.onchange = function() {{ window.updateDesertMap(); }};
        if (first) {{ radio.checked = true; first = false; }}
        label.appendChild(radio);
        label.appendChild(document.createTextNode(' ' + SCENARIO_LABELS[key]));
        scenarioDiv.appendChild(label);
    }}

    // Populate mode radio buttons
    var modeDiv = document.getElementById('mode-options');
    first = true;
    for (var key in MODE_LABELS) {{
        var label = document.createElement('label');
        var radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'mode';
        radio.value = key;
        radio.onchange = function() {{ window.updateDesertMap(); }};
        if (first) {{ radio.checked = true; first = false; }}
        label.appendChild(radio);
        label.appendChild(document.createTextNode(' ' + MODE_LABELS[key]));
        modeDiv.appendChild(label);
    }}

    // Initialize on page load
    setTimeout(function() {{
        window.updateDesertMap();
    }}, 500);
}})();
</script>
"""


# ---------------------------------------------------------------------------
# 9. Main
# ---------------------------------------------------------------------------
def main():
    """Run full school desert analysis."""
    print("=" * 60)
    print("School Desert Analysis")
    print("=" * 60)

    ensure_directories()

    # 1. Load schools
    print("\n[1/9] Loading school locations ...")
    schools = load_schools()

    # 2. Download district boundary
    print("\n[2/9] Loading district boundary ...")
    district_gdf = download_district_boundary(schools)
    district_polygon = district_gdf.union_all()

    # 3. Download/load road networks
    print("\n[3/9] Loading road networks ...")
    graphs = {}
    modes = ["drive", "bike", "walk"]
    for mode in modes:
        graphs[mode] = download_network(district_polygon, mode)

    # 4. Compute travel times from each school
    print("\n[4/9] Computing school-outward travel times ...")
    travel_times_by_mode = {}
    for mode in modes:
        print(f"\n  --- {mode.upper()} (no cutoff) ---")
        travel_times_by_mode[mode] = compute_school_travel_times(
            graphs[mode], schools,
            reverse=(mode == "drive"),
        )

    # 5. Create grid
    print("\n[5/9] Creating analysis grid ...")
    grid = create_grid(district_polygon)

    # 6. Compute desert scores
    print("\n[6/9] Computing desert scores for all scenarios ...")
    scores_df = compute_desert_scores(grid, travel_times_by_mode, graphs, SCENARIOS)

    # 7. Compute delta (change from baseline)
    print("\n[7/9] Computing deltas ...")
    baseline = scores_df[scores_df["scenario"] == "baseline"][
        ["grid_id", "mode", "min_time_seconds"]
    ].rename(columns={"min_time_seconds": "baseline_time"})

    scores_df = scores_df.merge(baseline, on=["grid_id", "mode"], how="left")
    scores_df["delta_seconds"] = scores_df["min_time_seconds"] - scores_df["baseline_time"]
    scores_df["min_time_minutes"] = scores_df["min_time_seconds"] / 60.0
    scores_df["delta_minutes"] = scores_df["delta_seconds"] / 60.0

    # Save CSV
    csv_path = DATA_PROCESSED / "school_desert_grid.csv"
    scores_df.to_csv(csv_path, index=False)
    _progress(f"Saved grid data to {csv_path} ({len(scores_df)} rows)")

    # 8. Rasterize → GeoTIFF → PNG overlays
    print("\n[8/9] Rendering heatmaps (GeoTIFF -> PNG) ...")
    heatmap_data = {}    # (scenario, mode, layer_type) → (b64_png, bounds)
    hover_grids = {}     # "scenario|mode|type" → base64 Float32Array
    grid_meta = None
    common_bounds = None
    TIFF_DIR.mkdir(parents=True, exist_ok=True)

    for scenario in SCENARIOS:
        for mode in modes:
            subset = scores_df[
                (scores_df["scenario"] == scenario) & (scores_df["mode"] == mode)
            ].copy()

            # --- Absolute time layer ---
            vmin, vmax = MODE_RANGES[mode]["abs"]
            vals_2d, meta, bounds = rasterize_grid(subset, "min_time_minutes",
                                                      district_polygon=district_polygon)
            if meta is not None and grid_meta is None:
                grid_meta = meta
            if bounds is not None and common_bounds is None:
                common_bounds = bounds

            # Save GeoTIFF
            if vals_2d is not None:
                tiff_path = TIFF_DIR / f"{scenario}_{mode}_abs.tif"
                save_geotiff(vals_2d, meta, tiff_path)
                hover_grids[f"{scenario}|{mode}|abs"] = encode_value_grid(vals_2d)

            b64 = colorize_raster(vals_2d, vmin, vmax, "RdYlGn_r")
            heatmap_data[(scenario, mode, "abs")] = (b64, bounds)

            # --- Delta layer (skip baseline) ---
            if scenario != "baseline":
                vmin_d, vmax_d = MODE_RANGES[mode]["delta"]
                vals_d, meta_d, bounds_d = rasterize_grid(subset, "delta_minutes",
                                                            district_polygon=district_polygon)
                if vals_d is not None:
                    tiff_path_d = TIFF_DIR / f"{scenario}_{mode}_delta.tif"
                    save_geotiff(vals_d, meta_d, tiff_path_d)
                    hover_grids[f"{scenario}|{mode}|delta"] = encode_value_grid(vals_d)
                b64_d = colorize_raster(vals_d, vmin_d, vmax_d, "Oranges")
                heatmap_data[(scenario, mode, "delta")] = (b64_d, bounds_d)
            else:
                heatmap_data[(scenario, mode, "delta")] = (None, None)

            _progress(f"  Rendered {scenario} / {mode}")

    _progress(f"GeoTIFFs saved to {TIFF_DIR}")

    # 9. Create interactive map
    print("\n[9/9] Creating interactive map ...")
    m = create_map(heatmap_data, schools, district_gdf, common_bounds,
                   hover_grids, grid_meta)

    map_path = ASSETS_MAPS / "school_desert_map.html"
    m.save(str(map_path))
    _progress(f"Saved map to {map_path}")

    # Summary stats
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print(f"  Map: {map_path}")
    print(f"  Data: {csv_path}")
    print(f"  Grid points: {len(grid)}")
    print(f"  Scenarios: {len(SCENARIOS)}")
    print(f"  Heatmap images: {sum(1 for v in heatmap_data.values() if v[0] is not None)}")

    # Print key stats for Ephesus closure
    ephesus_drive = scores_df[
        (scores_df["scenario"] == "no_ephesus") & (scores_df["mode"] == "drive")
    ]
    affected = ephesus_drive[ephesus_drive["delta_minutes"] > 1.0]
    print(f"\n  Ephesus closure impact (drive):")
    print(f"    Grid points with >1 min added drive time: {len(affected)}")
    if len(affected) > 0:
        print(f"    Max added drive time: {affected['delta_minutes'].max():.1f} min")
        print(f"    Mean added drive time (affected): {affected['delta_minutes'].mean():.1f} min")
    print("=" * 60)


if __name__ == "__main__":
    main()
