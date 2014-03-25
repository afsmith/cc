$(document).ready(function () {

    // Stripe init
    $('.subscribe-form button[type="submit"], .js_changeCard').click(function(e) {
        e.preventDefault();
        var _this = $(this),
            _form = _this.closest('form'),
            amount = _this.prop('id').replace('js_price_', ''),
            token = function(res) {
                _form.find('input[name="stripe_token"]').val(res.id);
                _form.trigger('submit');
            };

        StripeCheckout.open({
            key:                _form.data('stripe-key'),
            token:              token,
            billingAddress:     'true',
            name:               'Kneto',
            email:              CC_GLOBAL.user_email,
            description:        'Kneto Subscription',
            allowRememberMe:    false,
            amount:             amount,
            currency:           'EUR',
        });

        return false;
    });

    // add loading state
    $('#payment_wrapper button[type="submit"]').click(function () {
        $(this).button('loading');
    });

    // change class of invitation input
    $('.invitation_wrapper input').keyup(function () {
        var _this = $(this),
            this_val = _this.val(),
            this_button = _this.parent().find('.btn');

        if (this_val !== '') {
            this_button.removeClass('btn-default').addClass('btn-success').prop('disabled', false);
        } else {
            this_button.removeClass('btn-success').addClass('btn-default').prop('disabled', true);
        }
    });

    // send invitation
    $('.invitation_wrapper').on('click', '.btn[disabled!="disabled"]', function () {
        var _this = $(this),
            this_div = _this.closest('.input-group'),
            this_wrapper = _this.closest('.invitation_wrapper'),
            this_email = this_div.find('input').val();

        $.ajax({
            url: '/accounts/invite/',
            type: 'POST',
            dataType: 'json',
            data: {
                'email': this_email
            },
        }).done(function (resp) {
            _this.prop('disabled', true);
            this_wrapper.find('.alert').remove();

            if (resp.status === 'OK') {
                window.location.reload(true);
            } else {
                this_div.addClass('has-error');
                this_wrapper.append('<p class="alert alert-danger">' + resp.message + '</p>');
            }
        });
    });

    // remove active invitation click handler
    $('.active_invitation_wrapper').on('click', '.btn', function () {
        var _this = $(this),
            this_id = _this.closest('.input-group').prop('id').replace('js_invitation_', '');

        $.ajax({
            url: '/accounts/remove_invitation/' + this_id + '/',
            type: 'POST',
            dataType: 'json',
        }).done(function (resp) {
            _this.prop('disabled', true);
            window.location.reload(true);
        });
    });
    
    // active plan
    var active_plan = $('.active_plan');
    if ($('.active_plan').length) {
        active_plan.find('form').remove();
    }

}); // end document ready