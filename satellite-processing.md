# RUDRAM Satellite Analysis Lab & Remote Sensing Processing

## 1. Remote Sensing Sensors

1. **Sentinel-1 SAR C-Band**: Synthetic Aperture Radar (SAR) Dual-Pol (VV/VH) all-weather, day/night radar penetration through monsoonal cloud cover.
2. **Sentinel-2 MSI Optical**: 10m multi-spectral optical reflectance for surface water index (NDWI) and vegetation damage (NDVI).
3. **PyTorch U-Net CNN**: Deep learning segmentation interface for multi-class building and flood damage classification.

---

## 2. Sentinel-1 SAR Flood Extraction Workflow

```
Input AOI & Date Range (Pre/Post Event)
                 │
                 ▼
Query Copernicus Sentinel-1 GRD Collection
                 │
                 ▼
Apply Refined Lee Speckle Noise Filter
                 │
                 ▼
Calculate Backscatter Difference (dB Change < -3.0 dB)
                 │
                 ▼
Apply SRTM DEM Slope Threshold Mask (< 5° slope)
                 │
                 ▼
Vectorize Standing Inundation Polygons into GeoJSON
```

---

## 3. Spectral Indices

- **NDWI (Normalized Difference Water Index)**:
  $$\text{NDWI} = \frac{\text{Green} - \text{NIR}}{\text{Green} + \text{NIR}} = \frac{B3 - B8}{B3 + B8}$$
- **NDVI (Normalized Difference Vegetation Index)**:
  $$\text{NDVI} = \frac{\text{NIR} - \text{Red}}{\text{NIR} + \text{Red}} = \frac{B8 - B4}{B8 + B4}$$
