document.addEventListener("DOMContentLoaded", function() {

    function reloadPage(){

        var periodForm = document.getElementById("period-form");
        periodForm.submit();

    }

    // function generateQuotation(){
    //     var xhttp = new XMLHttpRequest();
    //     xhttp.onreadystatechange = function() {
    //         if (this.readyState == 4 && this.status == 200) {
    //             console.log('responseText:' + xmlhttp.responseText);
    //             try {
    //                 var data = JSON.parse(xmlhttp.responseText);
    //             } catch(err) {
    //                 console.log(err.message + " in " + xmlhttp.responseText);
    //                 return;
    //             }
    //             // document.getElementById("demo").innerHTML = this.responseText;
    //         }
    //     };
    //     xhttp.open("POST", "/analysis", true);
    //     xhttp.send();
    // }

    function AJAX_Request(e){
        e.preventDefault()
        var form = e.target
        var data = new FormData(form)
        var request = new XMLHttpRequest()
        
        request.onreadystatechange = function(){
            if (this.readyState == 4 && this.status == 200){
                console.log("AJAX Complete!");
                var json_obj = JSON.parse(request.responseText);
                var param_obj = json_obj['power']
                var equip_obj = json_obj['equipment']                
                results_box = document.querySelector('.quote-results-box')
                results_box.style.backgroundColor = "#f1f1f1";
                results_box.style.borderRadius = "1rem";
                var new_html = "<h1 class='body-heading'>Your Quotation</h1 >"
                // Add Input Parameters
                new_html += "<p>" + json_obj['description'] + "</p>"
                new_html += "<div class='param-box'>"
                new_html += "<h3 class='body-subheading'>" + param_obj['disp_name'] + "</h3>"
                new_html += "<p class='param-intro-text'>" + param_obj['description'] + "</p>"
                var params = param_obj['params']
                for (var param of Object.keys(params)) {
                    // Param = "Usage", param_obj[param] = dict(val, disp_name, unit, description)
                    new_html += "<p>" + params[param]['disp_name'] + ": " + params[param]['val'] + " " + params[param]['unit'] + "</p>"
                }
                new_html += "</div>"
                new_html += "<h2 class='body-heading'>" + equip_obj['disp_name'] + "</h2>"
                new_html += "<p>" + equip_obj['description'] + "</p>"
                var items = equip_obj['items']
                // new_html = ""
                for (var item of Object.keys(items)) {
                    // item = "Battery", equip_obj[item] = dict(description, disp_name, specs)
                    new_html += "<div class='param-box'>"
                    new_html += "<h4 class='body-subheading'>" + items[item]['disp_name'] + "</h4>"
                    new_html += "<p class='param-intro-text'>" + items[item]['description'] + "</p>"
                    var specs = items[item]['specs']
                    for (var spec of Object.keys(specs)) {
                        new_html += "<p>" + spec + ": " + specs[spec]['val'] + " " + specs[spec]['unit'] + "</p>"
                    }
                    new_html += "</div>"
                }
                results_box.innerHTML += new_html;
            }
        }
        
        request.open(form.method, form.action, true)
        request.timeout = 2000
        request.send(data)
    }

    document.getElementById('quote-form').addEventListener("submit", function(e){
        AJAX_Request(e)
    })
});