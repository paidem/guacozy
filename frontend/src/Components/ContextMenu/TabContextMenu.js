import React, {useContext} from 'react';

import {contextMenu, Item, Menu, Separator, Submenu} from "react-contexify";

import {SCREEN_SIZES} from "../../settings"
import {AppContext} from "../../Context/AppContext";
import {LayoutContext} from "../../Layout/LayoutContext";
import ShareTicketModal from "../Modals/ShareTicketModal";

// Context menu to be shown when user clicks on tab's name
function TabContextMenu(props) {
    const [appState,] = useContext(AppContext);
    const [layoutState,] = useContext(LayoutContext);

    const isTicketShared = ({event, props}) => {
        let tickets = appState.tickets.filter(t => t.id === props.tabid && !t.parent);
        return tickets.length === 0;
    };

    const duplicateTicket = (originalTicketid, tabName) => {
        appState.actions.duplicateticket(originalTicketid, (ticketid) => {
            appState.actions.activateTicket(ticketid, tabName);
            // update tickets, so ticket list is renewed
            appState.actions.updateTickets();
        })
    };

    // Executes when user selects action in tab's name context menu
    const onTabContextMenuAction = (event, props, action) => {
        // When menu is clicked, it is over other element and we need to stop
        // propagation, otherwise it conflicts with other events
        event.stopPropagation();

        switch (action) {
            case "reconnect":
                layoutState.actions.refreshTab(props.tabid);
                break;
            case "share":
                appState.actions.openModal({type: ShareTicketModal, data: {id: props.tabid, name: props.name}});
                break;
            case "disconnect":
                layoutState.actions.deleteTab(props.tabid);
                break;
            case "duplicate":
                duplicateTicket(props.tabid, props.name);
                break;
            case "screenSize":
                layoutState.actions.updateTabScreenSize(props.tabid, props.screenSize);
                break;
            default:
                window.alert("Wrong action: " + action)
        }
    };

    return (
        <Menu animation="fade" id="tab_context_menu" theme="dark">
            <Item
                onClick={({event, props}) => onTabContextMenuAction(event, props, "reconnect")}>Reconnect</Item>
            <Separator/>
            <Item disabled={isTicketShared}
                  onClick={({event, props}) => onTabContextMenuAction(event, props, "share")}>Share</Item>
            <Separator/>
            <Item disabled={isTicketShared}
                  onClick={({event, props}) => onTabContextMenuAction(event, props, "duplicate")}>Duplicate</Item>
            <Separator/>
            <Item
                onClick={({event, props}) => onTabContextMenuAction(event, props, "disconnect")}>Close</Item>
            <Submenu label="Screen size">
                <Item onClick={({event, props}) => onTabContextMenuAction(event, {
                    ...props,
                    screenSize: null
                }, "screenSize")}>Auto</Item>
                {SCREEN_SIZES.map(size =>
                    <Item onClick={({event, props}) => onTabContextMenuAction(event, {
                        ...props,
                        screenSize: {width: size[0], height: size[1]}
                    }, "screenSize")}>{size[0]} x {size[1]}</Item>
                )
                }
            </Submenu>
        </Menu>
    );
};


export default TabContextMenu;

export const handleTabContextMenuEvent = (e, data) => {
    e.preventDefault();
    contextMenu.show({
        id: "tab_context_menu",
        event: e,
        props: data
    });
};