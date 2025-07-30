import {assert} from 'chai';
import BEM from 'bem.js';
import jsdom from 'jsdom-global';
import simulant from 'simulant';
import sinon from 'sinon';
import {FakeLink} from '../../../js/components/fake-link/fake-link';
import {BLOCK_FAKE_LINK, MODIFIER_DOUBLE_CLICK} from '../../../js/components/fake-link/constants';
import {Utils} from '../../utils';

describe('fake-link/fake-link.js - FakeLink ', function () {
    before(() => {
        jsdom();
        this.node = document.createElement('div');
        this.node.className = BEM.getBEMClassName(BLOCK_FAKE_LINK);
        this.node.dataset.href = '/foo/bar';
        this.InputFilepicker = Utils.createTestableClass(FakeLink);
    });

    afterEach(() => {
        sinon.restore();
    });

    it('should construct', () => {
        let fakeLink = new this.InputFilepicker();
        sinon.replace(fakeLink, 'bindEvents', sinon.fake());
        fakeLink.constructor(this.node);
        assert(FakeLink);
        assert.equal(fakeLink.node, this.node);
        assert.equal(fakeLink.href, '/foo/bar');
    });

    it('should call bindEvents() when constructor is called', () => {
        let fakeLink = new this.InputFilepicker();
        sinon.replace(fakeLink, 'bindEvents', sinon.fake());
        fakeLink.constructor(this.node);
        assert.equal(fakeLink.bindEvents.callCount, 1);
    });

    it('should call navigate() when this.node is double clicked if MODIFIER_DOUBLE_CLICK is present', () => {
        let fakeLink = new this.InputFilepicker();
        BEM.toggleModifier(this.node, MODIFIER_DOUBLE_CLICK, true);
        sinon.replace(fakeLink, 'navigate', sinon.fake());
        fakeLink.constructor(this.node);
        simulant.fire(fakeLink.node, 'click');
        assert.equal(fakeLink.navigate.callCount, 0);
        simulant.fire(fakeLink.node, 'dblclick');
        assert.equal(fakeLink.navigate.callCount, 1);
    });

    it('should call navigate() when this.node is clicked if MODIFIER_DOUBLE_CLICK is not present', () => {
        let fakeLink = new this.InputFilepicker();
        BEM.toggleModifier(this.node, MODIFIER_DOUBLE_CLICK, false);
        sinon.replace(fakeLink, 'navigate', sinon.fake());
        fakeLink.constructor(this.node);
        simulant.fire(fakeLink.node, 'dblclick');
        assert.equal(fakeLink.navigate.callCount, 0);
        simulant.fire(fakeLink.node, 'click');
        assert.equal(fakeLink.navigate.callCount, 1);
    });
});
