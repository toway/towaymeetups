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
	    updateInputs('.in_person_info');
	    updateTables('.sp_person_info');
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

function updateInputs(class_name, obj) {
	if(typeof arguments[1] == 'undefined') {
		obj = {};
	}
	$(class_name).each(function (){
		el = $(this);
		id = el.attr('id');
		data_type = el.attr('data-type');
		if(typeof data_type == 'undefined') {
                	//console.log(id+"|UNDEF|"+data_type);
			if(id in obj) {
				el.val(obj[id]);
			}
		} else {
                	//console.log(id+"|DEF|"+data_type);
			if(data_type == 'date') {
				if(id in obj) {
					el.val(obj[id]);
				} else {
					el.datepicker({dateFormat:'yy-mm-dd'});
				}
			} else if(data_type == 'radio') {
				el_name = "input[name=" + el.attr('name') + "]";
				if(id in obj) {
					arg = obj[id] + "";
					$(el_name).each(function() {
						if(arg == $(this).attr("value") ) {
							$(this).prop("checked","checked");
						}
					});
				} else {
					$(el_name).each(function() {
						if($(this).attr("data-val") == $(this).attr("value") ) {
							$(this).prop("checked","checked");
						}
					});
				}
			} else if(data_type == 'select') {
				if(id in obj) {
					el.val(obj[id]+"");
				} else {
					el.val(el.attr('data-val'));
				}
			}
		}
	});
}

function updateTables(class_name, obj) {
	if(typeof arguments[1] == 'undefined') {
		obj = {};
	}
	$(class_name).each(function () {
		sp_id = $(this).attr('id');
		id = sp_id.substring(sp_id.indexOf('_')+1)
		sp_obj = $('#'+sp_id)
		data_type = sp_obj.attr('data-type');
		if(typeof data_type == 'undefined') {
			data_type = 'undefined';
		}
		value = '';
		if(id in obj) {
			value = obj[id];
			if(data_type == 'undefined') {
				sp_obj.html(value);
				return;//like continue; return false;->like break;
			}
		} else {
			value = sp_obj.attr('data-val');
		}
		if(data_type != 'undefined') {
			values = null;
			data_sel = sp_obj.attr('data-sel');
			if(typeof data_sel == 'undefined') {
				values = {};
				$("#" + id + " > option").each(function() {
					try {
						v = parseInt(this.value);
						values[v] = this.text;
					}
					catch(err) {
					}
				});
			} else {
				values = data_sel.split('|');
			}
			try {
				v = parseInt(value);
				sp_obj.html(values[v]);
			}
			catch(err) {
			}
		}
	});
}
