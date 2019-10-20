import React, {useContext, useEffect} from 'react';

import {Dimmer, Loader} from "semantic-ui-react";
import FlexLayout from "flexlayout-react";

import {AppContext} from "../../Context/AppContext";
import {LayoutContext} from "../../Layout/LayoutContext";
import {layoutFactory} from "../../Layout/layoutfactory";
import ConnectionContextMenu from "../ContextMenu/ConnectionContextMenu";
import TabContextMenu from "../ContextMenu/TabContextMenu";
import FolderContextMenu from "../ContextMenu/FolderContextMenu";

function App() {
    // Context
    const [appState, setAppState] = useContext(AppContext);
    const [layoutState,] = useContext(LayoutContext);

    useEffect(() => {
        appState.actions.checkLoginStatus(10);
    }, [appState.actions]);

    const getContent = () => {
        if (!appState.user) {
            return (
                <Dimmer active={appState.user == null}>
                    <Loader>
                        Loading<br/>
                        {appState.apiError}
                    </Loader>
                </Dimmer>
            )
        } else {
            return <FlexLayout.Layout ref={layoutState.layout} model={layoutState.model} factory={layoutFactory}/>
        }
    };

    return (
        <div className="App">
            {getContent()}
            <FolderContextMenu/>
            <ConnectionContextMenu/>
            <TabContextMenu/>
            {appState.activeModal}
            <Dimmer active={appState.user == null}>
                <Loader>
                    Loading<br/>
                    {appState.apiError}
                </Loader>
            </Dimmer>
        </div>
    );
}

export default App;
