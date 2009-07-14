// import Nevow.Athena
// import jquery
// import excanvas
// import flot

GraphDisplay.GraphWidget = Nevow.Athena.Widget.subclass('GraphDisplay.GraphWidget');

GraphDisplay.GraphWidget.methods(
    
    function __init__(self, node) {
        GraphDisplay.GraphWidget.upcall(self, "__init__", node);
        self.plot = $.plot($("[name=placeholder]"),
               [ [], [], [], [] ], { yaxis: { max: 40 },  xaxis: { max: 60 } }); // 4 series
        self.index = 0
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
        // llamada por el servidor para actualizar la pantalla
        var valores = data.split(',');
        var series = []
        for (i=0; i <= 3; i++){
            var serie = self.plot.getData()[i];
            serie.data.push([self.index,valores[i]]);
            series.push(serie);
        }
        self.plot.setData(series);
        //self.plot = $.plot($("[name=placeholder]"),
        //       series, { yaxis: { max: 40 }, });
        //self.plot.setupGrid();
        self.plot.draw();
        self.index++;
    }
);

