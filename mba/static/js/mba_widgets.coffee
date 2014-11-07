$ ()->
    $.widget "mbawidget.base",
        options:
            name: 'basewidget'
            title: null
            desc: null
            item:
                type:'local' # script, json is also available
                url: null
                var: null
            items: null
            width : null

            buttons: [
                {
                    name: 'save'
                    clsNames: 'btn btn-xs btn-primary'
                    value: '保&nbsp;&nbsp;存'
                    handler: 'save'
                },{
                    name: 'cancel'
                    clsNames: 'btn btn-xs btn-default'
                    value: '取&nbsp;&nbsp;消'
                    handler: 'cancel'
                }

            ]

        dialog: null
        visible: false

        _create: ()->

            this._on this.element,
                'click': "toggle"
            this._on this.document,
                'click': "hideDialog"

            return


        _destroy: ()->
            this._off this.element
            this._off this.document
            for index,item in $.dialog.find('button')
                this._off item
            this.dialog.remove()


        save: ()->
            console.log 'save'
            this.hideDialog()
            return false

        cancel: ()->
            console.log 'cancel'
            this.hideDialog()
            return false



        toggle: ()->
            if this.visible
                this.hideDialog()
            else
                this.showDialog()




            return false

        showDialog: ()->
            console.log "showDialog"
            offset = this.element.offset()
            offset.top += this.element.height() + 8
            self = this

            if not this.dialog

                if this.options.item.type != 'local'
                    this._buildDialog ()->
                        self.dialog.show().offset offset
                        self.visible = true
                        return
                    return

                else
                    this._buildDialog()

            this.dialog.show().offset offset
            this.visible = true

            return


        hideDialog: (e)->
            console.log 'before hideDialog'

            hide = false

            if this.dialog
                if  e
                    if this.dialog.find(e.target).length == 0
                        hide = true
                else
                    hide = true



            if hide
                console.log "hideDialog:"
                this.dialog.hide()
                this.visible = false

            return


        buildContent: ()->
            "NeedSubclass"


        _buildDialog: (cb)->
            type = this.options.item.type
            self = this
            if type  == 'script'
                $.getScript this.options.item.url,
                    (ret)->
                        eval ret
                        self.options.items = window[self.options.item.var]
                        self.buildDialog()
                        cb() if cb?
            else if type  == 'json'
                $.get this.options.item.url,
                    (ret)->
                        if ret.errcode == ret.SUCCESS
                            self.options.items = ret.retval
                            self.buildDialog()
                            cb() if cb?
                        else
                            alert ret.errmsg
            else
                this.buildDialog()

            return




        buildDialog: ()->

            console.log 'buildDialog:'



            buttons = this.options.buttons
            arr = []

            for item ,index in buttons
                button = $("<button/>")
                            .addClass item.clsNames
                            .attr "name", item.name
                            .val item.name
                            .html item.value
                            .attr "type", "button"
                btnhtml = button.prop('outerHTML')
                arr.push(btnhtml)


            desc = ""
            desc = "<small>(" + this.options.desc + ")</small>"  if this.options.desc

            title = $ "<div/>"
                .addClass "mba-dialog-title"
                .html(this.options.title + desc)
            content = $ "<div/>"
                .addClass "mba-dialog-content"
                .append( this.buildContent() )
            footer = $ "<div/>"
                .addClass "mba-dialog-footer"
                .append arr.join("&nbsp;&nbsp;&nbsp;")

            this.dialog = $ "<div/>"
                .addClass "mba-dialog"
                .append title[0]
                .append content[0]
                .append footer[0]
                .appendTo ( this.document.find "body" )

            if this.options.width
                this.dialog.css("width", this.options.width)

            for item,index  in  this.dialog.find("button")
                this._on item,
                    'click': this.options.buttons[index].handler


            return false


    return

$ ()->
    $.widget "mbawidget.plain",
        $.mbawidget.base,
        options:
            name: 'plainwidget'
            columns : 2


        buildContent: ()->
            table = ""

            cols = this.options.columns
            len = this.options.items.length
            rows = (len-1) / cols + 1

            for row in [0..rows-1]
                tr = ""
                for col in [0..cols-1]
                    if row*cols+col < len
                        item = this.options.items[row*cols+col]
                        td = "<td class='mba-dialog-item'>"+this.buildCell(item)+"</td>"
                    else
                        td = "<td class='mba-dialog-item'></td>"
                        break


                    tr += td

                tr = "<tr>" + tr + "</tr>"
                table += tr

            table = "<form><table>" + table + "</table></form>"
            return table

    return




$ ()->
    $.widget "mbawidget.radiocheck",
        $.mbawidget.plain,
        options:
            name: 'radiocheck'


        save: ()->
            val = this.dialog.find(":radio:checked").val()
            this.element.val val
            return this._super()


        buildCell: (item)->
            td = "<input type='radio'  name='"+this.options.name+"' value='"+item+"'/>"+item
            return td



    return

$ ()->
    $.widget "mbawidget.multicheck",
        $.mbawidget.plain,
        options:
            name: 'multicheck'
            maxcount: 3


        save: ()->
            checked = this.dialog.find ":checkbox:checked"

            val = ( $(item).val() for item in checked).slice(0,  this.options.maxcount)

            this.element.val val.join(",")
            return this._super()

        buildCell: (item)->
            td = "<input type='checkbox'  name='"+this.options.name+"' value='"+item+"'/>"+item
            return td




    return

$ ()->
    $.widget "mbawidget.radiotree",
        $.mbawidget.radiocheck,
        options:
            name: 'treewidget'




        buildContent: ()->
            content = ""
            items = this.options.items
            for item,index in items
                item =  "<a href='#' data-index="+index+" class='mba-dt-l1'>" + item.name + "</a>|"
                content += item

            content += "<hr/><div class='subnodes'></div>"

            return content



        buildDialog: ()->
            this._super()

            this._on this.dialog,
                'click a': '_buildL2'

            return false



        _buildL2: (e)->
            idx = parseInt $(e.target).attr("data-index")
            subitems = this.options.items[idx].items

            table = ""
            cols = 3
            len = subitems.length
            rows = (len-1) / cols + 1

            for row in [0..rows-1]
                tr = ""
                for col in [0..cols-1]
                    if row*cols+col < len
                        item = subitems[row*cols+col].name
                        td = "<td class='mba-di-l2'>"+this.buildCell(item)+"</td>"
                    else
                        td = "<td class='mba-di-l2'></td>"
                        break

                    tr += td

                tr = "<tr>" + tr + "</tr>"
                table += tr

            table = "<form><table>" + table + "</table></form>"

            this.dialog.find('.subnodes').html table


    return

$ ()->
    $.widget "mbawidget.multichecktree",
        $.mbawidget.multicheck,
        options:
            name: 'multichecktree'



        buildContent: ()->
            content = ""
            items = this.options.items
            for item,index in items
                item =  "<a href='#' data-index="+index+" class='mba-dt-l1'>" + item.name + "</a>|"
                content += item

            content += "<hr/><div class='subnodes'></div>"

            return content



        buildDialog: ()->
            this._super()

            this._on this.dialog,
                'click a': '_buildL2'

            return false



        _buildL2: (e)->
            idx = parseInt $(e.target).attr("data-index")
            subitems = this.options.items[idx].items

            table = ""
            cols = 3
            len = subitems.length
            rows = (len-1) / cols + 1

            for row in [0..rows-1]
                tr = ""
                for col in [0..cols-1]
                    if row*cols+col < len
                        item = subitems[row*cols+col].name
                        td = "<td class='mba-di-l2'>"+this.buildCell(item)+"</td>"
                    else
                        td = "<td class='mba-di-l2'></td>"
                        break

                    tr += td

                tr = "<tr>" + tr + "</tr>"
                table += tr

            subnodes = this.dialog.find '.subnodes'

            table = "<table id='subidx-"+idx+"'>" + table + "</table>"
            section = subnodes.find('table[id=subidx-'+idx+']')

            subnodes.find("table[id^=subidx]").hide()

            if section.length == 0 #can't find it
                subnodes.append table
            else:
                section.show()
            return


    return


