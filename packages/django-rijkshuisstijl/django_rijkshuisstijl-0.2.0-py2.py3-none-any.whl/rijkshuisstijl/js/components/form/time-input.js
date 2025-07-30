import flatpickr from 'flatpickr';
import {TIME_INPUTS} from './constants';


/**
 * Adds a timepicker to time inputs.
 * @class
 */
class TimeInput {
    /**
     * Constructor method.
     * @param {HTMLInputElement} node
     */
    constructor(node) {
        /** @type {HTMLInputElement} */
        this.node = node;

        this.update();
    }

    /**
     * Returns the placeholder string to use.
     * @return {string}
     */
    getPlaceholderFormat() {
        return this.isTime() ? '00:00' : '';
    }

    /**
     * Returns whether this.node is a time input.
     * @return bBoolean}
     */
    isTime() {
        return this.node.type === 'time';
    }

    /**
     * Updates the placholder (if any) with the format returned by this.getPlaceholderFormat().
     */
    updatePlaceholder() {
        if (!this.node.placeholder) {
            const placeholder = this.getPlaceholderFormat();
            this.node.placeholder = placeholder;
        }
    }

    /**
     * Adds the timepicker.
     */
    update() {
        this.updatePlaceholder();

        flatpickr(this.node, {
            enableTime: true,
            noCalendar: true,
            time_24hr: true
        });
    }
}


// Start!
[...TIME_INPUTS].forEach(node => new TimeInput(node));
