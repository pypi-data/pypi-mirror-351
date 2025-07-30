from dataclasses import dataclass
import numpy as np
from functools import cached_property
from shapely import MultiPoint, MultiPolygon, Polygon
from collections.abc import Callable
from scipy.spatial import Delaunay
from shapely.ops import unary_union
import shapely

DEFAULT_GRID_MAGNITUDE = 100

@dataclass
class Triangle():
    coords: np.ndarray 
    "Contains an array of 3 values, each of which contains the x y coordinates of the triangle's vertices."

    @cached_property
    def area(self) -> float: 
        """Calculate the area of a triangle given its vertices using the cross-product method."""
        v0, v1, v2 = self.coords
        return 0.5 * abs( (v1[0] - v0[0]) * (v2[1] - v0[1]) 
                        - (v2[0] - v0[0]) * (v1[1] - v0[1]))

    @cached_property
    def max_length(self) -> float:
        """Gets the maximum side length."""
        return max(self.side_lengths)
    
    @cached_property
    def side_lengths(self) -> list[float]:
        """Gets the side lengths."""
        v0, v1, v2 = self.coords
        side_lengths = [
            np.linalg.norm(v0 - v1),
            np.linalg.norm(v1 - v2),
            np.linalg.norm(v2 - v0)
        ]
        return side_lengths
  
    @cached_property
    def shape(self) -> Polygon:
        return Polygon(self.coords)


@dataclass
class DelaunayResult:
    name: str
    triangles: list[Triangle]
    input_points: MultiPoint
    
    def filter_triangles(self, filter: Callable[[Triangle], bool]) -> list[Triangle]:
        return [t for t in self.triangles if filter(t)]
    
    @cached_property
    def max_triangle_side_length(self) -> float:
        return max([t.max_length for t in self.triangles]) 
    
    @cached_property
    def max_triangle_area(self) -> float:
        return max([t.area for t in self.triangles])
    
    @cached_property
    def all_triangle_side_lengths(self) -> list[float]:
        all_side_lengths = []
        for t in self.triangles:
            all_side_lengths.extend(t.side_lengths)
        return all_side_lengths


@dataclass(frozen=True)
class GridResult:
    """A result of `PolygonResult.create_grid`, comprising the grid and the inputs used to create the grid. 
    Use `.grid` to get the grid of points. """
    grid: MultiPoint
    """Shapely Multipoint containing points that fill the area returned by create_bounding_area."""
    grid_spacing: float
    """The distance between points in the grid."""


@dataclass(frozen=True)
class AreaResult:
    """A result of `create_bounding_area`, comprising the polygon and the inputs used to create the area. 
    Use `.polygon` to get the polygon which bounds the points. """
    polygon: Polygon 
    """The Shapely Polygon bounding around all of the points (except outlier points if not requested).
    The polygon may be made up of more than one shape internally, however it will be a single 
    Shapely Polygon regareless of the number of distinct shapes."""
    buffer: float
    """The distance buffered around the points. """
    relative_distance_threshold: float
    """The distance at which triangles were culled from the complete triangulation."""

    def create_grid(self, grid_spacing: float|None = None) -> GridResult:
        """
        Creates a grid of points inside the polygon.
        
        Parameters
        ----------
        grid_spacing : float|None 
                    The distance between points on the grid. If None a default will be picked 
                    based on the magnitude of the range of the points.
        
        Returns
        -------
        Returns a `GridResult` containing points that fill the polygon's area.
        The grid of points that is created is the intersection of a rectangular grid of points and this area.
        """
        grid_spacing = (grid_spacing if grid_spacing is not None
                        else _calculate_grid_spacing(bounds=self.polygon.bounds))

        multipoint = _create_grid_of_points(self.polygon.bounds, 
                                            distance=grid_spacing,
                                            buffer=self.buffer)
        
        masked_points = multipoint.intersection(self.polygon)

        result = GridResult(grid=masked_points, grid_spacing=grid_spacing)

        return result
    

def create_bounding_area(points: MultiPoint, 
                         buffer: float|None = None,
                         include_outlier_points: bool = True,
                         relative_distance_threshold: float = 1.5) -> AreaResult:
    """
    Creates an area around the input points. The area may exclude some points if they are far away from other points
    
    Parameters
    ----------
        points : Multipoint
                 The shapely Multipoint containing the points to create an area around.
        buffer : float|None
                 The distance to buffer around the generated shape. 
                 If None, buffers by the lower quartile distance between the triangluated points.
        include_outlier_points : bool
                                 If true, then the shape generated will also include shapes around 
                                 points that are isolated, i.e. outside groups of nearby points.
        relative_distance_threshold : float
                                      The distance at which to cull triangles from the area. 
                                      Higher values will generate a larger, more loosely fitting 
                                      shape(s) whilst lower values will create smaller,
                                      more tightly fitting shape(s) with a higher likelihood of separate shapes.
    
    Returns
    ----------
    Returns a `AreaResult` bounding around all of the points (except outlier points if not requested).
    The polygon that is returned may be made up of more than one shape internally, however it will be returned
    as a single Shapely Polygon regareless of the number of distinct shapes.
    """
    _validate_points(points)
    
    dr = _calculate_delaunay_result(points)

    buffer = buffer if buffer is not None else _get_default_buffer(side_lengths=dr.all_triangle_side_lengths)

    polygon = _create_bounding_area(dr=dr, buffer=buffer,
                                 include_outlier_points=include_outlier_points, 
                                 relative_distance_threshold=relative_distance_threshold)
    
    result = AreaResult(
        polygon=polygon,
        buffer=buffer,
        relative_distance_threshold=relative_distance_threshold
    )
    
    return result
 

def get_grid_spacing_for_points(points: MultiPoint, magnitude: int | None = None) -> float:
    """
    Calculated the grid spacing for a given set of points. This method is designed to allow the calculation
    of a default value for the `grid_spacing` parameter of `create_spaced_points` to be done outside of the 
    `create_spaced_points` method so the value can be used elsewhere. 

    Returns the grid spacing.
    
    Parameters
    ----------
    points : Multipoint
             The shapely Multipoint containing the points to calculate the grid spacing for
    magnitude : int|None 
                Represents how many points there should be alongside the extents of the points. Default: 100

    Returns
    -------
    The grid spacing for the given magnitude, which is the default value calculated in `grid_spacing`.
    """
    if magnitude is None:
        magnitude = DEFAULT_GRID_MAGNITUDE

    assert magnitude is not None

    grid_spacing = _calculate_grid_spacing(points.bounds, magnitude)

    return grid_spacing


def _calculate_grid_spacing(bounds: tuple[float, float, float, float], magnitude: int = DEFAULT_GRID_MAGNITUDE) -> float:
    minx, miny, maxx, maxy = bounds

    width = abs(minx - maxx)
    height = abs(miny - maxy)

    largest_extent = max(width, height)

    grid_spacing = largest_extent / magnitude 

    return grid_spacing


def _get_default_buffer(side_lengths: list[float]) -> float:
    return np.percentile(side_lengths, 25)


def _create_grid_of_points(bounds: tuple[float, float, float, float], buffer: float, distance: float):
    # Create bounding box of coordinates to predict in
    minx, miny, maxx, maxy = bounds

    # construct rectangle of points to predict over 
    x_coords = list(np.arange(minx - buffer + distance / 2, maxx + buffer - distance / 2, distance))
    y_coords = list(np.arange(miny - buffer + distance / 2, maxy + buffer - distance / 2, distance))
    
    # If distance > range then coords list will be empty, set coords to middle of range
    x_coords = x_coords if x_coords != [] else [minx + (maxx - minx) / 2] 
    y_coords = y_coords if y_coords != [] else [miny + (maxy - miny) / 2] 

    x, y = np.meshgrid(x_coords, y_coords)
                                
    return MultiPoint(list(zip(x.flatten(),y.flatten())))


def _create_bounding_area(dr: DelaunayResult,
                         buffer: float,
                         include_outlier_points: bool,
                         relative_distance_threshold: float) -> Polygon:
    
    upper_threshold = _get_upper_outlier_threshold(dr.all_triangle_side_lengths, relative_distance_threshold=relative_distance_threshold)
    
    included_triangles = dr.filter_triangles(lambda t: t.max_length <= upper_threshold)
    triangluated_area = MultiPolygon([t.shape for t in included_triangles])
    bounding_area = unary_union(triangluated_area)
    
    if include_outlier_points:
        outlier_points = shapely.difference(dr.input_points, bounding_area)
        bounding_area = unary_union([outlier_points, bounding_area])

    polygon = bounding_area.buffer(buffer)
    
    return polygon


def _calculate_delaunay_result(points: MultiPoint, name: str = "") -> DelaunayResult:
    point_coords = [(p.x, p.y) for p in points.geoms]

    delaunay = Delaunay(point_coords)
    triangles: list[Triangle] = []

    for simplex in delaunay.simplices:
        # 'simplex' is a list of indices. Use it to index the points array:
        coords = delaunay.points[simplex]
        triangles.append(Triangle(coords=coords))
        
    return DelaunayResult(name=name, triangles=triangles, input_points=points)


def _get_upper_outlier_threshold(values: list[float], relative_distance_threshold: float):
    # Type is actually np array
    Q1 = np.percentile(values, 25)
    Q3 = np.percentile(values, 75)
    IQR = Q3 - Q1
    upper_threshold = Q3 + relative_distance_threshold * IQR

    return upper_threshold


def _validate_points(points: MultiPoint):
    if len(points.geoms) < 3:
        raise ValueError(f"Argument points must contain at least 3 points, contained only {len(points.geoms)}.")
    polygon = Polygon(points.geoms)
    if polygon.area <= 1e-13:
        raise ValueError(f"Argument points must not all be collinear.")
