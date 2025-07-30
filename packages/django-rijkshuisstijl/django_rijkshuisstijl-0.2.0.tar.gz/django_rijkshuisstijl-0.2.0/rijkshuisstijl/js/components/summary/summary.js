import BEM from 'bem.js';
import {SUMMARIES, BLOCK_SUMMARY, ELEMENT_KEY_VALUE, MODIFIER_EDIT} from './constants';


/** @const {number} getKeyValue() while loop limit. */
const MAX_ITERATION_COUNT = 10;


/**
 * Controls auto toggle inputs if not valid.
 * @class
 */
class SummaryEdit {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     */
    constructor(node) {
        /** @type {HTMLElement} */
        this.node = node;

        /** @type {NodeList} Children of node that can be validated. */
        this.validatables = this.node.querySelectorAll(':invalid, :valid');

        this.bindEvents();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        [...this.validatables].forEach(node => node.addEventListener('invalid', this.update.bind(this, node)));
    }

    /**
     * Finds the key value element associated with node.
     * @param {HTMLElement} node
     * @return {HTMLElement}
     */
    getKeyValue(node) {
        let i = 0;
        const className = BEM.getBEMClassName(BLOCK_SUMMARY, ELEMENT_KEY_VALUE);
        while (!node.classList.contains(className)) {
            i++;
            node = node.parentNode;

            if (i > MAX_ITERATION_COUNT) {
                throw `MAX_ITERATION_COUNT (${MAX_ITERATION_COUNT}) reached while trying to find key value element.`;
            }
        }

        return node;
    }

    /**
     * Makes sure node is visible if not valid.
     * @param {HTMLElement} node
     */
    update(node) {
        const toggle = this.getKeyValue(node);
        BEM.addModifier(toggle, MODIFIER_EDIT);
        node.focus();
        node.scrollIntoView();
    }

}

// Start!
[...SUMMARIES].forEach(node => new SummaryEdit(node));
