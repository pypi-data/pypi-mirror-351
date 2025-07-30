import {assert} from 'chai';
import {
    BLOCK_NAVIGATION_BAR,
    BLOCK_VIEW,
    MODIFIER_MENU_OPEN} from '../../../js/components/view/constants';

describe('toggle/constants.js', function () {
    it('should be able to import constants', () => {
        assert(BLOCK_VIEW);
        assert(MODIFIER_MENU_OPEN);
        assert(BLOCK_NAVIGATION_BAR);
    });
});
