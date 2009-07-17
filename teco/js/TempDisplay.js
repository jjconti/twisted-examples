// import Nevow.Athena
// import jquery

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
        
        self.todoTxt = document.createTextNode('');
        self.todo = self.nodeByAttribute('name', 'todo');
        self.todo.appendChild(self.todoTxt);
    },

    function doRead(self) {
        // ejecuta funcion read en el servidor
        self.callRemote("read");
        return false;
    },

    function doChange(self) {
        // ejecuta funcion change en el servidor
        var cual = $("input[name='consignas']:checked").val();
        var cuanto = $("[name='valor_consigna']").val();
        self.callRemote("change", cual, cuanto);
        return false;
    },
    
    function actualizarValores(self, data) {
        // llamada por el servidor para actualizar la pantalla
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

        self.todo.removeChild(self.todoTxt);
        self.todoTxt = document.createTextNode(' ' + valores);
        self.todo.appendChild(self.todoTxt);
    });

