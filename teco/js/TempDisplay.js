// import Nevow.Athena
// import jquery
// import json2

TempDisplay.TempWidget = Nevow.Athena.Widget.subclass('TempDisplay.TempWidget');

TempDisplay.TempWidget.methods(
    function __init__(self, node) {
        TempDisplay.TempWidget.upcall(self, "__init__", node);
        
        self.tempWidget = self.nodeByAttribute('name', 'terElement');

        self.nodos = {};
     
    },

    function doRead(self) {
        // ejecuta funcion read en el servidor
        self.callRemote("read");

        var boton = $("[name=botonLeer]");
        if (boton.attr('value') == "Leer"){
            boton.attr('value', "Detener");
        } else {
            boton.attr('value', "Leer");
        }
                
        return false;
    },

    function doChange(self) {
        // ejecuta funcion change en el servidor
        var cual = $("input[name='consignas']:checked").val();
        var cuanto = $("[name='valor_consigna']").val();
        self.callRemote("change", cual, cuanto);
        return false;
    },
    
    function actualizarValor(self, id, valor) {
        nodo =  self.nodeByAttribute('name', id);
        if (id in self.nodos) {
           self.nodos[id].removeChild(self.nodos[id].lastChild);
           self.nodos[id].appendChild(document.createTextNode(' ' + valor));
        } else {
            nodo.appendChild(document.createTextNode(' ' + valor));
            self.nodos[id] = nodo;
        };
        
    },
    
    function actualizarValores2(self, data) {
        dict = JSON.parse(data);
        $.each(dict, function(k,v) {
            self.actualizarValor(k, v);
        });

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

