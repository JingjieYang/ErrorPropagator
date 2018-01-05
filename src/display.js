import React, {Component} from 'react';
import {Tex} from 'react-tex';
import PropTypes from 'prop-types';


class LatexDisplay extends Component {
    render() {
        let contents = this.props.contents.filter((x) => x);
        let visible = contents.length >= (this.props.minItemsRequired || 1);
        contents = contents.join(this.props.connector || ' = ')
            .replace(/\\operatorname/g, '')
            .replace(/\\substack/g, '');
        return <div className={visible ? "" : "hidden"}><Tex texContent={contents}/></div>
    }
}

LatexDisplay.propTypes = {
    contents: PropTypes.arrayOf(PropTypes.string),
    connector: PropTypes.string,
    minItemsRequired: PropTypes.number
};

export default LatexDisplay;
