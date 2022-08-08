Satellite-Derived Bathymetry Toolkit
====================================


| **Acquire** | **Process** | **Interpolate** | **Calibrate**  | **Assemble** |
|:-:|:-:|:-:|:-:|:-:|
| Search and download relevant products | Apply Ratio Transform Algorithm (RTA) | Interpolate the sonar data (Bella Desgagnés) | Calibrate regarding the computed constants | Assemble the files and write the output |


- **Acquire Sentinel2 products: ```acquire.py```**
  
  In this file, we define the Sentinel2 class which allows us to search and download products from the Sentinel2 satellite program, whose data are stored     on the site [Scihub Copernicus](https://scihub.copernicus.eu/).
  
  <p align="center">
  <img src="https://github.com/SamuelDubos/SatelliteBathymetry/blob/main/acquire.png">
  <p/>
  
  The ```search``` and ```downolad``` methods mimic the actions available on the [page](https://scihub.copernicus.eu/dhus/#/home) above.

- **Collect and organize the products: ```collect.py```**
  
