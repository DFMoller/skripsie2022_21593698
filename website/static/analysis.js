document.addEventListener("DOMContentLoaded", function() {

    function reloadPage(){

        var periodForm = document.getElementById("period-form");
        periodForm.submit();

    }

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
                    new_html += "<p>" + params[param]['disp_name'] + ": <strong>" + params[param]['val'] + " " + params[param]['unit'] + "</strong></p>"
                }
                new_html += "</div>"
                new_html += "<h2 class='body-heading'>" + equip_obj['disp_name'] + "</h2>"
                new_html += "<p class='quote-intro-text'>" + equip_obj['description'] + "</p>"
                var items = equip_obj['items']
                // Add System Requirements
                for (var item of Object.keys(items)) {
                    // item = "Battery", items = dict(description, disp_name, specs)
                    new_html += "<div class='param-box'>"
                    new_html += "<h3 class='body-subheading'>" + items[item]['disp_name'] + "</h3>"
                    new_html += "<p class='param-intro-text'>" + items[item]['description'] + "</p>"
                    var specs = items[item]['specs']
                    for (var spec of Object.keys(specs)) {
                        new_html += "<p>" + spec + ": <strong>" + specs[spec]['val'] + " " + specs[spec]['unit'] + "</strong></p>"
                    }
                    new_html += "</div>"
                }
                // Add Quotation
                new_html += "<h2 class='body-heading'>" + quote_obj['disp_name'] + "</h2>"
                new_html += "<p class='quote-intro-text'>" + quote_obj['description'] + "</p>"
                var quote_items = quote_obj['items']
                for (var item of Object.keys(quote_items)) {
                    new_html += "<div class='param-box'>"
                    new_html += "<h3 class='body-subheading'>" + quote_items[item]['disp_name'] + "</h3>"
                    new_html += "<p class='param-intro-text'>" + quote_items[item]['description'] + "</p>"
                    var options = quote_items[item]['options']
                    options.forEach(element => {
                        // Sub-heading and introduction for component quotation
                        new_html += "<h4 class='body-subheading'>" + element['disp_name'] + "</h4>"
                        new_html += "<p class='param-intro-text'>" + element['description'] + "</p>"
                        const details = element['details'];
                        let item_combined_size = details.total_size.val;
                        let item_unit = details.total_size.unit;
                        let item_total_cost = details.total_cost.val;
                        let item_currency = details.total_cost.currency;
                        // Create table
                        new_html += "<table>";
                        new_html += "<tr><th>" + quote_items[item].disp_name + "</th><th>" + details.unit_size.disp_name + "</th><th>Cost</th><tr>";
                        let count = 0;
                        let num_units = details.num_units.val;
                        for (let i = 0; i < num_units; i++) {
                            count ++;
                            let cost = details.unit_cost.val;
                            let size = details.unit_size.val;
                            let item_name = "Unit " + count;
                            new_html += "<tr><td>" + item_name + "</td><td>" + size + " " + item_unit + "</td><td>" + item_currency + " " + cost + "</td></tr>";
                        }
                        new_html += "<tr><td class='hl_top'><strong>Totals</strong></td><td class='hl_top'><strong>" + item_combined_size + " " + item_unit + "</strong></td><td class='hl_top'><strong>" + item_currency + " " + item_total_cost + "</strong></td></tr>"
                        new_html += "</table>"
                    });
                    new_html += "</div>"
                }
                // Add totals
                let num_bat = quote_obj.items.battery.options[0].details.num_units.val;
                let num_inv = quote_obj.items.inverter.options[0].details.num_units.val;
                let num_pan = quote_obj.items.PV.options[0].details.num_units.val;
                let bat_unit_cost = quote_obj.items.battery.options[0].details.unit_cost.val;
                let inv_unit_cost = quote_obj.items.inverter.options[0].details.unit_cost.val;
                let pan_unit_cost = quote_obj.items.PV.options[0].details.unit_cost.val;
                let bat_total_cost = quote_obj.items.battery.options[0].details.total_cost.val;
                let inv_total_cost = quote_obj.items.inverter.options[0].details.total_cost.val;
                let pan_total_cost = quote_obj.items.PV.options[0].details.total_cost.val;
                let total_cost = bat_total_cost + inv_total_cost + pan_total_cost;
                new_html += "<h2 class='body-heading'>Total Cost</h2>"
                new_html += "<p class='quote-intro-text'>Find here the costs extracted from the sections above and added together.</p>"
                new_html += "<div class='param-box'>"
                new_html += "<h3 class='body-subheading'>Cost per Component</h3>"
                new_html += "<p class='param-intro-text'>Here is a summary cost breakdown.</p>"
                // Create table
                new_html += "<table>";
                new_html += "<tr><th>Item</th><th>Quantity</th><th>Unit Cost</th><th>Group Cost</th></tr>";
                new_html += "<tr><td>Battery(ies)</td><td>" + num_bat + "</td><td>R " + bat_unit_cost + "</td><td>R " + bat_total_cost + "</td></tr>";
                new_html += "<tr><td>Inverter(s)</td><td>" + num_inv + "</td><td>R " + inv_unit_cost + "</td><td>R " + inv_total_cost + "</td></tr>";
                new_html += "<tr><td>PV Panel(s)</td><td>" + num_pan + "</td><td>R " + pan_unit_cost + "</td><td>R " + pan_total_cost + "</td></tr>";
                new_html += "<tr><td class='hl_top'><strong>Total Cost</strong></td><td class='hl_top'> </td><td class='hl_top'> </td><td class='hl_top'><strong>R " + total_cost + "</strong></td></tr>";
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