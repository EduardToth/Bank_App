function reload_page_on_back_button(div_id, request_message) {
    window.addEventListener( "pageshow", function ( event ) {
            const historyTraversal = event.persisted ||
                (typeof window.performance != "undefined" &&
                    window.performance.navigation.type === 2);

            if ( historyTraversal ) {

                function loadXMLDoc() {
                    var xhttp = new XMLHttpRequest();
                    xhttp.onreadystatechange = function() {
                        if (this.readyState === 4 && this.status === 200) {
                            document.getElementById(div_id).innerHTML =
                                this.responseText;
                        }
                    };
                    xhttp.open("GET", request_message, true);
                    xhttp.send();
                }
                loadXMLDoc();
            }
        });
}