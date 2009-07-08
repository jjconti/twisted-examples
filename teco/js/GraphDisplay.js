// import Nevow.Athena
// import jquery
// import excanvas
// import flot

GraphDisplay.GraphWidget = Nevow.Athena.Widget.subclass('GraphDisplay.GraphWidget');

GraphDisplay.GraphWidget.methods(
    function __init__(self, node) {
        GraphDisplay.GraphWidget.upcall(self, "__init__", node);
        self.plot = $.plot($("[name=placeholder]"),
               [ [], [] ], { yaxis: { max: 40 }, xaxis: { max: 60 } });
        self.index = 0
    },
    function doStart(self) {
        // ejecuta funcion start en el servidor
        self.callRemote("start");
        return false;
    },
    
    function nuevoValor(self, valor1, valor2) {
        // llamada por el servidor para actualizar la pantalla
        serie1 = self.plot.getData()[0];
        serie2 = self.plot.getData()[1];
        serie1.data.push([self.index,valor1]);
        serie2.data.push([self.index,valor2]);        
        self.plot.setData([serie1, serie2]);
        //self.plot.setupGrid();
        self.plot.draw();
        self.index++;
    }
);

