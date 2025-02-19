# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This module defines annulus regions in both pixel and sky coordinates.
"""

import abc
import operator

import astropy.units as u
from astropy.wcs.utils import pixel_to_skycoord

from ..core.attributes import (ScalarPix, ScalarLength, QuantityLength,
                               ScalarSky)
from ..core.compound import CompoundPixelRegion
from ..core.core import PixelRegion, SkyRegion
from ..core.metadata import RegionMeta, RegionVisual
from ..core.pixcoord import PixCoord
from ..shapes.circle import CirclePixelRegion
from ..shapes.ellipse import EllipsePixelRegion, EllipseSkyRegion
from ..shapes.rectangle import RectanglePixelRegion, RectangleSkyRegion
from .._utils.wcs_helpers import pixel_scale_angle_at_skycoord

__all__ = ['AnnulusPixelRegion', 'AsymmetricAnnulusPixelRegion',
           'AsymmetricAnnulusSkyRegion',
           'CircleAnnulusPixelRegion', 'CircleAnnulusSkyRegion',
           'EllipseAnnulusPixelRegion', 'EllipseAnnulusSkyRegion',
           'RectangleAnnulusPixelRegion', 'RectangleAnnulusSkyRegion']


class AnnulusPixelRegion(PixelRegion, abc.ABC):
    """
    A base class for annulus pixel regions.
    """

    @property
    def _compound_region(self):
        return CompoundPixelRegion(self._inner_region, self._outer_region,
                                   operator.xor, self.meta, self.visual)

    @property
    def area(self):
        return self._outer_region.area - self._inner_region.area

    @property
    def bounding_box(self):
        return self._outer_region.bounding_box

    def contains(self, pixcoord):
        return self._compound_region.contains(pixcoord)

    def as_artist(self, origin=(0, 0), **kwargs):
        return self._compound_region.as_artist(origin, **kwargs)

    def to_mask(self, mode="center", subpixels=5):
        return self._compound_region.to_mask(mode, subpixels)

    def rotate(self, center, angle):
        """
        Rotate the region.

        Positive ``angle`` corresponds to counter-clockwise rotation.

        Parameters
        ----------
        center : `~regions.PixCoord`
            The rotation center point.
        angle : `~astropy.coordinates.Angle`
            The rotation angle.

        Returns
        -------
        region : `~regions.AnnulusPixelRegion`
            The rotated region (which is an independent copy).
        """
        changes = {}
        changes['center'] = self.center.rotate(center, angle)
        if hasattr(self, 'angle'):
            changes['angle'] = self.angle + angle
        return self.copy(**changes)


class CircleAnnulusPixelRegion(AnnulusPixelRegion):
    """
    A circular annulus in pixel coordinates.

    Parameters
    ----------
    center : `~regions.PixCoord`
        The position of the center of the annulus.
    inner_radius : float
        The inner radius of the annulus.
    outer_radius : float
        The outer radius of the annulus.
    meta : `~regions.RegionMeta`, optional
        A dictionary that stores the meta attributes of this region.
    visual : `~regions.RegionVisual`, optional
        A dictionary that stores the visual meta attributes of this
        region.

    Examples
    --------
    .. plot::
        :include-source:

        from regions import PixCoord, CircleAnnulusPixelRegion
        import matplotlib.pyplot as plt

        x, y = 6, 6
        inner_radius = 5.5
        outer_radius = 8
        fig, ax = plt.subplots(1, 1)

        center = PixCoord(x=x, y=y)
        reg = CircleAnnulusPixelRegion(center=center,
                                       inner_radius=inner_radius,
                                       outer_radius=outer_radius)
        patch = reg.as_artist(facecolor='none', edgecolor='red', lw=2)
        ax.add_patch(patch)

        plt.xlim(-5, 20)
        plt.ylim(-5, 20)
        ax.set_aspect('equal')
    """

    _component_class = CirclePixelRegion
    _params = ('center', 'inner_radius', 'outer_radius')
    center = ScalarPix('center')
    inner_radius = ScalarLength('inner_radius')
    outer_radius = ScalarLength('outer_radius')

    def __init__(self, center, inner_radius, outer_radius, meta=None,
                 visual=None):
        self.center = center
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.meta = meta or RegionMeta()
        self.visual = visual or RegionVisual()

    @property
    def _inner_region(self):
        return self._component_class(self.center, self.inner_radius,
                                     self.meta, self.visual)

    @property
    def _outer_region(self):
        return self._component_class(self.center, self.outer_radius,
                                     self.meta, self.visual)

    def to_sky(self, wcs):
        center = pixel_to_skycoord(self.center.x, self.center.y, wcs)
        _, pixscale, _ = pixel_scale_angle_at_skycoord(center, wcs)
        inner_radius = self.inner_radius * u.pix * pixscale
        outer_radius = self.outer_radius * u.pix * pixscale
        return CircleAnnulusSkyRegion(center, inner_radius, outer_radius,
                                      self.meta, self.visual)


class CircleAnnulusSkyRegion(SkyRegion):
    """
    A circular annulus in sky coordinates.

    Parameters
    ----------
    center : `~astropy.coordinates.SkyCoord`
        The position of the center of the annulus.
    inner_radius : `~astropy.units.Quantity`
        The inner radius of the annulus in angular units.
    outer_radius : `~astropy.units.Quantity`
        The outer radius of the annulus in angular units.
    meta : `~regions.RegionMeta`, optional
        A dictionary that stores the meta attributes of this region.
    visual : `~regions.RegionVisual`, optional
        A dictionary that stores the visual meta attributes of this
        region.
    """

    _params = ('center', 'inner_radius', 'outer_radius')
    center = ScalarSky('center')
    inner_radius = QuantityLength('inner_radius')
    outer_radius = QuantityLength('outer_radius')

    def __init__(self, center, inner_radius, outer_radius, meta=None,
                 visual=None):
        self.center = center
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.meta = meta or RegionMeta()
        self.visual = visual or RegionVisual()

    def to_pixel(self, wcs):
        center, pixscale, _ = pixel_scale_angle_at_skycoord(self.center, wcs)
        inner_radius = (self.inner_radius / pixscale).to(u.pix).value
        outer_radius = (self.outer_radius / pixscale).to(u.pix).value
        return CircleAnnulusPixelRegion(center, inner_radius, outer_radius,
                                        self.meta, self.visual)


class AsymmetricAnnulusPixelRegion(AnnulusPixelRegion):
    """
    Helper class for asymmetric annuli sky regions.

    Used for ellipse and rectangle pixel annulus regions.

    Parameters
    ----------
    center : `~regions.PixCoord`
        The position of the center of the annulus.
    center : `~regions.PixCoord`
        The position of the center of the annulus.
    inner_width : float
        The inner width of the annulus (before rotation) in pixels.
    inner_height : float
        The inner height of the annulus (before rotation) in pixels.
    outer_width : float
        The outer width of the annulus (before rotation) in pixels.
    outer_height : float
        The outer height of the annulus (before rotation) in pixels.
    angle : `~astropy.units.Quantity`, optional
        The rotation angle of the annulus, measured anti-clockwise. If
        set to zero (the default), the width axis is lined up with the x
        axis.
    """

    _params = ('center', 'inner_width', 'inner_height', 'outer_width',
               'outer_height', 'angle')
    center = ScalarPix('center')
    inner_width = ScalarLength('inner_width')
    outer_width = ScalarLength('outer_width')
    inner_height = ScalarLength('inner_height')
    outer_height = ScalarLength('outer_height')
    angle = QuantityLength('angle')

    def __init__(self, center, inner_width, outer_width, inner_height,
                 outer_height, angle=0 * u.deg, meta=None, visual=None):
        self.center = center
        self.inner_width = inner_width
        self.outer_width = outer_width
        self.inner_height = inner_height
        self.outer_height = outer_height
        self.angle = angle
        self.meta = meta or RegionMeta()
        self.visual = visual or RegionVisual()

    @property
    def _inner_region(self):
        return self._component_class(self.center, self.inner_width,
                                     self.inner_height, self.angle,
                                     self.meta, self.visual)

    @property
    def _outer_region(self):
        return self._component_class(self.center, self.outer_width,
                                     self.outer_height, self.angle,
                                     self.meta, self.visual)

    def to_sky_args(self, wcs):
        center = pixel_to_skycoord(self.center.x, self.center.y, wcs)
        _, pixscale, north_angle = pixel_scale_angle_at_skycoord(center, wcs)
        inner_width = (self.inner_width * u.pix * pixscale).to(u.arcsec)
        inner_height = (self.inner_height * u.pix * pixscale).to(u.arcsec)
        outer_width = (self.outer_width * u.pix * pixscale).to(u.arcsec)
        outer_height = (self.outer_height * u.pix * pixscale).to(u.arcsec)
        angle = self.angle - (north_angle - 90 * u.deg)

        return (center, inner_width, inner_height, outer_width, outer_height,
                angle)


class AsymmetricAnnulusSkyRegion(SkyRegion):
    """
    Helper class for asymmetric annuli sky regions.

    Used for ellipse and rectangle sky annulus regions.

    Parameters
    ----------
    center : `~astropy.coordinates.SkyCoord`
        The position of the center of the annulus.
    inner_width : `~astropy.units.Quantity`
        The inner width of the annulus (before rotation) as an angle.
    inner_height : `~astropy.units.Quantity`
        The inner height of the annulus (before rotation) as an angle.
    outer_width : `~astropy.units.Quantity`
        The outer width of the annulus (before rotation) as an angle.
    outer_height : `~astropy.units.Quantity`
        The outer height of the annulus (before rotation) as an angle.
    angle : `~astropy.units.Quantity`, optional
        The rotation angle of the annulus, measured anti-clockwise. If
        set to zero (the default), the width axis is lined up with the
        longitude axis of the celestial coordinates
    meta : `~regions.RegionMeta`, optional
        A dictionary that stores the meta attributes of this region.
    visual : `~regions.RegionVisual`, optional
        A dictionary that stores the visual meta attributes of this
        region.
    """

    _params = ('center', 'inner_width', 'inner_height', 'outer_width',
               'outer_height', 'angle')

    center = ScalarSky('center')
    inner_width = QuantityLength('inner_width')
    outer_width = QuantityLength('outer_width')
    inner_height = QuantityLength('inner_height')
    outer_height = QuantityLength('outer_height')
    angle = QuantityLength('angle')

    def __init__(self, center, inner_width, outer_width, inner_height,
                 outer_height, angle=0 * u.deg, meta=None, visual=None):
        self.center = center
        self.inner_width = inner_width
        self.outer_width = outer_width
        self.inner_height = inner_height
        self.outer_height = outer_height
        self.angle = angle
        self.meta = meta or RegionMeta()
        self.visual = visual or RegionVisual()

    def to_pixel_args(self, wcs):
        center, pixscale, north_angle = pixel_scale_angle_at_skycoord(
            self.center, wcs)
        center = PixCoord(center.x, center.y)
        inner_width = (self.inner_width / pixscale).to(u.pix).value
        inner_height = (self.inner_height / pixscale).to(u.pix).value
        outer_width = (self.outer_width / pixscale).to(u.pix).value
        outer_height = (self.outer_height / pixscale).to(u.pix).value
        angle = self.angle + (north_angle - 90 * u.deg)

        return (center, inner_width, inner_height, outer_width, outer_height,
                angle)


class EllipseAnnulusPixelRegion(AsymmetricAnnulusPixelRegion):
    """
    A elliptical annulus in pixel coordinates.

    Parameters
    ----------
    center : `~regions.PixCoord`
        The position of the center of the elliptical annulus.
    inner_width : float
        The inner width of the elliptical annulus (before rotation) in
        pixels.
    inner_height : float
        The inner height of the elliptical annulus (before rotation) in
        pixels.
    outer_width : float
        The outer width of the elliptical annulus (before rotation) in
        pixels.
    outer_height : float
        The outer height of the elliptical annulus (before rotation) in
        pixels.
    angle : `~astropy.units.Quantity`, optional
        The rotation angle of the elliptical annulus, measured
        anti-clockwise. If set to zero (the default), the width axis is
        lined up with the x axis.
    meta : `~regions.RegionMeta`, optional
        A dictionary that stores the meta attributes of this region.
    visual : `~regions.RegionVisual`, optional
        A dictionary that stores the visual meta attributes of this
        region.

    Examples
    --------
    .. plot::
        :include-source:

        from astropy.coordinates import Angle
        from regions import PixCoord, EllipseAnnulusPixelRegion
        import matplotlib.pyplot as plt

        x, y = 6, 6
        inner_width = 5.5
        inner_height = 3.5
        outer_width = 8.5
        outer_height = 6.5
        angle = Angle("45deg")

        fig, ax = plt.subplots(1, 1)

        center = PixCoord(x=x, y=y)
        reg = EllipseAnnulusPixelRegion(center=center, inner_width=inner_width,
                                        inner_height=inner_height,
                                        outer_width=outer_width,
                                        outer_height=outer_height, angle=angle)
        patch = reg.as_artist(facecolor='none', edgecolor='red', lw=2)
        ax.add_patch(patch)

        plt.xlim(-5, 20)
        plt.ylim(-5, 20)
        ax.set_aspect('equal')
    """

    _component_class = EllipsePixelRegion

    def to_sky(self, wcs):
        return EllipseAnnulusSkyRegion(
            *self.to_sky_args(wcs), meta=self.meta, visual=self.visual)


class EllipseAnnulusSkyRegion(AsymmetricAnnulusSkyRegion):
    """
    A elliptical annulus in `~astropy.coordinates.SkyCoord` coordinates.

    Parameters
    ----------
    center : `~astropy.coordinates.SkyCoord`
        The position of the center of the elliptical annulus.
    inner_width : `~astropy.units.Quantity`
        The inner width of the elliptical annulus (before rotation) as
        an angle.
    inner_height : `~astropy.units.Quantity`
        The inner height of the elliptical annulus (before rotation) as
        an angle.
    outer_width : `~astropy.units.Quantity`
        The outer width of the elliptical annulus (before rotation) as
        an angle.
    outer_height : `~astropy.units.Quantity`
        The outer height of the elliptical annulus (before rotation) as
        an angle.
    angle : `~astropy.units.Quantity`, optional
        The rotation angle of the elliptical annulus, measured
        anti-clockwise. If set to zero (the default), the width axis is
        lined up with the longitude axis of the celestial coordinates
    meta : `~regions.RegionMeta`, optional
        A dictionary that stores the meta attributes of this region.
    visual : `~regions.RegionVisual`, optional
        A dictionary that stores the visual meta attributes of this
        region.
    """

    _component_class = EllipseSkyRegion

    def to_pixel(self, wcs):
        return EllipseAnnulusPixelRegion(
            *self.to_pixel_args(wcs), meta=self.meta, visual=self.visual)


class RectangleAnnulusPixelRegion(AsymmetricAnnulusPixelRegion):
    """
    A rectangular annulus in pixel coordinates.

    Parameters
    ----------
    center : `~regions.PixCoord`
        The position of the center of the rectangular annulus.
    inner_width : float
        The inner width of the rectangular annulus (before rotation) in
        pixels.
    inner_height : float
        The inner height of the rectangular annulus (before rotation) in
        pixels.
    outer_width : float
        The outer width of the rectangular annulus (before rotation) in
        pixels.
    outer_height : float
        The outer height of the rectangular annulus (before rotation) in
        pixels.
    angle : `~astropy.units.Quantity`, optional
        The rotation angle of the rectangular annulus, measured
        anti-clockwise. If set to zero (the default), the width axis is
        lined up with the x axis.
    meta : `~regions.RegionMeta`, optional
        A dictionary that stores the meta attributes of this region.
    visual : `~regions.RegionVisual`, optional
        A dictionary that stores the visual meta attributes of this
        region.

    Examples
    --------
    .. plot::
        :include-source:

        from astropy.coordinates import Angle
        from regions import PixCoord, RectangleAnnulusPixelRegion
        import matplotlib.pyplot as plt

        x, y = 6, 6
        inner_width = 5.5
        inner_height = 3.5
        outer_width = 8.5
        outer_height = 6.5
        angle = Angle("45deg")

        fig, ax = plt.subplots(1, 1)

        center = PixCoord(x=x, y=y)
        reg = RectangleAnnulusPixelRegion(center=center,
                                          inner_width=inner_width,
                                          inner_height=inner_height,
                                          outer_width=outer_width,
                                          outer_height=outer_height,
                                          angle=angle)
        patch = reg.as_artist(facecolor='none', edgecolor='red', lw=2)
        ax.add_patch(patch)

        plt.xlim(-5, 20)
        plt.ylim(-5, 20)
        ax.set_aspect('equal')
    """

    _component_class = RectanglePixelRegion

    def to_sky(self, wcs):
        return RectangleAnnulusSkyRegion(
            *self.to_sky_args(wcs), meta=self.meta, visual=self.visual)


class RectangleAnnulusSkyRegion(AsymmetricAnnulusSkyRegion):
    """
    A rectangular annulus in `~astropy.coordinates.SkyCoord`
    coordinates.

    Parameters
    ----------
    center : `~astropy.coordinates.SkyCoord`
        The position of the center of the rectangular annulus.
    inner_width : `~astropy.units.Quantity`
        The inner width of the rectangular annulus (before rotation) as
        an angle.
    inner_height : `~astropy.units.Quantity`
        The inner height of the rectangular annulus (before rotation) as
        an angle.
    outer_width : `~astropy.units.Quantity`
        The outer width of the rectangular annulus (before rotation) as
        an angle.
    outer_height : `~astropy.units.Quantity`
        The outer height of the rectangular annulus (before rotation) as
        an angle.
    angle : `~astropy.units.Quantity`, optional
        The rotation angle of the rectangular annulus, measured
        anti-clockwise. If set to zero (the default), the width axis is
        lined up with the longitude axis of the celestial coordinates
    meta : `~regions.RegionMeta`, optional
        A dictionary that stores the meta attributes of this region.
    visual : `~regions.RegionVisual`, optional
        A dictionary that stores the visual meta attributes of this
        region.
    """

    _component_class = RectangleSkyRegion

    def to_pixel(self, wcs):
        return RectangleAnnulusPixelRegion(
            *self.to_pixel_args(wcs), meta=self.meta, visual=self.visual)
