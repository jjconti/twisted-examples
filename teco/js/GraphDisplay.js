// import Nevow.Athena
// import jquery
// import excanvas
// import flot

GraphDisplay.GraphWidget = Nevow.Athena.Widget.subclass('GraphDisplay.GraphWidget');

GraphDisplay.GraphWidget.methods(
    
    function __init__(self, node) {
        alert(node)
    
        GraphDisplay.GraphWidget.upcall(self, "__init__", node);
         self.tick = 0;
         
         var options = { legend: { noColumns: 2 }, 
                                  yaxis: { max: 50, min: 0 },  
                                  xaxis: { max: 275, min: 0 }}

         var options2 = { legend: { noColumns: 2 }, 
                                  yaxis: {  min: -0.5, max: 7.5 },  
                                  xaxis: {  min: 0, max: 275}}
         self.options = options;
         self.options2 = options2;        
         
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
         var datasets2 = {
                                    "r1" : { label: "r1",  data: [], 0: 0, 1: 1},
                                    "r2" : { label: "r2",  data: [], 0: 2, 1: 3},
                                    "r3" : { label: "r3",  data: [], 0: 4, 1: 5},
                                    "r4" : { label: "r4",  data: [], 0: 6, 1: 7},                                    
                                  }
        self.datasets = datasets
        self.datasets2 = datasets2
        // hard-code color indices to prevent them from shifting
        var i = 0;
        $.each(datasets, function(key, val) {
            val.color = i;
            i++;
         });
        $.each(datasets2, function(key, val) {
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
        var data2 = []
        $.each(datasets2, function(key, val){
            data2.push(val);
        });
        // Crear grafico
        self.plot = $.plot($("[name=placeholder]"), data, options);
        self.plot2 = $.plot($("[name=placeholder2]"), data2, options2);
    },

    function doPlot(self) {
        var series = self.plot.getData();
        $.each(series, function(i, s){
            s.data = self.datasets[s.label].data;
        });
        self.plot.setData(series);
        self.plot.draw();
        var series2 = self.plot2.getData();
        $.each(series2, function(i, s){
            s.data = self.datasets2[s.label].data;
        });
        self.plot2.setData(series2);
        self.plot2.draw();

    },

    function doStart(self) {
        // ejecuta funcion start en el servidor
        self.callRemote("start");

        var boton = $("[name=botonGraficar]");
        if (boton.attr('value') == "Graficar"){
            boton.attr('value', "Detener");
        } else {
            boton.attr('value', "Graficar");
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
        $.each(self.datasets2, function(k, v){
            v.data.push([self.tick, v[valores[i]]]);    // v[0] o v[1]
            i++;
        });
        self.doPlot();
        self.tick++;
        if (self.tick > 275){
            self.tick = 0;
            $.each(self.datasets, function(k, v){
                v.data = [[self.tick,valores[i]]];
                i++;
            });
            $.each(self.datasets2, function(k, v){
                v.data = [[self.tick,valores[i]]];
                i++;
            });            
        }        
    }
);

