import BEM from 'bem.js';
import {DATAGRID_FILTERS} from './constants';
import {BLOCK_INPUT, BLOCK_SELECT} from '../form/constants';

/**
 * Polyfills form association from datagrid filter.
 */
class DataGridFilter {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     */
    constructor(node) {
        /** @type {HTMLElement} */
        this.node = node;

        /** @type {(HTMLFormElement|null)} */
        this.form = this.getForm();

        /** @type {(HTMLInputElement|HTMLSelectElement|null)} */
        this.input = this.getInput();

        this.bindEvents();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        if (this.input) {
            this.input.addEventListener('change', this.onSubmit.bind(this));
        }
    }

    /**
     * Finds the form associated with the filter.
     * @return {(HTMLFormElement|null)}
     */
    getForm() {
        const input = this.getInput();
        if (input) {
            if (!input.form) {
                const formId = input.getAttribute('form');
                return document.getElementById(formId);
            }
            return input.form;
        }
    }

    /**
     * Finds the first input or select as child of this.node.
     * @return {(HTMLInputElement|HTMLSelectElement|null)}
     */
    getInput() {
        const input = BEM.getChildBEMNode(this.node, BLOCK_INPUT);
        const select = BEM.getChildBEMNode(this.node, BLOCK_SELECT);
        return input || select;
    }

    /**
     * Appends clone of inputs pointing to this.form before submitting it when browser does not support input form
     * attribute.
     */
    onSubmit() {
        const formId = this.form.id;
        const inputs = document.querySelectorAll(`[form="${formId}"]`);

        [...inputs].forEach(node => {
            const newNode = document.createElement('input');

            if (node.form) {  // Browser supports input form attribute.
                return;
            }

            newNode.name = node.name;
            newNode.type = 'hidden';
            newNode.value = node.value;

            this.form.appendChild(newNode);
        });

        this.form.submit();
    }
}


// Start!
[...DATAGRID_FILTERS].forEach(node => new DataGridFilter(node));



