import React, {useState} from 'react';

const AppContext = React.createContext([{}, () => {
}]);

const AppProvider = (props) => {

    const defaultState = {
        
    };
    
    const [state, setState] = useState(defaultState);

    return (
        <AppContext.Provider value={[state, setState]}>
            {props.children}
        </AppContext.Provider>
    );
};

export {AppContext, AppProvider};