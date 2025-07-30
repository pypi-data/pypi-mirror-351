import BEM from 'bem.js';
import {FAKE_LINKS, MODIFIER_DOUBLE_CLICK} from './constants';


/**
 * Class for fake (simulated) links.
 *
 * Toggle should have BLOCK_FAKE_LINK present in classList for detection.
 * Toggle should have data-href set to target location.
 * @class
 */
export class FakeLink {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     */
    constructor(node) {
        /** @type {HTMLElement} */
        this.node = node;

        /** @type {string} */
        this.href = this.node.dataset.href;

        this.bindEvents();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        if (BEM.hasModifier(this.node, MODIFIER_DOUBLE_CLICK)) {
            this.node.addEventListener('dblclick', this.navigate.bind(this));
        } else {
            this.node.addEventListener('click', this.navigate.bind(this));
        }
    }

    /**
     * Navigates to this.href.
     */
    navigate() {
        window.location = this.href;
    }
}

// Start!
[...FAKE_LINKS].forEach(node => new FakeLink(node));
