const CHHS_API_URL = 'https://chhs.data.ca.gov/resource/mffa-c6z5.json';
const FACILITY_TYPES = [
  "<all>",
  "ADOPTION AGENCY",
  "FOSTER FAMILY AGENCY",
  "FOSTER FAMILY AGENCY SUB"
];
const DEFAULT_ICON = 'http://maps.google.com/mapfiles/ms/icons/red-dot.png';
const SELECTED_ICON = 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'

var map = null;
var geocoder = null;
var user_marker = null;
var active_marker = null;
var all_markers = [];

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

  geocoder = new google.maps.Geocoder();

  if (user_address == null) return;

  geocoder.geocode( { 'address': user_address}, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      map.setCenter(results[0].geometry.location);
      user_marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location,
          icon: 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png'
      });

      // Add info window to marker.
      const info_content = "<b>Home:</b> " + user_address;
      add_info_to_marker(user_marker, info_content);

      map.setZoom(13);
    } else {
      console.log("Geocode was not successful for the following reason: " + status);
    }
  });
}

function add_info_to_marker(marker, content) {
  var infowindow = new google.maps.InfoWindow({content: content});
  marker.addListener('click', function() {
    infowindow.open(map, marker);
  });
}

function search_facilities_by_zip(facility_zip, facility_type, cb) {
  var params = {
    facility_type: facility_type,
    facility_zip: facility_zip,
  };
  if (facility_type == "<all>") delete params.facility_type;
  const url = CHHS_API_URL + "?" + $.param(params);

  $.ajax(url, {
    dataType: 'json'
  }).done(function (results) {
    cb(results);
  });
}

function render_results(results) {
  // Clear previous results.
  $('#results-list').empty();
  all_markers.forEach(function (marker) {
    marker.setMap(null);
  });
  all_markers = [];

  if (results.length == 0) {
    $('#results-list').html('<p>No results to show.</p>');
    return;
  }

  var bounds = new google.maps.LatLngBounds();
  // Always add current user to bounds.
  if (user_marker) bounds.extend(user_marker.getPosition());

  results.forEach(function (facility, index) {
    console.log(facility);
    const address = facility.facility_address + '<br/>' +
                    facility.facility_city + ',' +
                    facility.facility_state + ' ' +
                    facility.facility_zip + '<br/>';

    // Add facility to table.
    const record = $('<a class="list-group-item">').append(
      $('<address>').append(
        $('<em class="text-primary">').text(index + 1 + '. '),
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
      label: (index + 1).toString()
    });
    add_info_to_marker(marker, facility.facility_name);
    record.click(function () {
      // Zoom to location.
      map.setCenter(marker.getPosition());
      active_marker = marker;
    })
    bounds.extend(marker.getPosition());
    all_markers.push(marker);
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

function run_search() {
  const facility_zip = validate_zip('#zip-group', is_valid_zip);
  if (!facility_zip) return;

  const type_id = parseInt($('#facility-type option:selected').data('field'));
  const facility_type = FACILITY_TYPES[type_id];

  console.log("Running search for: ", facility_zip)
  search_facilities_by_zip(facility_zip, facility_type, render_results);
}

$(document).ready(function() {
  $('#run-search').click(run_search);
});
