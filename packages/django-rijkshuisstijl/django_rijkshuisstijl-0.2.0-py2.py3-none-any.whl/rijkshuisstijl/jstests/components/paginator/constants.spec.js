import {assert} from 'chai';
import {BLOCK_INPUT, BLOCK_PAGINATOR, PAGINATORS} from '../../../js/components/paginator/constants';

describe('paginator/constants.js', function () {
    it('should be able to import constants', () => {
        assert(BLOCK_PAGINATOR);
        assert(BLOCK_INPUT);
        assert(PAGINATORS);
    });
});
