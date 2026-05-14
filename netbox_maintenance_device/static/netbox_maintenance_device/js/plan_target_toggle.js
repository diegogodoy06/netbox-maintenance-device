// Disables the "other" target field when one of (Device, Virtual Machine) is selected,
// so users can't accidentally fill both. The server still enforces the XOR rule.

(function () {
    'use strict';

    function getCurrentValue(field) {
        // DynamicModelChoiceField hides the underlying <select>; its `.value` is the
        // canonical source of truth even when the UI widget is a custom combobox.
        return field && field.value ? field.value.toString().trim() : '';
    }

    function findRow(field) {
        // The form layout wraps each field in a row/group — disabling the row also
        // dims the label and the API-search input that DynamicModelChoiceField renders.
        return field.closest('.row, .field-group, .mb-3, fieldset, .form-group') || field.parentElement;
    }

    function setDisabled(field, disabled) {
        if (!field) return;

        field.disabled = disabled;

        var row = findRow(field);
        if (row) {
            row.classList.toggle('opacity-50', disabled);
            // Disable any nested inputs (e.g. the API-driven combobox uses a sibling
            // text input). `:scope` keeps this scoped to the current row.
            row.querySelectorAll(':scope input, :scope select, :scope button').forEach(function (el) {
                if (el !== field) {
                    el.disabled = disabled;
                }
            });
        }
    }

    function syncFields(deviceField, vmField) {
        var deviceVal = getCurrentValue(deviceField);
        var vmVal = getCurrentValue(vmField);

        if (deviceVal && !vmVal) {
            setDisabled(vmField, true);
            setDisabled(deviceField, false);
        } else if (vmVal && !deviceVal) {
            setDisabled(deviceField, true);
            setDisabled(vmField, false);
        } else {
            setDisabled(deviceField, false);
            setDisabled(vmField, false);
        }
    }

    function init() {
        var deviceField = document.getElementById('id_device');
        var vmField = document.getElementById('id_virtual_machine');

        if (!deviceField || !vmField) {
            return;
        }

        // Re-sync on any change to either field. `change` covers manual edits and
        // DynamicModelChoiceField's programmatic value updates; `input` catches typed
        // changes that some widgets fire before `change`.
        ['change', 'input'].forEach(function (evt) {
            deviceField.addEventListener(evt, function () { syncFields(deviceField, vmField); });
            vmField.addEventListener(evt, function () { syncFields(deviceField, vmField); });
        });

        // Run once at page load — handles the edit flow where one field is already set.
        syncFields(deviceField, vmField);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
