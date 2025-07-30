import BEM from 'bem.js';
import {BLOCK_DATAGRID, ELEMENT_ROW, MODIFIER_EDIT, DATAGRIDS} from './constants';

class DataGridEdit {
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
        this.node.addEventListener('rh-toggle', this.update.bind(this));
    }

    /**
     * Toggle MODIFIER_EDIT on this.node based on presense of datagrid__row--edit matches.
     */
    update() {
        const editable_row = BEM.getChildBEMNodes(this.node, BLOCK_DATAGRID, ELEMENT_ROW, MODIFIER_EDIT);
        const exp = Boolean(editable_row.length);
        BEM.toggleModifier(this.node, MODIFIER_EDIT, exp);
    }
}


// Start!
[...DATAGRIDS].forEach(node => new DataGridEdit(node));
