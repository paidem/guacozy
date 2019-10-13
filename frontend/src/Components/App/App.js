import React, {useContext, useEffect} from 'react';

import {Dimmer, Loader} from "semantic-ui-react";

import {AppContext} from "../../Context/AppContext";
import {LayoutContext} from "../../Layout/LayoutContext";

function App() {
    // Context
    const [appState,] = useContext(AppContext);
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
            return (
                <div>
                    Hello {appState.user.username}<br/>
                    <a href="/accounts/logout">Logout</a>
                </div>
            )
        }
    };

    return (
        <div className="App">
            {getContent()}
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
