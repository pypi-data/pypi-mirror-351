import {LINK_SELECTS} from './constants';

/**
 * Navigates to selected value of select on change.
 * @class
 */
export class LinkSelect {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     */
    constructor(node) {
        /** {HTMLElement} */
        this.node = node;
        this.bindEvents();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.node.addEventListener('change', this.navigate.bind(this));
    }

    /**
     * Navigates to the selected link, opens new window if this.node.dataset.target equals "_blank".
     */
    navigate() {
        const target = this.node.dataset.target;
        const href = this.node.value || this.node.dataset.value;

        if (target === '_blank') {
            window.open(href);
            return;
        }
        location.href = href;
    }
}


// Start!
[...LINK_SELECTS].forEach(node => new LinkSelect(node));
