import {assert} from 'chai';
import BEM from 'bem.js';
import jsdom from 'jsdom-global';
import simulant from 'simulant';
import sinon from 'sinon';
import {Search} from '../../../js/components/search/search';
import {Utils} from '../../utils';
import {BLOCK_SEARCH, ELEMENT_INPUT, MODIFIER_OPEN} from '../../../js/components/search/constants';
import {BLOCK_BUTTON, MODIFIER_PRIMARY, MODIFIER_SECONDARY} from '../../../js/components/button/constants';

describe('search/search.js - Search ', function () {
    before(() => {
        jsdom();
        this.node = document.createElement('div');
        this.node.className = BEM.getBEMClassName(BLOCK_SEARCH);
        this.input = document.createElement('input');
        this.input.className = BEM.getBEMClassName(BLOCK_SEARCH, ELEMENT_INPUT);
        this.node.appendChild(this.input);
        this.buttonPrimary = document.createElement('button');
        this.buttonPrimary.className = BEM.getBEMClassName(BLOCK_BUTTON, false, MODIFIER_PRIMARY);
        this.node.appendChild(this.buttonPrimary);
        this.buttonSecondary = document.createElement('button');
        this.buttonSecondary.className = BEM.getBEMClassName(BLOCK_BUTTON, false, MODIFIER_SECONDARY);
        this.node.appendChild(this.buttonSecondary);
        this.Search = Utils.createTestableClass(Search);
    });

    afterEach(() => {
        sinon.restore();
    });

    it('should construct', () => {
        let search = new this.Search();
        sinon.replace(search, 'bindEvents', sinon.fake());
        search.constructor(this.node);
        assert(Search);
        assert.equal(search.node, this.node);
        assert.equal(search.input, this.input);
        assert.equal(search.buttonPrimary, this.buttonPrimary);
        assert.equal(search.buttonSecondary, this.buttonSecondary);
    });

    it('should call bindEvents() when constructor is called', () => {
        let search = new this.Search();
        sinon.replace(search, 'bindEvents', sinon.fake());
        search.constructor(this.node);
        assert.equal(search.bindEvents.callCount, 1);
    });

    it('should call onClickButtonPrimary() when this.buttonPrimary receives click event', () => {
        let search = new this.Search();
        sinon.replace(search, 'onClickButtonPrimary', sinon.fake());
        search.constructor(this.node);
        simulant.fire(search.buttonPrimary, 'click');
        assert.equal(search.onClickButtonPrimary.callCount, 1);
    });

    it('should call onClickButtonSecondary() when this.buttonSecondary receives click event', () => {
        let search = new this.Search();
        sinon.replace(search, 'onClickButtonSecondary', sinon.fake());
        search.constructor(this.node);
        simulant.fire(search.buttonSecondary, 'click');
        assert.equal(search.onClickButtonSecondary.callCount, 1);
    });

    it('should call onBlur() when this.input receives blur event', () => {
        let search = new this.Search();
        sinon.replace(search, 'onBlur', sinon.fake());
        search.constructor(this.node);
        simulant.fire(search.input, 'blur');
        assert.equal(search.onBlur.callCount, 1);
    });

    it('should call onPressEnter() when this.input receives keypress event', () => {
        let search = new this.Search();
        sinon.replace(search, 'onPressEnter', sinon.fake());
        search.constructor(this.node);
        simulant.fire(search.input, 'keypress');
        assert.equal(search.onPressEnter.callCount, 1);
    });

    it('should prevent the default event actions when onPressEnter() is called with keycode 13', () => {
        let search = new this.Search();
        search.input = this.input;
        search.input.value = '';
        let eventMock = { target: search.input, keyCode: 13, preventDefault: sinon.fake() };
        search.onPressEnter(eventMock);
        assert.equal(eventMock.preventDefault.callCount, 1);
    });

    it('should call this.input.focus() when onClickButtonPrimary() is called and MODIFIER_OPEN is set set on this.node', () => {
        let search = new this.Search();
        search.node = this.node;
        search.input = this.input;
        search.input.value = '';
        sinon.spy(search.input, 'focus');
        BEM.addModifier(search.node, MODIFIER_OPEN);
        search.onClickButtonPrimary();
        assert.equal(search.input.focus.callCount, 1);
    });

    it('should call this.input.blur() when onClickButtonPrimary() is called and MODIFIER_OPEN is not set set on this.node', () => {
        let search = new this.Search();
        search.node = this.node;
        search.input = this.input;
        search.input.value = '';
        sinon.spy(search.input, 'blur');
        BEM.removeModifier(search.node, MODIFIER_OPEN);
        search.onClickButtonPrimary();
        assert.equal(search.input.blur.callCount, 1);
    });

    it('should call this.input.focus() when onClickButtonSecondary() is called', () => {
        let search = new this.Search();
        search.node = this.node;
        search.input = this.input;
        search.input.value = '';
        sinon.spy(search.input, 'focus');
        search.onClickButtonSecondary({preventDefault: () => {}});
        assert.equal(search.input.focus.callCount, 1);
    });

    it('should call this.close() when onBlur() is called, this.input has no value set and event does not have relatedTarget set', () => {
        let search = new this.Search();
        search.node = this.node;
        search.input = this.input;
        search.input.value = '';
        sinon.spy(search, 'close');
        search.onBlur({ relatedTarget: false });
        assert.equal(search.close.callCount, 1);
    });

    it('should not call this.close() when onBlur() is called, this.input has a value set and event does not have relatedTarget set', () => {
        let search = new this.Search();
        search.node = this.node;
        search.input = this.input;
        search.input.value = 'foo';
        sinon.spy(search, 'close');
        search.onBlur({ relatedTarget: false });
        assert.equal(search.close.callCount, 0);
    });

    it('should not call this.close() when onBlur() is called, this.input has no value set and event does have relatedTarget set', () => {
        let search = new this.Search();
        search.node = this.node;
        search.input = this.input;
        search.input.value = '';
        sinon.spy(search, 'close');
        search.onBlur({ relatedTarget: true });
        assert.equal(search.close.callCount, 0);
    });

    it('should not call this.close() when onBlur() is called, this.input has a value set and event does have relatedTarget set', () => {
        let search = new this.Search();
        search.node = this.node;
        search.input = this.input;
        search.input.value = 'foo';
        sinon.spy(search, 'close');
        search.onBlur({ relatedTarget: true });
        assert.equal(search.close.callCount, 0);
    });

    it('should remove MODIFIER_OPEN from this.node when close() is called', () => {
        let search = new this.Search();
        search.node = this.node;
        BEM.addModifier(search.node, MODIFIER_OPEN);
        search.close();
        assert.notOk(BEM.hasModifier(search.node, MODIFIER_OPEN));
    });
});
