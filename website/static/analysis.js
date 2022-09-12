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
                var quote_obj = json_obj['quotation']              
                results_box = document.querySelector('.quote-results-box')
                results_box.style.backgroundColor = "#f1f1f1";
                results_box.style.borderRadius = "1rem";
                var new_html = "<h1 class='body-heading'>Your Quotation</h1 >"
                // Add Input Parameters
                new_html += "<p class='quote-intro-text'>" + json_obj['description'] + "</p>"
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
                new_html += "<p class='quote-intro-text'>" + equip_obj['description'] + "</p>"
                var items = equip_obj['items']
                // Add Equipment Specification (Requirements)
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
                // Add Quotation
                new_html += "<h2 class='body-heading'>" + quote_obj['disp_name'] + "</h2>"
                new_html += "<p class='quote-intro-text'>" + quote_obj['description'] + "</p>"
                var quote_items = quote_obj['items']
                console.log(quote_obj)
                for (var item of Object.keys(quote_items)) {
                    new_html += "<div class='param-box'>"
                    new_html += "<h3 class='body-subheading'>" + quote_items[item]['disp_name'] + "</h3>"
                    new_html += "<p class='param-intro-text'>" + quote_items[item]['description'] + "</p>"
                    var options = quote_items[item]['options']
                    console.log(item)
                    options.forEach(element => {
                        // if (item == 'battery')
                        // console.log(element)
                        new_html += "<h4 class='body-subheading'>" + element['disp_name'] + "</h4>"
                        new_html += "<p class='param-intro-text'>" + element['description'] + "</p>"
                        for (var key of Object.keys(element['details'])) {
                            // console.log(" "+key)
                            
                            new_html += "<p>" + key + ": " + element['details'][key][0] + element['details'][key][1] + "</p>"
                        }
                    });
                    new_html += "</div>"
                }
                new_html += "<h2 class='body-heading'>Total Cost</h2>"
                new_html += "<p class='quote-intro-text'>Find here the costs extracted from the sections above and added together.</p>"
                new_html += "<div class='param-box'>"
                new_html += "<h3 class='body-subheading'>Cost per Component</h3>"
                new_html += "<p>Cost of Battery(ies): " + "R" + quote_obj['totals']['bat'] + "</p>"
                new_html += "<p>Cost of Inverter(s): " + "R" + quote_obj['totals']['inv'] + "</p>"
                new_html += "<p>Cost of Solar Panel(s): " + "R" + quote_obj['totals']['pv'] + "</p>"
                new_html += "<h4 class='body-subheading'>Total: " + "R" + quote_obj['totals']['total'] + "</h4>"
                new_html += "</div>"
                results_box.innerHTML = new_html;
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