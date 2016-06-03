const CHHS_API_URL = 'https://chhs.data.ca.gov/resource/mffa-c6z5.json';
const FACILITY_TYPES = [
  "<all>",
  "ADOPTION AGENCY",
  "FOSTER FAMILY AGENCY",
  "FOSTER FAMILY AGENCY SUB"
];
const SEARCH_RADII = [0, 5, 10, 15, 20, 50];
const LABELS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const DEFAULT_ICON = 'http://maps.google.com/mapfiles/ms/icons/red-dot.png';
const SELECTED_ICON = 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
const USER_MARKER_ICON = 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png'

var map = null;
var geocoder = null;
var user_marker = null;
var active_marker = null;
var info_window = null;
var circle = null;

function get_search_type() {
  const type_id = parseInt($('#facility-type option:selected').data('field'));
  return FACILITY_TYPES[type_id];
}

function get_search_radius() {
  const radius_id = parseInt($('#facility-radius option:selected').data('field'));
  return SEARCH_RADII[radius_id];
}

function get_search_location() {
  return $('#facility-location').val();
}

function find_zip_in(result) {
  for (i in result.address_components) {
    const component = result.address_components[i];
    if (component.types.indexOf('postal_code') >= 0) {
      return component.long_name;
    }
  }
}

function init_map() {
  const ca_latlng = {
    "lat" : 36.778261,
    "lng" : -119.4179324
  };

  // Create a map object and specify the DOM element for display.
  map = new google.maps.Map(document.getElementById('results-map'), {
    center: ca_latlng,
    scrollwheel: true,
    zoom: 7,
  });

  info_window = new google.maps.InfoWindow();

  var options = {
      imagePath: '/static/img/m'
  };
  marker_clusterer = new MarkerClusterer(map, [], options);

  geocoder = new google.maps.Geocoder();

  circle = new google.maps.Circle({
    strokeColor: '#F0573E',
    strokeOpacity: 0.75,
    strokeWeight: 2,
    fillColor: '#F0573E',
    fillOpacity: 0.05,
    map: map,
    radius: 0
  })

  if (user_address == null) return;
  run_location_search(user_address);
}

function search_facilities_by_zip(facility_zip, facility_type, cb) {
  var params = {
    facility_type: facility_type,
    facility_zip: facility_zip,
  };
  if (facility_type == FACILITY_TYPES[0]) delete params.facility_type;
  const url = CHHS_API_URL + "?" + $.param(params);
  console.log(url)
  $.ajax(url, {
    dataType: 'json'
  }).done(function (results) {
    console.log(results)
    cb(results);
  });
}

function distance(p1, p2) {
  const s1 = p1[0] - p2[0];
  const s2 = p1[1] - p2[1];
  return Math.sqrt((s1 * s1) + (s2 * s2));
}

function search_facilities_within_radius(location, facility_type, radius_mi, cb) {
  // $where=within_circle(location, 34.09, -117.67, 1000)
  const radius_m = radius_mi * 1609.34;  // 5 mi in m
  // [Lng, Lat] order to match HHS search results.
  const center = [location.lng(), location.lat()];
  // Draw circle around location.
  circle.setMap(map);
  circle.setCenter(location);
  circle.setRadius(radius_m);

  var params = {
    //'$limit': 10,
    '$where': 'within_circle(location,' +
              center[1].toString() + ',' +
              center[0].toString() + ',' +
              radius_m + ')',
    facility_type: facility_type,
  };
  if (facility_type == "<all>") delete params.facility_type;
  const url = CHHS_API_URL + "?" + $.param(params);

  $.ajax(url, {
    dataType: 'json'
  }).done(function (results) {
    // Sort by increasing distance from center.
    results.sort(function (p1, p2) {
      return distance(p1.location.coordinates, center) -
             distance(p2.location.coordinates, center);
    });
    cb(results);
  });
}

function clear_results() {
  if (user_marker) user_marker.setMap(null);
  marker_clusterer.clearMarkers();
  circle.setMap(null);

  $('#num-results').text(0);
  $('#results-list').html('<p>No results to show.</p>');
}

function show_info_for_marker(marker, info) {
  function _show_info() {
    info_window.close();
    info_window.setContent(info);
    info_window.setPosition(marker.getPosition());
    info_window.open(map);
    map.setCenter(marker.getPosition());
  }
  return _show_info;
}

function render_results(results) {
  $('#num-results').text(results.length);

  if (results.length == 0) {
    return;
  } else {
    $('#results-list').empty();
  }

  var bounds = new google.maps.LatLngBounds();
  // Always add current user to bounds.
  if (user_marker) bounds.extend(user_marker.getPosition());

  results.forEach(function (facility, index) {
    const address = facility.facility_address + '<br/>' +
                    facility.facility_city + ',' +
                    facility.facility_state + ' ' +
                    facility.facility_zip + '<br/>';

    // Add facility to table.
    const record = $('<a class="list-group-item">').append(
      $('<address>').append(
        $('<em class="text-primary">').text(LABELS[index % LABELS.length] + '. '),
        $('<strong>').text(facility.facility_name),
        $('<div>').html(address),  // CAREFUL HERE, potentially unsafe.
        $('<div>').text(facility.facility_telephone_number),
        $('<div>').text('Capacity: ' + facility.facility_capacity)
    )).appendTo('#results-list');

    // Create a marker and set its position.
    if (map == null) return;
    const coords = {
      lng: facility.location.coordinates[0],
      lat: facility.location.coordinates[1],
    };
    var marker = new google.maps.Marker({
      map: map,
      position: coords,
      title: facility.facility_name,
      label: LABELS[index % LABELS.length],
      zIndex: index
    });

    const show_info = show_info_for_marker(marker, facility.facility_name);
    marker.addListener('click', show_info);
    record.click(show_info);

    marker_clusterer.addMarker(marker);
    bounds.extend(marker.getPosition());
  });

  map.fitBounds(bounds);
}

function is_valid_zip(zip) {
  return zip.length == 5;
}

function validate_zip(group_id, validator) {
  const value = $(group_id).find('input').val();
  if (!validator(value)) {
    $(group_id).removeClass('has-success');
    $(group_id).addClass('has-warning');
    $(group_id).find('.success-status').hide();
    $(group_id).find('.failure-status').show();
  } else {
    $(group_id).removeClass('has-warning');
    $(group_id).addClass('has-success');
    $(group_id).find('.success-status').show();
    $(group_id).find('.failure-status').hide();
    return value;
  }
}


function run_location_search(starting_location) {
  clear_results();

  if (starting_location) {
    $('#zip-group input').val(starting_location);
  }

  const location_text = get_search_location();
  if (!location_text) return;

  console.log("Running geocoding for: ", location_text);
  geocoder.geocode( { 'address': location_text }, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      const result = results[0];
      map.setCenter(result.geometry.location);

      user_marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location,
          icon: USER_MARKER_ICON
      });

      const info_content = "<b>Home:</b> " + location_text;
      const show_info = show_info_for_marker(user_marker, info_content);
      user_marker.addListener('click', show_info);

      map.setZoom(13);

      // Set search to location in result, if found.
      const search_radius = get_search_radius();

      if (search_radius == 0) {
        // Run exact zipcode search.
        const facility_zip = find_zip_in(result);
        if (facility_zip) {
          console.log("Searching in zip:", facility_zip);
          search_facilities_by_zip(facility_zip, get_search_type(), render_results);
        } else {
          console.log("Couldn't resolve location's zipcode!");
        }
      } else {
        console.log("Searching within", search_radius, "mile radius");
        search_facilities_within_radius(result.geometry.location,
                                        get_search_type(),
                                        search_radius,
                                        render_results);
      }
    } else {
      console.log("Geocode was not successful for the following reason: " + status);
    }
  });
}
