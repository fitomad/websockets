/**
 * Evento `click` del boton de login
 */
id("buttonLogin").addEventListener("click", function(e) {
    var nickname = id("txtUsername").value
    var room = id("txtRoom").value
    var private = false

    var uri = "web/chat.html?nick=" + nickname + "&room=" + room + "&private=" + private
    window.location.replace(uri)
})

/**
 * Helper method.
 * Recupera un elemento del arbol DOM en base a su
 * identificador `id`
 * 
 * @param {*} identifier 
 */
function id(identifier)
{
    return document.getElementById(identifier)
}