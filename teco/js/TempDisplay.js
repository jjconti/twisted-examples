// import Nevow.Athena

TempDisplay.TempWidget = Nevow.Athena.Widget.subclass('TempDisplay.TempWidget');

TempDisplay.TempWidget.methods(
    function __init__(self, node) {
        TempDisplay.TempWidget.upcall(self, "__init__", node);
        self.tempWidget = self.nodeByAttribute('name', 'terElement');
        self.tempSala = self.nodeByAttribute('id', 'temp_sala');
        self.tempRetorno = self.nodeByAttribute('id', 'temp_retorno');
        self.tempExterior = self.nodeByAttribute('id', 'temp_exterior');
    },

    function doRead(self) {
        // ejecuta funcion read en servidor
        self.callRemote("read");
        return false;
    },

    function actualizarValores(self, data) {
        // llamada por servidor para actualizar valores
        var valores = data.split(',');
        self.tempSala.value = valores[0];
        self.tempRetorno.value = valores[1];
        self.tempExterior.value = valores[2];                
    });

