import {assert} from 'chai';
import BEM from 'bem.js';
import jsdom from 'jsdom-global';
import simulant from 'simulant';
import sinon from 'sinon';
import {ViewNavigation} from '../../../js/components/view/view';
import {Utils} from '../../utils';
import {
    BLOCK_NAVIGATION_BAR,
    BLOCK_VIEW,
    ELEMENT_INPUT,
    MODIFIER_MENU_OPEN,
    MODIFIER_OPEN
} from '../../../js/components/view/constants';
import {BLOCK_BUTTON} from '../../../js/components/button/constants';
import {BLOCK_TOGGLE} from '../../../js/components/toggle/constants';

describe('view/view.js - ViewNavigation ', function () {
    before(() => {
        jsdom();
        this.node = document.createElement('html');
        this.body = document.createElement('body');
        this.node.appendChild(this.body);
        this.node.className = BEM.getBEMClassName(BLOCK_VIEW);
        this.ViewNavigation = Utils.createTestableClass(ViewNavigation);
    });

    afterEach(() => {
        sinon.restore();
    });

    it('should construct', () => {
        let viewNavigation = new this.ViewNavigation();
        sinon.replace(viewNavigation, 'bindEvents', sinon.fake());
        viewNavigation.constructor(this.node);
        assert(ViewNavigation);
        assert.equal(viewNavigation.node, this.node);
        assert.equal(viewNavigation.body, this.body);
    });

    it('should call bindEvents() when constructor is called', () => {
        let view = new this.ViewNavigation();
        sinon.replace(view, 'bindEvents', sinon.fake());
        view.constructor(this.node);
        assert.equal(view.bindEvents.callCount, 1);
    });

    it('should call update() when body receives click event', () => {
        let viewNavigation = new this.ViewNavigation();
        sinon.replace(viewNavigation, 'update', sinon.fake());
        viewNavigation.constructor(this.node);
        simulant.fire(viewNavigation.body, 'click');
        assert.equal(viewNavigation.update.callCount, 1);
    });

    it('should call update() when body receives touchend event', () => {
        let viewNavigation = new this.ViewNavigation();
        sinon.replace(viewNavigation, 'update', sinon.fake());
        viewNavigation.constructor(this.node);
        simulant.fire(viewNavigation.body, 'touchend');
        assert.equal(viewNavigation.update.callCount, 1);
    });

    it('should update', () => {
        let button = document.createElement('button');
        button.className = BLOCK_BUTTON;
        button.dataset.toggleModifier = MODIFIER_MENU_OPEN;
        this.body.appendChild(button);

        let icon = document.createElement('span');
        icon.className = 'icon';
        button.appendChild(icon);

        let input = document.createElement('input');
        this.body.appendChild(input);

        let label = document.createElement('label');
        this.body.appendChild(input);

        let facet = document.createElement('span');
        facet.className = 'facet';
        this.body.appendChild(facet);

        let toggle = document.createElement('a');
        toggle.className = BLOCK_TOGGLE;
        this.body.appendChild(toggle);

        let viewNavigation = new this.ViewNavigation();
        sinon.replace(viewNavigation, 'close', sinon.fake());
        viewNavigation.constructor(this.node);

        [button, icon, input, label, facet, toggle].forEach(node => {
            simulant.fire(node, 'click');
            simulant.fire(node, 'touchend');
        });
        assert.equal(viewNavigation.close.callCount, 0);

        let navigationBar = document.createElement('div');
        navigationBar.className = BLOCK_NAVIGATION_BAR;
        this.body.appendChild(navigationBar);

        simulant.fire(navigationBar, 'click');
        simulant.fire(navigationBar, 'touchend');
        assert.equal(viewNavigation.close.callCount, 2);

        let link = document.createElement('a');
        link.href = '#';
        this.body.appendChild(link);

        simulant.fire(link, 'click');
        simulant.fire(link, 'touchend');
        assert.equal(viewNavigation.close.callCount, 4);
    });

    it('should do nothing if MODIFIER_MENU_OPEN is set on node and close() is called', () => {
        BEM.removeModifier(this.node, MODIFIER_MENU_OPEN);
        sinon.spy(document.activeElement, 'blur');
        let viewNavigation = new this.ViewNavigation();
        viewNavigation.constructor(this.node);
        viewNavigation.close();
        assert.notOk(BEM.hasModifier(this.node, MODIFIER_MENU_OPEN));
        assert.equal(document.activeElement.blur.callCount, 0);
    });

    it('should remove MODIFIER_MENU_OPEN if close() is called', () => {
        BEM.addModifier(this.node, MODIFIER_MENU_OPEN);
        let viewNavigation = new this.ViewNavigation();
        viewNavigation.constructor(this.node);
        viewNavigation.close();
        assert.notOk(BEM.hasModifier(this.node, MODIFIER_MENU_OPEN));
    });

    it('should call blur on active element if close() is called', () => {
        BEM.addModifier(this.node, MODIFIER_MENU_OPEN);
        sinon.spy(document.activeElement, 'blur');
        let viewNavigation = new this.ViewNavigation();
        viewNavigation.constructor(this.node);
        viewNavigation.close();
        assert.equal(document.activeElement.blur.callCount, 1);
    });
});
