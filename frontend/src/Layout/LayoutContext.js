import React, {useRef, useState} from 'react';
import FlexLayout from "flexlayout-react";
import {defaultLayout} from "./defaultLayout";

const LayoutContext = React.createContext([{}, () => {
}]);

const LayoutProvider = (props) => {
    const layoutRef = useRef();
    
    const defaultState = {
        model: FlexLayout.Model.fromJson(defaultLayout),
        layout: layoutRef,
    };

    const [state, setState] = useState(defaultState);
    
    return (
        <LayoutContext.Provider value={[state, setState]}>
            {props.children}
        </LayoutContext.Provider>
    );
};

export {LayoutContext, LayoutProvider};