import PropTypes from 'prop-types'

const Button = ({color, text, className, onClick}) => {
    return <button onClick={onClick} style={{backgroundColor: color}} className={className}>{text}</button>
}

Button.defaultProps = {
    color: 'black'
}

Button.propTypes = {
    text: PropTypes.string,
    color: PropTypes.string,
    className: PropTypes.string,
    onClick: PropTypes.func,
}

export default Button
