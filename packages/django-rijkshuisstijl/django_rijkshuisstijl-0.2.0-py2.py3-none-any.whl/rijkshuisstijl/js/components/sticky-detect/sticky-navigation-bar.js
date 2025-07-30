import BEM from 'bem.js';

import {MODIFIER_STUCK, STICKY_DETECTS} from './constants';
import * as debounce from 'debounce';


/**
 * Keeps track of sticky state.
 * @class
 */
class StickyDetect {
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
        window.addEventListener('scroll', debounce(this.update.bind(this)));
    }

    update() {
        const threshold = this.node.style.top || 0;
        const exp = this.node.getClientRects()[0].top <= threshold;
        const state = BEM.hasModifier(this.node, MODIFIER_STUCK);
        BEM.toggleModifier(this.node, MODIFIER_STUCK, exp);

        if(!state && exp) {
            window.scrollBy(0, 10);
        }
    }
}

// Start!
[...STICKY_DETECTS].forEach(node => new StickyDetect(node));
