import {SELECT_ALLS} from './constants';


/**
 * Class for generic select all checkboxes.
 * Toggle should have BLOCK_SELECT_ALL present in classList for detection.
 * Toggle should have data-select-all set to queryselector for target(s).
 * @class
 */
export class SelectAll {
    /**
     * Constructor method.
     * @param {HTMLInputElement} node
     */
    constructor(node) {
        /** @type {HTMLInputElement} */
        this.node = node;

        this.bindEvents();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.node.addEventListener('click', this.onClick.bind(this));
    }

    /**
     * Callback for this.node click.
     * @param {Event} e
     */
    onClick(e) {
        e.stopPropagation();
        e.preventDefault();
        setTimeout(this.toggle.bind(this));
    }

    /**
     * Performs toggle.
     * @param {boolean} [exp] If passed, add/removes this.toggleModifier based on exp.
     */
    toggle(exp = !this.getState()) {
        this.getTargets()
            .forEach(target => {
                let event = document.createEvent('Event');
                event.initEvent('change', true, true);
                setTimeout(() => target.dispatchEvent(event));
                target.checked = exp;
            });
        this.node.checked = exp;
    }

    /**
     * Returns the checkbox state.
     * @returns {boolean} Boolean
     */
    getState() {
        return this.node.checked;
    }

    /**
     * Returns all the targets for this.node.
     * @returns {*}
     */
    getTargets() {
        let targets = [];
        let selector = this.node.dataset.selectAll;
        selector.split(',')
            .filter(selector => selector.length)
            .forEach(selector => targets = [...targets, ...document.querySelectorAll(selector)]);
        return targets;
    }
}

// Start!
[...SELECT_ALLS].forEach(node => new SelectAll(node));
