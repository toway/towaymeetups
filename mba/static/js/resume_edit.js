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
			} else if(data_type == 'school') {
				UseSchoolWidget(el);
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
		if(typeof sp_id == 'undefined') {
			alert(class_name);
			return;
		}
		id = sp_id.substring(sp_id.indexOf('_')+1);
		sp_obj = $('#'+sp_id);
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

function mgr_create(pref, the_name) {
	var mgr = {
		curr_modify: -1,
		prefix:pref,
		name:the_name,
		container:function() {return '#'+this.name+'_container';},
		item_sel:function(id) {return '#'+this.prefix+'_div_'+id;},
		updated_span:function() {return this.container()+' .sp_'+this.prefix;},
		updated_input:function(){return this.container()+' .in_'+this.prefix;},
		btn_add:function(){return '#btn_'+this.prefix+'_add';},
		btn_save:function(){return '#btn_'+this.prefix+'_save';},
		btn_cancel:function(){return '#btn_'+this.prefix+'_cancel';},
		item_len:function(){return "#"+this.prefix+"_length";},
		div:function(id){return '#'+this.prefix+'_div_'+id;},
		form:function(id){return '#'+this.prefix+'_form_'+id;},
		edit:function(){return '.'+this.name+'-edit';},
		del:function(){return '.'+this.name+'-delete';},
		modify:function(id){return this.form(id)+' input[name='+this.name+']';}
	};
	return mgr;
}

function mgr_init(mgr) {
	 var delete_options = {
	   iframe: true,
	   success:function (rText, statusText, xhr, $form) {
		try {
			rlt_obj = jQuery.parseJSON(rText);
			if(rlt_obj['__result'] == 0) {
				$(mgr.item_sel(rlt_obj.id)).addClass('hidden');
			}
		}
		catch(err) {
		}
	   }
	 };

	 var inner_refresh = function() {
		updateInputs(mgr.updated_input());
		updateTables(mgr.updated_span());
		if($(mgr.item_len()).val() == "0") {
			$(mgr.form(0)).removeClass('hidden');
			mgr.curr_modify = 0;
			edu_modify(true);
		} else {
			edu_modify(false);
		} 
		$(mgr.edit()).click(function() {
			id = mgr.curr_modify;
			if(id != -1) {
				$(mgr.form(id)).addClass('hidden');
				$(mgr.div(id)).removeClass('hidden');
			}

			newid = $(this).attr('alt');
			$(mgr.form(newid)).removeClass('hidden');
			$(mgr.div(newid)).addClass('hidden');
			mgr.curr_modify = newid;

			edu_modify(true);
		});

		$(mgr.del()).click(function(){
			if(!window.confirm('确定删除吗？')) {
				return;
			}
			id = $(this).attr('alt');
			alert(mgr.modify(id));
			$(mgr.modify(id)).val('delete');
			$(mgr.form(id)).ajaxSubmit(delete_options);
		});
	};

	 var edu_modify = function(b) {
		if(b) {
		$(mgr.btn_add()).addClass('hidden');
		$(mgr.btn_save()).removeClass('hidden');
		$(mgr.btn_cancel()).removeClass('hidden');
		} else {
		$(mgr.btn_add()).removeClass('hidden');
		$(mgr.btn_save()).addClass('hidden');
		$(mgr.btn_cancel()).addClass('hidden');
		}
	 };

	$(mgr.btn_add()).click(function () {
		$(mgr.form(0)).removeClass('hidden');
		mgr.curr_modify = 0;
		edu_modify(true);
		});

	$(mgr.btn_cancel()).click(function() {
		id = mgr.curr_modify;
		$(mgr.form(id)).addClass('hidden');
		$(mgr.div(id)).removeClass('hidden');
		mgr.curr_modify = -1;
		edu_modify(false);
	});

	 var save_options = {
	   iframe: true,
	   success:function (rText, statusText, xhr, $form) {
		index = rText.indexOf('$');
		is_error = false;
		rlt_obj = {'__result':1};
		if(index >= 0) {
			rlt = rText.substring(0, index);
		} else {
			is_error = true;
			rlt = rText;
		}
		try {
			rlt_obj = jQuery.parseJSON(rlt);
		}
		catch(err) {
			is_error = true;
		}
		if(rlt_obj['__result'] == 0) {
			html = rText.substring(index+1);
			mgr.curr_modify = -1;
			$(mgr.container()).html($(html));
			inner_refresh();
		}
	   }
	 };

	$(mgr.btn_save()).click(function() {
		id = mgr.curr_modify;
		if(id != 0) {
			$(mgr.modify(id)).val('modify');
		}
		$(mgr.form(id)).ajaxSubmit(save_options);
	});

	//at last
	inner_refresh();
 }

//global object
eduMgr = mgr_create('edu','education');
expMgr = mgr_create('exp','experience');
prjMgr = mgr_create('prj','project');
(function () {
	$(document).ready(function(){
		mgr_init(eduMgr);
		mgr_init(expMgr);
		mgr_init(prjMgr);
	});

})();
