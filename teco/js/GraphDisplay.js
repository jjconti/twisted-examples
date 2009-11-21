// import Nevow.Athena
// import jquery
// import excanvas
// import flot
// import json2

GraphDisplay.GraphWidget = Nevow.Athena.Widget.subclass('GraphDisplay.GraphWidget');

GraphDisplay.GraphWidget.methods(
    
    function __init__(self, node) {
         GraphDisplay.GraphWidget.upcall(self, "__init__", node);
         self.tick = 0;
    },

    function inicializar(self, full){
         
         var datasets = {}
         $.each(full['entradasanalogicas'], function(i, v){
            datasets[v] = { label: v, data: [] }
         });
         $.each(full['registros'], function(i, v){
            datasets[v] = { label: v, data: [] }
         });
         
         var datasets2 = {}
         var e = 0
         ticksnames = []
         $.each(full['entradasdigitales'], function(i, v){
            datasets2[v] = { label: v, data: [], 0: e, 1: e+2 }
            ticksnames.push([e, v + '_off'])
            ticksnames.push([e+2, v + '_on'])
            e += 4
         });
         $.each(full['salidasdigitales'], function(i, v){
            datasets2[v] = { label: v, data: [], 0: e, 1: e+2 }
            ticksnames.push([e, v + '_off'])
            ticksnames.push([e+2, v + '_on'])
            e += 4
         });
         
        self.datasets = datasets
        self.datasets2 = datasets2

         var options = { legend: { noColumns: 2 }, 
                         yaxis: { max: 50, min: 0 },  
                         xaxis: { max: 275, min: 0 }}

         var options2 = { legend: { noColumns: 2 }, 
                          yaxis: { min: -0.5, max: e - 1.5, ticks: ticksnames},  
                          xaxis: { min: 0, max: 275 },
                          lines: { steps: true }
                          }
                          
         self.options = options;
         self.options2 = options2;              

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
        var choiceContainer2 = $("[name=choices2]");
        self.choiceContainer = choiceContainer;
        self.choiceContainer2 = choiceContainer2;

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
        choiceContainer2.find("input").click(function() {
                var data = [];
                self.choiceContainer2.find("input:checked").each(function () {
                    var key = $(this).attr("name");
                    if (key && self.datasets2[key]){
                        data.push(self.datasets2[key]);
                        }
                });
                if (data.length > 0) {
                    self.plot2 = $.plot($("[name=placeholder2]"), data, self.options2);
                } else {
                    self.plot2 = $.plot($("[name=placeholder2]"), [[]], self.options2);
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
        
    function saludar(self, msg){
        alert(msg)
    },

    function doPlot(self) {
        var series = self.plot.getData();
        $.each(series, function(i, s){
            s.data = self.datasets[s.label].data;
        });
        self.plot.setData(series);
//        self.plot.setupGrid() // reescala x e y
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
    
    function nuevoValor2(self, data) {
        data = JSON.parse(data);
        $.each(self.datasets, function(k, v){
            v.data.push([self.tick, data[k]]);
        });
        $.each(self.datasets2, function(k, v){
            v.data.push([self.tick, v[data[k]]]);    // v[0] o v[1]
        });
        
        self.doPlot();
        self.tick++;
        if (self.tick > 275){
            self.tick = 0;
            $.each(self.datasets, function(k, v){
                v.data = [[self.tick, data[k]]];
            });
            $.each(self.datasets2, function(k, v){
                v.data = [[self.tick, data[k]]];
            });            
        }        
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

