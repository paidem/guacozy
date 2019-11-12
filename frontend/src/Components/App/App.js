import React, {useContext, useEffect, useState} from 'react';

import {Dimmer, Loader} from "semantic-ui-react";
import FlexLayout from "flexlayout-react";

import {AppContext} from "../../Context/AppContext";
import {LayoutContext} from "../../Layout/LayoutContext";
import {layoutFactory} from "../../Layout/layoutfactory";
import ConnectionContextMenu from "../ContextMenu/ConnectionContextMenu";
import TabContextMenu from "../ContextMenu/TabContextMenu";
import FolderContextMenu from "../ContextMenu/FolderContextMenu";
import Confirm from "semantic-ui-react/dist/commonjs/addons/Confirm";
import isConnectionSafe from "../../Utils/isConnectionSafe";

function App() {
    // Context
    const [appState, setAppState] = useContext(AppContext);
    const [layoutState,] = useContext(LayoutContext);

    useEffect(() => {
        if (isConnectionSafe() || appState.confirmedUnsafeConnection)
        appState.actions.checkLoginStatus(10);
    }, [appState.actions, appState.confirmedUnsafeConnection]);

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

    const getHttpsWarning = () => {
        if (!isConnectionSafe() && !appState.confirmedUnsafeConnection) {
            return <Confirm
                header='You are accessing application over unsecure connection (http://)'
                content='This is a security risk. Your traffic is unencrypted. Also, clipboard sync will not work.'
                open={true}
                onCancel={() => {window.location.href = 'https:' + window.location.href.substring(window.location.protocol.length);} }
                onConfirm={() => {setAppState(state => ({...state, confirmedUnsafeConnection:true}))}}
                confirmButton={'I understand. Let me in!'}
                cancelButton={'Go to https:'+ window.location.href.substring(window.location.protocol.length)}


            />
        }
        return "HTTPS!";
    };

    return (
        <div className="App">
            {getHttpsWarning()}
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
