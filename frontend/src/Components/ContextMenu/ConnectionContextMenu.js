import React, {useContext} from 'react';

import {contextMenu, Item, Menu, Separator} from "react-contexify";
import {AppContext} from "../../Context/AppContext";
import {LayoutContext} from "../../Layout/LayoutContext";

//*************************//
// Connection context menu //
//*************************//


function ConnectionContextMenu(props) {
    const [appState,] = useContext(AppContext);
    const [layoutState,] = useContext(LayoutContext);

    // Connection context menu //
    // Executes when user selects action in tab's name context menu
    const onConnectionContextMenuAction = (event, props, action) => {
        switch (action) {
            case "connect":
                appState.actions.activateConnection(props.id, props.text, appState.user);
                break;
            case "edit":
                layoutState.actions.addIframeTab({url: "/admin/backend/connection/" + props.id + "/change/", name : "*"+props.text});
                break;
            default:
                window.alert("Action not implemented: " + action);
        }
    };


    return (
        <Menu animation="fade" id="connection_context_menu" theme="dark">
            <Item
                onClick={({event, props}) => onConnectionContextMenuAction(event, props, "connect")}>Connect</Item>
            {appState.user && appState.user.is_staff &&
            <Item
                onClick={({event, props}) => onConnectionContextMenuAction(event, props, "edit")}>Edit</Item>
            }
            <Separator/>
        </Menu>
    );
};

export default ConnectionContextMenu;

// Connection context menu //
// Action so handle connection's context menu action
// Activates menu with "connection_context_menu" (ConnectionContextMenu)
export const handleConnectionContextMenuEvent = (e, data) => {
    e.preventDefault();
    contextMenu.show({
        id: "connection_context_menu",
        event: e,
        props: data
    });
};

// *************************** end of Connection context menu ********************************** //