# Partner

Methods:

- <code title="get /partner/ping">client.partner.<a href="./src/atom_tickets/resources/partner/partner.py">ping</a>() -> object</code>

## V1

### Showtime

#### Details

Types:

```python
from atom_tickets.types.partner.v1.showtime import (
    ShowtimeDetails,
    DetailGetForMultipleVenuesResponse,
)
```

Methods:

- <code title="post /partner/v1/showtime/details/byIds">client.partner.v1.showtime.details.<a href="./src/atom_tickets/resources/partner/v1/showtime/details.py">get_by_ids</a>(\*\*<a href="src/atom_tickets/types/partner/v1/showtime/detail_get_by_ids_params.py">params</a>) -> <a href="./src/atom_tickets/types/partner/v1/showtime/showtime_details.py">ShowtimeDetails</a></code>
- <code title="get /partner/v1/showtime/details/byVenue/{venueId}">client.partner.v1.showtime.details.<a href="./src/atom_tickets/resources/partner/v1/showtime/details.py">get_by_venue</a>(venue_id, \*\*<a href="src/atom_tickets/types/partner/v1/showtime/detail_get_by_venue_params.py">params</a>) -> <a href="./src/atom_tickets/types/partner/v1/showtime/showtime_details.py">ShowtimeDetails</a></code>
- <code title="post /partner/v1/showtime/details/forVenues">client.partner.v1.showtime.details.<a href="./src/atom_tickets/resources/partner/v1/showtime/details.py">get_for_multiple_venues</a>(\*\*<a href="src/atom_tickets/types/partner/v1/showtime/detail_get_for_multiple_venues_params.py">params</a>) -> <a href="./src/atom_tickets/types/partner/v1/showtime/detail_get_for_multiple_venues_response.py">DetailGetForMultipleVenuesResponse</a></code>

### Venue

#### Details

Types:

```python
from atom_tickets.types.partner.v1.venue import PageInfo, VenueDetails
```

Methods:

- <code title="post /partner/v1/venue/details/byIds">client.partner.v1.venue.details.<a href="./src/atom_tickets/resources/partner/v1/venue/details.py">get_by_ids</a>(\*\*<a href="src/atom_tickets/types/partner/v1/venue/detail_get_by_ids_params.py">params</a>) -> <a href="./src/atom_tickets/types/partner/v1/venue/venue_details.py">VenueDetails</a></code>
- <code title="get /partner/v1/venue/details/byLocation">client.partner.v1.venue.details.<a href="./src/atom_tickets/resources/partner/v1/venue/details.py">get_by_location</a>(\*\*<a href="src/atom_tickets/types/partner/v1/venue/detail_get_by_location_params.py">params</a>) -> <a href="./src/atom_tickets/types/partner/v1/venue/venue_details.py">VenueDetails</a></code>
- <code title="get /partner/v1/venue/details/search">client.partner.v1.venue.details.<a href="./src/atom_tickets/resources/partner/v1/venue/details.py">search</a>(\*\*<a href="src/atom_tickets/types/partner/v1/venue/detail_search_params.py">params</a>) -> <a href="./src/atom_tickets/types/partner/v1/venue/venue_details.py">VenueDetails</a></code>

#### ByVendorVenueID

Methods:

- <code title="get /partner/v1/venues/byVendorVenueId/{vendorVenueId}">client.partner.v1.venue.by_vendor_venue_id.<a href="./src/atom_tickets/resources/partner/v1/venue/by_vendor_venue_id/by_vendor_venue_id.py">get</a>(vendor_venue_id) -> <a href="./src/atom_tickets/types/partner/v1/venue/venue_details.py">VenueDetails</a></code>

##### Showtimes

Methods:

- <code title="get /partner/v1/venues/byVendorVenueId/{vendorVenueId}/showtimes/byVendorShowtimeId/{vendorShowtimeId}">client.partner.v1.venue.by_vendor_venue_id.showtimes.<a href="./src/atom_tickets/resources/partner/v1/venue/by_vendor_venue_id/showtimes.py">get_by_vendor_showtime_id</a>(vendor_showtime_id, \*, vendor_venue_id) -> <a href="./src/atom_tickets/types/partner/v1/showtime/showtime_details.py">ShowtimeDetails</a></code>

#### Showtimes

Methods:

- <code title="get /partner/v1/venues/{venueId}/showtimes/byVendorShowtimeId/{vendorShowtimeId}">client.partner.v1.venue.showtimes.<a href="./src/atom_tickets/resources/partner/v1/venue/showtimes.py">get_by_vendor_showtime_id</a>(vendor_showtime_id, \*, venue_id) -> <a href="./src/atom_tickets/types/partner/v1/showtime/showtime_details.py">ShowtimeDetails</a></code>

### Production

Methods:

- <code title="get /partner/v1/productions/byVendorProductionId/{vendorProductionId}">client.partner.v1.production.<a href="./src/atom_tickets/resources/partner/v1/production/production.py">get_by_vendor_production_id</a>(vendor_production_id) -> <a href="./src/atom_tickets/types/partner/v1/production/production_details.py">ProductionDetails</a></code>

#### IDs

Types:

```python
from atom_tickets.types.partner.v1.production import IDGetByVenueResponse
```

Methods:

- <code title="get /partner/v1/production/ids/byVenue/{venueId}">client.partner.v1.production.ids.<a href="./src/atom_tickets/resources/partner/v1/production/ids.py">get_by_venue</a>(venue_id, \*\*<a href="src/atom_tickets/types/partner/v1/production/id_get_by_venue_params.py">params</a>) -> <a href="./src/atom_tickets/types/partner/v1/production/id_get_by_venue_response.py">IDGetByVenueResponse</a></code>

#### Details

Types:

```python
from atom_tickets.types.partner.v1.production import ProductionDetails
```

Methods:

- <code title="post /partner/v1/production/details/byIds">client.partner.v1.production.details.<a href="./src/atom_tickets/resources/partner/v1/production/details.py">get_by_ids</a>(\*\*<a href="src/atom_tickets/types/partner/v1/production/detail_get_by_ids_params.py">params</a>) -> <a href="./src/atom_tickets/types/partner/v1/production/production_details.py">ProductionDetails</a></code>

#### Search

Methods:

- <code title="get /partner/v1/production/search/byName">client.partner.v1.production.search.<a href="./src/atom_tickets/resources/partner/v1/production/search.py">get_by_name</a>(\*\*<a href="src/atom_tickets/types/partner/v1/production/search_get_by_name_params.py">params</a>) -> <a href="./src/atom_tickets/types/partner/v1/production/production_details.py">ProductionDetails</a></code>
