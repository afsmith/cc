var ing = new Ing(); 
$(document).ready(function() {
    $('#login_button').click(function(){
       $('#loginForm').submit();
       return false;
    });
    $('#loginForm input').keyup(function(event){
       if(event.keyCode == 13){
           $('#loginForm').submit();
       }       
    });   
    if(ing.helpers.cookie.get('ing_lang') != 'null'){
    	var lang = ing.helpers.cookie.get('ing_lang');
    	if (lang) {
    		$('#id_language').val(lang);
    	}        
    }
    $('#id_language').live('change', function(){
        ing.helpers.cookie.set('ing_lang', $(this).val(), ing.config.cookieTime);
    });
    //$('#id_language').sb();
});
