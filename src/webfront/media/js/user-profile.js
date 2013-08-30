var app = new Ing();
$(document).ready(function(){
    app.config.mediaURL = mediaURL;
    app.run();
    $('select').html('');
    app.gm.loadData();

    $('#cp').live('click', function(){
        var cnf = app.config.modal;
        $.nmManual(
          '/management/users/password/'
        );
        return false;
      })
    $('#sp').live('click', function(){
        //$.post(
        //    '/management/users/password/',
        //     $('#passChangeForm').serialize(),
        //    function(data, status, xmlHttpRequest){
        //        $('.nyroModalLink').html(data);
        //    });
        $('.nyroModalClose').live('click', function(){
            $.nmTop().close();
        });
				$.post(
						'/management/users/password/',
						$('#passChangeForm').serialize(),
						function(data, status, xmlHttpRequest) {
								if (xmlHttpRequest.status == 200 && data == "") {
									 $.nmTop().close();
							 } else {
									 $('.nyroModalLink').html(data);
							 }
				});

        return false;

      });
});
