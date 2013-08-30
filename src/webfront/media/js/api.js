var ingAPI = {
  'handlers': {},
  'register': function(name, type){
    this.handlers[type] = name;
    return true;
  },
  'unregister': function(type){
    delete this.handlers[type];
  },
  'get': function(type){
    if(this.handlers[type]){
      return this.handlers[type];
    }
    return false;
  } 
};
