// import Nevow.Athena

TempDisplay.TempWidget = Nevow.Athena.Widget.subclass('TempDisplay.TempWidget');

TempDisplay.TempWidget.methods(
    function __init__(self, node) {
        TempDisplay.TempWidget.upcall(self, "__init__", node);
        self.tempWidget = self.nodeByAttribute('name', 'terElement');
        self.tempSala = self.nodeByAttribute('name', 'temp_sala');
        self.tempSala.appendChild(document.createTextNode('');
        self.tempRetorno = self.nodeByAttribute('name', 'temp_retorno');
        self.tempRetorno.appendChild(document.createTextNode('');        
        self.tempExterior = self.nodeByAttribute('name', 'temp_exterior');
        self.tempExterior.appendChild(document.createTextNode('');                
    },

    function doRead(self) {
        // ejecuta funcion read en servidor
        self.callRemote("read");
        return false;
    },

    function actualizarValores(self, data) {
        // llamada por servidor para actualizar valores
        var valores = data.split(',');
        self.tempSala.firstChild.replaceNode(document.createTextNode(' ' + valores[0]));
        self.tempRetorno.firstChild.replaceNode(document.createTextNode(' ' + valores[1]));
        self.tempExterior.firstChild.replaceNode(document.createTextNode(' ' + valores[2]));                
    });

