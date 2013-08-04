from annoying.decorators import render_to

''' CC root views '''


@render_to('home.html')
def home(request):
    return {}


@render_to('step2.html')
def cc_step2(request):
    return {}
