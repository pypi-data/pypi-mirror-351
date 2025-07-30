import BEM from 'bem.js';
import {
    BLOCK_FILTER,
    ELEMENT_INPUT,
    FILTERS,
    MODIFIER_CLASS_ONLY,
    MODIFIER_MATCH,
    MODIFIER_NO_MATCH
} from './constants';


/**
 * Class for generic filters.
 * Filter should have MODIFIER_FILTER present in classList for detection.
 * Filter should have data-filter-target set to query selector for targets.
 * @class
 */
export class Filter {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     */
    constructor(node) {
        /** @type {HTMLElement} */
        this.node = node;

        /** @type {HTMLInputElement} */
        this.input = BEM.getChildBEMNode(this.node, BLOCK_FILTER, ELEMENT_INPUT);

        this.bindEvents();
        this.applyFilter();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.node.addEventListener('input', this.filter.bind(this));
    }

    /**
     * Applies/discard the filter based on this.input.value.
     */
    filter() {
        if (this.input.value) {
            this.applyFilter();
        } else {
            this.discardFilter();
        }
    }

    /**
     * Hides all the nodes matching query selector set in data-filter-target that don't match this.input.value.
     */
    applyFilter() {
        setTimeout(() => {
            let selection = document.querySelectorAll(this.node.dataset.filterTarget);
            let query = this.input.value.toUpperCase();

            [...selection].forEach(node => {
                BEM.addModifier(node, MODIFIER_MATCH);
                BEM.removeModifier(node, MODIFIER_NO_MATCH);

                if(!BEM.hasModifier(this.node, MODIFIER_CLASS_ONLY)) {
                    node.style.removeProperty('display');
                }

                if (!node.textContent.toUpperCase().match(query)) {
                    BEM.removeModifier(node, MODIFIER_MATCH);
                    BEM.addModifier(node, MODIFIER_NO_MATCH);

                    if(!BEM.hasModifier(this.node, MODIFIER_CLASS_ONLY)) {
                        node.style.display = 'none';
                    }
                }
            });
        });
    }

    /**
     * Removes display property from inline style of every node matching query selector set in data-filter-target.
     */
    discardFilter() {
        let selection = document.querySelectorAll(this.node.dataset.filterTarget);
        [...selection].forEach(node => {
            if(!BEM.hasModifier(this.node, MODIFIER_CLASS_ONLY)) {
                node.style.removeProperty('display');
            }
            BEM.removeModifier(node, MODIFIER_NO_MATCH);
            BEM.addModifier(node, MODIFIER_MATCH);
        });
    }
}


// Start!
[...FILTERS].forEach(filter => new Filter(filter));
