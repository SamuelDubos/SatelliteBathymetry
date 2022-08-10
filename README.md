Satellite-Derived Bathymetry Toolkit
====================================


| **Acquire** | **Process** | **Interpolate** | **Calibrate**  | **Assemble** |
|:-:|:-:|:-:|:-:|:-:|
| Search and download relevant products | Apply Ratio Transform Algorithm (RTA) | Interpolate the sonar data (Bella Desgagnés) | Calibrate regarding the computed constants | Assemble the files and write the output |


- **Acquire Sentinel2 products: ```acquire.py```**

In this file, we define the Sentinel2 class which allows us to ```search``` and ```download``` products from the Sentinel2 satellite program, whose data are stored on the site [Scihub Copernicus](https://scihub.copernicus.eu/).

<p align="center">
  <img src="https://github.com/SamuelDubos/SatelliteBathymetry/blob/main/screenshots/acquire.png" title="Scihub Copernicus OpenHub" style="width:80%">
<p/>

The two methods mimic the actions available on the [page](https://scihub.copernicus.eu/dhus/#/home) above.



- **Collect and organize the products: ```collect.py```**
  
In this file, four methods are defined that allow you to properly manage downloaded products, be it their location or their name. Those methods are then used in ```assemble.py```.

- **Apply the Ratio Transform Algorithm to a product: ```process.py```**

In this file, #TODO#
 
| **SCL (Scene Classification Layer)**: each pixel is assigned to a value, representing its class | **RTA (Ratio Transform Algorithm)**:  the unusable pixels are removed, the algorithm is applied |
|:---:|:---:|
![](https://github.com/SamuelDubos/SatelliteBathymetry/blob/main/screenshots/scl.png) | ![](https://github.com/SamuelDubos/SatelliteBathymetry/blob/main/screenshots/rta.png)
  
- **Interpolate the depths from a given timestamp: ```interpolate.py```**

In this file, #TODO#
  
