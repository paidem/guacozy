import React, {useCallback, useContext, useRef, useState} from 'react';
import {Button, Container, Icon, Input, Segment} from "semantic-ui-react";
import './ConnectionSidebar.css'
import ConnectionsTree from "../ConnectionsTree/ConnectionsTree";
import TicketsSegment from "../TicketsSegment/TicketsSegment";
import {AppContext} from "../../../Context/AppContext";
import {LayoutContext} from "../../../Layout/LayoutContext";
import {contextMenu, Item, Menu, Separator} from "react-contexify";
import {tabNameElement} from "../utils/tabutils";

function ConnectionSidebar(props) {
    const [appState,] = useContext(AppContext);
    const [layoutState,] = useContext(LayoutContext);
    const [treeNodeFilterString, setTreeNodeFilterString] = useState("");
    const [treeDraggable, setTreeDragable] = useState(false);
    const searchInputRef = useRef();

    // Use connection id to generate/retrieve ticket  and activate ticket in new tab
    // or find existing tab and focus it
    const activateConnection = useCallback((connectionid, tabName) => {
        appState.actions.createTicket(connectionid, appState.user.id,
            (ticketid) => {
                // Activate ticket (this will focus on existing tab or create new tab)
                layoutState.actions.activateTicket(ticketid, tabNameElement(ticketid, tabName), true);
                // Update tickets list
                appState.actions.updateTickets();
            })
    }, [appState.actions, layoutState.actions, appState.user]);

    //*************************//
    // Connection context menu //
    //*************************//

    // Context menu to be shown when user clicks on connection
    const ConnectionContextMenu = (props) => {
        return (
            <Menu animation="fade" id="connection_context_menu" theme="dark">
                <Item
                    onClick={({event, props}) => onConnectionContextMenuAction(event, props, "connect")}>Connect</Item>
                <Item
                    onClick={({event, props}) => onConnectionContextMenuAction(event, props, "edit")}>Edit</Item>
                <Separator/>
            </Menu>
        );
    };

    // Connection context menu //
    // Executes when user selects action in tab's name context menu
    const onConnectionContextMenuAction = (event, props, action) => {
        switch (action) {
            case "connect":
                activateConnection(props.id, props.text);
                break;
            default:
                window.alert("Action not implemented: " + action);
        }
    };

    // Connection context menu //
    // Action so handle connection's context menu action
    // Activates menu with "connection_context_menu" (ConnectionContextMenu)
    const handleConnectionContextMenuEvent = (e, data) => {
        e.preventDefault();
        contextMenu.show({
            id: "connection_context_menu",
            event: e,
            props: data
        });
    };

    /***
     * Takes node and returns it's representation. By default representation is just text
     * but here we use it mainly to bind to onDoubleClick event when clicking on connection node
     * @param node
     * @returns {*}
     */
    const nodeTitleConstructor = (node) => {
        if (node.isFolder) {
            return <span>{node.text}</span>
        } else {
            return <span
                onDoubleClick={() => activateConnection(node.id, node.text)}
                onContextMenu={(e) => {
                    handleConnectionContextMenuEvent(e, {
                        id: node.id.toString(),
                        text: node.text
                    })
                }}
            >{node.text}</span>
        }
    };

    const tabTitleConstructor = (ticketUUID, tabName) => (
        <span>{tabName}</span>
    );

    return (
        <Container className='sidebarContainer'>
            <Segment className='searchInputSegment' raised color='blue'>
                <Input size='small' fluid icon placeholder='Search...'
                       value={treeNodeFilterString}
                       onChange={(event) => {
                           setTreeNodeFilterString(event.target.value)
                       }}
                       onKeyDown={(event) => {
                           // Handle Esc button to clear
                           let code = event.charCode || event.keyCode;
                           code === 27 && setTreeNodeFilterString("")
                       }}
                       ref={searchInputRef}>
                    <input/>
                    <Icon name='times circle outline' size='large' link
                          onClick={() => setTreeNodeFilterString("")}/>
                </Input>
            </Segment>
            <Segment raised color='grey' className='connectionList'>
                <Button icon='refresh'
                        color='grey'
                        basic inverted
                        size='mini'
                        title='Reload'
                        className='topButton'
                        loading={appState.connectionsLoading || appState.ticketsLoading}
                        onClick={() => {
                            appState.actions.updateConnections();
                            appState.actions.updateTickets();
                        }
                        }
                />
                <Button icon='bars'
                        color={treeDraggable ? 'green' : 'grey'}
                        basic
                        size='mini'
                        title='Rearrange'
                        className='topButton'
                        onClick={() => setTreeDragable(!treeDraggable)}
                />
                <ConnectionsTree searchString={treeNodeFilterString}
                                 draggable={treeDraggable}
                                 nodeTitleConstructor={nodeTitleConstructor}
                                 disableDraggebleMode={() => {
                                     setTreeDragable(false)
                                 }}
                />
            </Segment>
            <Segment raised color='grey' className='ticketList'>
                <TicketsSegment
                    searchString={treeNodeFilterString}
                    tabTitleConstructor={tabTitleConstructor}
                />
            </Segment>
            <ConnectionContextMenu/>
        </Container>
    );
}

export default ConnectionSidebar;