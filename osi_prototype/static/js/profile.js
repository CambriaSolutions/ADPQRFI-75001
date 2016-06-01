$(document).ready(function() {
  const EDIT_API = window.location.pathname + 'edit';

  // toggle `popup` / `inline` mode
  $.fn.editable.defaults.mode = 'inline';
  $.fn.editable.defaults.ajaxOptions = {
    dataType: 'json' //  json response
  }

  const csrftoken = $('meta[name=csrf-token]').attr('content');

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken)
      }
    }
  })

  const successFn = function(response, newValue) {
    if (!response.success) return response.message;
  }

  const paramsFn = function(params) {
    var new_params = {};
    new_params[params['name']] = params.value;
    return new_params;
  }

  // Make fields editable.
  const editable = [
    '#blurb',
    '#last_name',
    '#phone_number',
    '#license_number',
    '#address',
    '#email',
    '#num_adults',
    '#num_children',
    '#num_capacity'
  ];

  editable.forEach(function(id) {
    $(id).editable({
      url: EDIT_API,
      send: 'always',
      success: successFn,
      params: paramsFn
    });
  });

  // Special handling for first name, so we can update the welcome message
  // in tandem.
  $('#first_name').editable({
    url: EDIT_API,
    send: 'always',
    params: paramsFn,
    success: function(response, newValue) {
      if (response.success) {
        $('#first-name-welcome').text(newValue);
      }
      return successFn(response, newValue)
    },
  })

  $('.user-preferences input[type=checkbox]').click(function(event) {
    const checkbox = event.target;
    const checked = $(checkbox).is(":checked");
    var data = {};
    data[checkbox.id] = checked;
    $.post(EDIT_API, data);
  });

  $('#fake-file-upload').click(function() {
    $('#real-file-upload').click();
  });

  $('#real-file-upload').change(function(e) {
    $('#user-photo-upload').submit();
  });

});