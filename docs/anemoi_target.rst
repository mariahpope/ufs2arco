Anemoi Targets
############

Introduce anemoi style target..

anemoi
-------------------------

Provide explanation

Example use::
  
  target:
    name: anemoi
    sort_channels_by_levels: True
    compute_temporal_residual_statistics: True
    statistics_period:
      start: 2022-02-01T06
      end: 2022-02-28T18
    forcings:
      - cos_latitude
      - sin_latitude
      - cos_longitude
      - sin_longitude
      - cos_julian_day
      - sin_julian_day
      - cos_local_time
      - sin_local_time
      - cos_solar_zenith_angle
      - insolation
    chunks:
      time: 1
      variable: -1
      ensemble: 1
      cell: -1

anemoi_inference_with_forcings
-------------------------

Provide explanation

Example use::

  target:
    name: anemoi_inference_with_forcings
    save_additional_step: True
    sort_channels_by_levels: True
    forcings:
      - cos_latitude
      - sin_latitude
      - cos_longitude
      - sin_longitude
      - cos_julian_day
      - sin_julian_day
      - cos_local_time
      - sin_local_time
      - cos_solar_zenith_angle
      - insolation
    chunks:
      time: 1
      variable: -1
      ensemble: 1
      cell: -1
      