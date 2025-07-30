import BEM from 'bem.js';
import {MODIFIER_HAS_VALUE, SELECTS} from './constants';

/**
 * Detects whether a select has a value.
 * @class
 */
export class Select {
    /**
     * Constructor method.
     * @param {HTMLSelectElement} node
     */
    constructor(node) {
        /** @type {HTMLSelectElement} */
        this.node = node;

        this.bindEvents();
        this.update();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.node.addEventListener('change', this.update.bind(this));
    }

    /**
     * Toggles MODIFIER_HAS_VALUE based on this.node.value.
     */
    update() {
        const exp = Boolean('' + this.node.value);
        BEM.toggleModifier(this.node, MODIFIER_HAS_VALUE, exp);
    }
}


// Start!
[...SELECTS].forEach(node => new Select(node));
