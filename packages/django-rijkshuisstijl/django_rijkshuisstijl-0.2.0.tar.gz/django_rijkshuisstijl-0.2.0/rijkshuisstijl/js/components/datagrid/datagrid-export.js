import BEM from 'bem.js';
import {
    BLOCK_DATAGRID,
    DATAGRID_EXPORTS,
    ELEMENT_CELL,
    ELEMENT_FORM,
    MODIFIER_ACTION,
    MODIFIER_CHECKBOX
} from './constants';
import {BLOCK_INPUT} from '../form/constants';
import {BLOCK_SELECT_ALL} from '../toggle/constants';

const MAX_ITERATION_COUNT = 100;

/**
 * Makes sure data grid export buttons default to current page selection.
 */
class DataGridExportHelper {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     */
    constructor(node) {
        /** @type {HTMLElement} */
        this.node = node;

        this.bindEvents();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.node.addEventListener('click', this.update.bind(this));
    }

    getDataGrid() {
        let node = this.node;
        let i = 0;
        while (!node.classList.contains(BLOCK_DATAGRID)) {
            i++;
            node = node.parentNode;

            if (i > MAX_ITERATION_COUNT) {
                throw `MAX_ITERATION_COUNT (${MAX_ITERATION_COUNT}) reached while trying to find data grid element.`;
            }
        }

        return node;
    }

    /**
     * Checks all checkboxes in the data grid if none has been checked.
     * @param {MouseEvent} e
     */
    update(e) {
        const dataGrid = this.getDataGrid();
        const checkboxCells = BEM.getChildBEMNodes(dataGrid, BLOCK_DATAGRID, ELEMENT_CELL, MODIFIER_CHECKBOX);
        const checkboxesInputs = [...checkboxCells].map(node => BEM.getChildBEMNode(node, BLOCK_INPUT));
        const selectedCheckboxInputs = checkboxesInputs.find(node => node.checked);

        // Only check checkboxes if none hase been already checked.
        if (!selectedCheckboxInputs) {
            e.preventDefault();
            const form = BEM.getChildBEMNode(dataGrid, BLOCK_DATAGRID, ELEMENT_FORM, MODIFIER_ACTION);
            const selectAll = BEM.getChildBEMNode(dataGrid, BLOCK_SELECT_ALL);

            // Select all checkboxes, including the "select all" toggle.
            selectAll.checked = true;
            checkboxesInputs.forEach(node => {
                node.checked = true;
            });

            const hiddenInput = document.createElement('input');
            hiddenInput.name = this.node.name;
            hiddenInput.value = this.node.value;
            hiddenInput.type = 'hidden';
            form.appendChild(hiddenInput);
            form.submit();
        }
    }
}


// Start!
[...DATAGRID_EXPORTS].forEach(node => new DataGridExportHelper(node));
