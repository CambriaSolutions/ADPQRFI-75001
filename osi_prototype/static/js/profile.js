$(document).ready(function() {
    const EDIT_API = window.location.pathname + 'edit';

    // toggle `popup` / `inline` mode
    $.fn.editable.defaults.mode = 'inline';
    $.fn.editable.defaults.ajaxOptions = {
        dataType: 'json' //  json response
    }

    const csrftoken = $('meta[name=csrf-token]').attr('content')

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    })

    const successFn = (response, newValue) => {
        console.log(response);
        if (!response.success) return response.message;
    }

    const paramsFn = (params) => {
        var new_params = {};
        new_params[params['name']] = params.value;
        return new_params;
    }

    // Make fields editable.
    const editable = [
        '#blurb',
        '#first_name',
        '#last_name',
        '#phone_number',
        '#license_number',
        '#address',
        '#email',
        '#num_adults',
        '#num_children',
        '#num_capacity'
    ];

    editable.forEach((id) => {
        $(id).editable({
            url: EDIT_API,
            send: 'always',
            success: successFn,
            params: paramsFn
        });
    });

    $('.user-preferences input[type=checkbox]').click((event) => {
        const checkbox = event.target;
        const checked = $(checkbox).is(":checked");
        $.post(EDIT_API, {[checkbox.id]: checked});
    });
});