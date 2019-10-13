import React, {useRef, useState} from 'react';

const LayoutContext = React.createContext([{}, () => {
}]);

const LayoutProvider = (props) => {
    const defaultState = {};

    const [state, setState] = useState(defaultState);
    
    return (
        <LayoutContext.Provider value={[state, setState]}>
            {props.children}
        </LayoutContext.Provider>
    );
};

export {LayoutContext, LayoutProvider};