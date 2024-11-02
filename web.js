function get_login_element(id_selector, password_selector) {
    let id_e = document.querySelector(id_selector);
    let password_e = document.querySelector(password_selector);
    let result = {
        'success': (id_e != null && password_e != null),
        'id': id_e,
        'password': password_e
    }
    return result;
}

window.get_login_element = get_login_element;

function fill_login_form(id, password) {
    let results = get_login_element("input#username", "input#password")

    if (results.success === true) {
        results.id.value = id
        results.password.value = password
    }
}

window.fill_login_form = fill_login_form;


function do_login() {
    let btn = document.querySelector("#login_submit")
    if (btn == null) {
        btn = document.querySelector("##login_submit")
    }
    btn.click()
}

window.do_login = do_login;

function setInput(input, text) {
    input.value = text
    const evt = new Event("input", {"bubbles": true, "cancelable": false});
    input.dispatchEvent(evt);
}

window.setInput = setInput;

// debug code start
// (function () {
//     let iframe = document.createElement('iframe')
//     document.body.appendChild(iframe)
//     window.console = iframe.contentWindow.console
// }())
// debug code end

function is_login() {
    let url = document.URL
    return !url.includes("login");
}

window.is_login = is_login;
