import {assert} from 'chai';
import {BLOCK_BUTTON, MODIFIER_PRIMARY, MODIFIER_SECONDARY} from '../../../js/components/button/constants';

describe('fake-link/constants.js', function () {
    it('should be able to import constants', () => {
       assert(BLOCK_BUTTON);
       assert(MODIFIER_PRIMARY);
       assert(MODIFIER_SECONDARY);
    });
});
