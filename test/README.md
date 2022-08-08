Unit tests
============

In order to run test.py, you must have an account on the [Scihub Copernicus website](https://scihub.copernicus.eu/dhus/#/home). If needed, you can find the registration steps [here](https://scihub.copernicus.eu/userguide/SelfRegistration).

<p align="center">
<img src="https://github.com/SamuelDubos/SatelliteBathymetry/blob/main/registration.png">
<p/>

When it is done, you can type the following command, replacing ```YourUsername``` and ```YourPassword```:
```
pytest test.py -v --username YourUsername --password YourPassword
```
Make sure the folder in which you are running test.py also contains the conftest.py file.
