//jshint ignore:start
import {
    DATE_INPUTS,
    DATE_RANGE_INPUTS,
    FORMS,
    FORM_CONTROLS,
    INPUT_FILEPICKERS,
    LINK_SELECTS,
    SELECTS,
    TIME_INPUTS
} from './constants';

// Start!
if (FORMS.length) {
    import(/* webpackChunkName: 'form' */ './form');
}

if (FORM_CONTROLS.length) {
    import(/* webpackChunkName: 'form-control' */ './form-control');
}

if (DATE_INPUTS.length || DATE_RANGE_INPUTS.length) {
    import(/* webpackChunkName: 'date-input' */ './date-input');
}

if (TIME_INPUTS.length) {
    import(/* webpackChunkName: 'time-input' */ './time-input');
}

if (INPUT_FILEPICKERS.length) {
    import(/* webpackChunkName: 'input-filepicker' */ './input-filepicker');
}

if (SELECTS.length) {
    import(/* webpackChunkName: 'select' */ './select');
}

if (LINK_SELECTS.length) {
    import(/* webpackChunkName: 'link-select' */ './link-select');
}

