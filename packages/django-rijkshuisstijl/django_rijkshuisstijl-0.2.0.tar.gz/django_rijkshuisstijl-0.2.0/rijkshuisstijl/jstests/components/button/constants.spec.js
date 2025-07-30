import {assert} from 'chai';
import {BLOCK_FAKE_LINK, FAKE_LINKS, MODIFIER_DOUBLE_CLICK} from '../../../js/components/fake-link/constants';

describe('fake-link/constants.js', function () {
    it('should be able to import constants', () => {
       assert(BLOCK_FAKE_LINK);
       assert(MODIFIER_DOUBLE_CLICK);
       assert(FAKE_LINKS);
    });
});
