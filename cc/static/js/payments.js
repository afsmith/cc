$(document).ready(function () {

    // Stripe init
    $('body').on('click', '.change-card, .subscribe-form button[type=submit]', function(e) {
        e.preventDefault();
        var _form = $(this).closest('form'),
            token = function(res) {
                _form.find('input[name=stripe_token]').val(res.id);
                _form.trigger('submit');
            };

        StripeCheckout.open({
            key:            _form.data('stripe-key'),
            name:           'Payment Method',
            panelLabel:     'Add Payment Method',
            billingAddress: 'true',
            name:           'Kneto',
            email:          CC_GLOBAL.user_email,
            description:    'Kneto Subscription',
            token:          token
        });

        return false;
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

    $('.invitation_wrapper').on('click', '.btn[disabled!=disabled]', function () {
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
                this_div.removeClass('has-error');
                log(resp)
            } else {
                this_div.addClass('has-error');
                this_wrapper.append('<p class="alert alert-danger">' + resp.message + '</p>');
            }
        });
    });
    
}); // end document ready