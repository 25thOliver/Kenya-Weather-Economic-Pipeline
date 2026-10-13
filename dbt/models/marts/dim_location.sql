/*
  dim_location - static dimension of Kenyan monitoring cities.
  Coordinates sourced from config/sources.yml.
  One row per city; used to enrich weather fact tables.
*/

SELECT *
FROM (
    VALUES
        ('Nairobi',  -1.286389,  36.817223, 'Nairobi County',     'East'),
        ('Mombasa',  -4.043477,  39.668206, 'Mombasa County',     'Coast'),
        ('Kisumu',   -0.102210,  34.761710, 'Kisumu County',      'West'),
        ('Nakuru',   -0.303099,  36.080025, 'Nakuru County',      'Central'),
        ('Eldoret',   0.514277,  35.269779, 'Uasin Gishu County', 'North Rift'),
        ('Garissa',  -0.453229,  39.646098, 'Garissa County',     'North East')
) AS t (
    location,
    latitude,
    longitude,
    county,
    region
)
