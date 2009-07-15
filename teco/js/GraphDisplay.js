// import Nevow.Athena
// import jquery
// import excanvas
// import flot

GraphDisplay.GraphWidget = Nevow.Athena.Widget.subclass('GraphDisplay.GraphWidget');

GraphDisplay.GraphWidget.methods(
    
    function __init__(self, node) {
    
        GraphDisplay.GraphWidget.upcall(self, "__init__", node);
         self.tick = 0;
         
         var options = { legend: { noColumns: 2 }, 
                                  yaxis: { max: 40, min: 10 },  
                                  xaxis: { max: 60, min: 0 }}
        self.options = options;
         
         var datasets = {
                                    "ea1" : { label: "ea1",  data: []},
                                    "ea2" : { label: "ea2",  data: []},
                                    "ea3" : { label: "ea3",  data: []},
                                    "ea4" : { label: "ea4",  data: []},
                                    "c1" : { label: "c1",  data: []},
                                    "c2" : { label: "c2",  data: []},
                                    "c3" : { label: "c3",  data: []},
                                    "c4" : { label: "c4",  data: []},                                    
                                  }
        self.datasets = datasets
        // hard-code color indices to prevent them from shifting
        var i = 0;
        $.each(datasets, function(key, val) {
            val.color = i;
            i++;
         });
        // insert checkboxes 
        var choiceContainer = $("[name=choices]");
        self.choiceContainer = choiceContainer;
        $.each(datasets, function(key, val) {
            choiceContainer.append('<input type="checkbox" name="' + key +
                                                  '" checked="checked" >' + val.label + '</input>');
        });
        choiceContainer.find("input").click(function() {
                var data = [];
                self.choiceContainer.find("input:checked").each(function () {
                    var key = $(this).attr("name");
                    if (key && self.datasets[key]){
                        data.push(self.datasets[key]);
                        }
                });
                if (data.length > 0) {
                    self.plot = $.plot($("[name=placeholder]"), data, self.options);
                } else {
                    self.plot = $.plot($("[name=placeholder]"), [[]], self.options);
                }
        });
        var data = []
        $.each(datasets, function(key, val){
            data.push(val);
        });
        self.plot = $.plot($("[name=placeholder]"), data, options);
    },

    function doPlot(self) {
        var series = self.plot.getData();
        $.each(series, function(i, s){
            s.data = self.datasets[s.label].data;
        });
        self.plot.setData(series);
        self.plot.draw();
    },

    function doStart(self) {
        // ejecuta funcion start en el servidor
        self.callRemote("start");

        var boton = $("[name=boton]");
        if (boton.attr('value') == "Start"){
            boton.attr('value', "Stop");
        } else {
            boton.attr('value', "Start");
        }

        return false;
    },
    
    function nuevoValor(self, data) {
        var valores = data.split(',');
        var i = 0;
        $.each(self.datasets, function(k, v){
            v.data.push([self.tick,valores[i]]);
            i++;
        });
        self.doPlot();
        self.tick++;
        if (self.tick > 60){
            self.tick = 0;
            $.each(self.datasets, function(k, v){
                v.data = [[self.tick,valores[i]]];
                i++;
            });
        }        
    }
);

