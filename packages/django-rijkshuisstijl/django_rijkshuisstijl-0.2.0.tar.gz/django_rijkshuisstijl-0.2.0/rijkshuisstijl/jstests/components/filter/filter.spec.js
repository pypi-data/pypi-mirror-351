import {assert} from 'chai';
import BEM from 'bem.js';
import jsdom from 'jsdom-global';
import simulant from 'simulant';
import sinon from 'sinon';
import {Filter} from '../../../js/components/filter/filter';
import {
    BLOCK_FILTER,
    ELEMENT_INPUT,
    MODIFIER_CLASS_ONLY,
    MODIFIER_MATCH,
    MODIFIER_NO_MATCH
} from '../../../js/components/filter/constants';
import {Utils} from '../../utils';

describe('filter/filter.js - Filter ', function () {
    before(() => {
        jsdom();
        this.node = document.createElement('div');
        this.node.className = BEM.getBEMClassName(BLOCK_FILTER);
        this.node.dataset.filterTarget = '.target';
        this.input = document.createElement('input');
        this.input.className = BEM.getBEMClassName(BLOCK_FILTER, ELEMENT_INPUT);
        this.node.appendChild(this.input);
        this.target = document.createElement('div');
        this.target.innerHTML = '<p>lorem ipsum...</p>';
        this.target.className = 'target';
        this.target2 = document.createElement('div');
        this.target2.innerHTML = '<p>dolor sit amet...</p>';
        this.target2.className = 'target';
        document.body.appendChild(this.target);
        document.body.appendChild(this.target2);
        this.Filter = Utils.createTestableClass(Filter);
    });

    after(() => {
        document.body.removeChild(this.target);
        document.body.removeChild(this.target2);
    });

    afterEach(() => {
        sinon.restore();
    });

    it('should construct', () => {
        let filter = new this.Filter();
        sinon.replace(filter, 'bindEvents', sinon.fake());
        sinon.replace(filter, 'applyFilter', sinon.fake());
        filter.constructor(this.node);
        assert(Filter);
        assert.equal(filter.node, this.node);
        assert.equal(filter.input, this.input);
    });

    it('should call bindEvents() when constructor is called', () => {
        let filter = new this.Filter();
        sinon.replace(filter, 'bindEvents', sinon.fake());
        filter.constructor(this.node);
        assert.equal(filter.bindEvents.callCount, 1);
    });

    it('should call filter() when this.node receives input event', () => {
        let filter = new this.Filter();
        sinon.spy(filter, 'filter');
        filter.constructor(this.node);
        simulant.fire(filter.node, 'input');
        assert.equal(filter.filter.callCount, 1);
    });

    it('should call applyFilter() when filter is called and when input.value is set', () => {
        let filter = new this.Filter();
        sinon.spy(filter, 'applyFilter');
        filter.node = this.node;
        filter.input = this.input;
        filter.input.value = '';
        filter.filter();
        assert.equal(filter.applyFilter.callCount, 0);
        filter.input.value = 'foo';
        filter.filter();
        assert.equal(filter.applyFilter.callCount, 1);
    });

    it('should call discardFilter() when filter is called and when input.value is not set', () => {
        let filter = new this.Filter();
        sinon.spy(filter, 'discardFilter');
        filter.node = this.node;
        filter.input = this.input;
        filter.input.value = 'foo';
        filter.filter();
        assert.equal(filter.discardFilter.callCount, 0);
        filter.input.value = '';
        filter.filter();
        assert.equal(filter.discardFilter.callCount, 1);
    });

    it('should show matches when applyFilter is called', (done) => {
        let filter = new this.Filter();
        sinon.replace(filter, 'bindEvents', sinon.fake());
        sinon.replace(filter, 'applyFilter', sinon.fake());
        filter.constructor(this.node);
        filter.input.value = 'lorem';
        filter.applyFilter();

        Utils.delay()
            .then(() => {
                assert.ok(BEM.hasModifier(this.target, MODIFIER_MATCH));
                assert.notOk(this.target.style.display);
                assert.ok(BEM.hasModifier(this.target2, MODIFIER_NO_MATCH));
                assert.equal(this.target2.style.display, 'none');
                done()
            });
    });

    it('should discard matches when applyFilter is discardFilter', () => {
        let filter = new this.Filter();
        sinon.replace(filter, 'bindEvents', sinon.fake());
        sinon.replace(filter, 'applyFilter', sinon.fake());
        filter.constructor(this.node);

        BEM.addModifier(this.target, MODIFIER_MATCH);
        this.target.style.removeProperty('display');
        BEM.addModifier(this.target2, MODIFIER_NO_MATCH);
        this.target2.style.display = 'none';

        filter.discardFilter();

        assert.ok(BEM.hasModifier(this.target, MODIFIER_MATCH));
        assert.notOk(this.target.style.display);
        assert.ok(BEM.hasModifier(this.target2, MODIFIER_MATCH));
        assert.notOk(this.target2.style.display);
    });

    it('should not apply display changes MODIFIER_CLASS_ONLY is present', (done) => {
        let node = document.createElement('div');
        node.className = BEM.getBEMClassName(BLOCK_FILTER);
        BEM.addModifier(node, MODIFIER_CLASS_ONLY);
        node.dataset.filterTarget = '.target';
        let input = document.createElement('input');
        input.className = BEM.getBEMClassName(BLOCK_FILTER, ELEMENT_INPUT);
        node.appendChild(this.input);
        let target = document.createElement('div');
        target.innerHTML = '<p>lorem ipsum...</p>';
        target.className = 'target';
        let target2 = document.createElement('div');
        target2.innerHTML = '<p>dolor sit amet...</p>';
        target2.className = 'target';
        document.body.appendChild(target);
        document.body.appendChild(target2);

        let filter = new Filter(node);
        filter.input.value = 'lorem';
        filter.applyFilter();

        Utils.delay(200)
            .then(() => {
                BEM.removeModifier(node, MODIFIER_CLASS_ONLY);
                document.body.removeChild(target)
                document.body.removeChild(target2)

                assert.ok(BEM.hasModifier(target, MODIFIER_MATCH));
                assert.notOk(target.style.display);
                assert.ok(BEM.hasModifier(target2, MODIFIER_NO_MATCH));
                assert.notOk(target2.style.display);
                done()
            });
    });
});
