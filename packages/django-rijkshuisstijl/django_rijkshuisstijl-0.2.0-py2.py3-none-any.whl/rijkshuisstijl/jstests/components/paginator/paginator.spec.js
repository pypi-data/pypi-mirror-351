import {assert} from 'chai';
import BEM from 'bem.js';
import jsdom from 'jsdom-global';
import simulant from 'simulant';
import sinon from 'sinon';
import {Paginator} from '../../../js/components/paginator/paginator';
import {
    BLOCK_INPUT,
    BLOCK_PAGINATOR,
    ELEMENT_INPUT,
    MODIFIER_MATCH,
    MODIFIER_NO_MATCH
} from '../../../js/components/paginator/constants';
import {Utils} from '../../utils';

describe('paginator/paginator.js - Paginator ', function () {
    before(() => {
        jsdom();
        this.node = document.createElement('div');
        this.node.className = BEM.getBEMClassName(BLOCK_PAGINATOR);
        this.node.dataset.paginatorTarget = '.target';
        this.input = document.createElement('input');
        this.input.className = BEM.getBEMClassName(BLOCK_INPUT);
        this.node.appendChild(this.input);
        this.Paginator = Utils.createTestableClass(Paginator);
    });

    afterEach(() => {
        sinon.restore();
    });

    it('should construct', () => {
        let paginator = new this.Paginator();
        sinon.replace(paginator, 'bindEvents', sinon.fake());
        paginator.constructor(this.node);
        assert(Paginator);
        assert.equal(paginator.node, this.node);
        assert.equal(paginator.input, this.input);
    });

    it('should call bindEvents() when constructor is called', () => {
        let paginator = new this.Paginator();
        sinon.replace(paginator, 'bindEvents', sinon.fake());
        paginator.constructor(this.node);
        assert.equal(paginator.bindEvents.callCount, 1);
    });

    it('should call onChange() when node receives submit event', () => {
        let paginator = new this.Paginator();
        sinon.replace(paginator, 'onChange', sinon.fake());
        paginator.constructor(this.node);
        simulant.fire(paginator.node, 'submit');
        assert.equal(paginator.onChange.callCount, 1);
    });

    it('should call onChange() when node receives change event', () => {
        let paginator = new this.Paginator();
        sinon.replace(paginator, 'onChange', sinon.fake());
        paginator.constructor(this.node);
        simulant.fire(paginator.node, 'change');
        assert.equal(paginator.onChange.callCount, 1);
    });

    it('should call onClick() when node receives click event', () => {
        let paginator = new this.Paginator();
        sinon.replace(paginator, 'onClick', sinon.fake());
        paginator.constructor(this.node);
        simulant.fire(paginator.node, 'click');
        assert.equal(paginator.onClick.callCount, 1);
    });

    it('should prevent the default event actions when onChange() is called', () => {
        let paginator = new this.Paginator();
        sinon.replace(paginator, 'navigate', sinon.fake());
        let eventMock = { target: this.node, preventDefault: sinon.fake() };
        paginator.onChange(eventMock);
        assert.equal(eventMock.preventDefault.callCount, 1);
    });

    it('should prevent the default event actions when onClick() is called', () => {
        let paginator = new this.Paginator();
        sinon.replace(paginator, 'navigate', sinon.fake());
        let eventMock = { target: this.node, preventDefault: sinon.fake() };
        paginator.onClick(eventMock);
        assert.equal(eventMock.preventDefault.callCount, 1);
    });

    it('should call navigate() when onChange() is called', () => {
        let paginator = new this.Paginator();
        sinon.replace(paginator, 'navigate', sinon.fake());
        let eventMock = { target: this.node, preventDefault: sinon.fake() };
        paginator.onChange(eventMock);
        assert.equal(paginator.navigate.callCount, 1);
    });

    it('should call navigate() when onClick() is called and data-page is set on this.node', () => {
        let paginator = new this.Paginator();
        paginator.node = this.node;
        paginator.node.dataset.page = 2;
        sinon.replace(paginator, 'navigate', sinon.fake());
        let eventMock = { target: this.node, preventDefault: sinon.fake() };
        paginator.onClick(eventMock);
        assert.equal(paginator.navigate.callCount, 1);
    });

    it('should not call navigate() when onClick() is called and data-page is not set on this.node', () => {
        let paginator = new this.Paginator();
        paginator.node = this.node;
        delete paginator.node.dataset.page;
        sinon.replace(paginator, 'navigate', sinon.fake());
        let eventMock = { target: this.node, preventDefault: sinon.fake() };
        paginator.onClick(eventMock);
        assert.equal(paginator.navigate.callCount, 0);
    });
});
