import BEM from 'bem.js';
import {MODIFIER_MENU_OPEN, NAVIGATION_BAR, VIEW} from './constants';


/**
 * Constains logic for dealing with the (mobile) navigation.
 */
export class ViewNavigation {
    /**
     * Constructor method.
     * @param {HTMLHtmlElement} node
     */
    constructor(node) {
        /** @type {HTMLHtmlElement} */
        this.node = node;

        /** @type {HTMLBodyElement} */
        this.body = node.querySelector('body');

        this.bindEvents();
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.body.addEventListener('click', this.update.bind(this));
        this.body.addEventListener('touchend', this.update.bind(this));
    }

    update(e) {
        let path = e.path || (e.composedPath && e.composedPath());
        let buttonClicked = e.target.dataset.toggleModifier && e.target.dataset.toggleModifier === MODIFIER_MENU_OPEN;
        let iconClicked = e.target.parentElement.dataset.toggleModifier && e.target.parentElement.dataset.toggleModifier === MODIFIER_MENU_OPEN;
        let inputClicked = e.target.tagName === 'INPUT';
        let labelClicked = e.target.tagName === 'LABEL';
        let facetClicked = e.target.className.includes('facet');
        let toggleClicked = e.target.className.includes('toggle') || e.target.parentElement.className.includes('toggle');

        if (buttonClicked || iconClicked || inputClicked || labelClicked || facetClicked || toggleClicked) {
            return;
        }

        if (!path || path.indexOf(NAVIGATION_BAR) === -1 || e.target.getAttribute('href')) {
            this.close();
        }
    }

    close() {
        if (!BEM.hasModifier(VIEW||this.node, MODIFIER_MENU_OPEN)) {
            return;
        }

        BEM.removeModifier(this.node, MODIFIER_MENU_OPEN);

        if (document.activeElement) {
            document.activeElement.blur();
        }
    }
}

// Start!
if (VIEW) {
    new ViewNavigation(VIEW);
}
