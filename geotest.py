# -*- coding: utf-8 -*-

from geopy import geocoders

# geolocator = Nominatim()
geolocator = geocoders.GoogleV3()
location = geolocator.geocode("Καστρί Νέα Ερυθραία")

print(location.address)
print((location.latitude, location.longitude))
