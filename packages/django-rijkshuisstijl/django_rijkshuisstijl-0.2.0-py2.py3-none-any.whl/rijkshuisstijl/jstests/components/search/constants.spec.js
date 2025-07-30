import {assert} from 'chai';
import {BLOCK_SEARCH, ELEMENT_INPUT, MODIFIER_OPEN, SEARCHES} from '../../../js/components/search/constants';

describe('search/constants.js', function () {
    it('should be able to import constants', () => {
        assert(BLOCK_SEARCH);
        assert(ELEMENT_INPUT);
        assert(MODIFIER_OPEN);
        assert(SEARCHES);
    });
});
