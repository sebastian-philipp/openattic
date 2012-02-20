{% load i18n %}

Ext.namespace("Ext.oa");

Ext.apply(Ext.form.VTypes, {
  LVName:     function(v) { return /^[A-Za-z0-9_\-]+$/.test(v); },
  LVNameText: "Must only contain alphanumeric characters or _ and -.",
  LVNameMask: /[A-Za-z0-9_\-]/
});

Ext.oa.Lvm__LogicalVolume_Panel = Ext.extend(Ext.Panel, {
  initComponent: function(){
    var currentChartId = null;
    var lvmPanel = this;
    var lvmGrid = this;
    var addVolume = function(event){
    var addwin = new Ext.Window({
      title: "{% trans "Add Volume" %}",
      layout: "fit",
      height: 350,
      width: 500,
      items: [{
        xtype: "form",
        autoScroll: true,
        border: false,
        bodyStyle: 'padding:5px 5px;',
        defaults: {
          xtype: "textfield",
          anchor: '-20px'
        },
        items: [{
            fieldLabel: "Name",
            allowBlank: false,
            name: "name",
            ref: 'namefield',
            vtype: "LVName"
          },
          tipify({
              xtype:      'combo',
              allowBlank: false,
              fieldLabel: "{% trans 'Volume Group' %}",
              name:       'volume',
              hiddenName: 'volume_id',
              store: {
                xtype: "directstore",
                fields: ["app", "obj", "id", "name"],
                directFn: lvm__VolumeGroup.ids
              },
              typeAhead:     true,
              triggerAction: 'all',
              emptyText:     "{% trans 'Select...' %}",
              selectOnFocus: true,
              displayField:  'name',
              valueField:    'id',
              ref:           'volfield',
              listeners: {
                select: function(self, record, index){
                  self.ownerCt.volume_free_megs = null;
                  self.ownerCt.sizelabel.setText( "{% trans "Querying data..." %}" );
                  lvm__VolumeGroup.get_free_megs( record.data.id, function( provider, response ){
                    self.ownerCt.volume_free_megs = response.result;
                    self.ownerCt.sizelabel.setText( String.format( "Max. {0} MB", response.result ) );
                  } );
                }
              }
            }, "{% trans 'The volume group in which you want the Volume to be created.' %}"),
          tipify({
              xtype:      'combo',
              fieldLabel: "{% trans 'File System' %}",
              name:       'filesystem_desc',
              hiddenName: 'filesystem_name',
              store: new Ext.data.DirectStore({
                fields: ["name", "desc"],
                directFn: lvm__LogicalVolume.avail_fs
              }),
              typeAhead:     true,
              triggerAction: 'all',
              emptyText:     "{% trans 'Select...' %}",
              selectOnFocus: true,
              displayField:  'desc',
              valueField:    'name',
              ref:      'fsfield'
            }, "{% trans 'If you want to use DRBD with this device, do not yet create a file system on it, even if you want to share it using NAS services later on.' %}"),
          {
            fieldLabel: "{% trans "Size in MB" %}",
            allowBlank: false,
            name: "megs",
            ref: 'sizefield',
            xtype: "numberfield"
          }, {
            xtype: "label",
            ref:   "sizelabel",
            text:  "{% trans "Waiting for volume selection..." %}",
            cls:   "form_hint_label"
          }, {
            fieldLabel: "{% trans 'Warning Level (%)' %}",
            allowBlank: false,
            name: "fswarning",
            ref: 'warnfield',
            value: 75,
            xtype: "numberfield"
          }, {
            fieldLabel: "{% trans 'Critical Level (%)' %}",
            allowBlank: false,
            name: "fscritical",
            ref: 'critfield',
            value: 85,
            xtype: "numberfield"
          }, {
            xtype: "authuserfield",
            ref:   'ownerfield',
            allowBlank: false
        }],
        buttons: [{
          text: "{% trans 'Create Volume' %}",
          icon: MEDIA_URL + "/icons2/16x16/actions/gtk-save.png",
          handler: function(self){
            if( !self.ownerCt.ownerCt.getForm().isValid() ){
              return;
            }
            var free = self.ownerCt.ownerCt.volume_free_megs;
            if( free === null || typeof free == "undefined" ){
              Ext.Msg.alert("{% trans "Error" %}",
                "{% trans "Please wait for the query for available space to complete." %}");
              return;
            }
            if( free < self.ownerCt.ownerCt.sizefield.getValue() ){
              Ext.Msg.alert("{% trans "Error" %}",
                interpolate( "{% trans "Your volume exceeds the available capacity of %s MB." %}",
                  [response.result]) );
              return;
            }
            var progresswin = new Ext.Window({
              title: "{% trans "Adding Volume" %}",
              layout: "fit",
              height: 250,
              width: 400,
              modal: true,
              html: "{% trans 'Please wait while your volume is being created...' %}"
            });
            progresswin.show();
            lvm__LogicalVolume.create({
              'vg': {
                'app': 'lvm',
                'obj': 'VolumeGroup',
                'id': self.ownerCt.ownerCt.volfield.getValue()
              },
              'filesystem': self.ownerCt.ownerCt.fsfield.getValue(),
              'name':       self.ownerCt.ownerCt.namefield.getValue(),
              'megs':       self.ownerCt.ownerCt.sizefield.getValue(),
              'fswarning':  self.ownerCt.ownerCt.warnfield.getValue(),
              'fscritical': self.ownerCt.ownerCt.critfield.getValue(),
              'owner': {
                'app': 'auth',
                'obj': 'User',
                'id': self.ownerCt.ownerCt.ownerfield.getValue()
              }
            }, function(provider, response){
              if( response.type == "rpc" ){
                lvmPanel.items.items[0].store.reload();
                progresswin.hide();
                addwin.hide();
              }else{
                progresswin.hide();
                alert(response.message);
              }
            });
            }
          },{
          text: "{% trans 'Cancel' %}",
          icon: MEDIA_URL + "/icons2/16x16/actions/gtk-cancel.png",
          handler: function(self){
            addwin.hide();
          }
        }]
      }]
    });
    addwin.show();
  };

    Ext.apply(this, Ext.apply(this.initialConfig, {
      id: "lvm__logicalvolume_panel_inst",
      title: "{% trans 'LVM' %}",
      layout: 'border',
      buttons: [{
        text: "",
        icon: MEDIA_URL + "/icons2/16x16/actions/reload.png",
        tooltip: "{% trans 'Reload' %}",
        handler: function(self){
          lvmPanel.items.items[0].store.reload();
        }
      }, {
        text: "{% trans "Set warning threshold" %}",
        icon: MEDIA_URL + "/icons2/16x16/status/dialog-warning.png",
        handler: function(self){
          var lvmGrid = lvmPanel.items.items[0];
          var sm = lvmGrid.getSelectionModel();
          if( sm.hasSelection() ){
            var sel = sm.selections.items[0];
            var addwin = new Ext.Window({
              title: "{% trans 'Update Levels' %}",
              layout: "fit",
              height: 180,
              width: 500,
              items: [{
                xtype: "form",
                border: false,
                bodyStyle: 'padding:5px 5px;',
                defaults: {
                  xtype: "textfield",
                  anchor: '-20px'
                },
                items: [ {
                    fieldLabel: "{% trans 'Warning Level (%)' %}",
                    allowBlank: false,
                    name: "fswarning",
                    ref: 'warnfield',
                    value: sel.data.fswarning,
                    xtype: "numberfield"
                  }, {
                    fieldLabel: "{% trans 'Critical Level (%)' %}",
                    allowBlank: false,
                    name: "fscritical",
                    ref: 'critfield',
                    value: sel.data.fscritical,
                    xtype: "numberfield"
                  } ],
                buttons: [{
                  text: "{% trans 'Update Levels' %}",
                  icon: MEDIA_URL + "/icons2/16x16/actions/gtk-save.png",
                  handler: function(self){
                    if( !self.ownerCt.ownerCt.getForm().isValid() ){
                      return;
                    }
                    lvm__LogicalVolume.set(sel.data.id, {
                      'fswarning':  self.ownerCt.ownerCt.warnfield.getValue(),
                      'fscritical': self.ownerCt.ownerCt.critfield.getValue()
                    }, function(provider, response){
                      if( response.result ){
                        lvmPanel.items.items[0].store.reload();
                        addwin.hide();
                      }
                    });
                  }
                }, {
                  text: "{% trans 'Cancel' %}",
                  icon: MEDIA_URL + "/icons2/16x16/actions/gtk-cancel.png",
                  handler: function(self){
                    addwin.hide();
                  }
                }]
              }]
            });
            addwin.show();
          }
        }
      }, {
        text: "{% trans "Mount" %}",
        icon: MEDIA_URL + "/oxygen/16x16/emblems/emblem-mounted.png",
        handler: function(self){
          var lvmGrid = lvmPanel.items.items[0];
          var sm = lvmGrid.getSelectionModel();
          if( sm.hasSelection() ){
            var sel = sm.selections.items[0];
            if( !sel.data.filesystem ){
              Ext.Msg.alert('Mounted',
                interpolate(
                  "{% trans "Volume %s does not have a file system and therefore cannot be mounted." %}",
                  [sel.data.name] ));
              return;
            }
            lvm__LogicalVolume.is_mounted( sel.data.id, function(provider, response){
              if( response.result ){
                Ext.Msg.alert('Mounted', interpolate( "{% trans "Volume %s is already mounted." %}", [sel.data.name] ));
                return;
              }
              lvm__LogicalVolume.is_in_standby( sel.data.id, function(provider, response){
                if( response.result ){
                  Ext.Msg.alert('Mounted',
                    interpolate( "{% trans "Volume %s cannot be mounted at the current time." %}", [sel.data.name] ));
                  return;
                }
                lvm__LogicalVolume.mount( sel.data.id, function(provider, response){
                  if( response.type === "exception" )
                    Ext.Msg.alert('Mounted', interpolate(
                      "{% trans "Volume %s could not be mounted, please check the logs." %}", [sel.data.name] ));
                  else
                    Ext.Msg.alert('Mounted', interpolate(
                      "{% trans "Volume %s has been mounted." %}", [sel.data.name] ));
                    lvmGrid.store.reload();
                } );
              } );
            } );
          }
        }
      }, {
        text: "{% trans "Unmount" %}",
        icon: MEDIA_URL + "/oxygen/16x16/emblems/emblem-unmounted.png",
        handler: function(self){
          var lvmGrid = lvmPanel.items.items[0];
          var sm = lvmGrid.getSelectionModel();
          if( sm.hasSelection() ){
            var sel = sm.selections.items[0];
            lvm__LogicalVolume.is_mounted( sel.data.id, function(provider, response){
              if( !response.result ){
                Ext.Msg.alert('Unmount', interpolate( "{% trans 'Volume %s is not mounted.' %}",
                                                          [sel.data.name] ));
              }
              else{
                Ext.Msg.confirm(
                  "{% trans 'Unmount' %}",
                  interpolate(
                    "{% trans 'Do you really want to umount %s?' %}",
                    [sel.data.name]),
                  function(btn){
                    if(btn == 'yes'){
                      lvm__LogicalVolume.unmount( sel.data.id, function(provider, response){
                        if( response.type === "exception" )
                          Ext.Msg.alert('Unmount', interpolate(
                            "{% trans 'Volume %s could not be unmounted, please check the logs.' %}",
                            [sel.data.name] ));
                        else{
                          Ext.Msg.alert('Unmount', interpolate(
                            "{% trans 'Volume %s has been unmounted.' %}",
                            [sel.data.name] ));
                          lvmGrid.store.reload();
                        }
                      });
                    }
                } );
              }
            } );
          }
        }
      }, {
        text: "{% trans 'Shares' %}",
        icon: MEDIA_URL + "/oxygen/16x16/emblems/emblem-unmounted.png",
        handler: function(self){
          var lvmGrid = lvmPanel.items.items[0];
          var sm = lvmGrid.getSelectionModel();
          if( sm.hasSelection() ){
            var sel = sm.selections.items[0];
            var shareswin = new Ext.Window({
              title: "{% trans "Add Volume" %}",
              layout: "fit",
              height: 300,
              width: 500,
              items: {
                xtype: "grid",
                store: {
                  xtype: 'directstore',
                  autoLoad: true,
                  fields: ['id', 'app', 'obj'],
                  directFn: lvm__LogicalVolume.get_shares,
                  baseParams: {id: sel.data.id}
                },
                colModel: new Ext.grid.ColumnModel({
                  defaults: {
                    sortable: true
                  },
                  columns: [ {
                    header: "{% trans 'App' %}",
                    width: 350,
                    dataIndex: "app"
                  }, {
                    header: "{% trans 'Object' %}",
                    width: 100,
                    dataIndex: "obj"
                  } ]
                })
              }
            } );
            shareswin.show();
          }
        }
      }, {
        text: "{% trans "Add Volume" %}",
        icon: MEDIA_URL + "/icons2/16x16/actions/add.png",
        handler: addVolume
      }, {
        text: "{% trans "Resize Volume" %}",
        icon: MEDIA_URL + "/icons2/16x16/actions/gtk-execute.png",
        handler: function(self){
          var lvmGrid = lvmPanel.items.items[0];
          var sm = lvmGrid.getSelectionModel();
          if( sm.hasSelection() ){
            var sel = sm.selections.items[0];
            lvm__VolumeGroup.get_free_megs( sel.json.vg.id, function( provider, response ){
              Ext.Msg.prompt(
              "{% trans 'Enter new size' %}",
              interpolate(
                "{% trans 'Please enter the desired size in MB you wish to resize volume <b>%s</b> to.' %}" + "<br/>" +
                "{% trans 'The current size is %s MB' %}" + "<br/>" + "<br/>" + "{% trans 'Max. +%s MB' %}",
                [sel.data.name, sel.data.megs, response.result]),
              function(btn, text){
                if( btn == 'ok' ){
                  if((text - sel.data.megs) > response.result){
                    Ext.Msg.alert("{% trans 'Error' %}","{% trans 'The size you entered exceeds the remaining space.' %}");
                    return;
                  }
                  Ext.Msg.confirm(
                    "{% trans 'Warning' %}",
                    interpolate(
                      "{% trans 'Do you really want to change Volume size of <b>%(lv)s</b> to <b>%(megs)s</b> MB?' %}",
                      { "lv": sel.data.name, "megs": text }, true ),
                    function(btn){
                      if( btn == 'yes' ){
                        var progresswin = new Ext.Window({
                          title: "{% trans "Resizing Volume" %}",
                          layout: "fit",
                          height: 250,
                          width: 400,
                          modal: true,
                          html: "{% trans 'Please wait while your volume is being resized...' %}"
                        });
                        progresswin.show();
                        lvm__LogicalVolume.set( sel.data.id, {"megs": parseFloat(text)}, function(provider, response){
                          lvmGrid.store.reload();
                          progresswin.hide();
                        } );
                      }
                    }
                  );
                }
              }
            );
            });
          }
        }
      }, {
        text: "{% trans 'Delete Volume' %}",
        icon: MEDIA_URL + "/icons2/16x16/actions/remove.png",
        handler: this.deleteVolume,
        scope: lvmGrid
      }],
      keys: [{ scope: this, key: [Ext.EventObject.DELETE], handler: this.deleteVolume},{key: [65], handler: addVolume}],
      items: [{
        xtype: 'grid',
        region: "center",
        ref: 'lvpanel',
        store: (function(){
          // Anon function that is called immediately to set up the store's DefaultSort
          var store = new Ext.data.DirectStore({
            fields: ['name', 'megs', 'filesystem', 'formatted', 'id', 'fs', 'vg', 'fswarning', 'fscritical',
              {
                name: 'fsfree',
                mapping: 'fs',
                sortType: 'asInt',
                convert: function( val, row ){
                  if( val === null || typeof val.stat === "undefined" )
                    return -1; // fake to sort unknown values always at the bottom
                  return val.stat.freeG.toFixed(2);
                }
              }, {
                name: 'fsused',
                mapping: 'fs',
                sortType: 'asInt',
                convert: function( val, row ){
                  if( val === null || typeof val.stat === "undefined" )
                    return -1;
                  return val.stat.usedG.toFixed(2);
                }
              }, {
                name: 'fspercent',
                mapping: 'fs',
                sortType: 'asInt',
                convert: function( val, row ){
                  if( val === null || typeof val.stat === "undefined" )
                    return -1;
                  return (val.stat.used / val.stat.size * 100 ).toFixed(2);
                }
              },{
                name: 'vgname',
                mapping: 'vg',
                convert: function(val, row){
                  if( val === null || typeof val === "undefined" )
                    return '';
                  return val.name;
                }
              }],
            baseParams: { "snapshot__isnull": true },
            directFn: lvm__LogicalVolume.filter
          });
          store.setDefaultSort("name");
          return store;
        }()),
        viewConfig: { forceFit: true },
        colModel:  new Ext.grid.ColumnModel({
          defaults: {
            sortable: true
          },
          columns: [{
            header: "{% trans "LV" %}",
            dataIndex: "name"
          }, {
            header: "{% trans "Size" %}",
            dataIndex: "megs",
            align: 'right',
            renderer: function( val, x, store ){
              if( val >= 1000 )
                return String.format("{0} GB", (val / 1000).toFixed(2));
              return String.format("{0} MB", val);
            }
          }, {
            header: "{% trans "FS" %}",
            dataIndex: "filesystem",
            renderer: function( val, x, store ){
              if( val )
                return val;
              return "&ndash;";
            }
          }, {
            header: "{% trans "Free" %}",
            dataIndex: "fsfree",
            align: 'right',
            renderer: function( val, x, store ){
              if( !val || val === -1 )
                return '';
              return String.format("{0} GB", val);
            }
          }, {
            header: "{% trans "Used" %}",
            dataIndex: "fsused",
            align: 'right',
            renderer: function( val, x, store ){
              if( !val || val === -1 )
                return '';
              return String.format("{0} GB", val);
            }
          }, {
            header: "{% trans "Used%" %}",
            dataIndex: "fspercent",
            align: 'right',
            renderer: function( val, x, store ){
              if( !val || val === -1 )
                return '';
              var id = Ext.id();
              (function(){
                new Ext.ProgressBar({
                  renderTo: id,
                  value: val/100.,
                  text:  String.format("{0}%", val),
                  cls:   ( val > store.data.fscritical ? "lv_used_crit" :
                          (val > store.data.fswarning  ? "lv_used_warn" : "lv_used_ok"))
                });
              }).defer(25)
              return '<span id="' + id + '"></span>';
            }
          },{
            header: "{% trans "Group" %}",
            dataIndex: "vgname",
            align: 'center'
          }]
        }),
        listeners: {
          cellmousedown: function( self, rowIndex, colIndex, evt ){
            var graph_enabled = Ext.state.Manager.get("storage_utilization_graph", false);
            var record = self.getStore().getAt(rowIndex);
            var chartpanel = self.ownerCt.items.items[1];
            var defer = false;
            if( !chartpanel.collapsed ){
              chartpanel.collapse();
              defer = true;
            }
            if( !record.data.filesystem || currentChartId === record.data.id || graph_enabled == false){
              currentChartId = null;
              return;
            }
            currentChartId = record.data.id;
            chartpanel.items.items[0].store.loadData([[
                record.data.id, record.data.name,
                record.data.fsused, record.data.fsfree,
                (record.data.megs / 1000).toFixed(2)
              ]]);
            if( defer )
              chartpanel.expand.defer(500, chartpanel);
            else
              chartpanel.expand();
          }
        }
      },
      {
        split: true,
        region: "east",
        title: "{% trans "Storage usage" %}",
        collapsible: true,
        width: 400,
        collapsed: true,
        layout: "fit",
        ref: 'chartpanel',
        items: new Ext.DataView({
          tpl: new Ext.XTemplate(
            '<tpl for=".">',
              '<div class="thumb-wrap" id="{name}">',
                '<img src="{{ PROJECT_URL }}/lvm/mem/{id}.png" width="450" title="{name}" />',
                '<span class="fsstat">{fsused} GB used &ndash; {fsfree} GB free &ndash; {total} GB total</span>',
              '</div>',
            '</tpl>'),
          singleSelect: true,
          autoHeight: true,
          itemSelector: 'div.thumb_wrap',
          loadingText: "{% trans 'Loading...' %}",
          store: new Ext.data.ArrayStore({
            fields: ['id', 'name', 'fsused', 'fsfree', 'total'],
            data: []
          })
        })
      }]
    }));
    Ext.oa.Lvm__LogicalVolume_Panel.superclass.initComponent.apply(this, arguments);
  },
  
  deleteVolume: function(self){
    var lvmGrid = this.items.items[0];
    var sm = lvmGrid.getSelectionModel();
      if( sm.hasSelection() ){
        var sel = sm.selections.items[0];
        Ext.Msg.confirm(
          "{% trans 'Confirm delete' %}",
          interpolate(
            "{% trans 'Really delete volume %s and all its shares?<br /><b>There is no undo and you will lose all data.</b>' %}",
            [sel.data.name] ),
          function(btn, text){
            if( btn == 'yes' ){
              lvm__LogicalVolume.remove( sel.data.id, function(provider, response){
                lvmGrid.store.reload();
              } );
            }
          }
        );
      }
    },
  
  onRender: function(){
    Ext.oa.Lvm__LogicalVolume_Panel.superclass.onRender.apply(this, arguments);
    this.items.items[0].store.reload();
    var self = this;
    var menu = new Ext.menu.Menu({
    items: [{
            id: 'delete',
            text: 'delete',
            icon: MEDIA_URL + "/icons2/16x16/actions/remove.png",
        }],
        listeners: {
          itemclick: function(item) {
                    self.deleteVolume()
          }
        }
    });
    this.items.items[0].on({
      'contextmenu': function(event) {
        if( this.getSelectionModel().hasSelection() ){
          event.stopEvent();
          this.getSelectionModel
          menu.showAt(event.xy);
        }
      }
    });
  }
});
                    
  

Ext.reg("lvm__logicalvolume_panel", Ext.oa.Lvm__LogicalVolume_Panel);

Ext.oa.Lvm__LogicalVolume_Module = Ext.extend(Object, {
  panel: "lvm__logicalvolume_panel",
  prepareMenuTree: function(tree){
    tree.appendToRootNodeById("menu_storage", {
      text: "{% trans 'Volume Management' %}",
      leaf: true,
      icon: MEDIA_URL + '/icons2/22x22/apps/volume.png',
      panel: "lvm__logicalvolume_panel_inst",
      href: '#'
    });
  }
});


window.MainViewModules.push( new Ext.oa.Lvm__LogicalVolume_Module() );

// kate: space-indent on; indent-width 2; replace-tabs on;
