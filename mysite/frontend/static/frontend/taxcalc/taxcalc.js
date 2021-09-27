
function setInputAttrs(ele) {
    // Get tax value coming from backend
    try { 
        var tax = tax_dict[ele.id] 
    } catch { 
        var tax = "" 
    }
    // Get current form value
    var req = request_form[ele.id]

    // Check for invalid input
    if (req != undefined && (isNaN(req) || (ele.id == "tax_rate" && (parseFloat(req) < 0 || parseFloat(req) > 100)))) {
        ele.classList.add('is-invalid')
    }
    else if (req) {
        ele.value = req
    }
    else if (typeof tax === 'number') {
        console.log(ele.id + " tax: " + tax)
        ele.value = tax
        ele.classList.remove('is-invalid')
        ele.readOnly = true
    }
}

function countPopulated(all_inps) {
    var populated = 0
    for (var i=0; i < all_inps.length; i++) {
        if (all_inps[i].value.length > 0) {
            populated++
        }
    }
    return populated
}

function clearInvalid(all_inps) {
    Array.from(all_inps).forEach(element => {
        element.classList.remove('is-invalid')
    });
}

function limitInput() {
    var all_inps = document.getElementsByClassName("trace");
    var populated = countPopulated(all_inps)
    clearInvalid(all_inps)

    if (populated > 2) {
        for (var i=0; i < all_inps.length; i++) {
            if (all_inps[i].readOnly == true) {
                all_inps[i].readOnly = false
                all_inps[i].value = ""
                populated--
            }
        }
    }
    if (populated == 2) {
        for (var i=0; i < all_inps.length; i++) {
            if (all_inps[i].value.length == 0) {
                all_inps[i].readOnly = true
            }
        }
    }
    else {
        for (var i=0; i < all_inps.length; i++) {
            all_inps[i].readOnly = false
        }
    }
}

/**
 * Validate all fields against bad input
 */
function validate() {
    var fields = document.getElementsByClassName("trace")
    var is_valid = true
    Array.from(fields).forEach(field => {
        var value = field.value
        if (value != undefined && (isNaN(value) || (field.id == "tax_rate" && (parseFloat(value) < 0 || parseFloat(value) > 100)))) {
            field.classList.add('is-invalid')
            is_valid = false
        }
    })
    if (!dontSubmitIfNoChange()) {
        is_valid = false
    }
    if (!is_valid) {
        document.activeElement.blur()
        return false
    }
    return true
}

/**
 * Clear all input
 * @param {Element} btn The 'clear' button
 */
function clearAll(btn) {
    var fields = document.getElementsByClassName("trace")
    Array.from(fields).forEach(element => {
        element.value = ""
        element.readOnly = false
        element.classList.remove('is-invalid')
    });
    btn.blur()
}

/**
 * Only submit form if values have changed
 * @returns {bool}
 */
function dontSubmitIfNoChange() {
    for (const [key, value] of Object.entries(tax_dict)) {
        try {
            if (document.getElementById(key).value != value) {
                return true
            }
        } catch { continue }
    }
    return false
}