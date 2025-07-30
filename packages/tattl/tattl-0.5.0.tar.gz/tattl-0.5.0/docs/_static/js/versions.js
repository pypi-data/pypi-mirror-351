/*
    Slightly tweaked code from https://github.com/pradyunsg/furo/pull/500 vendored here until it
    gets merged. This adds a functioning version selector to the sidebar.
*/

function setupVersionDropdown() {
    const checkboxInput = document.getElementById("checkbox_toggle");

    if (localStorage.getItem("version-dropdown-opened") === "true") {
        checkboxInput.checked = true;
    }

    const checkbox = document.getElementById("versions-label");
    checkbox.addEventListener("click", toggleDropdown);

    function toggleDropdown() {
        if (localStorage.getItem("version-dropdown-opened") === "true") {
            localStorage.setItem("version-dropdown-opened", "false");
        } else {
            localStorage.setItem("version-dropdown-opened", "true");
        }
    }
}

document.addEventListener("DOMContentLoaded", setupVersionDropdown);
