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
		if(typeof arguments[0] == 'undefined') {
			is_ok = false;
		}
		else {
			is_ok = true;
		}
        $(mbaForm.callbacks).each(function(num, item) {
            var oid = item[0];
            var callback = item[1];
			if(!is_ok) {
				callback(oid);
			} else if(oid in ajax_obj) {
				callback(oid, ajax_obj[oid]);
			}
        }
        );
    },
    focusFirstInput: function (el) {
        el = el || document.body;
        var input = $(el).find(':input')
          .filter('[id ^= deformField]')
          .filter('[type != hidden]')
          .first();
        if (input) {
            var raw = input.get(0);
            if (raw) {
                if (raw.type === 'text' || raw.type === 'file' || 
                    raw.type == 'password' || raw.type == 'text' || 
                    raw.type == 'textarea') { 
                    if (raw.className != "hasDatepicker") {
                        input.focus();
                    }
                }
            }
        }
    }

};
