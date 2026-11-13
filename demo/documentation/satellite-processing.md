# RUDRAM Satellite Analysis Lab

## Remote Sensing Workflow
- **Sentinel-1 SAR C-Band**: All-weather dual-pol radar backscatter thresholding (dB difference < -3.0 dB) with SRTM slope masking (< 5°).
- **Sentinel-2 MSI Optical**: NDWI surface water expansion and NDVI vegetation loss change detection.
- **Deep Learning**: PyTorch U-Net segmentation interface for multi-class damage detection.
- **Interactive Visualizer**: Before / After split swipe comparison slider.
