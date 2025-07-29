import io
import logging
import re
from concurrent.futures import ThreadPoolExecutor

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import odc
import odc.stac
import pandas as pd
import planetary_computer
import pystac
import rioxarray  # noqa: F401
import xarray as xr
from shapely.geometry import Polygon
from tqdm.auto import tqdm

from environmental_risk_metrics.base import BaseEnvironmentalMetric
from environmental_risk_metrics.utils.planetary_computer import (
    get_planetary_computer_items,
)

matplotlib.use(backend="Agg")

logger = logging.getLogger(__name__)


class Sentinel2(BaseEnvironmentalMetric):
    def __init__(
        self,
        start_date: str,
        end_date: str,
        gdf: gpd.GeoDataFrame,
        resolution: int = 10,
        entire_image_cloud_cover_threshold: int = 10,
        cropped_image_cloud_cover_threshold: int = 80,
        max_workers: int = 10,
        is_bare_soil_threshold: float = 0.25,
    ):
        sources = [
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            "https://planetarycomputer.microsoft.com/api/stac/v1",
        ]
        description = "Sentinel-2 data from Planetary Computer"

        super().__init__(sources=sources, description=description)
        self.collections = ["sentinel-2-l2a"]
        self.resolution = resolution
        self.entire_image_cloud_cover_threshold = entire_image_cloud_cover_threshold
        self.cropped_image_cloud_cover_threshold = cropped_image_cloud_cover_threshold
        self.max_workers = max_workers
        self.start_date = start_date
        self.end_date = end_date
        self.gdf = gdf.to_crs(epsg=4326)
        self.items = None
        self.xarray_data = None
        self.ndvi_data = None
        self.ndvi_thumbnails_data = None
        self.mean_ndvi_data = None
        self.is_bare_soil_threshold = is_bare_soil_threshold
        logger.debug("Initializing Sentinel2 client")

    def get_items(
        self,
        entire_image_cloud_cover_threshold: int = 20,
    ) -> list[pystac.Item]:
        """
        Search for Sentinel-2 items within a given date range and polygon.

        Args:
            entire_image_cloud_cover_threshold: Maximum cloud cover percentage to include in the search
            cropped_image_cloud_cover_threshold: Maximum cloud cover within a cropped image to include in the search

        Returns:
            List of pystac.Item objects
        """
        if self.items is not None:
            return self.items

        gdf = self.gdf.to_crs(epsg=4326)
        items = []

        def fetch_items(polygon):
            return get_planetary_computer_items(
                collections=self.collections,
                start_date=self.start_date,
                end_date=self.end_date,
                polygon=polygon,
                entire_image_cloud_cover_threshold=entire_image_cloud_cover_threshold,
            )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            items = list(tqdm(executor.map(fetch_items, gdf.geometry), total=len(gdf.geometry)))

        self.items = items
        return self.items

    def load_xarray(
        self,
        bands: list[str] = ["B02", "B03", "B04", "B08"],
        show_progress: bool = True,
        filter_cloud_cover: bool = True,
    ) -> xr.Dataset:
        """Load Sentinel-2 data for a given date range and polygon into an xarray Dataset.

        Args:
            bands: List of band names to load. Defaults to ["B02", "B03", "B04", "B08"]
            resolution: Resolution in meters. Defaults to 10
            max_workers: Maximum number of workers to use for loading the data
            show_progress: Whether to show a progress bar
            filter_cloud_cover: Whether to filter the data based on cloud cover
            entire_image_cloud_cover_threshold: Maximum cloud cover percentage to include in the search
            cropped_image_cloud_cover_threshold: Maximum cloud cover within a cropped image to include in the search

        Returns:
            xarray Dataset containing the Sentinel-2 data
        """
        if self.xarray_data is not None:
            return self.xarray_data
        logger.debug(
            f"Loading Sentinel-2 data for bands {bands} at {self.resolution}m resolution"
        )
        items_list = self.get_items(
            entire_image_cloud_cover_threshold=self.entire_image_cloud_cover_threshold,
        )

        if not items_list:
            logger.error(
                "No Sentinel-2 items found for the given date range and polygon"
            )
            raise ValueError(
                "No Sentinel-2 items found for the given date range and polygon"
            )

        # Sign the items to get access
        logger.debug("Signing items for access")
        self.xarray_data = []
        for items, geometry in tqdm(
            zip(items_list, self.gdf.geometry), total=len(self.gdf.geometry)
        ):
            signed_items = [planetary_computer.sign(i) for i in items]

            thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)

            # Load the data into an xarray Dataset
            logger.debug("Loading data into xarray Dataset")
            progress = tqdm
            ds = odc.stac.load(
                items=signed_items,
                bands=bands + ["SCL"],
                resolution=self.resolution,
                pool=thread_pool,
                geopolygon=geometry,
                progress=progress if show_progress else None,
            )

            if self.cropped_image_cloud_cover_threshold:
                logger.debug("Filtering data based on cloud cover using SCL band")
                cloud_clear_mask = (ds.SCL == 4) | (ds.SCL == 5)
                cloud_cover_pct = (1 - cloud_clear_mask.mean(dim=["x", "y"])) * 100
                logger.debug(
                    f"Cloud cover percentage: {cloud_cover_pct}. Filtering data based on {self.cropped_image_cloud_cover_threshold}% cloud cover threshold"
                )
                logger.debug(f"Dataset time steps before filtering: {len(ds.time)}")
                ds = ds.sel(
                    time=cloud_cover_pct <= self.cropped_image_cloud_cover_threshold
                )
                logger.debug(
                    f"Filtered dataset to {len(ds.time)} time steps based on {self.cropped_image_cloud_cover_threshold}% cloud cover threshold"
                )

            if filter_cloud_cover:
                cloud_clear_mask = (ds.SCL == 4) | (ds.SCL == 5)
                ds = ds.where(cloud_clear_mask, drop=True)

            logger.debug("Successfully loaded Sentinel-2 data")
            self.xarray_data.append(ds)
        return self.xarray_data

    def load_ndvi_images(
        self,
        filter_cloud_cover: bool = True,
    ) -> xr.Dataset:
        """Load NDVI data for a given date range and polygon.

        Args:
            filter_cloud_cover: Whether to filter the data based on cloud cover

        Returns:
            xarray Dataset containing the NDVI data
        """
        if self.ndvi_data is not None:
            return self.ndvi_data
        logger.debug("Loading NDVI data")
        self.ndvi_data = []
        for ds in self.load_xarray(
            bands=["B08", "B04"],
            filter_cloud_cover=filter_cloud_cover,
        ):
            logger.debug("Calculating NDVI from bands B08 and B04")
            ndvi = (ds.B08 - ds.B04) / (ds.B08 + ds.B04)
            logger.debug("Successfully calculated NDVI")
            self.ndvi_data.append(ndvi)
        return self.ndvi_data

    def ndvi_thumbnails(
        self,
        vmin: float = -0.2,
        vmax: float = 0.8,
        boundary_color: str = "red",
        boundary_linewidth: float = 2,
        add_colorbar: bool = False,
        add_labels: bool = False,
        bbox_inches: str = "tight",
        pad_inches: float = 0,
        image_format: str = "jpg",
        timestamp_format: str = "%Y-%m-%d",
    ) -> dict:
        """
        Plot NDVI images and return them as jpgs in a dictionary

        Args:
            ndvi: xarray DataArray containing NDVI data
            polygon: GeoJSON polygon used for the data fetch
            crs: Coordinate reference system of the NDVI data
            figsize: Figure size as (width, height) tuple
            vmin: Minimum value for NDVI color scale
            vmax: Maximum value for NDVI color scale
            boundary_color: Color of the polygon boundary
            boundary_linewidth: Line width of the polygon boundary
            add_colorbar: Whether to add a colorbar to the plot
            add_labels: Whether to add labels to the plot
            bbox_inches: Bounding box setting for saving figure
            pad_inches: Padding when saving figure
            image_format: Format to save images in
            timestamp_format: Format string for timestamp keys

        Returns:
            dict: Dictionary with timestamps as keys and image bytes as values
        """
        if self.ndvi_thumbnails_data is not None:
            return self.ndvi_thumbnails_data
        ndvi_list = self.load_ndvi_images()
        images = {}

        # Convert polygon coordinates to shapely Polygon
        self.ndvi_thumbnails_data = []
        for ndvi, geometry in zip(ndvi_list, self.gdf.geometry):
            crs = ndvi.coords["spatial_ref"].values.item()

            for time in ndvi.time:
                # Create new figure for each timestamp
                fig, ax = plt.subplots()

                # Plot NDVI data and polygon boundary
                ndvi.sel(time=time).plot(
                    ax=ax,
                    vmin=vmin,
                    vmax=vmax,
                    add_colorbar=add_colorbar,
                    add_labels=add_labels,
                )
                gpd.GeoDataFrame(
                    {"geometry": [geometry]}, geometry="geometry", crs=self.gdf.crs
                ).to_crs(crs).boundary.plot(
                    ax=ax, color=boundary_color, linewidth=boundary_linewidth
                )
                ax.set_axis_off()

                # Save plot to bytes buffer
                buf = io.BytesIO()
                plt.savefig(
                    buf,
                    format=image_format,
                    bbox_inches=bbox_inches,
                    pad_inches=pad_inches,
                )
                buf.seek(0)

                # Add to dictionary with timestamp as key
                timestamp = pd.Timestamp(time.values).strftime(timestamp_format)
                images[timestamp] = buf.getvalue()

                # Close figure to free memory
                plt.close(fig)
            self.ndvi_thumbnails_data.append(images)
        return self.ndvi_thumbnails_data

    def calculate_mean_ndvi(
        self,
        interpolate: bool = True,
        all_touched: bool = True,
    ) -> pd.DataFrame:
        """
        Calculate mean NDVI value for the given polygon at each timestamp

        Args:
            interpolate (bool): Whether to interpolate missing values
            all_touched (bool): Whether to use all touched for clipping
        Returns:
            pd.DataFrame: DataFrame with mean NDVI values
        """
        if self.mean_ndvi_data is not None:
            return self.mean_ndvi_data
        logger.debug("Calculating mean NDVI values for polygon")

        ndvi_images_list = self.load_ndvi_images()

        self.mean_ndvi_data = []
        for ndvi_images, geometry in zip(ndvi_images_list, self.gdf.geometry):
            # Convert to rioxarray and clip once for all timestamps
            crs = ndvi_images.coords["spatial_ref"].values.item()
            ndvi_images = ndvi_images.rio.write_crs(crs)
            clipped_data = ndvi_images.rio.clip(
                [geometry], self.gdf.crs, all_touched=all_touched
            )

            # Calculate means for all timestamps at once
            mean_values = clipped_data.mean(dim=["x", "y"]).values

            # Create dictionary mapping timestamps to means
            mean_ndvi = pd.DataFrame(
                mean_values, columns=["ndvi"], index=clipped_data.time.values
            )
            mean_ndvi.index = pd.to_datetime(mean_ndvi.index).date
            if interpolate:
                mean_ndvi = interpolate_ndvi(mean_ndvi, self.start_date, self.end_date)

            if self.is_bare_soil_threshold:
                mean_ndvi["is_bare_soil"] = mean_ndvi["ndvi"] < self.is_bare_soil_threshold

            logger.debug(f"Calculated mean NDVI for {len(mean_ndvi)} timestamps")
            self.mean_ndvi_data.append(mean_ndvi)
        return self.mean_ndvi_data

    def get_data(
        self,
        all_touched: bool = True,
        interpolate: bool = True,
    ) -> pd.DataFrame:
        """Get mean NDVI values for a given polygon"""
        mean_ndvi_df_list = self.calculate_mean_ndvi(
            interpolate=interpolate,
            all_touched=all_touched,
        )
        output = []
        for mean_ndvi_df in mean_ndvi_df_list:
            mean_ndvi_df = mean_ndvi_df.reset_index(names="date")
            mean_ndvi_df.index = pd.to_datetime(mean_ndvi_df.index).date
            mean_ndvi_dict = mean_ndvi_df.to_dict(orient="records")
            for record in mean_ndvi_dict:
                if 'ndvi' in record:
                    if pd.isna(record['ndvi']):
                        record.pop("ndvi")
                    else:
                        record['ndvi'] = round(record['ndvi'], 2)
                if 'interpolated_ndvi' in record:
                    record['interpolated_ndvi'] = round(record['interpolated_ndvi'], 2)
            output.append(mean_ndvi_dict)
        return output


def interpolate_ndvi(df: pd.DataFrame, start_date: str, end_date: str):
    """
    Create a DataFrame from NDVI values, interpolate missing dates, and plot the results.

    Args:
        mean_ndvi_values (dict): Dictionary of dates and NDVI values
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format

    Returns:
        pd.DataFrame: DataFrame with interpolated daily NDVI values
    """
    date_range = pd.date_range(
        start=pd.to_datetime(start_date), end=pd.to_datetime(end_date), freq="D"
    )
    df = df.reindex(date_range)
    df["interpolated_ndvi"] = df["ndvi"].interpolate(method="linear", limit_direction="both")
    return df
