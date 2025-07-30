import {assert} from 'chai';
import {BLOCK_SELECT_ALL, BLOCK_TOGGLE, SELECT_ALLS, TOGGLES} from '../../../js/components/toggle/constants';

describe('toggle/constants.js', function () {
    it('should be able to import constants', () => {
        assert(BLOCK_SELECT_ALL);
        assert(SELECT_ALLS);
        assert(BLOCK_TOGGLE);
        assert(TOGGLES);
    });
});
