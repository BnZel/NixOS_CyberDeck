# NixOS Database Analysis
This is a separate **Intel Compute Stick** to perform data analysis on the [NixOS Cyberdeck](../README.md). The purpose is to have a **portable embedded database** to store and process data (CPU, GPS, Barometric sensors). While this setup can be installed on the same device it's best to differentiate the task to avoid confusion and overhead.

## Overview
![nixexp_architecture](../images/diagrams/nixexp_architecture.jpg)

## Setup
* **[analysis.ipynb](./analysis.ipynb)**
* **cyberdeck.db**
* **[default.nix](./default.nix)**
* **[requirements.txt](./requirements.txt)**

In **default.nix** the following packages will be installed:
```
    # main data analysis tools
    pythonPackages.pandas
    pythonPackages.matplotlib
    pythonPackages.numpy
    pythonPackages.requests

    # optional but recommended
    packages = [ pkgs.screen pkgs.gcc pkgs.gnumake pkgs.pkg-config pkgs.openssl ];

    # needed to load jupyter notebook server
    LD_LIBRARY_PATH = lib.makeLibraryPath [ pkgs.stdenv.cc.cc ];
```
> The Jupyter NixOS package currently has issues, a post made in this [github issue](https://github.com/NixOS/nixpkgs/issues/255923) suggested to use the pip environment to install Jupyter. 

Python packages that aren't avaliable in Nix packages can be installed through ```pip install -r requirements.txt```:
* **GPS:** **[Geopandas](https://geopandas.org/en/stable/)** and related libraries
* **[DuckDB](https://duckdb.org/)**

### **DuckDB**:
Tables are already made for each hardware component.

#### Tables
![duckdb_tables](../images/database/duckdb_tables.png)

#### Barometric Table
![duckdb_barometric](../images/database/duckdb_barometric_table.png)

#### CPU Table
![duckdb_cpu](../images/database/duckdb_cpu_table.png)

#### GPS Table
Filtered for values that aren't non-zeroes. **SPATIAL** extension is needed to display the **lon_lat_geometry** column.
![duckdb_gps](../images/database/duckdb_gps_table.png)

### **Jupyter Notebook**
Can be used as reference.
### Geopandas
GPS points being plotted 

![geopandas_osm_output](../images/data_analysis/geopandas_osm_output.png)

### Matplotlib
Monitoring hardware usage over time. 
#### Barometric Plot
![baro_dt_temp](../images/data_analysis/baro_plot_dt_temp.png)

![baro_dt_pres](../images/data_analysis/baro_plot_dt_pres.png)

![baro_dt_alt](../images/data_analysis/baro_plot_dt_alt.png)

#### CPU Plot
![cpu_dt_temp](../images/data_analysis/cpu_plot_dt_temp.png)

![cpu_dt_load](../images/data_analysis/cpu_plot_dt_load.png)

![cpu_dt_mb](../images/data_analysis/cpu_plot_dt_mb.png)

![cpu_dt_per](../images/data_analysis/cpu_plot_dt_per.png)
