import React, {useRef, useState} from 'react';
import FlexLayout from "flexlayout-react";
import {defaultLayout} from "./defaultLayout";

const LayoutContext = React.createContext([{}, () => {
}]);

const LayoutProvider = (props) => {
    const layoutRef = useRef();

    const deleteTab = (tabid) => {
        state.model.doAction(FlexLayout.Actions.deleteTab(tabid));
    };

    const defaultState = {
        model: FlexLayout.Model.fromJson(defaultLayout),
        layout: layoutRef,
        actions: {
            deleteTab: deleteTab
        }
    };

    const [state, setState] = useState(defaultState);
    
    return (
        <LayoutContext.Provider value={[state, setState]}>
            {props.children}
        </LayoutContext.Provider>
    );
};

export {LayoutContext, LayoutProvider};