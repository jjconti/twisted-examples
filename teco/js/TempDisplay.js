// import Nevow.Athena
// import jquery
// import json2

TempDisplay.TempWidget = Nevow.Athena.Widget.subclass('TempDisplay.TempWidget');

TempDisplay.TempWidget.methods(
    function __init__(self, node) {
        TempDisplay.TempWidget.upcall(self, "__init__", node);
        
        self.tempWidget = self.nodeByAttribute('name', 'terElement');

        self.nodos = {};
        self.enableChangeFlag = false;
        self.firstTime = true;
    },

    function doRead(self) {
        // ejecuta funcion read en el servidor
        self.callRemote("read");

        // mostrar imagen Leyendo...
        if (self.firstTime) {
            $("[name=reading_img]").show();
            }

        var boton = $("[name=botonLeer]");
        if (boton.attr('value') == "Leer"){
            boton.attr('value', "Detener");
        } else {
            boton.attr('value', "Leer");
            self.firstTime = true;
        }

        return false;

    },

    function doChange(self) {
        // desactivar boton
        var boton = $("[name=botonCambiar]");
        boton.attr('disabled', 'disabled');
        var campo = $("[name=valor_consigna]");
        campo.attr('disabled', 'disabled');         
        $("[name=changing_img]").show();
        // ejecuta funcion change en el servidor
        var cual = $("input[name='consignas']:checked").val();
        var cuanto = $("[name='valor_consigna']").val();
        self.callRemote("change", cual, cuanto);
        return false;
    },

    function doChangeSD(self) {
        // desactivar boton
        var boton = $("[name=botonCambiar]");
        boton.attr('disabled', 'disabled');
        var campo = $("[name=valor_consigna]");
        campo.attr('disabled', 'disabled');         
        $("[name=changing_imgSD]").show();
        // ejecuta funcion change en el servidor
        var cual = $("input[name='consignasSD']:checked").val();
        var cuanto = $("[name='sd" + cual +"']").text();
        self.callRemote("changeSD", cual, cuanto);
        return false;
    },
        
    function enableChange(self) {
        self.enableChangeFlag = true;            
    },
    
    function errorMesg(self, msg) {
    
        // si el boton Cambiar esta desactivado, activarlo
        $("[name=error_msg]").val(msg);
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
        
        if (self.enableChangeFlag) {
            // si el boton Cambiar esta desactivado, activarlo
            var boton = $("[name=botonCambiar]");
            boton.removeAttr('disabled');
            var campo = $("[name=valor_consigna]");
            campo.removeAttr('disabled'); 
            $("[name=valor_consigna]").val('');
            $("[class=changing]").hide();
            self.enableChangeFlag = false;
        }

        if (self.firstTime) {
            $("[name=reading_img]").hide();
            
            // activar Cambiar
            var boton = $("[name=botonCambiar]");
            boton.removeAttr('disabled');
            var campo = $("[name=valor_consigna]");
            campo.removeAttr('disabled');
            
            self.firstTime = false;
            }
        // actualizar valores
        data = JSON.parse(data);
        $.each(data, function(k,v) {
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

