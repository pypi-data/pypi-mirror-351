import {assert} from 'chai';
import BEM from 'bem.js';
import jsdom from 'jsdom-global';
import simulant from 'simulant';
import sinon from 'sinon';
import {Toggle} from '../../../js/components/toggle/toggle';
import {Utils} from '../../utils';
import {BLOCK_TOGGLE, ELEMENT_INPUT, MODIFIER_OPEN} from '../../../js/components/toggle/constants';

describe('toggle/toggle.js - Toggle ', function () {
    before(() => {
        jsdom();
        this.node = document.createElement('div');
        this.node.className = BEM.getBEMClassName(BLOCK_TOGGLE);
        this.node.dataset.toggleTarget = '.foo';
        this.node.dataset.toggleModifier = 'foo';
        this.target = document.createElement('input');
        this.target.className = 'target';
        document.body.appendChild(this.target);
        this.Toggle = Utils.createTestableClass(Toggle);
    });

    after(() => {
        document.body.removeChild(this.target);
    });

    afterEach(() => {
        sinon.restore();
    });


    it('should construct', () => {
        let toggle = new this.Toggle();
        sinon.replace(toggle, 'bindEvents', sinon.fake());
        toggle.constructor(this.node);
        assert(Toggle);
        assert.equal(toggle.node, this.node);
        assert.equal(toggle.toggleModifier, 'foo');
    });

    it('should set toggleMobileState to true with data-toggle-mobile-state="true"', () => {
        let toggle = new this.Toggle();
        sinon.replace(toggle, 'bindEvents', sinon.fake());
        this.node.dataset.toggleMobileState = 'true';
        toggle.constructor(this.node);
        assert(Toggle);
        assert.equal(toggle.node, this.node);
        assert.equal(toggle.toggleMobileState, true);
    });

    it('should set toggleMobileState to false with data-toggle-mobile-state="false"', () => {
        let toggle = new this.Toggle();
        sinon.replace(toggle, 'bindEvents', sinon.fake());
        this.node.dataset.toggleMobileState = 'false';
        toggle.constructor(this.node);
        assert(Toggle);
        assert.equal(toggle.node, this.node);
        assert.equal(toggle.toggleMobileState, false);
    });

    it('should set toggleMobileState based on data-toggle-mobile-state set to an invalid value', () => {
        let toggle = new this.Toggle();
        sinon.replace(toggle, 'bindEvents', sinon.fake());
        this.node.dataset.toggleMobileState = 'foobar';
        toggle.constructor(this.node);
        assert(Toggle);
        assert.equal(toggle.node, this.node);
        assert.equal(toggle.toggleMobileState, false);
    });

    it('should call bindEvents() when constructor is called', () => {
        let toggle = new this.Toggle();
        sinon.replace(toggle, 'bindEvents', sinon.fake());
        toggle.constructor(this.node);
        assert.equal(toggle.bindEvents.callCount, 1);
    });

    it('should call onClick() when this.node receives click event', () => {
        let toggle = new this.Toggle();
        sinon.spy(toggle, 'onClick');
        toggle.constructor(this.node);
        simulant.fire(toggle.node, 'click');
        assert.equal(toggle.onClick.callCount, 1);
    });

    it('should prevent the default event actions when onClick() is with data-toggle-link-mode set to normal', () => {
        let toggle = new this.Toggle();
        this.node.dataset.toggleLinkMode = 'normal';
        toggle.constructor(this.node);
        let eventMock = { target: toggle.node, preventDefault: sinon.fake(), stopPropagation: sinon.fake() };
        toggle.onClick(eventMock);
        assert.equal(eventMock.preventDefault.callCount, 1);
    });

    it('should prevent the default event actions when onClick() is with data-toggle-link-mode set to positive', () => {
        let toggle = new this.Toggle();
        this.node.dataset.toggleLinkMode = 'positive';
        toggle.constructor(this.node);
        let eventMock = { target: toggle.node, preventDefault: sinon.fake(), stopPropagation: sinon.fake() };
        toggle.onClick(eventMock);
        assert.equal(eventMock.preventDefault.callCount, 1);
    });

    it('should prevent the default event actions when onClick() is with data-toggle-link-mode set to negative', () => {
        let toggle = new this.Toggle();
        this.node.dataset.toggleLinkMode = 'negative';
        toggle.constructor(this.node);
        let eventMock = { target: toggle.node, preventDefault: sinon.fake(), stopPropagation: sinon.fake() };
        toggle.onClick(eventMock);
        assert.equal(eventMock.preventDefault.callCount, 1);
    });

    it('should prevent the default event actions when onClick() is with data-toggle-link-mode set to prevent', () => {
        let toggle = new this.Toggle();
        this.node.dataset.toggleLinkMode = 'prevent';
        toggle.constructor(this.node);
        let eventMock = { target: toggle.node, preventDefault: sinon.fake(), stopPropagation: sinon.fake() };
        toggle.onClick(eventMock);
        assert.equal(eventMock.preventDefault.callCount, 1);
    });

    it('should call toggle() when onClick() is called', (done) => {
        let toggle = new this.Toggle();
        sinon.spy(toggle, 'toggle');
        this.node.dataset.toggleLinkMode = 'normal';
        toggle.constructor(this.node);
        let eventMock = { target: toggle.node, preventDefault: sinon.fake(), stopPropagation: sinon.fake() };
        toggle.onClick(eventMock);

        Utils.delay(100)
            .then(() => {
                assert.equal(toggle.toggle.callCount, 1);
                done();
            })
    });

    it('should call saveState() when onClick() is called', (done) => {
        let toggle = new this.Toggle();
        sinon.spy(toggle, 'saveState');
        this.node.dataset.toggleLinkMode = 'normal';
        toggle.constructor(this.node);
        let eventMock = { target: toggle.node, preventDefault: sinon.fake(), stopPropagation: sinon.fake() };
        toggle.onClick(eventMock);

        Utils.delay(100)
            .then(() => {
                assert.equal(toggle.saveState.callCount, 1);
                done();
            })
    });

    it('should call focus() when onClick() is called', (done) => {
        let toggle = new this.Toggle();
        sinon.spy(toggle, 'focus');
        this.node.dataset.toggleLinkMode = 'normal';
        toggle.constructor(this.node);
        let eventMock = { target: toggle.node, preventDefault: sinon.fake(), stopPropagation: sinon.fake() };
        toggle.onClick(eventMock);

        Utils.delay(100)
            .then(() => {
                assert.equal(toggle.focus.callCount, 1);
                done();
            })
    });

    it('should focus the correct target when focus() is called when data-focus-target is set and getState() returns true', () => {
        let toggle = new this.Toggle();
        sinon.replace(toggle, 'getState', () => true);
        this.node.dataset.focusTarget = '.target';
        toggle.constructor(this.node);
        sinon.spy(this.target, 'focus');
        toggle.focus();
        assert.equal(this.target.focus.callCount, 1);
    });

    it('should not focus the correct target when focus() is called when data-focus-target is not set and getState() returns true', () => {
        let toggle = new this.Toggle();
        sinon.replace(toggle, 'getState', () => true);
        delete this.node.dataset.focusTarget;
        toggle.constructor(this.node);
        sinon.spy(this.target, 'focus');
        toggle.focus();
        assert.equal(this.target.focus.callCount, 0);
    });

    it('should not focus the correct target when focus() is called when data-focus-target is not set and getState() returns false', () => {
        let toggle = new this.Toggle();
        sinon.replace(toggle, 'getState', () => false);
        delete this.node.dataset.focusTarget;
        toggle.constructor(this.node);
        sinon.spy(this.target, 'focus');
        toggle.focus();
        assert.equal(this.target.focus.callCount, 0);
    });

    it('should toggle this.toggleModifier to all targets returns by getTargets()', () => {
        BEM.removeModifier(this.target, 'foo');
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        sinon.replace(toggle, 'getTargets', () => [this.target]);
        sinon.replace(toggle, 'getExclusive', () => []);
        toggle.toggle();
        assert.ok(BEM.hasModifier(this.target, 'foo'));
        toggle.toggle();
        assert.notOk(BEM.hasModifier(this.target, 'foo'));
    });

    it('should add this.toggleModifier to all targets returns by getTargets()', () => {
        BEM.removeModifier(this.target, 'foo');
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        sinon.replace(toggle, 'getTargets', () => [this.target]);
        sinon.replace(toggle, 'getExclusive', () => []);
        toggle.toggle(true);
        assert.ok(BEM.hasModifier(this.target, 'foo'))
        toggle.toggle(true);
        assert.ok(BEM.hasModifier(this.target, 'foo'))
    });

    it('should remove this.toggleModifier to all targets returns by getTargets()', () => {
        BEM.removeModifier(this.target, 'foo');
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        sinon.replace(toggle, 'getTargets', () => [this.target]);
        sinon.replace(toggle, 'getExclusive', () => []);
        toggle.toggle(false);
        assert.notOk(BEM.hasModifier(this.target, 'foo'));
        toggle.toggle(false);
        assert.notOk(BEM.hasModifier(this.target, 'foo'))
    });

    it('should be able to use exclusive toggles', () => {
        let hihatOpen = document.createElement('div');
        hihatOpen.className = 'hihat-open hihat-open--audible hats';
        document.body.appendChild(hihatOpen);
        let hihatClosed = document.createElement('div');
        hihatClosed.className = 'hihat-closed hats';
        document.body.appendChild(hihatClosed);

        let node = document.createElement('div');
        node.dataset.toggleExclusive = '.hats';
        node.dataset.toggleTarget = '.hihat-closed';
        node.dataset.toggleModifier = 'audible';

        let toggle = new this.Toggle();
        toggle.constructor(node);

        assert.ok(BEM.hasModifier(hihatOpen, 'audible'));
        assert.notOk(BEM.hasModifier(hihatClosed, 'audible'));

        toggle.toggle(true);

        assert.notOk(BEM.hasModifier(hihatOpen, 'audible'));
        assert.ok(BEM.hasModifier(hihatClosed, 'audible'));
    });

    it('should return false when getState() is called and the first target does not have this.toggleModifier applied', () => {
        BEM.removeModifier(this.target, 'foo');
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        sinon.replace(toggle, 'getTargets', () => [this.target]);
        assert.equal(toggle.getState(), false);
    });

    it('should return true when getState() is called and the first target does have this.toggleModifier applied', () => {
        BEM.addModifier(this.target, 'foo');
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        sinon.replace(toggle, 'getTargets', () => [this.target]);
        assert.equal(toggle.getState(), true);
    });

    it('should return null when getState() is called and no targets are found', () => {
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        sinon.replace(toggle, 'getTargets', () => []);
        assert.equal(toggle.getState(), null);
    });

    it('should call getRelated() with selector from data-toggle-target when getTargets() is called', () => {
        let toggle = new this.Toggle();
        sinon.spy(toggle, 'getRelated');
        toggle.constructor(this.node);
        toggle.getTargets();
        assert.equal(toggle.getRelated.callCount, 1);
        assert.equal(toggle.getRelated.getCall(0).args[0], '.foo');
    });

    it('should return an empty array if no targets can be found when getRelated() is called', () => {
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        assert.deepEqual(toggle.getRelated('.bar'), []);
    });

    it('should return an array of elements if targets can be found when getRelated() is called', () => {
        let foo = document.createElement('div');
        foo.className = 'foo';
        document.body.appendChild(foo);
        let bar = document.createElement('div');
        bar.className = 'bar';
        document.body.appendChild(bar);
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        assert.deepEqual(toggle.getRelated('.foo, .bar'), [foo, bar]);
    });

    it('should be able to save the state (true) to localStorage using saveState() if id is set on node', () => {
        sinon.spy(localStorage, 'setItem');
        this.node.id = 'node';
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        sinon.replace(toggle, 'getState', () => true);
        toggle.saveState();
        assert.equal(localStorage.setItem.callCount, 1);
        assert.equal(localStorage.setItem.getCall(0).args[0], 'ToggleButton#node.modifierApplied');
        assert.equal(localStorage.setItem.getCall(0).args[1], true);
    });

    it('should be able to save the state (false) to localStorage using saveState() if id is set on node', () => {
        sinon.spy(localStorage, 'setItem');
        this.node.id = 'node';
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        sinon.replace(toggle, 'getState', () => false);
        toggle.saveState();
        assert.equal(localStorage.setItem.callCount, 1);
        assert.equal(localStorage.setItem.getCall(0).args[0], 'ToggleButton#node.modifierApplied');
        assert.equal(localStorage.setItem.getCall(0).args[1], false);
    });

    it('should not save the state to localStorage using saveState() if id is not set on node', () => {
        sinon.spy(localStorage, 'setItem');
        this.node.removeAttribute('id');
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        sinon.replace(toggle, 'getState', () => false);
        toggle.saveState();
        assert.equal(localStorage.setItem.callCount, 0);
    });

    it('should log a warning if saving to localStorage fails when saveState() is called', () => {
        sinon.replace(localStorage, 'setItem', () => { throw new Error('error')});
        sinon.replace(console, 'warn', sinon.fake());
        this.node.id = 'node';
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        sinon.replace(toggle, 'getState', () => false);
        toggle.saveState();
        assert.equal(console.warn.callCount, 1);
        assert.equal(console.warn.getCall(0).args[1], 'Unable to save state to localstorage');
    });

    it('should be able to restore the state (true) using restoreState()', () => {
        this.node.id = 'node';
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        toggle.toggleMobileState = undefined;
        sinon.replace(localStorage, 'getItem', () => 'true');
        sinon.spy(toggle, 'toggle');
        toggle.restoreState();
        assert.equal(toggle.toggle.callCount, 1);
        assert.equal(toggle.toggle.getCall(0).args[0], true);
    });

    it('should be able to restore the state (false) using restoreState()', () => {
        this.node.id = 'node';
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        toggle.toggleMobileState = undefined;
        sinon.replace(localStorage, 'getItem', () => 'false');
        sinon.spy(toggle, 'toggle');
        toggle.restoreState();
        assert.equal(toggle.toggle.callCount, 1);
        assert.equal(toggle.toggle.getCall(0).args[0], false);
    });

    it('should be able to restore the state (invalid) using restoreState()', () => {
        this.node.id = 'node';
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        toggle.toggleMobileState = undefined;
        sinon.replace(localStorage, 'getItem', () => 'foobar');
        sinon.spy(toggle, 'toggle');
        toggle.restoreState();
        assert.equal(toggle.toggle.callCount, 1);
        assert.equal(toggle.toggle.getCall(0).args[0], false);
    });

    it('should not be able to restore the state using restoreState() if no id has been set', () => {
        this.node.removeAttribute('id');
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        toggle.toggleMobileState = undefined;
        sinon.spy(toggle, 'toggle');
        toggle.restoreState();
        assert.equal(toggle.toggle.callCount, 0);
    });

    it('should not be able to restore the state using restoreState() if toggleMobileState is set (false) and a mobile screen size is matched', () => {
        this.node.removeAttribute('id');
        sinon.replace(window, 'matchMedia', () => ({matches: true}));
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        toggle.toggleMobileState = false;
        sinon.spy(toggle, 'toggle');
        toggle.restoreState();
        assert.equal(toggle.toggle.callCount, 1);
        assert.equal(toggle.toggle.getCall(0).args[0], false);
    });

    it('should not be able to restore the state using restoreState() if toggleMobileState is set (true) and a mobile screen size is matched', () => {
        this.node.removeAttribute('id');
        sinon.replace(window, 'matchMedia', () => ({matches: true}));
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        toggle.toggleMobileState = true;
        sinon.spy(toggle, 'toggle');
        toggle.restoreState();
        assert.equal(toggle.toggle.callCount, 1);
        assert.equal(toggle.toggle.getCall(0).args[0], true);
    });

    it('should not log a warning if restoring from localStorage fails when restoreState() is called', () => {
        sinon.replace(localStorage, 'getItem', () => { throw new Error('error')});
        sinon.spy(console, 'warn');
        this.node.id = 'node';
        let toggle = new this.Toggle();
        toggle.constructor(this.node);
        toggle.toggleMobileState = undefined;
        toggle.restoreState();
        assert.equal(console.warn.callCount, 0);
    });
});
