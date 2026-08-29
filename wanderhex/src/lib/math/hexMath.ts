import type { GridOrientation, Point2D } from '../types';

export interface HexGeometry {
  width: number;
  height: number;
  xSpacing: number;
  ySpacing: number;
  radius: number;
}

export function calculateHexGeometry(orientation: GridOrientation, hexRadius: number): HexGeometry {
  let width: number;
  let height: number;
  let xSpacing: number;
  let ySpacing: number;

  if (orientation === 'pointy') {
    width = Math.sqrt(3) * hexRadius;
    height = 2 * hexRadius;
    xSpacing = width;
    ySpacing = 1.5 * hexRadius;
  } else {
    // flat-topped
    width = 2 * hexRadius;
    height = Math.sqrt(3) * hexRadius;
    xSpacing = 1.5 * hexRadius;
    ySpacing = height;
  }

  return { width, height, xSpacing, ySpacing, radius: hexRadius };
}

/**
 * Calculates pixel coordinates for a column and row in a rectangular grid,
 * accounting for pointy (odd-r horizontal offset) and flat (odd-q vertical offset).
 */
export function getRectHexCenter(
  col: number,
  row: number,
  geo: HexGeometry,
  orientation: GridOrientation,
  originX: number,
  originY: number
): Point2D {
  if (orientation === 'pointy') {
    return {
      x: originX + col * geo.xSpacing + (row % 2 !== 0 ? geo.xSpacing / 2 : 0),
      y: originY + row * geo.ySpacing
    };
  }
  return {
    x: originX + col * geo.xSpacing,
    y: originY + row * geo.ySpacing + (col % 2 !== 0 ? geo.ySpacing / 2 : 0)
  };
}

export function getHexCorners(center: Point2D, radius: number, orientation: GridOrientation): Point2D[] {
  const corners: Point2D[] = [];
  // Pointy starts at 30 deg (PI / 6); Flat-topped starts at 0 deg
  const angleOffset = orientation === 'pointy' ? Math.PI / 6 : 0;
  for (let i = 0; i < 6; i++) {
    const angle = angleOffset + (i * Math.PI) / 3;
    corners.push({
      x: center.x + radius * Math.cos(angle),
      y: center.y + radius * Math.sin(angle)
    });
  }
  return corners;
}

export function isPointInPolygon(point: Point2D, corners: Point2D[]): boolean {
  let inside = false;
  for (let i = 0, j = corners.length - 1; i < corners.length; j = i++) {
    const xi = corners[i].x;
    const yi = corners[i].y;
    const xj = corners[j].x;
    const yj = corners[j].y;
    const intersect = yi > point.y !== yj > point.y && point.x < ((xj - xi) * (point.y - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}