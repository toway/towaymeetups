$(document).ready(function(){
    mbaForm.load();
});

var mbaForm_loaded = false;

var mbaForm  = {
    callbacks: [],

    addCallback: function (oid, callback) {
        mbaForm.callbacks.push([oid, callback]);
    },

    load: function() {
      $(function() {
        if (!mbaForm_loaded) {
            mbaForm.processCallbacks();
            mbaForm.focusFirstInput();
            mbaForm_loaded = true;
      }});
    },
            
    processCallbacks: function (ajax_obj) {
	arg_len = arguments.length;
        $(mbaForm.callbacks).each(function(num, item) {
            var oid = item[0];
            var callback = item[1];
	    if((arg_len != 0) || (oid in ajax_obj) ) {
            	callback(oid, ajax_obj[oid]);
	    } else {
            	callback(oid, null);
	    }
            }
        );
    }

};
