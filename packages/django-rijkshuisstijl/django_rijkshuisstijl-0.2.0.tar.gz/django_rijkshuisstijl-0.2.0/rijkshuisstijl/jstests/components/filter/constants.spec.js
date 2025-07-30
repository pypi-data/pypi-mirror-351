import {assert} from 'chai';
import {
    BLOCK_FILTER,
    ELEMENT_INPUT, FILTERS,
    MODIFIER_FILTER,
    MODIFIER_MATCH,
    MODIFIER_NO_MATCH
} from '../../../js/components/filter/constants';

describe('filter/constants.js', function () {
    it('should be able to import constants', () => {
        assert(BLOCK_FILTER);
        assert(ELEMENT_INPUT);
        assert(MODIFIER_FILTER);
        assert(MODIFIER_MATCH);
        assert(MODIFIER_NO_MATCH);
        assert(FILTERS);
    });
});
