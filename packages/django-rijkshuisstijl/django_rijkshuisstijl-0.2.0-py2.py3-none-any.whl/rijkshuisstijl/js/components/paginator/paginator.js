import BEM from 'bem.js';
import URI from 'urijs';
import {BLOCK_INPUT, PAGINATORS} from './constants';


/**
 * Contains logic for making the paginator work with existing GET params.
 * @class
 */
export class Paginator {
    /**
     * Constructor method.
     * @param {HTMLFormElement} node
     */
    constructor(node) {
        /** @type {HTMLFormElement} */
        this.node = node;

        /** @type {HTMLInputElement} */
        this.input = BEM.getChildBEMNode(this.node, BLOCK_INPUT);

        this.bindEvents();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.node.addEventListener('submit', this.onChange.bind(this));
        this.node.addEventListener('change', this.onChange.bind(this));
        this.node.addEventListener('click', this.onClick.bind(this));
    }

    /**
     * Callback for change event on this.node.
     * @param {Event} e
     */
    onChange(e) {
        e.preventDefault();
        this.navigate();
    }

    /**
     * Callback for click event on this.node.
     * @param {Event} e
     */
    onClick(e) {
        e.preventDefault();
        if (e.target.dataset.page) {
            this.navigate(e.target.dataset.page);
        }
    }

    /**
     * Navigate to the page specified in this.input.
     */
    navigate(page = this.input.value) {
        window.location = URI(window.location).setSearch(this.input.name, page);
    }
}


// Start!
[...PAGINATORS].forEach(node => new Paginator(node));
