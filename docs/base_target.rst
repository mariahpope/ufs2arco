Base Target
############

The base target is the typical representation of gridded 
weather or climate data. It is designed to mirror the structure 
of the chosen data source (e.g. HRRR, GFS). This is the target to 
chose if you are looking for a user-friendly and familiar data 
structure that preseves the layout seen in model outputs. 
All chosen dates and variables are loaded into the standard 
multidimensional array structure (time, latitude, longitude, level). 
The dataset will usually be compatible with any typical scientific 
Python workflow.

This target is best used for general purpose use, exploratory data analysis, 
and any workflow that expects conventional multidimensional arrays.

Example use::
  
  target
    name: base
    rename:
      level: pressure
      geopotential_at_surface: orography
    chunks:
      time: 1
      variable: -1
      ensemble: 1
      cell: -1
