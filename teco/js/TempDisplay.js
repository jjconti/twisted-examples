// import Nevow.Athena

TempDisplay.TempWidget = Nevow.Athena.Widget.subclass('TempDisplay.TempWidget');

TempDisplay.TempWidget.methods(
    function __init__(self, node) {
        TempDisplay.TempWidget.upcall(self, "__init__", node);
        
        self.tempWidget = self.nodeByAttribute('name', 'terElement');

        self.tempSalaTxt = document.createTextNode('');
        self.tempSala = self.nodeByAttribute('name', 'temp_sala')
        self.tempSala.appendChild(self.tempSalaTxt);

        self.tempRetornoTxt = document.createTextNode('');
        self.tempRetorno = self.nodeByAttribute('name', 'temp_retorno');
        self.tempRetorno.appendChild(self.tempRetornoTxt);

        self.tempExteriorTxt = document.createTextNode('');
        self.tempExterior = self.nodeByAttribute('name', 'temp_exterior');
        self.tempExterior.appendChild(self.tempExteriorTxt);
    },

    function doRead(self) {
        // ejecuta funcion read en servidor
        self.callRemote("read");
        return false;
    },

    function actualizarValores(self, data) {
        // llamada por servidor para actualizar valores
        var valores = data.split(',');
        
        self.tempSala.removeChild(self.tempSalaTxt);
        self.tempSalaTxt = document.createTextNode(' ' + valores[0]);
        self.tempSala.appendChild(self.tempSalaTxt);

        self.tempRetorno.removeChild(self.tempRetornoTxt);
        self.tempRetornoTxt = document.createTextNode(' ' + valores[1]);
        self.tempRetorno.appendChild(self.tempRetornoTxt);

        self.tempExterior.removeChild(self.tempExteriorTxt);
        self.tempExteriorTxt = document.createTextNode(' ' + valores[2]);
        self.tempExterior.appendChild(self.tempExteriorTxt);
    });

