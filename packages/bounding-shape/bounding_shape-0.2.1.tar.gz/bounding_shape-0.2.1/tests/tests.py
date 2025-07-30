from unittest import TestCase
import numpy as np
from shapely import MultiPoint, Point

from src.bounding_shape.bounding_shape import create_bounding_area, get_grid_spacing_for_points

class TestBoundingArea(TestCase):
    def test_simple_triangle(self):
        # Creates points which form a single triangle
        points = MultiPoint([[0.0, 0.0], [1.0, 2.0], [2.0, 0.0]])

        result = create_bounding_area(points=points, buffer=0.1)
        self.assertTrue(result.polygon.contains(points))
        self.assertFalse(result.polygon.contains(Point(-1.0, -1.0)))

        # Check fields are populated correctly
        self.assertEqual(result.buffer, 0.1)
        self.assertIsNotNone(result.relative_distance_threshold)
        
    
    def test_larger_shape(self):
        # Creates points which form a pentagon
        points = MultiPoint([[0.0, 0.0], [0.0, 2.0], [1.0, 3.0], [2.0, 2.0], [2.0, 0.0]])
        result = create_bounding_area(points=points, buffer=0.1, include_outlier_points=True)
        self.assertTrue(result.polygon.contains(points))
        self.assertFalse(result.polygon.contains(Point(-1.0, -1.0)))

    
    def test_larger_shape_exclude_outlying_point(self):
        x_coords = list(np.arange(0, 5, 1))
        y_coords = list(np.arange(0, 3, 1))
        
        x, y = np.meshgrid(x_coords, y_coords)
                                    
        close_points = list(zip(x.flatten(),y.flatten()))
        distant_point = (20, 20)
                
        points = MultiPoint(close_points + [distant_point])
        result = create_bounding_area(points=points, buffer=0.1, include_outlier_points=False)
        polygon = result.polygon
        self.assertTrue(polygon.contains(MultiPoint(close_points)))
        self.assertFalse(polygon.contains(Point(-1.0, -1.0)))
        self.assertFalse(polygon.contains(Point(distant_point)))

    def test_default_parameters_are_populated(self):
        points = MultiPoint([[0.0, 0.0], [0.0, 2.0], [1.0, 3.0], [2.0, 2.0], [2.0, 0.0]])
        result = create_bounding_area(points=points)

        self.assertIsNotNone(result.buffer) 
        self.assertIsNotNone(result.relative_distance_threshold)


class TestGrid(TestCase):
    def test_simple_triangle(self):
        # Creates points which form a single triangle

        points = MultiPoint([[0.0, 0.0], [0.0, 100.0], [100.0, 100.0], [100.0, 0.0]])
        area_result = create_bounding_area(points=points, buffer=0.1)

        grid_result = area_result.create_grid(grid_spacing=20)
        # Points spaced at 10, 30, 50, 70, 90
        self.assertEqual(len(grid_result.grid.geoms), 25)

        # Check field is populated correctly
        self.assertEqual(grid_result.grid_spacing, 20)

    def test_default_parameter_is_populated(self):
        # Creates points which form a single triangle

        points = MultiPoint([[0.0, 0.0], [0.0, 100.0], [100.0, 100.0], [100.0, 0.0]])
        area_result = create_bounding_area(points=points, buffer=0.1)

        grid_result = area_result.create_grid()

        # Check field is populated correctly
        self.assertIsNotNone(grid_result.grid_spacing)


class TestDefaults(TestCase):
    def test_get_default_grid_spacing_for_points(self):
        points = MultiPoint([[0.0, 0.0], [0.0, 100.0], [100.0, 100.0], [100.0, 0.0]])
        
        spacing = get_grid_spacing_for_points(points, 100)

        # 100 / length
        self.assertEqual(spacing, 1.0)

    def test_get_grid_spacing_for_narrow_shape(self):
        points = MultiPoint([[0.0, 0.0], [0.0, 100.0], [1.0, 100.0], [1.0, 0.0]])

        # Length of square
        spacing = get_grid_spacing_for_points(points, 100)

        self.assertEqual(spacing, 1.0)


class TestFailureCases(TestCase):
    def test_two_points(self):
        points = MultiPoint([[0.0, 0.0], [1.0, 2.0]])
        with self.assertRaises(ValueError):
            create_bounding_area(points=points, buffer=0.1)

    def test_one_point(self):
        points = MultiPoint([[0.0, 0.0]])
        with self.assertRaises(ValueError):
            create_bounding_area(points=points, buffer=0.1)

    def test_three_colinear_points(self):
        points = MultiPoint([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
        with self.assertRaises(ValueError):
            create_bounding_area(points=points, buffer=0.1)

    def test_extremely_small_area(self):
        very_small_float = 2e-14
        points = MultiPoint([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0 + very_small_float]])
        with self.assertRaises(ValueError):
            create_bounding_area(points=points, buffer=0.1)