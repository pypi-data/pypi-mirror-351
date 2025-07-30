import BEM from 'bem.js';
import {
    BLOCK_TABS,
    ELEMENT_LINK,
    ELEMENT_LIST_ITEM,
    ELEMENT_TAB,
    ELEMENT_TRACK,
    MODIFIER_ACTIVE,
    TABS
} from './constants';

/**
 * Contains logic for tabs.
 * @class
 */
class Tabs {
    /**
     * Constructor method.
     * @param {HTMLElement} node
     */
    constructor(node) {
        /** @type {HTMLElement} */
        this.node = node;

        /** @type {NodeList} */
        this.listItems = BEM.getChildBEMNodes(this.node, BLOCK_TABS, ELEMENT_LIST_ITEM);

        /** @type {NodeList} */
        this.links = BEM.getChildBEMNodes(this.node, BLOCK_TABS, ELEMENT_LINK);

        /** @type {NodeList} */
        this.track = BEM.getChildBEMNode(this.node, BLOCK_TABS, ELEMENT_TRACK);

        /** @type {NodeList} */
        this.tabs = BEM.getChildBEMNodes(this.node, BLOCK_TABS, ELEMENT_TAB);

        this.bindEvents();
        if (!this.activateHashLinkTab()) {
            this.activateCurrentTab();
        }

    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        [...this.links].forEach(link => this.bindLink(link));
        window.addEventListener('popstate', this.activateHashLinkTab.bind(this));
        window.addEventListener('resize', this.activateCurrentTab.bind(this));
    }

    /**
     * Binds link click to callback.
     * @param {HTMLAnchorElement} link
     */
    bindLink(link) {
        link.addEventListener('click', this.onClick.bind(this));
    }

    /**
     * (Re)activates the active tab, or the first tab.
     */
    activateCurrentTab() {
        let id = this.getActiveTabId();
        if (id) {
            this.activateTab(id);
        }
    }

    /**
     * (Re)activates the active tab, or the first tab.
     */
    activateHashLinkTab() {
        const id = window.location.hash.replace('#', '');

        const node = document.getElementById(id);
        if (node && node.classList.contains(BEM.getBEMClassName(BLOCK_TABS, ELEMENT_TAB))) {
            const listener = () => {
                window.scrollTo(0, 0);
                window.removeEventListener('scroll', listener);
            };
            window.addEventListener('scroll', listener);
            this.activateTab(id);

            return true;
        }
    }

    /**
     * Returns the active tab id (this.node.dataset.tabId) or the first tab's id.
     * @returns {(string|void)}
     */
    getActiveTabId() {
        let tabId = this.node.dataset.tabId;

        if (tabId) {
            return tabId;
        } else {
            try {
                return this.tabs[0].id;
            } catch (e) {
            }
        }

    }

    /**
     * Handles link click event.
     * @param {MouseEvent} e
     */
    onClick(e) {
        e.preventDefault();
        let link = e.target;
        let id = link.attributes.href.value.replace('#', '');
        history.pushState({}, document.title, link);
        this.activateTab(id);
    }

    /**
     * Activates tab with id.
     * @param {string} id The id of the tab.
     * @return {HTMLElement}
     */
    activateTab(id) {
        let link = [...this.links].find(link => link.attributes.href.value === '#' + id);
        let listItem = this.getListItemByLink(link);
        let tabIndex = [...this.tabs].findIndex(tab => tab.id === id);
        let tab = this.tabs[tabIndex];

        [...this.listItems, ...this.tabs].forEach(node => BEM.removeModifier(node, MODIFIER_ACTIVE));
        [listItem, tab].forEach(node => BEM.addModifier(node, MODIFIER_ACTIVE));
        this.node.dataset.tabId = id;

        // Support leaflet.
        //
        // Leaflet won't render correctly if not visible. Therefore, we need to invalidate it's size to re-render it.
        // We don't have a direct reference to the leaflet instances so we try to find the callbacks in
        // window._leaflet_events, then call it when activating the tab (if the even name matches resize).
        //
        // FIXME: There is probably a better way to do this.
        try {
            Object.entries(window._leaflet_events).forEach(([event_name, callback]) => {
               if (event_name.indexOf('resize') > -1) {
                    callback();
               }
            });
        } catch (e) {}
    }

    /**
     * Finds the list item containing link up the DOM tree.
     * @param {HTMLAnchorElement} link
     */
    getListItemByLink(link) {
        let listItemClassName = BEM.getBEMClassName(BLOCK_TABS, ELEMENT_LIST_ITEM);
        let i = 0;

        while (!link.classList.contains(listItemClassName)) {
            link = link.parentElement;

            if (i > 100) {
                console.error('Failed to find list item');
                break;
            }
        }
        return link;
    }
}


// Start!
[...TABS].forEach(tabs => new Tabs(tabs));

