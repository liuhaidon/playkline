// checkbox选中的值,类型为list
function checkboxvalue(name) {
    var j = {};
    var obj = document.getElementsByName(name);
    var check_val = [];
    for (var k in obj) {
        if (obj[k].checked)
            check_val.push(obj[k].value);
    }
    return check_val;
}