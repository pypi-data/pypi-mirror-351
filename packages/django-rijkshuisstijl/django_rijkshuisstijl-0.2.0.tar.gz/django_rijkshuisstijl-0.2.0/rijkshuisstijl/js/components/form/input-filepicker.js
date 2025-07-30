import {INPUT_FILEPICKERS} from './constants';


/**
 * Updates label on input file picker.
 * @class
 */
class InputFilePicker {
    /**
     * Constructor method.
     * @param {HTMLLabelElement} node
     */
    constructor(node) {
        /** @type {HTMLLabelElement} */
        this.node = node;

        /** @type {HTMLInputElement} */
        this.input = this.node.previousElementSibling;

        this.bindEvents();
    }

    /**
     * Returns the name of the selected file or an empty string.
     * @return {string}
     */
    getFileName() {
        if (this.input.files.length) {
            return this.input.files[0].name;
        }
        return '';
    }

    /**
     * Binds events to callbacks.
     */
    bindEvents() {
        this.input.addEventListener('change', this.update.bind(this));
    }

    /**
     * Updates the textcontent of the input file picker with the input's selected file name.
     */
    update() {
        this.node.textContent = this.getFileName();
    }
}


// START!
[...INPUT_FILEPICKERS].forEach(node => new InputFilePicker(node));
