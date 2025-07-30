import BEM from 'bem.js';
import {BLOCK_BUTTON, MODIFIER_PRIMARY, MODIFIER_SECONDARY} from '../button/constants';
import {SEARCHES, BLOCK_SEARCH, ELEMENT_INPUT, MODIFIER_OPEN} from './constants';


/**
 * Contains additional logic controlling search widget.
 * NOTE: Open/close behaviour controlled by button (ToggleButton).
 * @class
 */
export class Search {
    /**
     * Constructor method.
     * @param {HTMLFormElement} node
     */
    constructor(node) {
        /** @type {HTMLFormElement} */
        this.node = node;

        /** @type {HTMLInputElement} */
        this.input = BEM.getChildBEMNode(this.node, BLOCK_SEARCH, ELEMENT_INPUT);

        /** @type {HTMLButtonElement} */
        this.buttonPrimary = BEM.getChildBEMNode(this.node, BLOCK_BUTTON, false, MODIFIER_PRIMARY);

        /** @type {HTMLButtonElement} */
        this.buttonSecondary = BEM.getChildBEMNode(this.node, BLOCK_BUTTON, false, MODIFIER_SECONDARY);

        this.bindEvents();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.buttonPrimary.addEventListener('click', this.onClickButtonPrimary.bind(this));
        this.buttonSecondary.addEventListener('click', this.onClickButtonSecondary.bind(this));
        this.input.addEventListener('blur', this.onBlur.bind(this));
        this.input.addEventListener('keypress', this.onPressEnter.bind(this));
    }

    /**
     * Callback for keypress event on focused input.
     * Submits for if the user pressed enter and there is an input value.
     */
    onPressEnter(e) {
        const keyCode = e.keyCode;
        if (keyCode === 13) {
            e.preventDefault();
            if (this.input.value) {
                this.input.form.submit();
            }
        }
    }

    /**
     * Callback for click event on this.buttonPrimary.
     * Submits form if input has value.
     * Focuses this.input if MODIFIER_OPEN is set on this.node.
     * Blurs this.input otherwise.
     */
    onClickButtonPrimary() {
        if (BEM.hasModifier(this.node, MODIFIER_OPEN)) {
            if (this.input.value) {
                this.input.form.submit();
            }
            this.input.focus();
        } else {
            this.input.blur();
        }
    }

    /**
     * Callback for click event on this.buttonSecondary.
     * Clears/focuses this.input.
     * @param {Event} e
     */
    onClickButtonSecondary(e) {
        e.preventDefault();
        this.input.value = '';
        this.input.focus();
    }

    /**
     * Callback for blur event on this.input.
     * Calls this.close() if input does not have value.
     * @param {Event} e
     */
    onBlur(e) {
        if (!this.input.value && !e.relatedTarget) {
            this.close();
        }
    }

    /**
     * Additional control for removing MODIFIER_OPEN for this.node.
     * NOTE: Open/close behaviour controlled by button (ToggleButton).
     */
    close() {
        BEM.removeModifier(this.node, MODIFIER_OPEN);
    }
}


// Start!
[...SEARCHES].forEach(search => new Search(search));
