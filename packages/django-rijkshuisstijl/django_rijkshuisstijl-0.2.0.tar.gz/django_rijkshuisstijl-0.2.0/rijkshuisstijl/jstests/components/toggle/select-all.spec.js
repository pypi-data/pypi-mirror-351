import {assert} from 'chai';
import BEM from 'bem.js';
import jsdom from 'jsdom-global';
import simulant from 'simulant';
import sinon from 'sinon';
import {BLOCK_SELECT_ALL, ELEMENT_INPUT, MODIFIER_OPEN} from '../../../js/components/toggle/constants';
import {SelectAll} from '../../../js/components/toggle/select-all';
import {Utils} from '../../utils';

describe('toggle/select-all.js - SelectAll ', function () {
    before(() => {
        jsdom();
        this.node = document.createElement('input');
        this.node.className = BEM.getBEMClassName(BLOCK_SELECT_ALL);
        this.SelectAll = Utils.createTestableClass(SelectAll);
    });

    afterEach(() => {
        sinon.restore();
    });

    it('should construct', () => {
        let selectAll = new this.SelectAll();
        sinon.replace(selectAll, 'bindEvents', sinon.fake());
        selectAll.constructor(this.node);
        assert(SelectAll);
        assert.equal(selectAll.node, this.node);
    });

    it('should call bindEvents() when constructor is called', () => {
        let selectAll = new this.SelectAll();
        sinon.replace(selectAll, 'bindEvents', sinon.fake());
        selectAll.constructor(this.node);
        assert.equal(selectAll.bindEvents.callCount, 1);
    });

    it('should call onClick() when this.node receives click event', () => {
        let selectAll = new this.SelectAll();
        sinon.spy(selectAll, 'onClick');
        sinon.replace(selectAll, 'toggle', sinon.fake());
        selectAll.constructor(this.node);
        simulant.fire(selectAll.node, 'click');
        assert.equal(selectAll.onClick.callCount, 1);
    });

    it('should prevent the default event actions when onClick() is called', () => {
        let selectAll = new this.SelectAll();
        sinon.replace(selectAll, 'toggle', sinon.fake());
        selectAll.constructor(this.node);
        let eventMock = { preventDefault: sinon.fake(), stopPropagation: sinon.fake() };
        selectAll.onClick(eventMock);
        assert.equal(eventMock.preventDefault.callCount, 1);
    });

    it('should stop propagating the event when onClick() is called', () => {
        let selectAll = new this.SelectAll();
        sinon.replace(selectAll, 'toggle', sinon.fake());
        selectAll.constructor(this.node);
        let eventMock = { preventDefault: sinon.fake(), stopPropagation: sinon.fake() };
        selectAll.onClick(eventMock);
        assert.equal(eventMock.stopPropagation.callCount, 1);
    });

    it('should call toggle() when onClick() is called', (done) => {
        let selectAll = new this.SelectAll();
        sinon.replace(selectAll, 'toggle', sinon.fake());
        selectAll.constructor(this.node);
        let eventMock = { preventDefault: sinon.fake(), stopPropagation: sinon.fake() };
        selectAll.onClick(eventMock);

        Utils.delay()
            .then(() => {
                assert.equal(selectAll.toggle.callCount, 1);
                assert.equal(selectAll.toggle.getCall(0).args[0], undefined);
                done()
            });
    });

    it('should trigger a change event on every target when toggle() is called', (done) => {
        let node1 = document.createElement('input');
        let node2 = document.createElement('input');

        sinon.replace(node1, 'dispatchEvent', sinon.fake());
        sinon.replace(node2, 'dispatchEvent', sinon.fake());

        let selectAll = new this.SelectAll();
        sinon.replace(selectAll, 'getTargets', sinon.fake.returns([node1, node2]));
        selectAll.constructor(this.node);

        selectAll.toggle();
        assert.equal(selectAll.getTargets.callCount, 1);

        Utils.delay(100)
            .then(() => {
                assert.equal(node1.dispatchEvent.callCount, 1);
                assert.equal(node2.dispatchEvent.callCount, 1);
                assert.equal(node1.dispatchEvent.getCall(0).args[0].type, 'change');
                assert.equal(node2.dispatchEvent.getCall(0).args[0].type, 'change');
                done();
            })
    });

    it('should set the checked state of this.node to exp if toggle() is called', () => {
        let selectAll = new this.SelectAll();
        sinon.replace(selectAll, 'getTargets', sinon.fake.returns([]));
        selectAll.constructor(this.node);
        selectAll.node.checked = false;
        selectAll.toggle();
        assert.equal(selectAll.node.checked, true);
        selectAll.toggle(true);
        assert.equal(selectAll.node.checked, true);
        selectAll.toggle(false);
        assert.equal(selectAll.node.checked, false);
        selectAll.toggle(true);
        assert.equal(selectAll.node.checked, true);
    });

    it('should return the checked state of node when getState() is called', () => {
        let selectAllNode = document.createElement('input');
        selectAllNode.dataset.selectAll = '.foo, .bar';

        let node1 = document.createElement('input');
        node1.className = 'foo';
        let node2 = document.createElement('input');
        node2.className = 'bar';

        document.body.appendChild(node1);
        document.body.appendChild(node2);

        let selectAll = new this.SelectAll();
        selectAll.constructor(selectAllNode);

        assert.deepEqual(selectAll.getTargets(), [node1, node2]);

        document.body.removeChild(node1);
        document.body.removeChild(node2);
    });
});
